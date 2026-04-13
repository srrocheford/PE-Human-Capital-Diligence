#!/usr/bin/env python3
"""
PE Human Capital Tracker — General-Purpose Scraper
===================================================
Three-tier data collection strategy per year:
  Tier 1 (best):  Archived JSON API endpoint  → clean structured data, titles always present
  Tier 2:         Archived HTML page           → regex extraction, may or may not have titles
  Tier 3 (TODO):  Live site via Playwright     → current snapshot only, no history

To onboard a new firm, fill out FIRM_CONFIG at the bottom of this file.
No other code changes needed.

Usage:
    python pe_scraper_general.py

Requires: requests, pandas
"""

import re, time, json
from datetime import datetime
import requests
import pandas as pd

CDX_API = "https://web.archive.org/cdx/search/cdx"


# ─────────────────────────────────────────────────────────────────────────────
# FIRM CONFIGURATION  (edit this section per firm)
# ─────────────────────────────────────────────────────────────────────────────

FIRM_CONFIG = {
    # ── Identity ──────────────────────────────────────────────────────────────
    "firm_name": "Water Street Healthcare Partners",
    "firm_slug": "water-street-healthcare-partners",
    "start_year": 2012,
    "output_file": "/sessions/vibrant-blissful-galileo/mnt/DSAIL Project/waterstreet_human_capital.json",

    # ── Tier 1: JSON API sources ───────────────────────────────────────────────
    # List of API endpoints to search for archived JSON snapshots.
    # For each domain, we query Wayback CDX for application/json responses.
    # If multiple endpoints match, list them in preference order.
    # 'field_map' maps the API's field names to our canonical fields:
    #   name_first, name_last, name_full, title, role_slug, role_name
    "api_sources": [
        {
            "domain":        "waterstreet.com",
            "endpoint":      "waterstreet.com/api/people.json",  # exact URL to fetch
            "data_path":     "data",                             # key in response JSON containing the list
            "field_map": {
                "name_first": "firstName",
                "name_last":  "lastName",
                "title":      "title",
                "role_slug":  "role.slug",   # dot-notation for nested fields
            },
            # Maps role slugs from the API → our canonical function names
            "function_map": {
                "investment-team": "Investment Partners",
                "associates":      "Associates",
                "operating-team":  "Operating Resources",
                "corporate-team":  "Corporate Resources",
                "internal-operations": "Corporate Resources",
            },
        }
    ],

    # ── Tier 2: HTML sources ───────────────────────────────────────────────────
    # List of HTML pages to scrape.  Each entry needs:
    #   'base_url'    : the archived URL to query CDX for
    #   'extractor'   : name of a registered HTML extractor function (see EXTRACTORS below)
    #   'function_map': maps whatever the site uses (slugs, CSS classes) → canonical function names
    "html_sources": [
        {
            "base_url":  "waterstreet.com/our-people/",
            "extractor": "li_class_name_title",   # see EXTRACTORS dict below
            "function_map": {
                "investment-partners": "Investment Partners",
                "associates":          "Associates",
                "operating-partners":  "Operating Resources",
                "operating-resources": "Operating Resources",
                "advisors":            "Executive Advisors",
                "corporate-resources": "Corporate Resources",
                "support-team":        "Support Team",
                "executive-advisors":  "Executive Advisors",
            },
        },
    ],

    # ── Function display order ─────────────────────────────────────────────────
    "function_order": [
        "Investment Partners", "Associates", "Operating Resources",
        "Executive Advisors", "Corporate Resources", "Support Team", "Other",
    ],

    # ── Coverage note (shown in output) ───────────────────────────────────────
    "coverage_note": (
        "Tier 1 (JSON API): 2020, 2025 via waterstreet.com/api/people.json. "
        "Tier 2 (HTML): 2013–2019 via waterstreet.com/our-people/. "
        "2020+ /people/ page is JS-rendered and yields no HTML data."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# SENIORITY LEVELS  (shared across all firms for promotion detection)
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_ORDER = {
    "analyst":            1,
    "associate":          2,
    "senior associate":   3,
    "vice president":     3,
    "vp":                 3,
    "principal":          4,
    "managing director":  5,
    "md":                 5,
    "partner":            6,
    "managing partner":   7,
    "co-founder":         8,
    "president":          8,
    "chief":              8,
    "operating partner":  5,
    "executive advisor":  6,
    "senior advisor":     5,
    "ceo":                7,
    "coo":                7,
    "cfo":                7,
    "cmo":                6,
    "cio":                5,
}


# ─────────────────────────────────────────────────────────────────────────────
# HTML EXTRACTORS  (add new patterns here for new site types)
# ─────────────────────────────────────────────────────────────────────────────

def extractor_li_class_name_title(html: str, function_map: dict) -> list[dict]:
    """
    Water Street / similar sites:
      <li class="associates">
        <a href="...">
          <span class="name">Rob George</span>
          <span class="title">Associate</span>
        </a>
      </li>
    """
    pattern = (
        r'<li\s+class="([^"]+)"[^>]*>\s*'
        r'<a\s+href="[^"]*"[^>]*>.*?'
        r'<span\s+class="name">([^<]+)</span>\s*'
        r'<span\s+class="title">([^<]+)</span>'
    )
    people = []
    for func_cls, raw_name, raw_title in re.findall(pattern, html, re.DOTALL):
        func_cls = func_cls.strip()
        if func_cls not in function_map:
            continue
        name = normalize_name(raw_name)
        if not name or len(name) < 3:
            continue
        people.append({
            "name":     name,
            "title":    raw_title.strip(),
            "function": function_map[func_cls],
            "tier":     "html",
        })
    return people


def extractor_option_value_slug(html: str, function_map: dict) -> list[dict]:
    """
    Linden / dropdown sites:
      <option value="/team/investment-team/john-doe/">John Doe</option>
    Function comes from the URL slug, no title available.
    """
    pattern = r'<option\s+value="[^"]+/team/([^/"]+)/[^/"]+/">\s*([^<]+?)\s*</option>'
    people = []
    for func_slug, raw_name in re.findall(pattern, html, re.DOTALL):
        if func_slug not in function_map:
            continue
        name = normalize_name(raw_name)
        if not name or len(name) < 3:
            continue
        people.append({
            "name":     name,
            "title":    None,
            "function": function_map[func_slug],
            "tier":     "html",
        })
    return people


def extractor_article_h3_paragraph(html: str, function_map: dict,
                                   title_function_map: dict | None = None,
                                   article_class: str = "half_article",
                                   heading_class: str = "half_article-heading") -> list[dict]:
    """
    HGGC / flat-list sites (no function sections on page):
      <article class="half_article epsilon">
        <header class="half_article-heading">
          <h3>Bryan Adams</h3>
          <p>Senior Advisor</p>
        </header>
      </article>

    Since function is not encoded in the HTML structure, it's inferred from
    the title via title_function_map (regex patterns → function name).
    function_map is ignored here (kept for API compatibility).
    """
    # Grab each article block
    art_pattern = (
        r'<article[^>]*class="[^"]*' + re.escape(article_class) + r'[^"]*"[^>]*>'
        r'(.*?)</article>'
    )
    # Within each article, find the heading block
    hdr_pattern = (
        r'<header[^>]*class="[^"]*' + re.escape(heading_class) + r'[^"]*"[^>]*>'
        r'.*?<h3[^>]*>\s*([^<]+?)\s*</h3>'
        r'.*?<p[^>]*>\s*([^<]*?)\s*</p>'
    )

    people = []
    for art_body in re.findall(art_pattern, html, re.DOTALL):
        m = re.search(hdr_pattern, art_body, re.DOTALL)
        if not m:
            continue
        raw_name  = m.group(1).strip()
        raw_title = m.group(2).strip()
        name = normalize_name(raw_name)
        if not name or len(name) < 3:
            continue
        func = _infer_function_from_title(raw_title, title_function_map)
        people.append({
            "name":     name,
            "title":    raw_title or None,
            "function": func,
            "tier":     "html",
        })
    return people


def extractor_div_name_title(html: str, function_map: dict,
                             title_function_map: dict | None = None,
                             wrapper_class: str = "team-member",
                             name_class: str = "team-member__name",
                             title_class: str = "team-member__title") -> list[dict]:
    """
    Generic BEM-style team card:
      <div class="team-member">
        <h3 class="team-member__name">Jane Smith</h3>
        <p class="team-member__title">Principal</p>
      </div>

    Covers Audax, LLR-style sites. Configurable class names via html_source.
    function_map is ignored; function inferred from title_function_map.
    """
    card_pattern = (
        r'<(?:div|article|li)[^>]*class="[^"]*' + re.escape(wrapper_class) + r'[^"]*"[^>]*>'
        r'(.*?)</(?:div|article|li)>'
    )
    name_pat  = r'class="[^"]*' + re.escape(name_class)  + r'[^"]*"[^>]*>\s*([^<]+?)\s*<'
    title_pat = r'class="[^"]*' + re.escape(title_class) + r'[^"]*"[^>]*>\s*([^<]*?)\s*<'

    people = []
    for block in re.findall(card_pattern, html, re.DOTALL):
        nm = re.search(name_pat,  block, re.DOTALL)
        tt = re.search(title_pat, block, re.DOTALL)
        if not nm:
            continue
        raw_name  = nm.group(1).strip()
        raw_title = tt.group(1).strip() if tt else ""
        name = normalize_name(raw_name)
        if not name or len(name) < 3:
            continue
        func = _infer_function_from_title(raw_title, title_function_map)
        people.append({
            "name":     name,
            "title":    raw_title or None,
            "function": func,
            "tier":     "html",
        })
    return people


def _infer_function_from_title(title: str, title_function_map: dict | None) -> str:
    """
    Given a title string and a {regex_pattern: function_name} map,
    return the first matching function name, or 'Other' if no match.
    Comparison is case-insensitive.
    """
    if not title_function_map or not title:
        return "Other"
    t = title.lower()
    for pattern, func in title_function_map.items():
        if re.search(pattern, t, re.IGNORECASE):
            return func
    return "Other"


# Registry — add new extractor functions here
EXTRACTORS = {
    "li_class_name_title":   extractor_li_class_name_title,
    "option_value_slug":     extractor_option_value_slug,
    "article_h3_paragraph":  extractor_article_h3_paragraph,
    "div_name_title":        extractor_div_name_title,
}


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def normalize_name(name: str) -> str:
    name = name.strip()
    name = re.sub(r'\b[A-Z]\.\s*', ' ', name)
    return re.sub(r'\s+', ' ', name).strip()


def get_level(title: str) -> int | None:
    if not title:
        return None
    t = title.lower()
    for keyword, level in sorted(LEVEL_ORDER.items(), key=lambda x: -len(x[0])):
        if keyword in t:
            return level
    return None


def get_nested(obj: dict, dotpath: str):
    """Resolve dot-notation path in a dict: 'role.slug' → obj['role']['slug']"""
    keys = dotpath.split(".")
    for k in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(k)
    return obj


def fetch_html(timestamp: str, original_url: str, max_retries: int = 3) -> str | None:
    url = f"https://web.archive.org/web/{timestamp}id_/{original_url}"
    for attempt in range(max_retries):
        try:
            r = requests.get(url, timeout=45,
                headers={"User-Agent": "PE-Diligence-Research-Tool/1.0"})
            r.raise_for_status()
            return r.text
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 5 * (2 ** attempt)
                print(f"      retry {attempt+1} in {wait}s — {e}")
                time.sleep(wait)
            else:
                print(f"      ⚠ Failed: {e}")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# TIER 1: JSON API DISCOVERY + EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def discover_api_snapshots(api_source: dict, start_year: int) -> list[dict]:
    """
    Query CDX for all archived JSON responses on the domain.
    Returns yearly snapshots (closest to Dec 31) for the configured endpoint.
    """
    domain   = api_source["domain"]
    endpoint = api_source["endpoint"]
    print(f"  [Tier 1] CDX API scan: {domain} (JSON, from {start_year})")

    try:
        r = requests.get(CDX_API, params={
            "url":    f"{domain}/*",
            "output": "json",
            "fl":     "timestamp,original,mimetype,statuscode",
            "filter": ["statuscode:200", "mimetype:application/json"],
            "from":   f"{start_year}0101",
            "limit":  500,
        }, timeout=60)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"    ⚠ CDX scan failed: {e}")
        return []

    if len(data) <= 1:
        print(f"    → No JSON endpoints found on {domain}")
        return []

    # Show all discovered JSON endpoints
    endpoints_found = sorted(set(row[1] for row in data[1:]))
    print(f"    → {len(endpoints_found)} unique JSON endpoint(s) found:")
    for ep in endpoints_found:
        count = sum(1 for row in data[1:] if row[1] == ep)
        print(f"       {ep}  ({count} snapshots)")

    # Filter to the configured endpoint (normalize protocol for comparison)
    def strip_proto(url: str) -> str:
        return re.sub(r'^https?://', '', url).rstrip('/')

    norm_endpoint = strip_proto(endpoint)
    matching = [row for row in data[1:] if strip_proto(row[1]) == norm_endpoint]
    if not matching:
        print(f"    ⚠ Configured endpoint '{endpoint}' not found in archives")
        return []

    # Pick closest to Dec 31 per year
    by_year: dict[str, dict] = {}
    for row in matching:
        ts   = row[0]
        year = ts[:4]
        try:
            snap_dt  = datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))
            distance = abs((datetime(int(year), 12, 31) - snap_dt).days)
        except ValueError:
            continue
        if year not in by_year or distance < by_year[year]["distance"]:
            by_year[year] = {
                "timestamp":   ts,
                "original":    row[1],
                "distance":    distance,
                "actual_date": snap_dt.strftime("%Y-%m-%d"),
                "source_type": "api",
            }

    result = sorted(
        [{"timestamp": v["timestamp"], "original": v["original"],
          "year": k, "actual_date": v["actual_date"], "source_type": "api"}
         for k, v in by_year.items()],
        key=lambda x: x["year"]
    )
    print(f"    → {len(result)} yearly API snapshots: {[s['year'] for s in result]}")
    return result


