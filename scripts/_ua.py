"""Shared User-Agent construction for every open-data endpoint these engines call.

Federal open-data endpoints (SEC EDGAR, CMS, Socrata, openFDA, USPTO, CDC) throttle
by User-Agent as well as by IP, and SEC blocks outright on a generic or missing agent.
A published plugin whose every installation sends an identical string is exactly the
pattern they rate-limit, so the contact is required from the environment rather than
carried as a default here.

    export HH_CONTACT="Your Name (you@example.com)"

SEC's documented variable is honoured as an alias so an existing EDGAR setup keeps
working:

    export SEC_USER_AGENT="Your Name (you@example.com)"

Auditability note: the agent string embeds the plugin version and the calling tool, so
a request appearing in an agency's logs is traceable back to a specific script at a
specific version.
"""
import os
import sys

VERSION = "0.1.0"
PLUGIN = os.environ.get("HH_PLUGIN_NAME", "sec-forensics")


def contact() -> str:
    for var in ("HH_CONTACT", "SEC_USER_AGENT"):
        v = os.environ.get(var, "").strip()
        if v:
            return v
    sys.exit(
        "error: HH_CONTACT is not set.\n\n"
        "Open-data endpoints rate-limit unidentified and shared User-Agent strings;\n"
        "SEC EDGAR blocks them outright. This must be your own contact, not a shared\n"
        "default. Set it once:\n\n"
        '    export HH_CONTACT="Your Name (you@example.com)"\n'
    )


def user_agent(tool: str) -> dict:
    return {"User-Agent": f"{PLUGIN}/{VERSION} {tool} ({contact()})"}


def headers(tool: str, **extra) -> dict:
    h = user_agent(tool)
    h.update(extra)
    return h
