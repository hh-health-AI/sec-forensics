---
name: edgar-forensics
description: >
  This skill should be used when the user asks for a "forensic scan", "quality of
  earnings", "red flags in the filings", "is the revenue real", "accounting risk",
  "channel stuffing", "reserve release", "non-GAAP bridge", or wants a filings-based
  integrity check on a healthcare issuer before initiating or shorting.
metadata:
  version: "0.1.0"
  layer: "Financial"
---

# EDGAR forensic scan

Run a healthcare-tuned accounting red-flag screen from XBRL company facts and filing
text, and convert anything found into a testable claim rather than an insinuation.

## Workflow

1. **Resolve the issuer to a CIK** and pull company facts
   (`scripts/edgar_client.py --cik 0000320193 --facts`).
2. **Run the ratio panel** (`scripts/forensic_ratios.py`) across at least 12 quarters:
   DSO, DIO, receivables growth versus revenue growth, gross margin trend, accruals
   ratio, cash conversion (CFO ÷ net income), capitalised software as a share of R&D,
   deferred revenue movement, and — where the taxonomy exposes it — rebate and
   chargeback accruals as a share of gross revenue.
3. **Apply the sector overlay.** Match the issuer to a business model and read the
   ratios through the right lens. The same DSO increase means something different for
   a hospital operator (payer mix or denial rates), a medtech (distributor loading),
   and a specialty pharma (channel and gross-to-net).
4. **Read the words, not just the numbers.** Full-text search the filings
   (`--search`) for: change in accounting estimate, restatement, material weakness,
   going concern, subsequent event, auditor change, segment redefinition, and any
   change in the wording of the revenue-recognition policy. A quietly reworded policy
   note is worth more than any ratio.
5. **Check the non-GAAP bridge.** List every add-back for the last eight quarters and
   flag any that recurs in five or more. Recurring "one-time" items are the most
   reliable single indicator that management is managing the number.
6. **Corroborate externally, or stand down.** A revenue-recognition suspicion should be
   tested against an independent volume series (`rx-utilization` → sdud-trx-proxy or
   `provider-economics` → hospital-margin-forensics). A red flag with no external
   corroboration is a question for the next call, not a thesis.
7. **State the falsifier.** Write the specific disclosure that would clear the flag,
   and the date it is next expected. This is what makes the brief actionable.
8. Emit the brief.

## Discipline

Rank findings by whether they affect **cash**, **the trajectory**, or only
**presentation**. Presentation issues are common and rarely move a stock alone; cash
issues are rare and usually terminal. Do not present a presentation issue with the
rhetoric of a cash issue.

Never assert fraud. Describe the accounting choice, its effect on reported numbers,
and the disclosure that would resolve it.

## Not-automatic

A red-flag ratio does not license a fraud claim or a short. It licenses a specific
question, a corroboration attempt, and a named falsifier.

Reference: `references/healthcare-red-flags.md`. Contract: `../../references/evidence-brief.md`.
