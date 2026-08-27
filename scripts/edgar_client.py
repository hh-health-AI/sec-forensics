#!/usr/bin/env python3
"""SEC EDGAR client: company lookup, XBRL company facts, submissions, full-text search.

Stdlib only, no key. EDGAR requires a descriptive User-Agent with a contact address
and limits requests to roughly 10/second. Set SEC_USER_AGENT, e.g.:

    export SEC_USER_AGENT="Acme Capital research@acme.com"

Usage
-----
    python3 edgar_client.py --ticker VRTX --resolve
    python3 edgar_client.py --cik 0000875320 --facts > facts.json
    python3 edgar_client.py --cik 0000875320 --submissions --forms 8-K --limit 20
    python3 edgar_client.py --search '"material weakness"' --cik 0000875320
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request

TICKERS = "https://www.sec.gov/files/company_tickers.json"
FACTS = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SUBS = "https://data.sec.gov/submissions/CIK{cik}.json"
FTS = "https://efts.sec.gov/LATEST/search-index?q={q}"
FTS2 = "https://efts.sec.gov/LATEST/search-index?q={q}&dateRange=custom"


def ua():
    u = os.environ.get("SEC_USER_AGENT")
    if not u:
        sys.stderr.write("SEC_USER_AGENT not set. EDGAR blocks anonymous clients. "
                         'Export SEC_USER_AGENT="Firm Name contact@firm.com".\n')
        sys.exit(1)
    return {"User-Agent": u, "Accept-Encoding": "gzip, deflate", "Host": None}


def get(url, host=None):
    h = {k: v for k, v in ua().items() if v}
    if host:
        h["Host"] = host
    req = urllib.request.Request(url, headers=h)
    time.sleep(0.12)  # stay under ~10 req/s
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def pad(cik):
    return str(cik).lstrip("CIK").lstrip("0").zfill(10)


def resolve(ticker):
    data = get(TICKERS)
    t = ticker.upper()
    for _, row in data.items():
        if (row.get("ticker") or "").upper() == t:
            return {"ticker": row["ticker"], "title": row["title"],
                    "cik": pad(row["cik_str"])}
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ticker")
    ap.add_argument("--cik")
    ap.add_argument("--resolve", action="store_true")
    ap.add_argument("--facts", action="store_true")
    ap.add_argument("--submissions", action="store_true")
    ap.add_argument("--forms", nargs="*", default=[])
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--search", help="full-text search phrase (2001 onward)")
    a = ap.parse_args()

    cik = pad(a.cik) if a.cik else None
    if a.ticker:
        r = resolve(a.ticker)
        if not r:
            sys.stderr.write("Ticker not found in the SEC company_tickers file.\n")
            sys.exit(2)
        cik = r["cik"]
        if a.resolve:
            json.dump(r, sys.stdout, indent=2); print(); return

    if a.search:
        q = urllib.parse.quote(a.search)
        url = f"https://efts.sec.gov/LATEST/search-index?q={q}"
        if cik:
            url += f"&ciks={cik}"
        try:
            json.dump(get(url, host="efts.sec.gov"), sys.stdout, indent=2); print()
        except urllib.error.HTTPError as e:
            sys.stderr.write(f"Full-text search returned HTTP {e.code}. EDGAR's FTS "
                             "endpoint path changes periodically; the browser UI at "
                             "efts.sec.gov/LATEST/search-index?q= shows the current "
                             "shape. Fall back to --submissions plus document fetch.\n")
            sys.exit(3)
        return

    if not cik:
        ap.error("--cik or --ticker required")

    if a.facts:
        json.dump(get(FACTS.format(cik=cik), host="data.sec.gov"), sys.stdout, indent=2)
        print(); return

    if a.submissions:
        d = get(SUBS.format(cik=cik), host="data.sec.gov")
        recent = d.get("filings", {}).get("recent", {})
        rows = []
        for i in range(len(recent.get("form", []))):
            form = recent["form"][i]
            if a.forms and form not in a.forms:
                continue
            rows.append({
                "form": form,
                "filingDate": recent["filingDate"][i],
                "reportDate": recent.get("reportDate", [""] * (i + 1))[i],
                "primaryDocument": recent["primaryDocument"][i],
                "accessionNumber": recent["accessionNumber"][i],
                "items": recent.get("items", [""] * (i + 1))[i],
                "url": (f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                        f"{recent['accessionNumber'][i].replace('-', '')}/"
                        f"{recent['primaryDocument'][i]}"),
            })
            if len(rows) >= a.limit:
                break
        json.dump({"cik": cik, "name": d.get("name"), "filings": rows},
                  sys.stdout, indent=2)
        print(); return

    ap.error("pick one of --resolve / --facts / --submissions / --search")


if __name__ == "__main__":
    main()