def extract_from_api(timestamp: str, original_url: str, api_source: dict) -> list[dict]:
    """Fetch one archived API snapshot and parse people from it."""
    raw = fetch_html(timestamp, original_url)
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"      ⚠ JSON parse error: {e}")
        return []

    # Navigate to the list of people
    data_path = api_source.get("data_path")
    if data_path:
        records = payload.get(data_path, [])
    else:
        records = payload if isinstance(payload, list) else []

    field_map    = api_source["field_map"]
    function_map = api_source["function_map"]
    people = []

    for rec in records:
        # Build name
        if "name_full" in field_map:
            raw_name = get_nested(rec, field_map["name_full"]) or ""
        else:
            first = get_nested(rec, field_map.get("name_first", "")) or ""
            last  = get_nested(rec, field_map.get("name_last",  "")) or ""
            raw_name = f"{first} {last}".strip()

        name  = normalize_name(raw_name)
        title = get_nested(rec, field_map.get("title", "title")) if "title" in field_map else None

        # Resolve function
        role_slug = get_nested(rec, field_map.get("role_slug", "")) if "role_slug" in field_map else None
        role_name = get_nested(rec, field_map.get("role_name", "")) if "role_name" in field_map else None
        func = (
            function_map.get(role_slug)
            or function_map.get(role_name)
            or "Other"
        )

        if not name or len(name) < 3:
            continue

        people.append({
            "name":     name,
            "title":    title,
            "function": func,
            "tier":     "api",
        })

    return people


