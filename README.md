# The AI Power Tax

**How much of your electricity bill is AI? Type your address and find out.**

### 👉 [Try it: aalind0.github.io/ai-power-tax](https://aalind0.github.io/ai-power-tax/)

Look up any US address to see how much your utility's price has gone up since 2020, how much of it traces to
data-center demand, and what's already locked in. The home page opens on a 3D spike map of the extra dollars a
month the same electricity costs versus 2020, then shows the data-center slice in the PJM grid.

- **Your bill** (`index.html`): the answer up top (increase since 2020, data-center share, locked-in charges), then tabs for why it went up, past & next, your dollar, data centers near you, who pays, and what you can do.
- **How it works** (`story.html`): seven short chapters, from the life of a kilowatt-hour to the evidence on both sides.
- **Findings** (`findings.html`): 14 interactive findings from the data.

Companion to [Compute Atlas](https://github.com/aalind0/compute-atlas).

## Run it
```bash
node scripts/serve.mjs 8124
```
Open http://localhost:8124. It's a static site with no build step, so any static host works, including GitHub Pages.

## Rebuild the site data
```bash
python3 -I scripts/site/build_site_data.py      # data/processed → assets/data/*.json
python3 -I scripts/site/build_spikes.py         # hero spike map → assets/data/spikes.json
python3 -I scripts/site/build_dc_regional.py    # data-center estimates outside PJM → assets/data/dc_regional.json
(cd scripts/site && npm i) && node scripts/site/topo.mjs 0.18 30000   # territories → TopoJSON
```

## Layout
| Path | What |
|---|---|
| `index.html`, `story.html`, `findings.html` | The three pages |
| `css/site.css`, `js/` | `hero3d.js` the spike map, `main.js` the lookup flow, `lookup.js` geocoding and utility matching, `report.js` the bill, `story.js` the chapters, `findings.js` the findings, `charts.js` the d3 charts |
| `assets/data/` | Compact site data, including per-state utility files loaded on demand |
| `data/processed/` | The research datasets (see `research/`) |
| `research/` | Brief, per-area findings and sources, `INSIGHTS.md` |
| `scripts/` | Research fetchers per area, site build, local server |

## Data and method
Prices are EIA-861/861M revenue ÷ sales per utility. "Extra a month since 2020" holds each utility's average usage
constant, so it reflects price, not weather. In PJM the data-center share is the independent market monitor's
attribution of capacity costs to data-center load, spread over PJM's kWh. Outside PJM it is a labeled estimate per
region, built from public filings and grid-operator statements (sources linked on each bill). T&D spending is from
FERC Form 1 via Catalyst PUDL; data-center load from EPRI and LBNL; energy burden from DOE LEAD; shutoffs from
EIA-112; policy from state PUCs and statutes. Unverified items carry a badge on the site. S&P-sourced rate-case
detail is excluded from the repo; only aggregates are used. Nothing here is financial, legal or energy advice.
