"""
Firm Registry
=============
All registered PE firms. Two states:

  configured=True  → scraping sources are wired up; ready to run
  configured=False → registered for the Lovable dropdown but recon not yet done

To onboard a new firm:
  1. Set configured=True
  2. Fill in api_sources and/or html_sources
  3. Set function_order to match the firm's team categories
  4. Push to GitHub → Railway auto-deploys
"""

FIRMS = {

    # ══════════════════════════════════════════════════════════════════════════
    # CONFIGURED — ready to scrape
    # ══════════════════════════════════════════════════════════════════════════

    "water-street-healthcare-partners": {
        "configured":  True,
        "firm_name":   "Water Street Healthcare Partners",
        "firm_slug":   "water-street-healthcare-partners",
        "hq":          "Chicago, IL",
        "fund_size":   "~$1.5B",
        "focus":       "Healthcare",
        "start_year":  2012,
        "output_file": "/tmp/water-street-healthcare-partners_human_capital.json",
        "coverage_note": (
            "Tier 1 (JSON API): 2020, 2025 via waterstreet.com/api/people.json. "
            "Tier 2 (HTML): 2013–2019 via waterstreet.com/our-people/. "
            "2020+ /people/ page is JS-rendered and yields no HTML data."
        ),
        "api_sources": [
            {
                "domain":    "waterstreet.com",
                "endpoint":  "waterstreet.com/api/people.json",
                "data_path": "data",
                "field_map": {
                    "name_first": "firstName",
                    "name_last":  "lastName",
                    "title":      "title",
                    "role_slug":  "role.slug",
                },
                "function_map": {
                    "investment-team":     "Investment Partners",
                    "associates":          "Associates",
                    "operating-team":      "Operating Resources",
                    "corporate-team":      "Corporate Resources",
                    "internal-operations": "Corporate Resources",
                },
            }
        ],
        "html_sources": [
            {
                "base_url":  "waterstreet.com/our-people/",
                "extractor": "li_class_name_title",
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
        "function_order": [
            "Investment Partners", "Associates", "Operating Resources",
            "Executive Advisors", "Corporate Resources", "Support Team", "Other",
        ],
    },

    "linden-capital-partners": {
        "configured":  True,
        "firm_name":   "Linden Capital Partners",
        "firm_slug":   "linden-capital-partners",
        "hq":          "Chicago, IL",
        "fund_size":   "~$2.4B",
        "focus":       "Healthcare",
        "start_year":  2014,
        "output_file": "/tmp/linden-capital-partners_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2014–2023 via lindenllc.com/team/, "
            "2024–2026 via linden.com/team/. "
            "No JSON API discovered. Finance not separately tracked pre-2019 "
            "(combined with Human Capital in older site slug)."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":  "lindenllc.com/team/",
                "extractor": "option_value_slug",
                "function_map": {
                    "investment-team":       "Investment Team",
                    "human-capital":         "Human Capital",
                    "human-capital-finance": "Human Capital",
                    "finance":               "Finance",
                    "it":                    "Information Technology",
                    "investor-relations":    "Investor Relations",
                    "portfolio":             "Portfolio Operations",
                    "portfolio-operations":  "Portfolio Operations",
                },
            },
            {
                "base_url":  "linden.com/team/",
                "extractor": "option_value_slug",
                "function_map": {
                    "investment-team":      "Investment Team",
                    "human-capital":        "Human Capital",
                    "finance":              "Finance",
                    "it":                   "Information Technology",
                    "investor-relations":   "Investor Relations",
                    "portfolio-operations": "Portfolio Operations",
                },
            },
        ],
        "function_order": [
            "Investment Team", "Human Capital", "Finance",
            "Information Technology", "Investor Relations", "Portfolio Operations", "Other",
        ],
    },


    # ══════════════════════════════════════════════════════════════════════════
    # PENDING CONFIGURATION — show in dropdown, recon not yet done
    # ══════════════════════════════════════════════════════════════════════════

    "gtcr": {
        "configured": False,
        "firm_name":  "GTCR",
        "firm_slug":  "gtcr",
        "hq":         "Chicago, IL",
        "fund_size":  "~$11.5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/gtcr_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "flexpoint-ford": {
        "configured": False,
        "firm_name":  "Flexpoint Ford",
        "firm_slug":  "flexpoint-ford",
        "hq":         "Chicago, IL",
        "fund_size":  "~$3.5B",
        "focus":      "Financial Services / Healthcare",
        "start_year": 2010,
        "output_file": "/tmp/flexpoint-ford_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "shore-capital-partners": {
        "configured": False,
        "firm_name":  "Shore Capital Partners",
        "firm_slug":  "shore-capital-partners",
        "hq":         "Chicago, IL",
        "fund_size":  "~$3B",
        "focus":      "Healthcare",
        "start_year": 2010,
        "output_file": "/tmp/shore-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "cressey-and-company": {
        "configured": False,
        "firm_name":  "Cressey & Company",
        "firm_slug":  "cressey-and-company",
        "hq":         "Chicago, IL",
        "fund_size":  "~$2B",
        "focus":      "Healthcare",
        "start_year": 2010,
        "output_file": "/tmp/cressey-and-company_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "wind-point-partners": {
        "configured": False,
        "firm_name":  "Wind Point Partners",
        "firm_slug":  "wind-point-partners",
        "hq":         "Chicago, IL",
        "fund_size":  "~$2B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/wind-point-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "parthenon-capital-partners": {
        "configured": False,
        "firm_name":  "Parthenon Capital Partners",
        "firm_slug":  "parthenon-capital-partners",
        "hq":         "Boston, MA",
        "fund_size":  "~$3B",
        "focus":      "Services",
        "start_year": 2010,
        "output_file": "/tmp/parthenon-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "charlesbank-capital-partners": {
        "configured": False,
        "firm_name":  "Charlesbank Capital Partners",
        "firm_slug":  "charlesbank-capital-partners",
        "hq":         "Boston, MA",
        "fund_size":  "~$3.5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/charlesbank-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "harvest-partners": {
        "configured": False,
        "firm_name":  "Harvest Partners",
        "firm_slug":  "harvest-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$2.5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/harvest-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "ridgemont-equity-partners": {
        "configured": False,
        "firm_name":  "Ridgemont Equity Partners",
        "firm_slug":  "ridgemont-equity-partners",
        "hq":         "Charlotte, NC",
        "fund_size":  "~$2.3B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/ridgemont-equity-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "audax-private-equity": {
        "configured": False,
        "firm_name":  "Audax Private Equity",
        "firm_slug":  "audax-private-equity",
        "hq":         "Boston, MA",
        "fund_size":  "~$3.5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/audax-private-equity_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "sentinel-capital-partners": {
        "configured": False,
        "firm_name":  "Sentinel Capital Partners",
        "firm_slug":  "sentinel-capital-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$4B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/sentinel-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "odyssey-investment-partners": {
        "configured": False,
        "firm_name":  "Odyssey Investment Partners",
        "firm_slug":  "odyssey-investment-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$3B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/odyssey-investment-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "midocean-partners": {
        "configured": False,
        "firm_name":  "MidOcean Partners",
        "firm_slug":  "midocean-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/midocean-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "vestar-capital-partners": {
        "configured": False,
        "firm_name":  "Vestar Capital Partners",
        "firm_slug":  "vestar-capital-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$2.5B",
        "focus":      "Consumer / Healthcare",
        "start_year": 2010,
        "output_file": "/tmp/vestar-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "oak-hill-capital-partners": {
        "configured": False,
        "firm_name":  "Oak Hill Capital Partners",
        "firm_slug":  "oak-hill-capital-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$4B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/oak-hill-capital-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "norwest-equity-partners": {
        "configured": False,
        "firm_name":  "Norwest Equity Partners",
        "firm_slug":  "norwest-equity-partners",
        "hq":         "Minneapolis, MN",
        "fund_size":  "~$2.5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/norwest-equity-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "littlejohn-and-co": {
        "configured": False,
        "firm_name":  "Littlejohn & Co",
        "firm_slug":  "littlejohn-and-co",
        "hq":         "Greenwich, CT",
        "fund_size":  "~$2B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/littlejohn-and-co_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "thomas-h-lee-partners": {
        "configured": False,
        "firm_name":  "Thomas H. Lee Partners",
        "firm_slug":  "thomas-h-lee-partners",
        "hq":         "Boston, MA",
        "fund_size":  "~$5B",
        "focus":      "Diversified",
        "start_year": 2010,
        "output_file": "/tmp/thomas-h-lee-partners_human_capital.json",
        "coverage_note": "Pending configuration.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

}


def get_firm(slug: str) -> dict | None:
    return FIRMS.get(slug)


def list_firms() -> list[dict]:
    return [
        {
            "slug":       slug,
            "name":       cfg["firm_name"],
            "hq":         cfg.get("hq", ""),
            "fund_size":  cfg.get("fund_size", ""),
            "focus":      cfg.get("focus", ""),
            "start_year": cfg["start_year"],
            "configured": cfg.get("configured", False),
        }
        for slug, cfg in FIRMS.items()
    ]