# ─────────────────────────────────────────────────────────────────────────────
# TIER 2: HTML SNAPSHOT DISCOVERY + EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def discover_html_snapshots(html_source: dict, start_year: int) -> list[dict]:
    """CDX query for HTML snapshots of a given URL, one per year closest to Dec 31."""
    base_url = html_source["base_url"]
    print(f"  [Tier 2] CDX HTML scan: {base_url}")
    try:
        r = requests.get(CDX_API, params={
            "url":    base_url,
            "output": "json",
            "fl":     "timestamp,original,statuscode",
            "filter": "statuscode:200",
            "from":   f"{start_year}0101",
            "limit":  1000,
        }, timeout=60)
        r.raise_for_status()
        data = r.json()
        if len(data) <= 1:
            print("    → 0 snapshots")
            return []
    except Exception as e:
        print(f"    ⚠ CDX error: {e}")
        return []

    by_year: dict[str, dict] = {}
    for row in data[1:]:
        ts, year = row[0], row[0][:4]
        try:
            snap_dt  = datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))
            distance = abs((datetime(int(year), 12, 31) - snap_dt).days)
        except ValueError:
            continue
        if year not in by_year or distance < by_year[year]["distance"]:
            by_year[year] = {
                "timestamp":   ts,
                "original":    row[1],
                "distance":    distance,
                "actual_date": snap_dt.strftime("%Y-%m-%d"),
            }

    result = sorted(
        [{"timestamp": v["timestamp"], "original": v["original"],
          "year": k, "actual_date": v["actual_date"], "source_type": "html"}
         for k, v in by_year.items()],
        key=lambda x: x["year"]
    )
    print(f"    → {len(result)} yearly HTML snapshots: {[s['year'] for s in result]}")
    return result


