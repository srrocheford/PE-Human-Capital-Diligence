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
        "configured": True,
        "firm_name":  "GTCR",
        "firm_slug":  "gtcr",
        "hq":         "Chicago, IL",
        "fund_size":  "~$11.5B",
        "focus":      "Diversified",
        "start_year": 2016,
        "domain":     "gtcr.com",
        "output_file": "/tmp/gtcr_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2016–2019 via gtcr.com/team/ (10 snapshots, ~56–61 people/snap). "
            "WordPress child theme with team-hover card pattern; name/title in <span class='name/title'>. "
            "Site migrated to Vue SPA (gtcr-vue theme) in 2020 — snapshots from 2020+ are JS-only shells; "
            "Tier 3 (Playwright) required for 2020+ coverage. "
            "Older 2010–2011 who-we-are/ page archived (47 snapshots) but names only, no titles — skipped."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":     "gtcr.com/team/",
                "extractor":    "div_name_title",
                "function_map": {},
                "title_function_map": {
                    r"chief financial officer|controller":                      "Finance",
                    r"general counsel|compliance":                              "Legal & Compliance",
                    r"chief talent|human resources|director of events|chief information|director of information": "Operations",
                    r"managing director|vice president|principal|associate":    "Investment Team",
                },
                "wrapper_class": "team-hover",
                "name_class":    "name",
                "title_class":   "title",
            }
        ],
        "function_order": [
            "Investment Team", "Finance", "Legal & Compliance", "Operations", "Other"
        ],
    },

    "flexpoint-ford": {
        "configured": True,
        "firm_name":  "Flexpoint Ford",
        "firm_slug":  "flexpoint-ford",
        "hq":         "Chicago, IL",
        "fund_size":  "~$3.5B",
        "focus":      "Financial Services / Healthcare",
        "start_year": 2015,
        "domain":     "flexpointford.com",
        "output_file": "/tmp/flexpoint-ford_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2015–2016 via flexpointford.com/team/ (30 snapshots, ~30 people/snap). "
            "Cards are <div class='item {location} {sector}' data-sort-name='...'> with "
            "<p class='name'> and <p class='job-title'>. Split on data-sort-name attr. "
            "Location/sector tags (Chicago, New-York, financial, healthcare, credit) appear as "
            "CSS classes on card div — useful for future filter work."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":    "flexpointford.com/team/",
                "extractor":   "data_attr_split",
                "function_map": {},
                "split_attr":  "data-sort-name",
                "name_class":  "name",
                "title_class": "job-title",
                "title_function_map": {
                    r"chief executive|ceo":                                         "Leadership",
                    r"chief financial|chief operating|chief compliance|controller":  "Finance & Operations",
                    r"general counsel|legal":                                        "Legal",
                    r"managing director|partner":                                    "Investment Team",
                    r"principal|vice president":                                     "Investment Team",
                    r"associate|analyst":                                            "Investment Team",
                    r"operating":                                                    "Operating Resources",
                },
            }
        ],
        "function_order": [
            "Leadership", "Investment Team", "Finance & Operations",
            "Operating Resources", "Legal", "Other"
        ],
    },

    "shore-capital-partners": {
        "configured": False,
        "firm_name":  "Shore Capital Partners",
        "firm_slug":  "shore-capital-partners",
        "hq":         "Chicago, IL",
        "fund_size":  "~$3B",
        "focus":      "Healthcare",
        "start_year": 2010,
        "domain":     "shorecp.com",
        "output_file": "/tmp/shore-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: shorecp.com (not shorecapital.com). No Wayback team-page snapshots found yet — site may use JS rendering.",
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
        "domain":     "cresseyco.com",
        "output_file": "/tmp/cressey-and-company_human_capital.json",
        "coverage_note": "Correct domain: cresseyco.com (cressey.com is an unrelated real estate firm). No Wayback snapshots found — likely JS-rendered.",
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
        "domain":     "wppartners.com",
        "output_file": "/tmp/wind-point-partners_human_capital.json",
        "coverage_note": "Correct domain: wppartners.com (not windpointpartners.com). No Wayback team-page snapshots found.",
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
        "domain":     "parthenoncapital.com",
        "output_file": "/tmp/parthenon-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: parthenoncapital.com. No Wayback team-page snapshots found — likely JS-rendered.",
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
        "domain":     "charlesbank.com",
        "output_file": "/tmp/charlesbank-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: charlesbank.com. No Wayback team-page snapshots found — team page likely JS-rendered.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "harvest-partners": {
        "configured": True,
        "firm_name":  "Harvest Partners",
        "firm_slug":  "harvest-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$2.5B",
        "focus":      "Diversified",
        "start_year": 2023,
        "domain":     "harvestpartners.com",
        "output_file": "/tmp/harvest-partners_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2023–2025 via harvestpartners.com/people/ (21 snapshots, ~110 people/snap). "
            "Cards are <a class='team-member'> tags with data-group attribute encoding function directly "
            "(private-equity, structured-capital, credit-and-capital-markets, ascend, "
            "investor-relations, operations-and-administration, portfolio-support-group). "
            "Name in <span class='name'>, title in <span class='position'>."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":     "harvestpartners.com/people/",
                "extractor":    "anchor_team_card",
                "function_map": {},
                "wrapper_class": "team-member",
                "name_class":    "name",
                "title_class":   "position",
                "group_attr":    "data-group",
                "group_function_map": {
                    "private-equity":                "Private Equity",
                    "structured-capital":            "Structured Capital",
                    "credit-and-capital-markets":    "Credit & Capital Markets",
                    "ascend":                        "Ascend",
                    "investor-relations":            "Investor Relations",
                    "operations-and-administration": "Operations & Administration",
                    "portfolio-support-group":       "Portfolio Support",
                },
            }
        ],
        "function_order": [
            "Private Equity", "Structured Capital", "Credit & Capital Markets",
            "Ascend", "Investor Relations", "Portfolio Support",
            "Operations & Administration", "Other"
        ],
    },

    "ridgemont-equity-partners": {
        "configured": False,
        "firm_name":  "Ridgemont Equity Partners",
        "firm_slug":  "ridgemont-equity-partners",
        "hq":         "Charlotte, NC",
        "fund_size":  "~$2.3B",
        "focus":      "Diversified",
        "start_year": 2010,
        "domain":     "ridgemontep.com",
        "output_file": "/tmp/ridgemont-equity-partners_human_capital.json",
        "coverage_note": "Domain confirmed: ridgemontep.com. No Wayback team-page snapshots found — likely JS-rendered.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "audax-private-equity": {
        "configured": True,
        "firm_name":  "Audax Private Equity",
        "firm_slug":  "audax-private-equity",
        "hq":         "Boston, MA",
        "fund_size":  "~$3.5B",
        "focus":      "Diversified",
        "start_year": 2019,
        "domain":     "audaxprivateequity.com",
        "output_file": "/tmp/audax-private-equity_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2019–2026 via audaxprivateequity.com/team/ (52 snapshots). "
            "Function inferred from title — extractor class names may need tuning."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":    "audaxprivateequity.com/team/",
                "extractor":   "div_name_title",
                "function_map": {},
                # Common PE firm BEM class patterns — update if extractor returns 0 people
                "wrapper_class": "team-member",
                "name_class":    "team-member__name",
                "title_class":   "team-member__title",
                "title_function_map": {
                    r"operating partner":                          "Operating Resources",
                    r"partner|managing director|md|co-founder|president|executive director": "Investment Team",
                    r"vice president|vp|principal":                "Investment Team",
                    r"associate|analyst|director":                 "Investment Team",
                    r"finance|controller|accountant|cfo":          "Finance",
                    r"operations|chief of staff|admin|assistant|receptionist|legal|compliance|counsel": "Support",
                    r"senior advisor|advisor":                     "Executive Advisors",
                },
            }
        ],
        "function_order": [
            "Investment Team", "Operating Resources", "Finance",
            "Executive Advisors", "Support", "Other",
        ],
    },

    "sentinel-capital-partners": {
        "configured": False,
        "firm_name":  "Sentinel Capital Partners",
        "firm_slug":  "sentinel-capital-partners",
        "hq":         "New York, NY",
        "fund_size":  "~$4B",
        "focus":      "Diversified",
        "start_year": 2010,
        "domain":     "sentinelpartners.com",
        "output_file": "/tmp/sentinel-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: sentinelpartners.com (not sentinelcapital.com). JSON files found are Lottie animations, not team data. Need HTML extractor config.",
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
        "domain":     "odysseyinvestment.com",
        "output_file": "/tmp/odyssey-investment-partners_human_capital.json",
        "coverage_note": "Ajax team API found: odysseyinvestment.com/Home/TeamMemberAj/{id}. Needs custom extractor for ID-based endpoint pattern.",
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
        "domain":     "midoceanpartners.com",
        "output_file": "/tmp/midocean-partners_human_capital.json",
        "coverage_note": "Domain confirmed: midoceanpartners.com. No Wayback team-page snapshots found — likely JS-rendered.",
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
        "domain":     "vestarcapital.com",
        "output_file": "/tmp/vestar-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: vestarcapital.com. No Wayback team-page snapshots found.",
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
        "domain":     "oakhill.com",
        "output_file": "/tmp/oak-hill-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: oakhill.com (not oakhillcapital.com). No Wayback team-page snapshots found.",
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
        "domain":     "nep.com",
        "output_file": "/tmp/norwest-equity-partners_human_capital.json",
        "coverage_note": "Correct domain: nep.com (not norwestep.com). WP API exists but only oembed endpoints — no team data in API. Need HTML extractor config.",
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
        "domain":     "littlejohnllc.com",
        "output_file": "/tmp/littlejohn-and-co_human_capital.json",
        "coverage_note": "Correct domain: littlejohnllc.com (not littlejohnco.com). No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "thomas-h-lee-partners": {
        "configured": True,
        "firm_name":  "Thomas H. Lee Partners",
        "firm_slug":  "thomas-h-lee-partners",
        "hq":         "Boston, MA",
        "fund_size":  "~$5B",
        "focus":      "Diversified",
        "start_year": 2023,
        "domain":     "thl.com",
        "output_file": "/tmp/thomas-h-lee-partners_human_capital.json",
        "coverage_note": (
            "Tier 1 (WP REST API): 2023 via thl.com/wp-json/wp/v2/people (one batch snapshot, ~50+ people). "
            "Name at title.rendered; title at acf.bio_facts_feature.position. "
            "department taxonomy IDs present but not resolved — function inferred from title instead. "
            "HTML /people/ page is JS-rendered (React), no useful static snapshots. "
            "Limited historical depth: Wayback only captured the API once (Feb 2023)."
        ),
        "api_sources": [
            {
                "domain":   "thl.com",
                "endpoint": "wp-json/wp/v2/people",
                "field_map": {
                    "name_full": "title.rendered",
                    "title":     "acf.bio_facts_feature.position",
                },
                "function_map": {},
                "title_function_map": {
                    r"chief executive|ceo|co-ceo":                              "Leadership",
                    r"chief financial|chief operating|chief compliance|controller|cfo|coo": "Finance & Operations",
                    r"general counsel|legal|compliance":                        "Legal & Compliance",
                    r"managing director|partner|co-head|head of":               "Investment Team",
                    r"principal|vice president":                                 "Investment Team",
                    r"associate|analyst":                                        "Investment Team",
                    r"operating partner|operating advisor":                      "Operating Partners",
                    r"investor relations|business development":                  "Investor Relations",
                    r"human capital|talent|people":                              "Human Capital",
                    r"senior advisor|executive advisor|advisor":                 "Senior Advisors",
                    r"assistant|coordinator|receptionist|office|admin":          "Administration",
                },
            }
        ],
        "html_sources": [],
        "function_order": [
            "Leadership", "Investment Team", "Operating Partners",
            "Finance & Operations", "Legal & Compliance",
            "Investor Relations", "Human Capital", "Senior Advisors",
            "Administration", "Other"
        ],
    },

    "abry-partners": {
        "configured": False, "firm_name": "Abry Partners", "firm_slug": "abry-partners",
        "hq": "Boston, MA", "fund_size": "~$3B", "focus": "Media / Telecom / Services",
        "start_year": 2010, "domain": "abry.com",
        "output_file": "/tmp/abry-partners_human_capital.json",
        "coverage_note": "Domain confirmed: abry.com. No Wayback team-page snapshots found — likely JS-rendered.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "american-securities": {
        "configured": False, "firm_name": "American Securities", "firm_slug": "american-securities",
        "hq": "New York, NY", "fund_size": "~$5B", "focus": "Diversified",
        "start_year": 2010, "domain": "american-securities.com",
        "output_file": "/tmp/american-securities_human_capital.json",
        "coverage_note": "Domain confirmed: american-securities.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "arsenal-capital-partners": {
        "configured": False, "firm_name": "Arsenal Capital Partners", "firm_slug": "arsenal-capital-partners",
        "hq": "New York, NY", "fund_size": "~$3B", "focus": "Healthcare / Industrials",
        "start_year": 2010, "domain": "arsenalcapital.com",
        "output_file": "/tmp/arsenal-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: arsenalcapital.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "berkshire-partners": {
        "configured": False, "firm_name": "Berkshire Partners", "firm_slug": "berkshire-partners",
        "hq": "Boston, MA", "fund_size": "~$5B", "focus": "Diversified",
        "start_year": 2010, "domain": "berkshirepartners.com",
        "output_file": "/tmp/berkshire-partners_human_capital.json",
        "coverage_note": "Domain confirmed: berkshirepartners.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "blue-point-capital-partners": {
        "configured": False, "firm_name": "Blue Point Capital Partners", "firm_slug": "blue-point-capital-partners",
        "hq": "Cleveland, OH", "fund_size": "~$1B", "focus": "Diversified",
        "start_year": 2010, "domain": "bluepointcapital.com",
        "output_file": "/tmp/blue-point-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: bluepointcapital.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "ci-capital-partners": {
        "configured": False, "firm_name": "CI Capital Partners", "firm_slug": "ci-capital-partners",
        "hq": "New York, NY", "fund_size": "~$1.5B", "focus": "Diversified",
        "start_year": 2010, "domain": "cicapllc.com",
        "output_file": "/tmp/ci-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: cicapllc.com (not cicapital.com). No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "comvest-partners": {
        "configured": False, "firm_name": "Comvest Partners", "firm_slug": "comvest-partners",
        "hq": "West Palm Beach, FL", "fund_size": "~$2B", "focus": "Diversified",
        "start_year": 2010, "domain": "comvest.com",
        "output_file": "/tmp/comvest-partners_human_capital.json",
        "coverage_note": "Domain confirmed: comvest.com. Note: credit arm sold to Manulife 2025; PE arm remains independent at comvestprivateequity.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "excellere-partners": {
        "configured": False, "firm_name": "Excellere Partners", "firm_slug": "excellere-partners",
        "hq": "Denver, CO", "fund_size": "~$500M", "focus": "Healthcare / Business Services",
        "start_year": 2010, "domain": "excellere.com",
        "output_file": "/tmp/excellere-partners_human_capital.json",
        "coverage_note": "Domain confirmed: excellere.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "ffl-partners": {
        "configured": False, "firm_name": "FFL Partners", "firm_slug": "ffl-partners",
        "hq": "San Francisco, CA", "fund_size": "~$2B", "focus": "Healthcare / Financial Services",
        "start_year": 2010, "domain": "fflpartners.com",
        "output_file": "/tmp/ffl-partners_human_capital.json",
        "coverage_note": "Domain confirmed: fflpartners.com. JSON found is a Joomla scheduler endpoint, not team data. Need HTML extractor config.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "frontenac-company": {
        "configured": False, "firm_name": "Frontenac Company", "firm_slug": "frontenac-company",
        "hq": "Chicago, IL", "fund_size": "~$1B", "focus": "Diversified",
        "start_year": 2010, "domain": "frontenac.com",
        "output_file": "/tmp/frontenac-company_human_capital.json",
        "coverage_note": "Domain confirmed: frontenac.com. No Wayback team-page snapshots found — likely JS-rendered.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "great-hill-partners": {
        "configured": False, "firm_name": "Great Hill Partners", "firm_slug": "great-hill-partners",
        "hq": "Boston, MA", "fund_size": "~$3B", "focus": "Technology / Services",
        "start_year": 2010, "domain": "greathillpartners.com",
        "output_file": "/tmp/great-hill-partners_human_capital.json",
        "coverage_note": "Domain confirmed: greathillpartners.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "hggc": {
        "configured": True,
        "firm_name":  "HGGC",
        "firm_slug":  "hggc",
        "hq":         "Palo Alto, CA",
        "fund_size":  "~$2B",
        "focus":      "Diversified",
        "start_year": 2013,
        "domain":     "hggc.com",
        "output_file": "/tmp/hggc_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2013–2026 via www.hggc.com/team/ (161 snapshots). "
            "Flat team list — function inferred from title keywords. "
            "No JSON API available."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":  "www.hggc.com/team/",
                "extractor": "article_h3_paragraph",
                # article_class / heading_class use defaults (half_article / half_article-heading)
                "function_map": {},  # not used — function inferred from title
                "title_function_map": {
                    # ORDER MATTERS: more-specific patterns first
                    r"operating partner":                          "Operating Resources",
                    r"fund controller|fund accountant|accountant|controller|cfo": "Finance",
                    r"finance":                                    "Finance",
                    r"business development":                       "Business Development",
                    r"senior advisor|executive advisor":           "Executive Advisors",
                    r"partner|co-founder|co-chief|managing director|managing partner|president|executive director": "Investment Team",
                    r"vice president|vp|principal":                "Investment Team",
                    r"associate|analyst|director":                 "Investment Team",
                    r"chief of staff|director of operations|executive assistant|philanthropy|compliance|counsel|receptionist|admin|legal|support|office": "Support",
                },
            }
        ],
        "function_order": [
            "Investment Team", "Operating Resources", "Finance",
            "Business Development", "Executive Advisors", "Support", "Other",
        ],
    },

    "huron-capital-partners": {
        "configured": False, "firm_name": "Huron Capital Partners", "firm_slug": "huron-capital-partners",
        "hq": "Detroit, MI", "fund_size": "~$750M", "focus": "Services",
        "start_year": 2022, "domain": "huroncapital.com",
        "output_file": "/tmp/huron-capital-partners_human_capital.json",
        "coverage_note": "HTML team page at huroncapital.com/people/ — snapshots from 2022–2025. Limited recent-only coverage. Needs extractor config.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "incline-equity-partners": {
        "configured": False, "firm_name": "Incline Equity Partners", "firm_slug": "incline-equity-partners",
        "hq": "Pittsburgh, PA", "fund_size": "~$1.5B", "focus": "Industrials / Services",
        "start_year": 2010, "domain": "inclineequity.com",
        "output_file": "/tmp/incline-equity-partners_human_capital.json",
        "coverage_note": "Domain confirmed: inclineequity.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "jll-partners": {
        "configured": False, "firm_name": "JLL Partners", "firm_slug": "jll-partners",
        "hq": "New York, NY", "fund_size": "~$2B", "focus": "Healthcare",
        "start_year": 2010, "domain": "jllpartners.com",
        "output_file": "/tmp/jll-partners_human_capital.json",
        "coverage_note": "Wix API + HTML team page at jllpartners.com/team/ (2010–2026). Ready to configure.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "kelso-and-company": {
        "configured": False, "firm_name": "Kelso & Company", "firm_slug": "kelso-and-company",
        "hq": "New York, NY", "fund_size": "~$3B", "focus": "Diversified",
        "start_year": 2010, "domain": "kelso.com",
        "output_file": "/tmp/kelso-and-company_human_capital.json",
        "coverage_note": "Drupal JSON API found at kelso.com/team/{name}?_format=json. Ready to configure.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "ksl-capital-partners": {
        "configured": False, "firm_name": "KSL Capital Partners", "firm_slug": "ksl-capital-partners",
        "hq": "Denver, CO", "fund_size": "~$4B", "focus": "Travel / Leisure",
        "start_year": 2010, "domain": "kslcapital.com",
        "output_file": "/tmp/ksl-capital-partners_human_capital.json",
        "coverage_note": "Domain confirmed: kslcapital.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "leeds-equity-partners": {
        "configured": False, "firm_name": "Leeds Equity Partners", "firm_slug": "leeds-equity-partners",
        "hq": "New York, NY", "fund_size": "~$1.5B", "focus": "Education / Technology",
        "start_year": 2010, "domain": "leedsequity.com",
        "output_file": "/tmp/leeds-equity-partners_human_capital.json",
        "coverage_note": "Domain confirmed: leedsequity.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "llr-partners": {
        "configured": True,
        "firm_name":  "LLR Partners",
        "firm_slug":  "llr-partners",
        "hq":         "Philadelphia, PA",
        "fund_size":  "~$3B",
        "focus":      "Technology / Healthcare",
        "start_year": 2010,
        "domain":     "llrpartners.com",
        "output_file": "/tmp/llr-partners_human_capital.json",
        "coverage_note": (
            "Tier 2 (HTML): 2010–2026 via www.llrpartners.com/team/. "
            "Excellent 16-year coverage. Function inferred from title — extractor class names may need tuning."
        ),
        "api_sources": [],
        "html_sources": [
            {
                "base_url":    "www.llrpartners.com/team/",
                "extractor":   "div_name_title",
                "function_map": {},
                "wrapper_class": "team-member",
                "name_class":    "team-member__name",
                "title_class":   "team-member__title",
                "title_function_map": {
                    r"operating partner":                          "Operating Resources",
                    r"partner|managing director|md|co-founder|president|executive director": "Investment Team",
                    r"vice president|vp|principal":                "Investment Team",
                    r"associate|analyst|director":                 "Investment Team",
                    r"finance|controller|accountant|cfo":          "Finance",
                    r"operations|chief of staff|admin|assistant|receptionist|legal|compliance|counsel": "Support",
                    r"senior advisor|advisor":                     "Executive Advisors",
                },
            }
        ],
        "function_order": [
            "Investment Team", "Operating Resources", "Finance",
            "Executive Advisors", "Support", "Other",
        ],
    },

    "lovell-minnick-partners": {
        "configured": False, "firm_name": "Lovell Minnick Partners", "firm_slug": "lovell-minnick-partners",
        "hq": "Radnor, PA", "fund_size": "~$3B", "focus": "Financial Services",
        "start_year": 2010, "domain": "lmpartners.com",
        "output_file": "/tmp/lovell-minnick-partners_human_capital.json",
        "coverage_note": "Correct domain: lmpartners.com (not lovellminnick.com). No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "monomoy-capital-partners": {
        "configured": False, "firm_name": "Monomoy Capital Partners", "firm_slug": "monomoy-capital-partners",
        "hq": "New York, NY", "fund_size": "~$1.5B", "focus": "Industrials",
        "start_year": 2010, "domain": "mcpfunds.com",
        "output_file": "/tmp/monomoy-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: mcpfunds.com (not monomoycapital.com). No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "olympus-partners": {
        "configured": False, "firm_name": "Olympus Partners", "firm_slug": "olympus-partners",
        "hq": "Stamford, CT", "fund_size": "~$3B", "focus": "Services / Healthcare",
        "start_year": 2010, "domain": "olympuspartners.com",
        "output_file": "/tmp/olympus-partners_human_capital.json",
        "coverage_note": "Domain confirmed: olympuspartners.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "one-rock-capital-partners": {
        "configured": False, "firm_name": "One Rock Capital Partners", "firm_slug": "one-rock-capital-partners",
        "hq": "New York, NY", "fund_size": "~$4B", "focus": "Industrials",
        "start_year": 2010, "domain": "onerock.com",
        "output_file": "/tmp/one-rock-capital-partners_human_capital.json",
        "coverage_note": "Correct domain: onerock.com (not onerockcapital.com). No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "pamlico-capital": {
        "configured": False, "firm_name": "Pamlico Capital", "firm_slug": "pamlico-capital",
        "hq": "Charlotte, NC", "fund_size": "~$2B", "focus": "Diversified",
        "start_year": 2010, "domain": "pamlicocapital.com",
        "output_file": "/tmp/pamlico-capital_human_capital.json",
        "coverage_note": "Domain confirmed: pamlicocapital.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "primus-capital": {
        "configured": False, "firm_name": "Primus Capital", "firm_slug": "primus-capital",
        "hq": "Cleveland, OH", "fund_size": "~$500M", "focus": "Healthcare",
        "start_year": 2010, "domain": "primuscapital.com",
        "output_file": "/tmp/primus-capital_human_capital.json",
        "coverage_note": "Domain confirmed: primuscapital.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "sterling-partners": {
        "configured": False, "firm_name": "Sterling Partners", "firm_slug": "sterling-partners",
        "hq": "Chicago, IL", "fund_size": "~$1B", "focus": "Diversified",
        "start_year": 2010, "domain": "sterlingpartners.com",
        "output_file": "/tmp/sterling-partners_human_capital.json",
        "coverage_note": "Domain confirmed: sterlingpartners.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "sverica-capital-management": {
        "configured": False, "firm_name": "Sverica Capital Management", "firm_slug": "sverica-capital-management",
        "hq": "Boston, MA", "fund_size": "~$1B", "focus": "Diversified",
        "start_year": 2010, "domain": "sverica.com",
        "output_file": "/tmp/sverica-capital-management_human_capital.json",
        "coverage_note": "Domain confirmed: sverica.com. No Wayback team-page snapshots found.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "towerbrook-capital-partners": {
        "configured": False, "firm_name": "TowerBrook Capital Partners", "firm_slug": "towerbrook-capital-partners",
        "hq": "New York, NY", "fund_size": "~$5B", "focus": "Diversified",
        "start_year": 2010, "domain": "towerbrook.com",
        "output_file": "/tmp/towerbrook-capital-partners_human_capital.json",
        "coverage_note": "HTML team page at towerbrook.com/team/ — 54 snapshots but only 2010–2013. Historical data only. Needs extractor config.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "vistria-group": {
        "configured": False, "firm_name": "The Vistria Group", "firm_slug": "vistria-group",
        "hq": "Chicago, IL", "fund_size": "~$3B", "focus": "Diversified / Impact",
        "start_year": 2019, "domain": "vistria.com",
        "output_file": "/tmp/vistria-group_human_capital.json",
        "coverage_note": "HTML team page at www.vistria.com/who-we-are/ — 10 snapshots, 2019–2020 only. Very limited. Needs extractor config.",
        "api_sources": [], "html_sources": [], "function_order": [],
    },

    "wynnchurch-capital": {
        "configured": False, "firm_name": "Wynnchurch Capital", "firm_slug": "wynnchurch-capital",
        "hq": "Chicago, IL", "fund_size": "~$2.5B", "focus": "Industrials",
        "start_year": 2012, "domain": "wynnchurch.com",
        "output_file": "/tmp/wynnchurch-capital_human_capital.json",
        "coverage_note": "HTML team page at www.wynnchurch.com/who-we-are/ — 2 snapshots, 2012–2013 only. Very limited historical data. Needs extractor config.",
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
