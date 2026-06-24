from __future__ import annotations

DEMO_MODE = True
DEMO_COMPANY = "Parsons Corporation"
DEMO_TICKER = "PSN"

# USPTO PatentsView API
PATENTS_BASE = "https://search.patentsview.org/api/v1/patent/"
PATENTS_RATE_LIMIT = 0.5

# CourtListener
COURTLISTENER_BASE = "https://www.courtlistener.com/api/rest/v4"
COURTLISTENER_RATE_LIMIT = 1.0

# SEC EDGAR
EDGAR_EFTS = "https://efts.sec.gov/LATEST/search-index"
EDGAR_BASE = "https://data.sec.gov/submissions"
EDGAR_RATE_LIMIT = 0.1

# USASpending (contract award history — authoritative federal awards database)
USASPENDING_BASE = "https://api.usaspending.gov/api/v2"
USASPENDING_RATE_LIMIT = 0.5

CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# IP strength thresholds (total patent count)
IP_STRONG_MIN = 100
IP_MODERATE_MIN = 25
IP_WEAK_MIN = 5

# Litigation risk thresholds
LIT_CRITICAL_ACTIVE = 5
LIT_ELEVATED_ACTIVE = 3
LIT_ELEVATED_REGULATORY = 1

# Contract dependency thresholds (primary agency share)
CONTRACT_HIGH_DEP_PCT = 0.60
CONTRACT_MODERATE_PCT = 0.30

# CPC top-level domain labels
CPC_DOMAINS: dict[str, str] = {
    "G06F": "Computing Systems",
    "G06N": "AI / Machine Learning",
    "H04L": "Network Security",
    "H04W": "Wireless Communications",
    "G08B": "Signaling Systems",
    "G01S": "Radar / Remote Sensing",
    "F41":  "Weapons / Munitions",
    "B64":  "Aerospace / Unmanned Systems",
    "G06Q": "Business / Finance Systems",
    "E01":  "Civil Engineering / Infrastructure",
    "H01Q": "Antenna Systems",
    "G06V": "Image / Video Recognition",
}

# Recent period for velocity comparison (years)
RECENT_YEARS = 3
BASELINE_YEARS = 4

TIER_COLORS: dict[str, str] = {
    "STRONG":          "green",
    "MODERATE":        "yellow",
    "WEAK":            "yellow",
    "MINIMAL":         "red",
    "CRITICAL":        "red",
    "ELEVATED":        "yellow",
    "NORMAL":          "green",
    "CLEAR":           "green",
    "HIGH":            "red",
    "MEDIUM":          "yellow",
    "LOW":             "green",
    "CLEAN":           "green",
    "HIGH_DEPENDENCY": "red",
    "DIVERSIFIED":     "green",
}