def extract_from_html(timestamp: str, original_url: str, html_source: dict) -> list[dict]:
    """Fetch one archived HTML page and extract people using the configured extractor."""
    html = fetch_html(timestamp, original_url)
    if not html:
        return []
    extractor_fn = EXTRACTORS.get(html_source["extractor"])
    if not extractor_fn:
        print(f"      ⚠ Unknown extractor: {html_source['extractor']}")
        return []

    # Build kwargs — extractor receives function_map always, plus any extra
    # config keys the new extractors accept (title_function_map, class overrides)
    kwargs = {}
    for key in ("title_function_map", "article_class", "heading_class",
                "wrapper_class", "name_class", "title_class"):
        if key in html_source:
            kwargs[key] = html_source[key]

    import inspect
    sig = inspect.signature(extractor_fn)
    # Only pass kwargs the function actually accepts
    accepted = set(sig.parameters.keys())
    filtered = {k: v for k, v in kwargs.items() if k in accepted}

    return extractor_fn(html, html_source.get("function_map", {}), **filtered)


# ─────────────────────────────────────────────────────────────────────────────
# YEAR PLAN: merge API + HTML, prefer API
# ─────────────────────────────────────────────────────────────────────────────

def build_year_plan(api_snaps: list[dict], html_snaps: list[dict]) -> list[dict]:
    """
    Merge API and HTML snapshot lists.
    For any year with both, API wins (richer data, always has titles).
    Returns sorted list of {year, source_type, snapshot_meta, source_config_key}
    """
    by_year: dict[str, dict] = {}

    for snap in html_snaps:
        by_year[snap["year"]] = {**snap, "tier_label": "HTML"}

    for snap in api_snaps:
        # API always overwrites HTML for the same year
        by_year[snap["year"]] = {**snap, "tier_label": "API ✓"}

    result = sorted(by_year.values(), key=lambda x: x["year"])
    print(f"\n  Year plan ({len(result)} years):")
    for s in result:
        print(f"    {s['year']}  [{s['tier_label']:<6}]  {s['actual_date']}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS (promotions, departures, tenure)
# ─────────────────────────────────────────────────────────────────────────────

def analyze(df: pd.DataFrame):
    df = df.copy()
    df["year"]      = df["year"].astype(int)
    df["name_norm"] = df["name"].apply(lambda n: n.lower().strip())
    df = df.sort_values("year")
    latest_year = int(df["year"].max())

    arrivals, departures, tenure_rows, promotions = [], [], [], []

    for norm, group in df.groupby("name_norm"):
        group        = group.sort_values("year").drop_duplicates(subset="year")
        canon        = group.iloc[0]["name"]
        func         = group.iloc[-1]["function"]
        first_yr     = int(group["year"].min())
        last_yr      = int(group["year"].max())
        tenure_yr    = last_yr - first_yr
        still_active = (last_yr == latest_year)

        arrivals.append({
            "name": canon, "function": group.iloc[0]["function"], "arrival_year": first_yr,
        })
        tenure_rows.append({
            "name": canon, "function": func, "first_seen": first_yr,
            "last_seen": last_yr, "tenure_years": tenure_yr, "still_active": still_active,
        })
        if not still_active:
            departures.append({
                "name": canon, "function": func, "last_seen": last_yr,
                "approx_departure_year": last_yr + 1, "tenure_years": tenure_yr,
            })

        # Promotion detection (only when titles are present)
        prev_title, prev_level, prev_year = None, None, None
        for _, row in group.iterrows():
            curr_title = row.get("title") or ""
            curr_level = get_level(curr_title)
            curr_year  = int(row["year"])
            if prev_title and curr_title and curr_title != prev_title:
                if curr_level and prev_level and curr_level > prev_level:
                    promotions.append({
                        "name":                canon,
                        "function":            row["function"],
                        "from_title":          prev_title,
                        "to_title":            curr_title,
                        "last_year_in_role":   prev_year,
                        "first_year_in_new":   curr_year,
                        "years_in_prior_role": curr_year - prev_year,
                    })
            prev_title = curr_title or prev_title  # don't reset to empty
            prev_level = curr_level or prev_level
            prev_year  = curr_year

    return (
        pd.DataFrame(arrivals),
        pd.DataFrame(departures if departures else []),
        pd.DataFrame(tenure_rows),
        pd.DataFrame(promotions if promotions else []),
    )


def headcount_pivot(df: pd.DataFrame, function_order: list) -> list[dict]:
    df = df.copy()
    df["year"] = df["year"].astype(int)
    rows = []
    for year, ydf in df.groupby("year"):
        counts = ydf.groupby("function").size().to_dict()
        row = {"year": int(year)}
        for func in function_order:
            row[func] = int(counts.get(func, 0))
        row["total"] = sum(row[f] for f in function_order if f in row)
        rows.append(row)
    return sorted(rows, key=lambda x: x["year"])


def turnover_metrics(departures_df: pd.DataFrame, tenure_df: pd.DataFrame,
                     function_order: list, latest_year: int) -> list[dict]:
    rows = []
    for func in function_order:
        ften = tenure_df[tenure_df["function"] == func]
        fdep = departures_df[departures_df["function"] == func] if len(departures_df) else pd.DataFrame()
        total_ever = len(ften)
        if total_ever == 0:
            continue
        n_active   = int(len(ften[ften["still_active"]]))
        n_departed = int(len(fdep))
        retention  = round(n_active / total_ever, 4)
        avg_tenure = round(float(fdep["tenure_years"].mean()), 1) if len(fdep) > 0 else None
        rows.append({
            "function":                    func,
            "total_ever_employed":         total_ever,
            "currently_active":            n_active,
            "active_as_of_year":           latest_year,
            "total_leavers":               n_departed,
            "retention_rate":              retention,
            "avg_tenure_before_departure": avg_tenure,
            "leaver_names":                sorted(fdep["name"].tolist()) if len(fdep) else [],
        })
    return rows


def promotion_summary(promotions_df: pd.DataFrame) -> list[dict]:
    if len(promotions_df) == 0:
        return []
    summary = (promotions_df
               .groupby(["from_title", "to_title"])
               .agg(n_observed=("years_in_prior_role", "count"),
                    avg_years_in_prior_role=("years_in_prior_role", "mean"))
               .reset_index()
               .sort_values("avg_years_in_prior_role"))
    return [
        {
            "from_title": row["from_title"],
            "to_title":   row["to_title"],
            "n_observed": int(row["n_observed"]),
            "avg_years_in_prior_role": round(float(row["avg_years_in_prior_role"]), 1),
        }
        for _, row in summary.iterrows()
    ]


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT: JSON
# ─────────────────────────────────────────────────────────────────────────────

def build_json(cfg, raw_df, hc_rows, departures_df, tenure_df,
               turnover_rows, promotions_df, promo_summary_rows, output_path):

    output = {
        "firm":              cfg["firm_name"],
        "firm_slug":         cfg["firm_slug"],
        "coverage_note":     cfg["coverage_note"],
        "generated_at":      datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "years_covered":     sorted([int(y) for y in raw_df["year"].unique()]),
        "data_tiers_used":   sorted(raw_df["tier"].unique().tolist()),
        "summary": {
            "unique_people":    int(raw_df["name"].nunique()),
            "total_records":    len(raw_df),
            "total_departures": len(departures_df),
            "total_promotions": len(promotions_df),
        },
        "headcount_by_year":  hc_rows,
        "turnover_metrics":   turnover_rows,
        "promotions_detail":  promotions_df.to_dict(orient="records") if len(promotions_df) > 0 else [],
        "promotions_summary": promo_summary_rows,
        "departures_detail":  (
            departures_df.sort_values(["function", "approx_departure_year"])
                         .to_dict(orient="records") if len(departures_df) > 0 else []
        ),
        "tenure": (
            tenure_df.sort_values(["function", "tenure_years"], ascending=[True, False])
                     .to_dict(orient="records")
        ),
        "raw_snapshots": (
            raw_df[["name", "title", "function", "year", "tier"]]
                  .sort_values(["year", "name"])
                  .to_dict(orient="records")
        ),
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"  ✅  Saved → {output_path}")
    return output


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run(cfg: dict = FIRM_CONFIG):
    firm      = cfg["firm_name"]
    start_yr  = cfg["start_year"]
    func_ord  = cfg["function_order"]
    out_file  = cfg["output_file"]

    print(f"\n{'='*60}")
    print(f"  {firm} — Human Capital Tracker")
    print(f"{'='*60}\n")

    # ── Tier 1: Discover API snapshots ────────────────────────────────────────
    api_snaps_by_source: dict[int, tuple] = {}  # year → (snap, api_source_config)
    all_api_snaps = []
    for api_src in cfg.get("api_sources", []):
        snaps = discover_api_snapshots(api_src, start_yr)
        for s in snaps:
            all_api_snaps.append(s)
            api_snaps_by_source[s["year"]] = (s, api_src)

    # ── Tier 2: Discover HTML snapshots ───────────────────────────────────────
    html_snaps_by_source: dict[int, tuple] = {}  # year → (snap, html_source_config)
    all_html_snaps = []
    for html_src in cfg.get("html_sources", []):
        snaps = discover_html_snapshots(html_src, start_yr)
        for s in snaps:
            all_html_snaps.append(s)
            if s["year"] not in html_snaps_by_source:
                html_snaps_by_source[s["year"]] = (s, html_src)

    # ── Merge: API wins over HTML for the same year ────────────────────────────
    year_plan = build_year_plan(all_api_snaps, all_html_snaps)
    print(f"\n  Total years to scrape: {len(year_plan)}\n")

    # ── Scrape ────────────────────────────────────────────────────────────────
    print("[Scraping...]\n")
    all_records: list[dict] = []

    for i, plan_entry in enumerate(year_plan, 1):
        yr  = plan_entry["year"]
        ts  = plan_entry["timestamp"]
        orig = plan_entry["original"]
        tier = plan_entry["source_type"]
        label = plan_entry["tier_label"]
        print(f"  [{i:>2}/{len(year_plan)}] {yr} ({plan_entry['actual_date']}) [{label}] ...",
              end=" ", flush=True)

        if tier == "api":
            _, api_src = api_snaps_by_source[yr]
            people = extract_from_api(ts, orig, api_src)
        else:
            _, html_src = html_snaps_by_source[yr]
            people = extract_from_html(ts, orig, html_src)

        if people:
            for p in people:
                p["year"] = yr
            all_records.extend(people)
            titles_preview = sorted(set(p["title"] for p in people if p.get("title")))[:5]
            print(f"{len(people)} people  titles: {titles_preview or ['(none)']}")
        else:
            print("0 extracted")

        time.sleep(1.5)

    if not all_records:
        print("\n⚠  No records extracted.")
        return

    # ── Build DataFrames ──────────────────────────────────────────────────────
    cols = ["name", "title", "function", "year", "tier"]
    raw_df = (pd.DataFrame(all_records)[cols]
              .dropna(subset=["name"])
              .drop_duplicates(subset=["name", "year"])
              .sort_values(["year", "name"])
              .reset_index(drop=True))

    print(f"\n  Records: {len(raw_df)} | Unique people: {raw_df['name'].nunique()} "
          f"| Years: {raw_df['year'].nunique()}")
    print(f"  Tiers used: {raw_df['tier'].value_counts().to_dict()}")
    print(f"  Titles found: {sorted(raw_df['title'].dropna().unique())}")

    # ── Analysis ──────────────────────────────────────────────────────────────
    arrivals_df, departures_df, tenure_df, promotions_df = analyze(raw_df)
    latest_year   = int(raw_df["year"].max())
    hc_rows       = headcount_pivot(raw_df, func_ord)
    turnover_rows = turnover_metrics(departures_df, tenure_df, func_ord, latest_year)
    promo_summary = promotion_summary(promotions_df)

    print(f"\n  Departures: {len(departures_df)}")
    print(f"  Promotions: {len(promotions_df)}")
    if len(promotions_df) > 0:
        print("\n  Promotion transitions:")
        for _, row in promotions_df.iterrows():
            print(f"    {row['name']:<28} {row['from_title']} → {row['to_title']}  "
                  f"({row['years_in_prior_role']} yrs)")

    # ── Write JSON ────────────────────────────────────────────────────────────
    print(f"\n[Building JSON...]\n")
    output = build_json(cfg, raw_df, hc_rows, departures_df, tenure_df,
                        turnover_rows, promotions_df, promo_summary, out_file)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  HEADCOUNT TREND:")
    for row in hc_rows:
        bar = "█" * int(row["total"] / 2)
        print(f"    {row['year']}  {row['total']:>3}  {bar}")

    print(f"\n  TURNOVER SUMMARY:")
    for row in turnover_rows:
        print(f"    {row['function']:<24} {row['total_leavers']:>3} leavers  "
              f"{row['retention_rate']:.0%} retention")

    if promo_summary:
        print(f"\n  PROMOTION SUMMARY:")
        for row in promo_summary:
            print(f"    {row['from_title']:>22} → {row['to_title']:<22} "
                  f"avg {row['avg_years_in_prior_role']} yrs  (n={row['n_observed']})")
    print(f"{'─'*60}\n")

    return output


if __name__ == "__main__":
    run()
