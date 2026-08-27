# Evidence-brief contract (shared across all desk engines)

Every skill in every engine plugin terminates in this six-field brief. It is the
only output format your view layer accepts.
Do not paraphrase the field names — the capstone parses them.

```
**Layer:** Clinical | Regulatory | Commercial | Competitive | Financial | Valuation | Risk
**Finding:** <one to three sentences>
  · Source: <dataset / endpoint / document, with URL>
  · Retrieved: <YYYY-MM-DD — the date you pulled it>
  · Data vintage: <the period the DATA covers, plus known lag and suppression>
**Moves:** <named model variable(s), with direction and magnitude where defensible>
  e.g. "FY27 net revenue −6% to −9%"; "LOE date pulled forward from 2029-06 to 2028-01"
**Not-automatic:** <what this finding explicitly does NOT license you to conclude>
**Follow-up observable:** <the next dated, checkable thing that confirms or kills it>
**Confidence:** <0.0–1.0> — <one clause of justification>
```

## Rules that make the contract load-bearing

1. **Retrieved ≠ vintage.** Most open healthcare data carries material lag. A brief
   that reports a retrieval date but no vintage is incomplete and must be rejected.
2. **Vintage gates confidence.** Cap confidence when the vintage is stale relative to
   the decision horizon: SDUD ~1–2 quarters + `<11` suppression; Part D and Open
   Payments annual; 13F 45-day and long-only; IRS 990 ~1yr+; HCRIS quarterly and
   restated; FAERS spontaneous and under-reported; NRDL/HTA event-driven.
3. **Moves names a variable, not a mood.** "Bullish for the franchise" is not a move.
   "Peak-sales assumption +$180m; adoption curve inflects two quarters earlier" is.
4. **Not-automatic is mandatory.** Open administrative data is a proxy. State the
   inferential step you are not taking — it is what stops a proxy becoming a thesis.
5. **One brief per skill run.** If a run produces several findings, emit several briefs.
6. **Confidence is calibrated, not rhetorical.** Score it as a forecast you would be
   Brier-scored on, because a Brier-scored calibration tracker will.
