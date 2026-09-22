#!/usr/bin/env python3
"""Compute a healthcare-tuned forensic ratio panel from SEC XBRL company facts.

Stdlib only. Feed it the JSON produced by `edgar_client.py --facts`.

Usage
-----
    python3 edgar_client.py --ticker XYZ --facts > facts.json
    python3 forensic_ratios.py --facts facts.json --model specialty-pharma

Models: specialty-pharma | medtech | tools-dx | provider | payor | generic

Ratios are screening prompts, not verdicts. Nothing here establishes fraud.
"""
import argparse, datetime, json, math, sys

TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax",
                "RevenueFromContractWithCustomerIncludingAssessedTax",
                "Revenues", "SalesRevenueNet"],
    "receivables": ["AccountsReceivableNetCurrent", "ReceivablesNetCurrent"],
    "inventory": ["InventoryNet"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "rnd": ["ResearchAndDevelopmentExpense"],
    "deferred_revenue": ["ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent"],
    "goodwill": ["Goodwill"],
    "intangibles_additions": ["PaymentsToAcquireIntangibleAssets"],
    "capitalised_software": ["CapitalizedComputerSoftwareNet",
                             "PaymentsToDevelopSoftware"],
    "assets": ["Assets"],
}

MODEL_NOTES = {
    "specialty-pharma": [
        "Rising DSO with a payer-mix shift toward Medicaid/Part D: test the gross-to-net "
        "reserve. Cross-read rx-utilization -> gross-to-net-bridge.",
        "Strip collaboration and milestone revenue; trend product revenue alone.",
        "Inventory build into a known LOE is a red flag, not prudence.",
    ],
    "medtech": [
        "Receivables growth outrunning revenue growth is the distributor-loading tell.",
        "Warranty reserve flat against rising MAUDE events: cross-read fda-safety-signals.",
        "Watch capitalised development against flat R&D expense.",
    ],
    "tools-dx": [
        "Instrument-placement revenue timing vs consumable life: read the policy note.",
        "Academic end-market softness hides in mix. Cross-read epi-demand -> "
        "nih-reporter-endmarket.",
    ],
    "provider": [
        "Post-606, implicit price concessions move between revenue reduction and bad "
        "debt without changing cash. Watch the classification, not the ratio.",
        "Acquisition-driven growth masks same-facility trends. Demand same-store metrics.",
        "Cross-read provider-economics -> hospital-margin-forensics for the cost-report view.",
    ],
    "payor": [
        "Prior-period IBNR reserve releases flatter current MLR. Read the development "
        "table, never the headline MLR.",
        "Risk-adjustment revenue growing faster than acuity evidence is the RADV risk.",
        "Cross-read provider-economics -> ma-margin-normalization.",
    ],
    "generic": ["No sector overlay applied. Pick a model for the healthcare-specific reads."],
}


INSTANTS = {"receivables", "inventory", "deferred_revenue", "goodwill",
            "capitalised_software", "assets"}


def days(start, end):
    return (datetime.date.fromisoformat(end) -
            datetime.date.fromisoformat(start)).days + 1


def series(facts, keys, instant=False, as_of=None):
    """Select one tag, retaining actual periods and the latest eligible filing.

    A comparative period's fy/fp describes its filing, not necessarily the
    observation. Never use those fields as the period key.
    """
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in keys:
        selected = {}
        for row in gaap.get(tag, {}).get("units", {}).get("USD", []):
            if row.get("form") not in ("10-Q", "10-K", "10-Q/A", "10-K/A"):
                continue
            if not row.get("filed") or (as_of and row["filed"] > as_of):
                continue
            start, end, value = row.get("start"), row.get("end"), row.get("val")
            if not end or not isinstance(value, (int, float)) or isinstance(value, bool):
                continue
            if not math.isfinite(value) or bool(start) == instant:
                continue
            try:
                duration = days(start, end) if start else 0
                datetime.date.fromisoformat(end)
            except ValueError:
                continue
            if start and duration <= 0:
                continue
            key = (start, end)
            record = {k: row.get(k) for k in
                      ("start", "end", "val", "filed", "accn", "form")}
            record.update(tag=tag, duration_days=duration)
            previous = selected.get(key)
            rank = (row["filed"], row.get("accn", ""))
            if previous is None or rank > (previous["filed"], previous.get("accn") or ""):
                selected[key] = record
            elif rank == (previous["filed"], previous.get("accn") or "") and value != previous["val"]:
                raise ValueError("Conflicting facts for the same period and filing: " + tag)
        if selected:
            return sorted(selected.values(), key=lambda r: (r["end"], r["start"] or ""))
    return []


def quarters(rows):
    """Use reported quarters or derive them from nested, same-start YTD periods."""
    result = {}
    for row in rows:
        if 70 <= row["duration_days"] <= 110:
            result[(row["start"], row["end"])] = dict(row, derived=False)
    for current in rows:
        for previous in rows:
            if current["start"] != previous["start"] or previous["end"] >= current["end"]:
                continue
            start = (datetime.date.fromisoformat(previous["end"]) +
                     datetime.timedelta(days=1)).isoformat()
            duration = days(start, current["end"])
            if not 70 <= duration <= 110:
                continue
            key = (start, current["end"])
            if key in result:
                continue
            result[key] = dict(current, start=start, duration_days=duration,
                               val=current["val"] - previous["val"], derived=True,
                               components=[previous, current])
    return sorted(result.values(), key=lambda r: (r["end"], r["start"]))


