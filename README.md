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
