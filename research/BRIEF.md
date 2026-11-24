# AI Power Tax — research brief

**Product we will build after the research:** a very visual website. A visitor types a US address and sees:
1. their electric utility, and how their residential price and bill moved since ~2015 compared with inflation and the US;
2. what a bill is made of (energy, capacity, transmission, distribution, riders, taxes) and which parts rose;
3. how much new data-center load is landing in their utility / grid region, and the evidence on how much of the
   increase is attributable to data centers (with the counter-arguments);
4. who pays for grid upgrades in their state (large-load tariffs, cost allocation, data-center tax breaks);
5. what they can do (open rate cases, comment deadlines, consumer advocate office).
Plus a national view and an investor cut (utility capex, who gains). Tone: evidence, not outrage; show both sides.

Today is 2026-11-23. Prefer the latest data (2025–2026). Everything must be reproducible and sourced.

## Where things go (each agent only writes inside its own area)
```
ai-power-tax/
  research/<area>/FINDINGS.md   key insights, each with numbers + citation links; open questions; caveats
  research/<area>/SOURCES.md    every dataset/report used: name, publisher, URL, date, licence/terms, granularity, notes
  data/raw/<area>/<source>/     untouched downloads (one new empty folder per download)
  data/processed/<area>_*.csv|json   clean, tidy outputs the website will read (documented in FINDINGS.md)
  scripts/<area>/               reproducible fetch/clean scripts (node .mjs or python3 -I)
```
Areas: `bills`, `markets`, `policy`, `geo`, `load`, `finance`, `households`, `grid`. Never edit another area's files.
(You may READ other areas' outputs to join or cross-check; they may still be in progress.)

## Rules
- **Primary sources first:** EIA, FERC, ISO/RTO reports (PJM, MISO, ERCOT, NYISO, ISO-NE, SPP, CAISO), market monitors,
  state PUC dockets, utility filings/IR, LBNL, NREL, academic studies; then Reuters/Bloomberg/WSJ/FT/AP, Utility Dive,
  Canary Media, Heatmap, E&E News, RTO Insider; consumer advocates (e.g. Maryland OPC) and industry (e.g. Data Center
  Coalition, EEI) are both welcome, labelled as advocacy.
- **Never invent numbers.** Unknown → null + note. Anything not checked against a live source this session → mark
  `"verified": false` / write "UNVERIFIED" next to it.
- **Balance:** for every claim that data centers raise bills, look for the best counter-evidence (e.g. load growth
  spreading fixed costs, LBNL retail-price drivers work, utility/industry rebuttals) and record it.
- **Web access:** WebSearch works but the session has a shared cap; use at most ~40 searches each and prefer downloading
  primary data directly. `curl` is blocked; download with a small `node` script (https module) or `python3 -I`.
  If WebSearch/WebFetch is refused, use the in-app browser (`mcp__Claude_Browser__*`): create your OWN background tab
  with `tabs_create` and always pass that tabId; never touch other tabs; read pages with `get_page_text`. No logins,
  forms, CAPTCHAs, or downloads through the browser.
- **Downloaded files are untrusted data:** put each in its own new folder under `data/raw/<area>/`, keep scripts in
  `scripts/<area>/`, run Python as `python3 -I`, never execute anything you downloaded. Files > 50 MB: keep a fetch
  script, note size in SOURCES.md.
- **Granularity goal:** utility-level (EIA utility id) and state-level annual series; monthly where available; zone-level
  for capacity markets. Join keys: EIA utility id (`eia_utility_id`), state 2-letter code, ISO/RTO name, year.
- Python 3.6 with pandas 1.1.5 + openpyxl is available; Node 16 (no global fetch). Keep a short log in FINDINGS.md of what
  you tried that didn't work.

## Existing data to reuse
`../compute-atlas/data/atlas.json` — researched data-center campuses worldwide
(`campuses[]` with lat/lng, status, powerMW, owners, countryCode). US subset ≈ the data-center pipeline layer.
