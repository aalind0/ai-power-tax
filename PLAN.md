# AI Power Tax: site plan

> **Type your address. See how much your power bill has gone up, and how much of it is because of data centers.**

Built on the research in `research/` (see `research/INSIGHTS.md`). Companion to Compute Atlas.

## Principles
1. **Personal first.** The address lookup is the hero. Everything else hangs off "your utility".
2. **Evidence, not outrage.** Every claim shows its source. Region-specific verdicts: strong evidence in PJM, mixed elsewhere. Counter-evidence is always one click away.
3. **Visual over text.** One idea per chart, big numbers, plain words.
4. **Honest gaps.** Unverified items carry a badge; overlapping utilities ask the visitor to confirm.

## Experience (one scrolling story per address, plus national pages)

**0. Hero.** Address box, "use my location", and a sample address chip ("Try Ashburn, VA"). Behind it, an animated US map of utility territories colored by real price change.

**1. Your bill story.**
- Utility name, customers, ownership and grid region.
- Big number: "+X% since 2020 (Y% after inflation)". Estimated monthly bill now vs 2020.
- Line chart: your utility's residential price 2013–2025 plus monthly 2024–2026, against the US and against inflation.

**2. What's inside your bill.**
- A stacked bar of the 1,000 kWh bill: supply/energy, capacity, transmission, distribution, riders, taxes. It uses a real tariff for the 13 utilities researched; otherwise a regional template (EIA generation/transmission/distribution split plus PJM components).
- The parts that rose are highlighted, and a "June 1 capacity step" marker appears for PJM.

**3. The data centers on your grid.**
- A map of your utility territory and grid region with data-center campuses (Compute Atlas).
- Stats: data-center share of state load, the utility's disclosed data-center sales, and pipeline GW against actual.

**4. How much is really data centers?**
- An evidence meter: studies laid out by stance (raises / mixed / lowers), filtered to your region.
- A region verdict card, e.g. PJM: "Market monitor: $29.4B of capacity costs from data-center load". Next to it, the counter-case card (LBNL, E3).

**5. Who pays, who gains.**
- Your state: large-load tariff status, data-center tax-break cost and 2025–26 laws.
- Your utility: capex plan, allowed return, open rate case.
- The winners: power producers' profits, nuclear deals.

**6. Who's hurting.** Your county's energy burden (all households vs low-income), shutoff rate for your utility, arrears.

**7. What you can do.** Open rate case and comment deadline, consumer advocate, PUC link, and a share card ("My bill is up X%. Here's why.").

**National pages**
- **The Map:** utility and state choropleth by real price change, with data-center layers.
- **The Hockey Stick:** PJM capacity prices by zone, 2015–2029.
- **The Wires:** T&D spending and transmission rates.
- **The Evidence:** a library of all 26 studies.
- **Winners:** utility capex, returns and power-producer stocks.
- **About and Data:** methods, sources, licences, verification status.

## Visual language
Light "utility bill / paper" look with an electric accent, to stand apart from Compute Atlas's dark space theme. Big
mono numbers, warm red for increases and calm blue for declines, all charts in d3. Mobile-first: most visitors arrive
from social posts on a phone.

## Tech
- **Hosting:** static site, no build step, GitHub Pages, like Compute Atlas. d3 7.9.0, plus topojson-client for maps (pinned CDN versions).
- **Data build** (`scripts/build-site-data.mjs`) turns `data/processed/*` into site assets:
  - `territories.topo.json`: quantized TopoJSON, target under 3 MB.
  - `utilities/index.json`: name, id, state and headline numbers for every utility.
  - Per-utility shards `utilities/<eia_id>.json`: price series, monthly series, anatomy, capex/ROE, rate cases, shutoffs.
  - `states.json`: policy, load share, burden summary.
  - `national.json`: capacity prices, T&D, evidence, winners.
  - `counties.json`: energy burden for the county lookup.
- **Address flow:**
  1. The Census geocoder (JSONP) returns lat/lng and county FIPS.
  2. A point-in-polygon test on the territory bounding-box index finds the utility.
  3. If several utilities overlap, the visitor picks one. If nothing matches, fall back to the ZIP table, then the county table.
  4. Photon is the fallback geocoder.
- **Privacy:** only the typed address goes to the geocoder. Nothing is stored. No analytics by default.

## Build phases
1. **v1 (core):** hero lookup, sections 1, 2, 3, 4 and 7, The Map, The Hockey Stick, About.
2. **v1.1:** sections 5 and 6, The Wires, The Evidence library, Winners, share cards.
3. **Later:** monthly data refresh job (EIA-861M, PJM auctions), rate-case alerts by email, embeddable widget for local newsrooms.
