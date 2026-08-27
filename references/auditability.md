# What "auditable" means here

These engines are built to institutional investor standards. That is a claim about
specific mechanisms, not a tone, so here is the whole list. If any of them is not true
of an output, the output is not finished.

## 1. Every finding is traceable to a primary source

No finding enters a brief without a named source, a retrieval date and the **vintage of
the underlying data** — which is a different date, and usually much earlier. CMS, FAERS
and HCRIS all publish on lags measured in quarters. A figure retrieved today from data
collected eighteen months ago is an eighteen-month-old figure, and the brief says so.

## 2. Confidence is gated by vintage, not by conviction

The confidence score on a brief cannot exceed what the freshness of the data supports.
An analyst who feels certain about a stale number still has to write down a low score.

## 3. Silence is never a negative finding

Every script fails loudly on an empty result set. An endpoint returning nothing means
the query was wrong, the dataset moved, or the data is not published yet — it does not
mean the thing being measured is zero. This is the single most common way open-data
work produces confident wrong answers.

## 4. Known limitations travel with the number

Population restriction, cell suppression, join ambiguity and publication lag are stated
in-line where the figure appears, not deferred to a methodology footnote nobody reads.
A Medicaid utilisation proxy is never presented as national volume.

## 5. Reproducible months later, by someone else

Scripts are stdlib-only Python 3 with no pip install, take `--help`, and print to
stdout. There is no hidden state and no environment to recreate. Where an MCP server is
used, its resolved commit SHA is pinned in `bin/versions.lock`, so the code that
produced a figure can be checked out again.

## 6. Open data only, and no silent substitution

Every input is free and public. If an analysis genuinely needs IQVIA, Symphony,
Definitive, EvaluatePharma or Citeline, the engine says so and stops. It does not quietly
swap in a proxy and present it as equivalent to the paid panel.

## 7. Evidence and view are separated

Engines produce evidence. They do not issue recommendations, price targets or
positioning calls. The separation exists so that the evidence can be audited on its own
merits by someone who disagrees with the conclusion.

## 8. Third-party code is pinned and disclosed

Optional MCP servers are independent community projects standing between you and the
primary source. They are pinned by commit, listed by name and license, and never
authoritative for a figure entering a brief — you cannot cite the internals of someone
else's server.

## 9. Requests are attributable

The User-Agent on every outbound call embeds the plugin, its version and your own
contact string, so a request in an agency's logs traces back to a specific script at a
specific version. The contact is required from the environment; there is no shared
default.
