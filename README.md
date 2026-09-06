# sec-forensics

Filings-driven forensic and positioning overlays for healthcare filers.

| Skill | Moves | Sub-sector | Ease/Impact |
|---|---|---|---|
| `edgar-forensics` | Short thesis; quality-of-earnings gate on longs | all | 3 / 4 |
| `insider-catalyst-patterns` | Position sizing / conviction into a catalyst | #biopharma | 3 / 3 |
| `ownership-crowding` | Crowding risk, squeeze potential, sizing discipline | all | 3 / 3 |

**Agent:** `filing-watcher` — daily 8-K item scan and Form 4 clusters ahead of known
catalysts; quarterly 13F and semi-monthly short-interest refresh.

**Data:** data.sec.gov (companyfacts, XBRL frames, submissions) · efts.sec.gov
(full-text search, 2001 onward) · Form 4 / 13F / 13D-G · FINRA short interest and
Reg SHO threshold lists. All free, no key.

Set `SEC_USER_AGENT` (e.g. `"Desk Name research@firm.com"`) before running scripts.

## Standard of evidence

Built to **institutional investor standards: rigorous and auditable.** 
In short: every finding carries a source, a retrieval
date and the vintage of the underlying data; confidence is gated by vintage rather
than conviction; scripts fail loudly on empty result sets so silence is never read as
a negative finding; known limitations travel in-line with the number; and evidence
stays separated from view, because this engine issues no recommendations.

## Setup

Open-data endpoints rate-limit unidentified and shared User-Agents, and SEC EDGAR
blocks them outright, so your contact string is required rather than defaulted:

```bash
export HH_CONTACT="Your Name (you@example.com)"
```

## Author

HH-health-ai

## Disclaimers

Not affiliated with, endorsed by, or connected to CMS, HHS, the FDA, the SEC, the
USPTO, the CDC, the EMA or any other government agency. All data is retrieved from
public endpoints subject to those agencies' own terms.

Nothing here is investment advice, and no output should be read as a recommendation to
buy or sell any security. These engines produce evidence for a human analyst to weigh.

Optional MCP servers are independent third-party projects under their own licenses.
Review them before use.

## License

MIT — see [LICENSE](LICENSE).

## Ratio calculation and output compatibility

The calculator emits schema version 2. DSO/DIO use period-end balances matched
to annual or four-contiguous-quarter flows and their actual day counts. Partial
quarters are never silently annualized. Missing or mismatched periods produce null.

Use `--as-of YYYY-MM-DD` to exclude later filings. Facts retain start/end dates,
filing dates and accessions; the latest eligible filing wins per period. Quarterly
cash flows can be derived from same-start YTD disclosures, with components retained.
Derived periods can combine filing vintages; inspect them when restatements matter.

Breaking changes: YoY fields now contain fractional changes (0.20 = 20%), raw_series
contains dated objects, and `cfo_to_net_income_ttm` replaces the overlapping-period
cash-conversion metric. USD US-GAAP facts only; custom/IFRS tags are not mapped.

## Regression tests

Run offline with Python 3.10 or newer (standard library only):

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic fixtures and mocked APIs; they do not certify live endpoint
availability or current regulatory facts. GitHub Actions runs the same tests on PRs.
