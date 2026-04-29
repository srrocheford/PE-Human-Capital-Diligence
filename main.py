"""
PE Human Capital Diligence — FastAPI Backend
=============================================
Endpoints:
  GET  /                      health check
  GET  /firms                 list all registered firms
  POST /scrape/{firm_slug}    kick off a scrape job (returns job_id immediately)
  GET  /jobs/{job_id}         poll job status; includes data + GitHub URL when done
  GET  /firms/{firm_slug}     fetch cached data from GitHub (no scrape triggered)

Environment variables (set in Railway dashboard):
  GITHUB_TOKEN   — classic PAT with repo scope
  GITHUB_OWNER   — srrocheford
  GITHUB_REPO    — PE-Human-Capital-Diligence
"""

import os, json, uuid, base64, traceback
from datetime import datetime, timezone

import requests as http_requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from firms_registry import get_firm, list_firms
from pe_scraper_general import run as run_scraper, scrape_fund_history

# ─────────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PE Human Capital Diligence API",
    description="Scrapes Wayback Machine snapshots to track PE firm team changes over time.",
    version="1.0.0",
)

# Allow all origins so Lovable (and any future frontend) can call freely.
# Tighten to your Lovable domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store — resets on dyno restart, fine for a research tool.
# Replace with Redis if you need persistence across restarts.
jobs: dict[str, dict] = {}

# GitHub config
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "srrocheford")
GITHUB_REPO  = os.environ.get("GITHUB_REPO",  "PE-Human-Capital-Diligence")
GITHUB_BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"


# ─────────────────────────────────────────────────────────────────────────────
# GITHUB HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _gh_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def push_json_to_github(filename: str, data: dict, commit_msg: str) -> str:
    """
    Create or update a file in the GitHub repo via the Contents API.
    Returns the raw GitHub URL for the file.
    """
    content_b64 = base64.b64encode(
        json.dumps(data, indent=2, default=str).encode()
    ).decode()

    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{filename}"

    # Fetch existing SHA (required to update an existing file)
    existing = http_requests.get(url, headers=_gh_headers())
    sha = existing.json().get("sha") if existing.status_code == 200 else None

    payload = {
        "message": commit_msg,
        "content": content_b64,
        "branch":  GITHUB_BRANCH,
        "committer": {
            "name":  "PE Diligence Bot",
            "email": "bot@pe-diligence.com",
        },
    }
    if sha:
        payload["sha"] = sha

    r = http_requests.put(url, headers=_gh_headers(), json=payload)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"GitHub push failed: {r.status_code} — {r.text[:300]}")

    return f"{RAW_BASE}/{filename}"


def fetch_from_github(filename: str) -> dict | None:
    """Fetch an already-scraped JSON file from GitHub raw URL."""
    url = f"{RAW_BASE}/{filename}"
    r = http_requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None


# ─────────────────────────────────────────────────────────────────────────────
# BACKGROUND TASK
# ─────────────────────────────────────────────────────────────────────────────

def _do_scrape(job_id: str, firm_slug: str) -> None:
    """Runs in the background. Scrapes, pushes to GitHub, updates job store."""
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()

    cfg = get_firm(firm_slug).copy()
    tmp_path = f"/tmp/{firm_slug}_human_capital.json"
    cfg["output_file"] = tmp_path

    try:
        output = run_scraper(cfg)

        if output is None:
            raise RuntimeError("Scraper returned no data — check Wayback availability.")

        filename   = f"{firm_slug}_human_capital.json"
        commit_msg = (
            f"Update {cfg['firm_name']} data — "
            f"{output['summary']['unique_people']} people, "
            f"{len(output['years_covered'])} years scraped"
        )
        raw_url = push_json_to_github(filename, output, commit_msg)

        jobs[job_id].update({
            "status":       "done",
            "finished_at":  datetime.now(timezone.utc).isoformat(),
            "github_url":   raw_url,
            "summary":      output["summary"],
            "years_covered": output["years_covered"],
        })

    except Exception as e:
        jobs[job_id].update({
            "status":      "failed",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "error":       str(e),
            "traceback":   traceback.format_exc(),
        })


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {
        "status":  "ok",
        "service": "PE Human Capital Diligence API",
        "version": "1.0.0",
        "firms_registered": len(list_firms()),
    }


@app.get("/firms")
def get_firms():
    """List all registered firms with their slugs and coverage start years."""
    return {"firms": list_firms()}


