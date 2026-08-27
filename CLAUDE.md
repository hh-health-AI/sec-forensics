# sec-forensics — standing instructions

**Layers covered:** Financial + Risk.
**Anchor plugin for SEC EDGAR.** your view layer currently uses EDGAR/web without
declaring it; consume this plugin's access rather than re-declaring. If a hosted EDGAR
MCP appears, declare it HERE only.

## What this engine is for

Two jobs that a generic finance plugin does not do well for healthcare:

1. **Forensic quality-of-earnings screening tuned to healthcare business models.**
   Generic red-flag frameworks miss the failure modes specific to this sector.
2. **Positioning and insider overlays around clinical and regulatory catalysts**,
   where the event calendar is known in advance and ownership is unusually concentrated.

## Healthcare-specific forensic patterns worth screening for

Generic Schilit-style checks apply, but these are the sector's recurring ones:

- **Gross-to-net reserve manipulation.** Rebate and chargeback accruals are estimates
  under management control. An accrual that falls as a share of gross revenue while
  the payer mix shifts toward Medicaid or Part D is the classic tell.
- **Specialty-pharmacy channel stuffing.** Revenue recognised into a captive or
  closely-held distribution channel. Watch DSO and channel inventory disclosures.
- **Distributor inventory in medtech.** Sell-in versus sell-through. A quarter made on
  distributor loading shows up as receivables growth outrunning revenue.
- **Capitalised software and development costs** in digital health and tools, which
  convert opex into an asset and flatter margins.
- **Collaboration and milestone revenue timing** in biopharma — lumpy, discretionary,
  and often used to hit a number. Strip it and look at product revenue alone.
- **Provider bad-debt and implicit price concessions.** Post-ASC 606, uncompensated
  care moves between revenue reduction and bad debt; the classification choice changes
  reported revenue without changing cash.
- **Payor incurred-but-not-reported (IBNR) reserve development.** Prior-period reserve
  releases flattering current-period MLR. Look at the development table, not the ratio.
- **Non-GAAP bridges** that exclude recurring items: "one-time" restructuring in five
  consecutive years, or perpetual acquisition-related amortisation adjustments.

## Access rules

data.sec.gov and efts.sec.gov require a descriptive **User-Agent** with a contact
address and are rate-limited to about 10 requests/second. Set `SEC_USER_AGENT` in the
environment. Do not parallelise past the limit; EDGAR blocks by IP.

## Chaining

a catalyst engine (catalyst dates for the insider overlay) · `provider-economics`
(cost-report cross-read on hospital filers) · `rx-utilization` (independent volume
evidence to test a revenue-recognition question) · your view layer → thesis,
sell-discipline, and the cross-cutting a forensic quality gate.

**Non-overlap check:** you may already run separate single-name research and valuation tooling. This engine supplies *evidence*, not a
second earnings review. If the question is "how was the quarter", route it there.
## Connector

Declares **`sec-edgar`** (`stefanoamorelli/sec-edgar-mcp`) — this plugin is the anchor.
It parses XBRL directly, so financial-statement figures come back at exact filed
precision rather than reconstructed, and it has real Form 4 transaction tooling.
your view layer consumes this session; it must not re-declare EDGAR.

`SEC_USER_AGENT` is required by both the server and the scripts — EDGAR blocks by IP
on a missing or generic agent, and the block is not obvious from the error. Set it
once in the environment; the `.mcp.json` passes it through.

The server is AGPL-3.0 and is not affiliated with the SEC. Run
`bin/install-mcp-servers.sh sec-edgar` before first use; until then `edgar_client.py`
and the other scripts work unchanged.

## Standard of evidence

This engine is built to **institutional investor standards: rigorous and auditable.**
That is a claim about specific mechanisms, and the full list is in
`references/auditability.md`. The load-bearing ones:

- Every finding carries a source, a retrieval date and the **vintage of the underlying
  data** — a different and usually much earlier date.
- Confidence is gated by vintage, not by conviction.
- Scripts fail loudly on empty result sets. Silence is never a negative finding.
- Known limitations travel with the number, in-line, not in a footnote.
- Evidence and view stay separated. This engine does not issue recommendations.

## Desk conventions (all engines)

- **One connector, one plugin — for plugin-level servers only.** A self-hosted
  stdio server is declared in exactly one plugin's `.mcp.json`; co-installed
  plugins share every server session-wide, so a second declaration buys a
  duplicate process, not extra capability. **Account-level hosted connectors are
  different**: CMS Coverage, PopHIVE, ClinicalTrials.gov, PubMed, ChEMBL,
  bioRxiv and Scholar Gateway are connected once in the directory and are visible
  to every plugin. Plugins reference those; they never declare or own them.
  Full map in `references/mcp-setup.md`.
- **MCP for the analyst, scripts for the watcher.** Both paths ship in every
  plugin and they are not redundant. Interactive query refinement goes through
  the server; unattended scheduled evidence goes through the script, because a
  watcher has to be deterministic and re-runnable against the same vintage.
  Where the two disagree, the script wins for anything entering a brief — you
  cannot cite the internals of a third-party server.
- **Engines produce evidence, not views.** An engine skill ends at the brief. The
  your view layer is the only place a position
  is argued. Do not write a recommendation into an engine output.
- **Open data only.** Every input here is free and public. If an analysis needs
  IQVIA, Symphony, Definitive, EvaluatePharma or Citeline, say so and stop — do
  not silently substitute a proxy for the paid panel and present it as equivalent.
- **Cite the vintage every time.** See `references/evidence-brief.md`.
- **Chain, don't duplicate.** These eight engines cross-reference each other by
  name. Anything outside them — valuation models, single-name research, the
  portfolio view layer — is chained into, never reimplemented here. An engine
  that starts doing valuation has stopped being an engine.
- **Scripts are stdlib-only Python 3.** No pip installs. Every script takes
  `--help`, prints JSON or CSV to stdout, and fails loudly on an empty result set
  rather than returning silence that reads like a negative finding.
