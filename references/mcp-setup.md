# Connector architecture for the healthcare engines

## Two kinds of connector — they follow different rules

**Account-level (hosted).** Connected once in the Claude connector directory and
visible to every plugin in the session. Not declared in any `.mcp.json`. Plugins
*reference* these; they never own them, so the one-connector rule does not apply.

| Server | Auth | Referenced by |
|---|---|---|
| CMS Coverage (`hcls.mcp.claude.com/cms_coverage`) | authless | `provider-economics` |
| PopHIVE — Yale harmonised US surveillance | authless | `epi-demand` |
| ClinicalTrials.gov, PubMed, ChEMBL, bioRxiv, Scholar Gateway | authless | multiple |

**Plugin-level (self-hosted stdio).** Declared in exactly one plugin's `.mcp.json`.
This is where the one-connector rule bites: co-installed plugins share the session,
so a second declaration is a duplicate server process, not extra capability.

| Server | Declared in | Consumed by |
|---|---|---|
| `sec-edgar` | `sec-forensics` | your view layer |
| `fda` (openFDA + Orange/Purple Book) | `fda-safety-signals` | `ip-exclusivity` |
| `wonder` (CDC WONDER) | `epi-demand` | — |
| `medicare` (CMS Socrata) | `rx-utilization` | `provider-economics` |
| `ema` | `global-access` | `ip-exclusivity` |

`ip-exclusivity`, `provider-economics` and `evidence-catalysts` declare nothing by
design. That is not a gap — see the division of labour below.

## MCP or script? The test is who is in the loop

Both paths ship in every plugin. They are not redundant; they answer to different
callers.

- **A human refining a query → MCP.** The analyst does not know the right filter
  until they have seen the wrong one. Round-trip latency matters, exactness matters,
  and the model needs to iterate.
- **A schedule producing evidence → script.** The watcher agents run unattended.
  They need to be deterministic, cacheable, diffable, and re-runnable against the
  same vintage three months later when someone asks why the desk was short.

Where the two disagree, **the script is authoritative for anything that goes in a
brief**, because a third-party server sits between you and the source of record and
you cannot cite its internals.

## Vintage hazard: cached reference data

`fda-mcp` ships *locally cached* Orange Book and Purple Book snapshots. Convenient for
a lookup, unsafe for loss-of-exclusivity work: patent listings and use codes change on
a monthly cycle and a stale snapshot silently moves an LOE date. `ip-exclusivity`
therefore keeps `orange_book_loe.py` and `purple_book.py` as the primary path — they
parse the live EOB archive — and treats the MCP as convenience only. Any LOE date that
reaches a brief must carry the archive's own publication date.

## Install

```bash
bin/install-mcp-servers.sh          # clone, build, write versions.lock
bin/install-mcp-servers.sh --verify # smoke-test each server starts and speaks MCP
```

Servers land in `$HC_MCP_HOME` (default `~/.healthcare-mcp`). The installer records
the resolved commit SHA of every server in `versions.lock` and reuses it on every
later run, so a rebuild cannot silently pick up new upstream code. To move a server
forward, edit the ref in `versions.lock` deliberately and re-run.

## Supply-chain posture

Every plugin-level server is third-party community code standing between the desk and
a primary source. Before desk use:

- Read the source. These are small repos; this is an afternoon, not a project.
- Keep `versions.lock` under version control and review the diff on any bump.
- Mount no credentials. None of these servers needs a secret beyond `SEC_USER_AGENT`
  (a contact string, not a key) and an optional `OPENFDA_API_KEY` rate-limit token.
- `sec-edgar-mcp` is AGPL-3.0. Internal use is not distribution, but that is a call
  for counsel, not for this file.
- No server is affiliated with or endorsed by the agency whose data it serves.