def ttm(rows):
    """Annual observations or four contiguous quarters; never sum overlapping YTDs."""
    result = {r["end"]: dict(r, basis="reported annual")
              for r in rows if 350 <= r["duration_days"] <= 380}
    qs = quarters(rows)
    for last in qs:
        if last["end"] in result:
            continue
        chain = [last]
        while len(chain) < 4:
            target = (datetime.date.fromisoformat(chain[0]["start"]) -
                      datetime.timedelta(days=1)).isoformat()
            candidates = [r for r in qs if r["end"] == target]
            if len(candidates) != 1:
                break
            chain.insert(0, candidates[0])
        if len(chain) == 4 and 350 <= days(chain[0]["start"], last["end"]) <= 380:
            result[last["end"]] = {
                "start": chain[0]["start"], "end": last["end"],
                "val": sum(r["val"] for r in chain),
                "duration_days": days(chain[0]["start"], last["end"]),
                "basis": "four contiguous quarters", "components": chain,
            }
    return result


def safe_div(a, b):
    if a is None or b is None or b <= 0:
        return None
    return round(a / b, 4)


def year_ago(records, end):
    candidates = [r for r in records if 350 <= days(r["end"], end) - 1 <= 380]
    return min(candidates, key=lambda r: abs(days(r["end"], end) - 366)) if candidates else None


def analyse(facts, model="generic", periods=12, as_of=None):
    data = {name: series(facts, tags, name in INSTANTS, as_of)
            for name, tags in TAGS.items()}
    if not any(data.values()):
        raise ValueError("No usable dated USD facts; check input, tags, and --as-of.")
    flows = {name: ttm(rows) for name, rows in data.items() if name not in INSTANTS}
    revenue = flows.get("revenue", {})
    # Fix one observation date for the entire panel. A newer balance cannot be
    # divided by an older revenue period simply because both are 'latest'.
    end = max((r["end"] for rows in data.values() for r in rows), default=None)
    def balance(name):
        return next((r["val"] for r in data[name] if r["end"] == end), None)
    def flow(name):
        return flows.get(name, {}).get(end)
    def value(name):
        row = flow(name)
        return row["val"] if row else None
    rev, cogs = flow("revenue"), flow("cogs")
    rec, inv = balance("receivables"), balance("inventory")
    panel = {
        "dso_days_latest": safe_div(rec * rev["duration_days"], rev["val"])
            if rec is not None and rev else None,
        "dio_days_latest": safe_div(inv * cogs["duration_days"], cogs["val"])
            if inv is not None and cogs else None,
        "receivables_growth_yoy": None, "revenue_growth_yoy": None,
        "receivables_vs_revenue_gap": None,
        "cfo_to_net_income_ttm": None,
    }
    prev_rec = year_ago(data["receivables"], end)
    prev_rev = year_ago(list(revenue.values()), end)
    if rec is not None and prev_rec and prev_rec["val"] > 0:
        panel["receivables_growth_yoy"] = round(rec / prev_rec["val"] - 1, 4)
    if rev and prev_rev and prev_rev["val"] > 0:
        panel["revenue_growth_yoy"] = round(rev["val"] / prev_rev["val"] - 1, 4)
    rg, vg = panel["receivables_growth_yoy"], panel["revenue_growth_yoy"]
    if rg is not None and vg is not None and prev_rec["end"] == prev_rev["end"]:
        panel["receivables_vs_revenue_gap"] = round(rg - vg, 4)
    ni, cfo = flow("net_income"), flow("cfo")
    if ni and cfo and ni["start"] == cfo["start"]:
        panel["cfo_to_net_income_ttm"] = safe_div(cfo["val"], ni["val"])
    for name in ("capitalised_software", "goodwill", "deferred_revenue"):
        panel[name + "_latest"] = balance(name)
    panel["rnd_latest"] = value("rnd")
    return {
        "schema_version": 2, "entity": facts.get("entityName"), "cik": facts.get("cik"),
        "model": model, "as_of_filing_date": as_of, "observation_end": end,
        "panel": panel, "raw_series": {k: v[-periods:] for k, v in data.items()},
        "ttm_inputs": {k: v.get(end) for k, v in flows.items()},
        "sector_overlay": MODEL_NOTES[model],
        "limitations": [
            "USD us-gaap facts only; first usable tag per metric. No custom-tag mapping.",
            "Latest eligible filing wins for each actual period. Derived quarters may "
            "combine separately filed YTD observations; inspect their components.",
            "DSO/DIO use period-end balances and matched TTM flows, not average balances.",
            "Missing or mismatched periods return null, never an annualized partial quarter.",
            "YoY fields are fractional changes (0.20 means 20%), not growth multiples.",
            "Cash conversion uses matched TTM periods and requires positive net income.",
            "Read product revenue, reserve disclosures and independent volume evidence "
            "before interpreting a screening ratio. No output establishes fraud.",
        ],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--facts", required=True)
    ap.add_argument("--model", default="generic", choices=list(MODEL_NOTES))
    ap.add_argument("--periods", type=int, default=12,
                    help="number of source observations shown per metric")
    ap.add_argument("--as-of", help="include only filings available on YYYY-MM-DD")
    a = ap.parse_args()
    try:
        if a.periods < 1:
            raise ValueError("--periods must be positive")
        if a.as_of:
            datetime.date.fromisoformat(a.as_of)
        with open(a.facts, encoding="utf-8") as f:
            result = analyse(json.load(f), a.model, a.periods, a.as_of)
    except (ValueError, KeyError, TypeError) as exc:
        ap.exit(2, "Invalid or insufficient facts: " + str(exc) + "\n")
    json.dump(result, sys.stdout, indent=2, allow_nan=False)
    print()


if __name__ == "__main__":
    main()
