#!/usr/bin/env python3
"""Detect open-market insider purchase clusters from SEC Form 4 filings.

Stdlib only. Needs SEC_USER_AGENT.

Usage
-----
    python3 form4_clusters.py --cik 0000875320 --days 120
    python3 form4_clusters.py --cik 0000875320 --days 180 --min-insiders 3

Strips option exercises, tax withholding (code F) and gifts. Sales are reported but
deliberately down-weighted: insider selling is a poor signal.
"""
import argparse, collections, datetime, json, os, re, sys, time, urllib.request

SUBS = "https://data.sec.gov/submissions/CIK{cik}.json"
ARCH = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{doc}"


def headers():
    u = os.environ.get("SEC_USER_AGENT")
    if not u:
        sys.stderr.write('SEC_USER_AGENT not set. Export "Firm Name contact@firm.com".\n')
        sys.exit(1)
    return {"User-Agent": u}


def fetch(url):
    time.sleep(0.12)
    req = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", errors="replace")


def tag(xml, name):
    m = re.search(rf"<{name}>\s*(?:<value>)?\s*([^<]+)", xml)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cik", required=True)
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--min-insiders", type=int, default=3)
    ap.add_argument("--max-filings", type=int, default=80)
    a = ap.parse_args()

    cik = str(a.cik).lstrip("0").zfill(10)
    subs = json.loads(fetch(SUBS.format(cik=cik)))
    recent = subs.get("filings", {}).get("recent", {})
    cutoff = (datetime.date.today() - datetime.timedelta(days=a.days)).isoformat()

    txns, checked = [], 0
    for i, form in enumerate(recent.get("form", [])):
        if form != "4" or recent["filingDate"][i] < cutoff:
            continue
        if checked >= a.max_filings:
            break
        checked += 1
        acc = recent["accessionNumber"][i].replace("-", "")
        doc = recent["primaryDocument"][i]
        url = ARCH.format(cik=str(int(cik)), acc=acc, doc=doc)
        try:
            xml = fetch(url.replace(".html", ".xml") if doc.endswith(".html") else url)
        except Exception:  # noqa: BLE001
            continue
        owner = tag(xml, "rptOwnerName")
        officer = tag(xml, "officerTitle")
        for block in re.findall(r"<nonDerivativeTransaction>.*?</nonDerivativeTransaction>",
                                xml, re.S):
            code = tag(block, "transactionCode")
            ad = tag(block, "transactionAcquiredDisposedCode")
            shares = tag(block, "transactionShares")
            price = tag(block, "transactionPricePerShare")
            plan = "1" if re.search(r"10b5-1", block, re.I) or re.search(r"10b5-1", xml, re.I) else "0"
            if code in ("F", "G", "A") and code != "P":
                continue
            try:
                sh = float(shares or 0)
            except ValueError:
                sh = 0.0
            txns.append({"owner": owner, "title": officer, "date": recent["filingDate"][i],
                         "code": code, "acquired_disposed": ad, "shares": sh,
                         "price": price, "possible_10b5_1_plan": plan, "url": url})

    buys = [t for t in txns if t["code"] == "P" and t["acquired_disposed"] == "A"]
    sells = [t for t in txns if t["code"] == "S"]
    buyers = collections.Counter(t["owner"] for t in buys)
    officers_buying = {t["owner"] for t in buys if t["title"]}

    out = {
        "cik": cik,
        "entity": subs.get("name"),
        "window_days": a.days,
        "form4_filings_examined": checked,
        "open_market_purchases": buys,
        "open_market_sales_downweighted": sells,
        "distinct_buyers": len(buyers),
        "operating_officers_among_buyers": sorted(officers_buying),
        "cluster_detected": len(buyers) >= a.min_insiders,
        "reading": [
            "One director buying is noise. Three or more insiders buying on the open "
            "market in a short window, INCLUDING operating executives, is the only "
            "pattern with any historical basis.",
            "Weight by size relative to the individual's existing holding, not dollars.",
            "Sales are a poor signal (diversification, tax, scheduled plans). The one "
            "interesting element is the ADOPTION DATE of a 10b5-1 plan relative to a "
            "known catalyst.",
            "This is a sizing overlay within an existing thesis, never a thesis on its own.",
            "Insider activity licenses NO inference about non-public trial data.",
        ],
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
