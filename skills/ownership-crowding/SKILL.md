---
name: ownership-crowding
description: >
  This skill should be used when the user asks "who owns this", "is it crowded",
  "13F", "hedge fund ownership", "short interest", "squeeze risk", "days to cover",
  "Reg SHO threshold", or wants a positioning overlay before sizing a healthcare position.
metadata:
  version: "0.1.0"
  layer: "Risk"
---

# Ownership and crowding overlay

Assemble a positioning picture from free sources and translate it into a sizing and
liquidity constraint.

## Workflow

1. **Aggregate 13F holdings** for the issuer across the last four quarters. Separate
   the three groups, which behave completely differently:
   - Passive index holders — irrelevant to crowding, large in size.
   - Long-only active — slow, sticky, price-insensitive on the margin.
   - Hedge funds — the crowding that matters.
2. **Compute concentration**: the share of float held by the top 10 active holders,
   and the change in that share over four quarters. The *change* is the signal;
   the level is context.
3. **Pull 13D/G filings** for activist or strategic positions and any recent crossings
   of the 5% threshold.
4. **Layer short interest.** FINRA publishes short interest twice monthly; compute days
   to cover against average daily volume. Check the Reg SHO threshold list for
   persistent delivery failures.
5. **Build the sizing constraint.** Days of the desk's own volume to exit at 20% of ADV,
   under both normal and stressed (one-third) liquidity. This is the number that
   actually binds in a drawdown and the reason this skill exists.
6. **Read the combination.** High hedge-fund concentration plus high days-to-cover plus
   a dated binary catalyst is the setup for violent two-way moves — it argues for a
   smaller position or an options expression, not for a directional view.
7. Emit the brief.

## Caveats that cap confidence

13F is long-only, US-listed, filed 45 days after quarter end, and excludes shorts,
swaps and most derivatives — so it systematically understates hedge-fund exposure and
misses the entire short book. A crowding read from 13F alone is directional at best.
Short interest is twice-monthly with its own lag.

## Non-duplication

The desk already runs your valuation tooling for what the price implies and
`macro-pm-lens` for crowding as a discipline question. This skill supplies the raw
positioning evidence to those, and does not restate their conclusions.

## Not-automatic

Crowding is not a directional signal. It is a constraint on size and on the expression
of a view, and briefs from this skill must say so.

Contract: `../../references/evidence-brief.md`.
