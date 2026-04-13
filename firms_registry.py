"""
Firm Registry
=============
Add a new firm here to make it available in the API.
Each entry maps a firm_slug → FIRM_CONFIG dict (same format as pe_scraper_general.py).

The output_file path is overridden at runtime by the API — set it to anything.
"""

FIRMS = {

    # ── Water Street Healthcare Partners ──────────────────────────────────────
    "water-street-healthcare-partners": {
        "firm_name": "Water Street Healthcare Partners",
        "firm_slug": "water-street-healthcare-partners",
        "start_year": 2012,
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
                    "investment-team":    "Investment Partners",
                    "associates":         "Associates",
                    "operating-team":     "Operating Resources",
                    "corporate-team":     "Corporate Resources",
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

    # ── Linden Capital Partners ───────────────────────────────────────────────
    "linden-capital-partners": {
        "firm_name": "Linden Capital Partners",
        "firm_slug": "linden-capital-partners",
        "start_year": 2014,
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
                    "investment-team":        "Investment Team",
                    "human-capital":          "Human Capital",
                    "human-capital-finance":  "Human Capital",
                    "finance":                "Finance",
                    "it":                     "Information Technology",
                    "investor-relations":     "Investor Relations",
                    "portfolio":              "Portfolio Operations",
                    "portfolio-operations":   "Portfolio Operations",
                },
            },
            {
                "base_url":  "linden.com/team/",
                "extractor": "option_value_slug",
                "function_map": {
                    "investment-team":        "Investment Team",
                    "human-capital":          "Human Capital",
                    "finance":                "Finance",
                    "it":                     "Information Technology",
                    "investor-relations":     "Investor Relations",
                    "portfolio-operations":   "Portfolio Operations",
                },
            },
        ],
        "function_order": [
            "Investment Team", "Human Capital", "Finance",
            "Information Technology", "Investor Relations", "Portfolio Operations", "Other",
        ],
    },

}


def get_firm(slug: str) -> dict | None:
    return FIRMS.get(slug)


def list_firms() -> list[dict]:
    return [
        {
            "slug":       slug,
            "name":       cfg["firm_name"],
            "start_year": cfg["start_year"],
        }
        for slug, cfg in FIRMS.items()
    ]
