# Pre-Acquisition Brief Generator

**Pre-Acquisition Brief Generator assembles a due-diligence snapshot of a company before you decide to pursue it.** Given a target company, it pulls the company's patents, litigation history, securities filings, and federal contract record from public sources and compiles them into a single scored brief covering IP strength, litigation risk, and regulatory exposure.

## What it does

- Pulls patents from USPTO
- Pulls litigation history from CourtListener
- Pulls securities filings from SEC EDGAR
- Pulls federal contract history from USASpending
- Scores the target on IP strength, litigation risk, and regulatory exposure, and lists recommended diligence questions for counsel

This sits earlier in the deal timeline than a formal regulatory screen: it answers "what does this target actually look like?" before anyone files anything.

## How it works

Claude synthesizes the pulled records into prose; the scoring is deterministic. Every data source is public. The demo runs against a seeded example target with no API key required.

## Usage

```bash
pip install -r requirements.txt
python main.py demo
```

## About

Pre-Acquisition Brief Generator is a command-line tool, part of a portfolio of national-security and defense-compliance software. It compiles public information to support human due diligence; it is not legal advice.
