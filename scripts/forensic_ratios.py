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
import argparse, collections, json, sys

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


def series(facts, keys, unit_pref=("USD",)):
    out = {}
    usgaap = facts.get("facts", {}).get("us-gaap", {})
    for k in keys:
        node = usgaap.get(k)
        if not node:
            continue
        for unit, rows in node.get("units", {}).items():
            if unit_pref and unit not in unit_pref:
                continue
            for r in rows:
                if r.get("form") not in ("10-Q", "10-K"):
                    continue
                end = r.get("end")
                if not end:
                    continue
                key = (end, r.get("fp"), r.get("fy"))
                out.setdefault(key, r.get("val"))
        if out:
            break
    return dict(sorted(out.items(), key=lambda kv: kv[0][0]))


def latest_n(s, n=12):
    items = list(s.items())[-n:]
    return [(k[0], v) for k, v in items]


def safe_div(a, b):
    try:
        return round(a / b, 3) if b else None
    except TypeError:
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--facts", required=True)
    ap.add_argument("--model", default="generic", choices=list(MODEL_NOTES))
    ap.add_argument("--periods", type=int, default=12)
    a = ap.parse_args()

    with open(a.facts, encoding="utf-8") as f:
        facts = json.load(f)

    data = {name: latest_n(series(facts, tags), a.periods) for name, tags in TAGS.items()}

    def val(name, i):
        rows = data.get(name) or []
        return rows[i][1] if len(rows) > abs(i) else None

    panel = collections.OrderedDict()
    rev, rec, inv, cogs = val("revenue", -1), val("receivables", -1), val("inventory", -1), val("cogs", -1)
    rev_p, rec_p = val("revenue", -5), val("receivables", -5)

    panel["dso_days_latest"] = safe_div(rec * 365, rev) if rec and rev else None
    panel["dio_days_latest"] = safe_div(inv * 365, cogs) if inv and cogs else None
    panel["receivables_growth_yoy"] = safe_div(rec, rec_p) if rec and rec_p else None
    panel["revenue_growth_yoy"] = safe_div(rev, rev_p) if rev and rev_p else None
    if panel["receivables_growth_yoy"] and panel["revenue_growth_yoy"]:
        panel["receivables_vs_revenue_gap"] = round(
            panel["receivables_growth_yoy"] - panel["revenue_growth_yoy"], 3)
        panel["receivables_gap_read"] = (
            "Receivables outrunning revenue by more than ~10pp for two consecutive "
            "periods is the classic channel/collection warning. Corroborate with an "
            "independent volume series before concluding anything."
            if panel["receivables_vs_revenue_gap"] and panel["receivables_vs_revenue_gap"] > 0.10
            else "No material divergence in the latest period.")

    ni_series = [v for _, v in (data.get("net_income") or []) if v is not None]
    cfo_series = [v for _, v in (data.get("cfo") or []) if v is not None]
    if ni_series and cfo_series:
        n = min(len(ni_series), len(cfo_series), 8)
        ni_sum, cfo_sum = sum(ni_series[-n:]), sum(cfo_series[-n:])
        panel["cfo_to_net_income_multi_period"] = safe_div(cfo_sum, ni_sum)
        panel["cash_conversion_read"] = (
            "CFO/NI persistently below 1.0 across several years is the most durable "
            "single warning in this sector. Above 1.0 with heavy D&A is normal.")

    panel["capitalised_software_latest"] = val("capitalised_software", -1)
    panel["rnd_latest"] = val("rnd", -1)
    panel["goodwill_latest"] = val("goodwill", -1)
    panel["deferred_revenue_latest"] = val("deferred_revenue", -1)

    out = {
        "entity": facts.get("entityName"),
        "cik": facts.get("cik"),
        "model": a.model,
        "panel": panel,
        "raw_series": data,
        "sector_overlay": MODEL_NOTES[a.model],
        "mandatory_next_steps": [
            "Read the words: full-text search for change in accounting estimate, "
            "restatement, material weakness, going concern, auditor change, and any "
            "reworded revenue-recognition policy note.",
            "List every non-GAAP add-back for eight quarters; flag any recurring in 5+.",
            "Rank findings as cash / trajectory / presentation. Do not present a "
            "presentation issue with the rhetoric of a cash issue.",
            "Corroborate externally against an independent volume series, or stand down.",
            "Write the specific disclosure that would clear each flag, with its date.",
        ],
        "disclaimer": "Screening prompts only. Nothing here establishes fraud, and no "
                      "output of this script should assert it.",
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