@app.post("/scrape/{firm_slug}")
def trigger_scrape(firm_slug: str, background_tasks: BackgroundTasks):
    """
    Kick off a scrape for a registered firm.
    Returns a job_id immediately — poll GET /jobs/{job_id} for status.
    Scraping typically takes 2–5 minutes.
    """
    cfg = get_firm(firm_slug)
    if not cfg:
        raise HTTPException(
            status_code=404,
            detail=f"Firm '{firm_slug}' not found. Call GET /firms for the list."
        )
    if not cfg.get("configured", False):
        raise HTTPException(
            status_code=400,
            detail=f"'{cfg['firm_name']}' is registered but not yet configured for scraping. Check back soon."
        )

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id":     job_id,
        "firm_slug":  firm_slug,
        "firm_name":  cfg["firm_name"],
        "status":     "queued",
        "queued_at":  datetime.now(timezone.utc).isoformat(),
    }

    background_tasks.add_task(_do_scrape, job_id, firm_slug)

    return {
        "job_id":    job_id,
        "firm_slug": firm_slug,
        "status":    "queued",
        "poll_url":  f"/jobs/{job_id}",
        "message":   "Scraping started. Poll /jobs/{job_id} every 15s for status.",
    }


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    """
    Poll this endpoint after calling POST /scrape/{firm_slug}.
    Status values: queued → running → done | failed
    When done, the response includes github_url (raw JSON) and a summary.
    """
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@app.get("/firms/{firm_slug}")
def get_firm_data(firm_slug: str):
    """
    Return already-scraped data for a firm directly from GitHub (no new scrape).
    Returns 404 if the firm hasn't been scraped yet.
    """
    cfg = get_firm(firm_slug)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Firm '{firm_slug}' not in registry.")

    filename = f"{firm_slug}_human_capital.json"
    data = fetch_from_github(filename)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No scraped data found for '{firm_slug}'. Run POST /scrape/{firm_slug} first."
        )
    return data


@app.get("/fund-history/{firm_slug}")
def get_fund_history(firm_slug: str):
    """
    Return the manually curated fund history for a firm from the registry.
    Includes fund_size_per_head if headcount data is already cached on GitHub.
    Does NOT trigger a new press-release scrape (use POST /scrape-fund-history/{firm_slug} for that).
    """
    cfg = get_firm(firm_slug)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Firm '{firm_slug}' not in registry.")

    fund_history = cfg.get("fund_history_manual", [])

    # Attempt to enrich with cached headcount data for fund_size_per_head calc
    from pe_scraper_general import compute_fund_size_per_head
    fund_size_per_head = []
    filename = f"{firm_slug}_human_capital.json"
    cached = fetch_from_github(filename)
    if cached and fund_history:
        hc_rows = cached.get("headcount_by_year", [])
        fund_size_per_head = compute_fund_size_per_head(hc_rows, fund_history)

    return {
        "firm_slug":          firm_slug,
        "firm_name":          cfg["firm_name"],
        "fund_history":       fund_history,
        "fund_size_per_head": fund_size_per_head,
    }


def _do_scrape_fund_history(job_id: str, firm_slug: str) -> None:
    """Background task: scrapes press releases for fund close data."""
    jobs[job_id]["status"] = "running"
    jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    cfg = get_firm(firm_slug)
    try:
        results = scrape_fund_history(cfg)
        jobs[job_id].update({
            "status":       "done",
            "finished_at":  datetime.now(timezone.utc).isoformat(),
            "fund_history": results,
            "count":        len(results),
        })
    except Exception as e:
        jobs[job_id].update({
            "status":      "failed",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "error":       str(e),
        })


@app.post("/scrape-fund-history/{firm_slug}")
def trigger_fund_history_scrape(firm_slug: str, background_tasks: BackgroundTasks):
    """
    Kick off a press-release scrape to auto-discover fund close dates and sizes.
    Searches the firm's own Wayback-archived news pages + PR Newswire/BusinessWire.
    Returns a job_id — poll GET /jobs/{job_id} for results (typically 1–3 min).
    """
    cfg = get_firm(firm_slug)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Firm '{firm_slug}' not in registry.")

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id":    job_id,
        "firm_slug": firm_slug,
        "firm_name": cfg["firm_name"],
        "status":    "queued",
        "type":      "fund_history",
        "queued_at": datetime.now(timezone.utc).isoformat(),
    }
    background_tasks.add_task(_do_scrape_fund_history, job_id, firm_slug)
    return {
        "job_id":   job_id,
        "status":   "queued",
        "poll_url": f"/jobs/{job_id}",
        "message":  "Fund history scrape started. Poll /jobs/{job_id} for results.",
    }
