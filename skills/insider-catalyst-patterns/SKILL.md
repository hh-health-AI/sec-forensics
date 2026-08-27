---
name: insider-catalyst-patterns
description: >
  This skill should be used when the user asks about "insider buying", "Form 4",
  "insider selling before the readout", "10b5-1", "management conviction", or wants an
  insider-transaction overlay on a name approaching a clinical or regulatory catalyst.
metadata:
  version: "0.1.0"
  layer: "Risk"
---

# Insider patterns around catalysts

Overlay Form 4 activity on a known catalyst calendar and extract the small amount of
genuine signal from a very noisy series.

## Workflow

1. Pull Form 4 filings for the issuer (`scripts/form4_clusters.py --cik ...`).
2. **Strip the noise first.** Remove: option exercises, tax withholding (code F),
   gifts, and anything executed under a pre-existing 10b5-1 plan. What remains —
   open-market discretionary purchases and non-plan sales — is the only part worth
   reading.
3. **Look for clusters, not individuals.** One director buying is noise. Three or more
   insiders buying in the open market within a short window, especially including
   operating executives rather than only board members, is the pattern with any
   historical basis.
4. **Overlay the catalyst calendar** from a catalyst engine → catalyst-calendar.
   Position the transactions relative to the expected readout or PDUFA date.
5. **Weight by role and by size relative to holdings.** A CEO adding 20% to an existing
   stake means more than a director adding a token position. Size matters relative to
   the individual's own holding, not in dollars.
6. **Read sales with heavy scepticism.** Insider selling is a terrible signal: it
   reflects diversification, tax, divorce, and scheduled plans. Note the *adoption
   date* of any 10b5-1 plan — plans adopted shortly before a catalyst, and the amended
   cooling-off requirements, are the only genuinely interesting part of sales data.
7. Emit the brief as a **sizing overlay**, not a directional call.

## Honest expectations

The academic evidence on insider purchases is real but modest, and it is strongest for
routine operating businesses over long horizons — not for binary biotech events. Treat
this skill as a tie-breaker on position size within an existing thesis. It is not a
thesis generator, and a brief from this skill should never be the primary evidence for
a position.

## Not-automatic

Insider activity does not license an inference about non-public trial data. Say this
explicitly in every brief from this skill.

Contract: `../../references/evidence-brief.md`.
