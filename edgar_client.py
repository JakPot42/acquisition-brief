"""SEC EDGAR client — regulatory exposure flags from 10-K filings."""
from __future__ import annotations

import time
import requests

from config import EDGAR_EFTS, EDGAR_BASE, EDGAR_RATE_LIMIT
from models import RegulatoryExposure, RegulatoryFlag
from seed_data import DEMO_REGULATORY_DATA

_EXPORT_TERMS = ["ITAR", "EAR", "export control", "export administration",
                 "International Traffic in Arms", "Bureau of Industry"]
_WEAKNESS_TERMS = ["material weakness", "material weaknesses"]
_CONCERN_TERMS  = ["going concern", "substantial doubt about"]


def fetch_regulatory_data(company: str, ticker: str, *, demo_mode: bool = True) -> dict:
    """Return raw regulatory data dict (demo or live)."""
    if demo_mode:
        return dict(DEMO_REGULATORY_DATA)

    # Live: fetch most recent 10-K text from EDGAR EFTS
    time.sleep(EDGAR_RATE_LIMIT)
    resp = requests.get(
        EDGAR_EFTS,
        params={"q": f'"{company}"', "forms": "10-K", "dateRange": "custom",
                "startdt": "2022-01-01", "enddt": "2025-12-31"},
        timeout=15,
    )
    resp.raise_for_status()
    hits = resp.json().get("hits", {}).get("hits") or []
    if not hits:
        return {"material_weakness": False, "going_concern": False,
                "export_control_mentions": 0, "government_revenue_pct": 0.0, "flags": []}

    # Fetch the filing text from the first result
    accession = hits[0].get("_id", "").replace("-", "")
    cik = hits[0].get("_source", {}).get("entity_id", "")
    time.sleep(EDGAR_RATE_LIMIT)
    doc_resp = requests.get(
        f"https://efts.sec.gov/LATEST/search-index?q=%22{company}%22&forms=10-K&dateRange=custom&startdt=2024-01-01&enddt=2025-12-31",
        timeout=15,
    )
    text = doc_resp.text if doc_resp.ok else ""

    mw  = any(t.lower() in text.lower() for t in _WEAKNESS_TERMS)
    gc  = any(t.lower() in text.lower() for t in _CONCERN_TERMS)
    ec  = sum(1 for t in _EXPORT_TERMS if t.lower() in text.lower())
    return {"material_weakness": mw, "going_concern": gc,
            "export_control_mentions": ec, "government_revenue_pct": 0.0, "flags": []}


def build_regulatory_exposure(company: str, ticker: str, raw: dict) -> RegulatoryExposure:
    """Convert raw EDGAR data dict into RegulatoryExposure dataclass."""
    flags: list[RegulatoryFlag] = []
    for f in raw.get("flags") or []:
        flags.append(RegulatoryFlag(
            flag_type=f.get("flag_type") or "OTHER",
            severity=f.get("severity") or "INFORMATIONAL",
            description=f.get("description") or "",
            filing_period=f.get("filing_period") or "",
            excerpt=f.get("excerpt") or "",
        ))

    mw  = bool(raw.get("material_weakness"))
    gc  = bool(raw.get("going_concern"))
    ec  = int(raw.get("export_control_mentions") or 0)
    gov = float(raw.get("government_revenue_pct") or 0.0)

    tier = _exposure_tier(mw, gc, ec, gov)
    return RegulatoryExposure(
        company=company,
        ticker=ticker,
        material_weakness=mw,
        going_concern=gc,
        export_control_mentions=ec,
        government_revenue_pct=gov,
        flags=flags,
        exposure_tier=tier,
    )


def _exposure_tier(mw: bool, gc: bool, ec_mentions: int, gov_pct: float) -> str:
    if mw or gc:
        return "HIGH"
    if ec_mentions >= 5 and gov_pct >= 0.70:
        return "MODERATE"
    if ec_mentions > 0 or gov_pct >= 0.50:
        return "LOW"
    return "CLEAN"
