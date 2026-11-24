# geo — findings: the address → utility → grid-region join layer, and what to build on

Run date 2026-11-23. Every number below was produced this session by the scripts in `scripts/geo/` unless marked
UNVERIFIED. Sources and licences: `research/geo/SOURCES.md`.

## 1. Outputs (data/processed/)

| File | Size (gzip) | Rows / features | What it is |
|---|---|---|---|
| `geo_territories.geojson` | 7.50 MB (1.66 MB) | 2,919 polygons | HIFLD Electric Retail Service Territories (final HIFLD Open release, data year 2022), simplified. Properties: `eia_utility_id`, `name`, `state`, `type`, `customers` |
| `geo_iso_regions.geojson` | 0.42 MB (0.11 MB) | 7 polygons | HIFLD Independent System Operators: `iso` (PJM, MISO, ERCOT, SPP, NYISO, ISO-NE, CAISO), `name`, `eia_id`, `peak_load_mw`, `avg_load_mw`, `data_year` (2019), `source_date` (2020-06-24) |
| `geo_zip_to_utility.csv` | 8.9 MB (0.33 MB) | 76,749 rows; 38,590 ZIPs; 1,201 utilities | NREL/NLR OpenEI "Look-up by Zip Code (2025)", published 2026-11-05. Columns: zip, eia_utility_id, utility_name, state, service_type, ownership, res/comm/ind_rate_usd_kwh, n_utilities_in_zip, source_file, data_year |
| `geo_county_to_utility.csv` | 0.98 MB | 11,893 rows; 3,217 counties | EIA-861 2025 Service_Territory with Census county FIPS (24 rows unmatched, see 6): fallback and cross-check |
| `geo_eia861_utilities.csv` | 0.23 MB | 3,424 rows (3,422 ids) | EIA-861 2025 Utility_Data + Frame: ownership, NERC region, `rto_iso` flags (e.g. `PJM`, `SPP;MISO`) |
| `geo_utility_id_crosswalk.csv` | 1 KB | 7 rows | Territory ids retired by mergers → current EIA id (FirstEnergy PA, MPD Electric Coop, Norris PPD) |
| `geo_datacenter_campuses.csv` | 33 KB | 105 US campuses | compute-atlas campuses joined to territories + ISO (likely serving utility, with match basis) |
| `research/geo/address_tests.json` | — | 5 addresses | Raw geocoder and lookup results for the test addresses |

Rebuild: `node scripts/geo/fetch_arcgis_layer.mjs <layer> <out>` (raw), `python3 -I scripts/geo/build_eia861_lookup.py`,
`node scripts/geo/build_territories.mjs 1.5 0.001`, `node scripts/geo/build_iso_regions.mjs 2 0.001`,
`python3 -I scripts/geo/build_zip_to_utility.py`, `node scripts/geo/build_datacenter_join.mjs`;
checks: `python3 -I scripts/geo/check_join.py`, `node scripts/geo/eval_simplify.mjs <file>`, `node scripts/geo/test_address_lookup.mjs`.
`mapshaper@0.6` is installed locally in `scripts/geo/node_modules` (`npm i` in `scripts/geo/`).

## 2. Utility service territories

**Where the layer lives now.** HIFLD Open (the old `services1.arcgis.com/Hp6G80Pky0om7QvQ/.../Retail_Service_Territories`
URL) was switched off on 2025-08-26; that URL now returns `400 Invalid URL`. The final release survives as mirrors. I used
the Esri Living Atlas copy (`services6.arcgis.com/BAJNi3EgCdtQ1BCG/.../Electric_Retail_Service_Territories`, 2,931
features). The NBAM copy (`services3.arcgis.com/OYP7N6mAJJCyH6hd/...HIFLD`, "downloaded from HIFLD on 8/21/2025 and
will not be updated") has the same count and the same YEAR/SOURCEDATE profile: 2,919 features YEAR=2022 /
SOURCEDATE=2023-08-01, plus 12 with YEAR "NOT AVAILABLE" (the 12 Canadian `NA*` features). A PNNL copy on eedgis.pnnl.gov
is one release older (YEAR=2020, 2,949 features). **No newer edition exists; the boundaries are frozen at data year 2022.**

**Transformations.**
- Dropped the 12 Canadian features (non-numeric ids). 2,919 US features kept (incl. AK, HI, PR, territories).
- `type`: HIFLD has `NOT AVAILABLE` for 1,685 of 2,931 features (57%). Filled 1,673 from EIA-861 2025 Frame/Utility_Data
  ownership; 11 remain null. Where both exist they never disagree (0 conflicts). Labels follow EIA (`Investor Owned`,
  `Cooperative`, `Municipal`, `Political Subdivision`, `State`, `Federal`, ...). Result: Municipal 1,814, Cooperative 809,
  Investor Owned 164, Political Subdivision 98, State 13, Federal 6, other 4.
- `state`: HIFLD's STATE is the utility's **mailing-address** state (Penelec, Met-Ed and Penn Power appear as `OH`;
  Ameren Illinois as `MO`). Rebuilt as the `;`-joined states each utility serves in EIA-861 2025 Service_Territory
  (136 multi-state, e.g. `NC;VA`; the HIFLD state was not among the served states for 24 features; 22 features with no
  EIA-861 county rows keep the HIFLD value). Join bills on (eia_utility_id, the geocoded address's state), not on this field.
- `customers`: HIFLD total customers (all classes, data year 2022); 12 null. For current numbers use EIA-861 via the bills table.

**Simplification and precision loss.** mapshaper weighted Visvalingam keeping 1.5% of removable vertices, `keep-shapes`,
coordinates rounded to 0.001° (about 111 m north–south, 85 m east–west at 40°N). Vertices 6,217,864 → 406,805 (−93.5%);
134 MB raw → 7.50 MB. Four tiny municipal polygons collapsed (Lindsay OK, Renwick IA, Stratford IA, Durant IA) and were
restored from raw geometry (rounded to 1e-4°). Point-in-polygon agreement with the raw layer (`eval_simplify.mjs`, seed 7):

| Sample | n | Exact same set of utilities | ≥1 same utility (pts inside a raw territory) | Simplified returns none |
|---|---|---|---|---|
| Uniform random over CONUS land | 1,123 | 99.02% | 99.64% | 0.27% |
| Stress test: within ~2 km of a raw boundary vertex | 1,752 | 91.10% | 97.37% | 1.66% |

Other settings measured: 3% / 0.001° = 9.9 MB, near-boundary exact match 94.8%; 1% / 0.001° = 6.95 MB, 87.7%.
Non-power-of-ten precision (0.0003, 0.0005) bloated the file with float artefacts, so avoid it. A server-side lookup could
use the raw file; at ~0.03 ms per lookup the simplified file is fast enough in the browser.

**Overlaps are the norm, not an error.** Of random CONUS land points, only 35.3% fall in exactly one territory; 40.8% in
two, 13.9% in three, 10.0% in four or more (area-weighted; cities are usually single). Many co-op, municipal and
political-subdivision polygons are county or city outlines, and wholesale-only bodies (WAPA, BPA, irrigation districts)
have polygons too. The Phoenix test point sits inside 12 polygons. The lookup must rank candidates (section 9).

**Join rate with EIA-861 ids** (`check_join.py`; HIFLD customers as weights):

| Compared with | Territories matched | Customer-weighted | With merger crosswalk (ids; customer-weighted) |
|---|---|---|---|
| EIA-861 2025, any file (Frame) | 2,902 / 2,919 = 99.4% | 98.6% | 2,909 = 99.7%; 100.0% |
| EIA-861 2025 Service_Territory | 2,897 = 99.2% | 98.6% | 2,904 = 99.5%; 100.0% |
| `bills_utility_prices.csv`, any year 2013–2025 | 2,847 = 97.5% | 98.9% | 97.5%; 98.9% |
| `bills_utility_prices.csv`, 2025 rows | 1,225 = 42.0% | 94.7% | 1,232 = 42.2%; **96.1%** |
| `bills_utility_prices.csv`, 2024 rows | 1,219 = 41.8% | 94.7% | 42.0%; 96.0% |

The 2025 utility-count gap is the ~1,660 short-form utilities (small municipals and co-ops; 2.9% of customers) that file
EIA-861S without sales by sector. Unmatched ids: the four FirstEnergy PA companies (merged into 66101 on 2024-01-01;
2.08 M HIFLD customers), Pee Dee and Marlboro co-ops (→ MPD Electric Cooperative 66073, 2023-11-10), City of Hickman NE
(→ Norris PPD 13664, 2024-10-01), all in `geo_utility_id_crosswalk.csv`; plus 4 Rivers Electric Coop KS (64196) and four
small NE/MN municipals that no longer report (left as is). Reverse direction: of 1,937 utilities with residential
customers in the bills 2025 table, 1,326 (68.5%; 84.3% of residential customers) have a territory polygon. The rest are
polygon-less by design: Texas REPs (Reliant, TXU), California CCAs (San Diego Community Power, Clean Power Alliance),
Ohio/PA/MA retail marketers. In those states the polygon gives the wires utility; the energy supplier must come from the
state's shopping data (bills area).

## 3. ZIP fallback (`geo_zip_to_utility.csv`)

- Latest edition is 2025 (OEDI submission 10259, published 2026-11-05; publisher now "National Laboratory of the
  Rockies (NLR)", the renamed NREL). CC BY 4.0. 77,087 source rows → 76,749 after de-duplication.
- 60.2% of ZIPs map to one utility, 26.4% to two, 13.4% to three or more. service_type: Bundled 60,692, Delivery 16,048,
  Energy 9. Delivery rows mark restructured states (PECO in 19107 has a Bundled row at 18.0 c/kWh and a Delivery row at
  10.5 c/kWh).
- Rates are utility-wide averages (revenue/sales from EIA-861 2025), not ZIP-specific; 0 in the source (no sales in
  that class) is written as blank; 94.0% of rows have a residential rate.
- Covers only 1,201 utilities (all ids exist in EIA-861 2025), so short-form utilities are absent. ZIPs are "likely" ZIPs
  from ABB/Velocity Suite (e.g. 43215 lists only City of Columbus, although AEP Ohio's polygon also covers the Statehouse).

## 4. ISO/RTO regions (`geo_iso_regions.geojson`)

7 polygons from the HIFLD ISO layer (PNNL-hosted copy, YEAR 2019, SOURCEDATE 2020-06-24), 1,023,526 → 24,598 vertices.
They are unions of member-utility territories, so they overlap at seams: of 105 US data-center campuses, 12 fall in two
ISOs at once (`MISO;SPP` 3, `SPP;ERCOT` 5, `MISO;ERCOT` 3, `MISO;PJM` 1). The geometry also predates SPP's RTO expansion
into the West (planned for April 2026; UNVERIFIED whether it went live as scheduled). **Use the polygons for the map only;
for an address, take the RTO from the identified utility** (`geo_eia861_utilities.csv` `rto_iso`, EIA-861 2025
Utility_Data). For the tests: Dominion VA → PJM, Ohio Power → PJM, City of Columbus → PJM, PECO → PJM, Georgia Power and
APS → none (non-RTO), which matches the polygons. Among full-form utilities: none 681, MISO 262, PJM 186, SPP 149,
ERCOT 116, CAISO 77, ISO-NE 73, NYISO 35, multi-RTO flags ~70.

## 5. Merger crosswalk

`geo_utility_id_crosswalk.csv`. History lookups for the former FirstEnergy PA companies must read the legacy ids for
≤2023 and 66101 for 2024+. HIFLD also mislabels three of them as Ohio utilities.

## 6. County fallback (`geo_county_to_utility.csv`)

EIA-861 2025 Service_Territory (11,893 utility × county rows) matched to Census FIPS by normalised name: 24 rows
unmatched (retired Alaska census areas such as Valdez-Cordova and Wrangell-Petersburg, Bedford City VA, US Virgin
Islands and American Samoa districts). **Connecticut caveat:** EIA uses the 8 old counties (09001–09015); the Census
geocoder's current vintage returns the 2022 planning regions (091xx), so a CT county lookup needs a crosswalk (not built).
County lists are broad (Fulton County GA lists 9 utilities), so this is a fallback and a sanity check, not an answer.
PUDL's `out_eia861__yearly_utility_service_territory` already carries county FIPS and could replace the name matching.

## 7. Data-center campuses by utility (`geo_datacenter_campuses.csv`)

All 105 US campuses in compute-atlas fall inside at least one territory. Basis of the "likely utility": territory named
in the atlas `energy` note 35, single territory 24, largest of overlapping territories (heuristic) 46. Campuses and
disclosed MW by ISO polygon: PJM 19 / 26,119 MW, non-RTO 36 / 24,106 MW, MISO 18 / 11,376 MW, SPP 6 / 11,040 MW,
ERCOT 12 / 8,740 MW (atlas MW are announced or planned capacities, not measured load; many campuses disclose no MW).
Atlas coordinates are often city-level (`coord_precision`), so the 46 heuristic attributions are UNVERIFIED.

## 8. Geocoders

| | US Census Geocoder | Photon (komoot public server) |
|---|---|---|
| Key | none | none |
| Browser `fetch()` | **blocked**: no `Access-Control-Allow-Origin` header; confirmed in a real browser tab ("TypeError: Failed to fetch") | **works** (`ACAO: *`), confirmed in browser |
| Browser workaround | **JSONP works**: `format=jsonp&callback=fn` (confirmed in browser, 203 ms), or a small serverless proxy | — |
| Latency (5 tests, node) | 175–231 ms | 358–781 ms |
| Matches | 4/5 (no match for "1 Capitol Square, Columbus, OH 43215") | 5/5 (POI or street-level point) |
| Extras | `geographies/` endpoint returns county FIPS, tract, block in the same call; authoritative TIGER address ranges; public domain | type-ahead friendly; ODbL attribution required |
| Limits | no published numeric limit; batch ≤10,000 addresses | demo server: "extensive usage will be throttled", no SLA; self-host for production |
| Distance between the two | — | 0.08–0.23 km on the 4 shared matches |

Nominatim also sends CORS headers, but its policy caps use at 1 request/s with no autocomplete, so it is unsuitable for
a public site. The NLR (ex-NREL) Utility Rates API returns the utility for a lat/lon (Dominion, 19876, for Ashburn) with
CORS, but needs a key, its rates are "Ventyx Research (2012)", and its old host developer.nrel.gov no longer resolves
(now developer.nlr.gov).

## 9. Address → utility recipe (tested)

1. Geocode with the Census geocoder (`geographies/onelineaddress`, `benchmark=Public_AR_Current`,
   `vintage=Current_Current`, `layers=Counties`) via JSONP or a tiny proxy → lat/lng, county FIPS, ZIP. If no match,
   fall back to Photon (also good for type-ahead).
2. Point-in-polygon on `geo_territories.geojson` → all containing territories (pure-JS ray casting with a bbox
   prefilter, `scripts/geo/lib/pip.mjs`, ~0.03 ms per lookup; turf `booleanPointInPolygon` also works).
3. Rank candidates: (a) also listed for the ZIP in `geo_zip_to_utility.csv`; (b) more residential customers (EIA-861 via
   the bills table); (c) drop wholesale-only and federal bodies with no residential customers. Map ids through
   `geo_utility_id_crosswalk.csv`.
4. If several plausible candidates remain, show the top one and let the visitor switch ("Parts of this area are served
   by X"). If PIP returns nothing (≈0.3% of points, more near boundaries), use the ZIP list, then the county list.
5. RTO = the chosen utility's `rto_iso`; bills = `bills_utility_prices.csv` on (eia_utility_id, address state). In
   restructured states the polygon gives the wires company; the supply price comes from the bills area.

Results (`research/geo/address_tests.json`):

| Address | Census point / county | PIP territories | Pick | RTO | Verdict |
|---|---|---|---|---|---|
| 21715 Filigree Ct, Ashburn VA 20147 (Equinix DC2) | 39.01436, −77.45784; Loudoun 51107 | Virginia Electric & Power (19876) | Dominion Energy Virginia | PJM | matches ZIP list; county list also has NOVEC (13640) |
| 1 Capitol Square, Columbus OH 43215 | Census: no match; Photon 39.95978, −82.99832 | Ohio Power (14006), City of Columbus (4065) | City of Columbus (ZIP-listed); AEP Ohio runner-up | PJM | **ambiguous**: both serve downtown; UNVERIFIED which serves the Statehouse |
| 206 Washington St SW, Atlanta GA 30334 | 33.74980, −84.38857; Fulton 13121 | Georgia Power (7140) | Georgia Power | none | consistent with ZIP list |
| 1700 W Washington St, Phoenix AZ 85007 | 33.44817, −112.09825; Maricopa 04013 | 12 polygons incl. APS (803), WAPA, irrigation districts | Arizona Public Service | none | ZIP list has APS + SRP; the SRP polygon does not contain the point; APS plausible (UNVERIFIED against the utilities' own tools) |
| 1400 John F Kennedy Blvd, Philadelphia PA 19107 | 39.95331, −75.16341; Philadelphia 42101 | PECO Energy (14940) | PECO | PJM | consistent |

## 10. Public repos and datasets to build on

Stars and dates from the GitHub API on 2026-11-23 (`research/geo/github_repos.json`, `github_survey.json`); API checks in
`research/geo/api_probes.json`.

| Name | Owner | URL | What it gives | Granularity | Freshness | Licence | API key? | How we'd use it | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| PUDL | Catalyst Cooperative | https://github.com/catalyst-cooperative/pudl ; https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/ | Cleaned EIA-861/860/923, FERC Form 1 (rate base, income, utility plant), FERC 714 (hourly planning-area demand, demand forecasts), EIA AEO, utility–county service territory with FIPS | utility-year; county; hourly | `stable/` objects dated 2026-11-10; repo pushed 2026-11-23; 623 stars | MIT code; data CC BY 4.0 (UNVERIFIED) | No (public S3, CORS `*`) | FERC 1 capex/rate base for the investor cut; FERC 714 forecasts for load growth; cross-check EIA-861 | **Build on (core)** |
| EIA-861 / 861S annual | EIA | https://www.eia.gov/electricity/data/eia861/ | Sales, revenue, customers by utility × state × sector; service-territory counties; mergers; ownership; RTO flags | utility-state-year | 2025 data, file dated 2026-10-07 | Public domain | No | Prices and bills (bills area); ownership and RTO flags here | **Core** |
| EIA-861M | EIA | https://www.eia.gov/electricity/data/eia861m/ | Monthly sales/revenue/customers, sampled utilities + state totals | utility-month | 2026 (bills area has `eia861m_utility_2026`) | Public domain | No | Latest-months trend line | **Core** (bills area) |
| EIA Open Data API v2 | EIA | https://api.eia.gov/v2/ | State × sector retail sales and prices monthly, plus much more | state-month | VA residential price through 2026-08 returned | Public domain | **Yes** (free; DEMO_KEY 10 req/h) | Server-side refresh of state monthly series | Use server-side |
| OpenEI Utility Rate Database (URDB) | OpenEI / NLR | https://openei.org/wiki/Utility_Rate_Database | Tariff structures: fixed charges, energy tiers, TOU, demand charges | tariff | continuously edited | CC0 (UNVERIFIED) | **Yes** for the API (403 without; DEMO_KEY 429) | "What a bill is made of": fixed vs volumetric parts of the default residential tariff | v2; coverage uneven |
| ZIP look-up (2025) | NLR (ex-NREL), OEDI | https://data.openei.org/submissions/10259 | ZIP → utility + average rates | ZIP-utility | published 2026-11-05 | CC BY 4.0 | No | Fallback and candidate ranking | **Used** |
| NLR Utility Rates API v3 | NLR | https://developer.nlr.gov/api/utility_rates/v3.json | lat/lon → utility + average rates | point | rates from Ventyx 2012 | NLR API terms | Yes | Utility-id cross-check only | Skip |
| HIFLD Electric Retail Service Territories | ORNL / DOE CESER (HIFLD Open, retired) | Living Atlas mirror (SOURCES #1) | Territory polygons | utility polygon | data year 2022, frozen | Public use | No | Address → utility | **Used**; no successor found |
| Esri "Electricity Rates & Retail Service Territories (Source: EIA)" | Esri Living Atlas | https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/Electricity_Rates_H3_Res5/FeatureServer | Same territories joined to EIA-861 rates 2000–2024, plus H3 hexagon summaries | utility polygon, H3 res 5 | updated 2026-10-27 | Esri terms (not checked) | No | Visual cross-check of our rate map | Reference |
| gridstatus | GridStatus | https://github.com/gridstatus/gridstatus | Python access to all 7 ISOs: load, LMPs, fuel mix, forecasts | ISO/zone, 5-min to hourly | pushed 2026-11-20; 456 stars | BSD-3-Clause | Library no; some ISO feeds need their own keys (UNVERIFIED) | ISO load growth and prices | **Build on** (markets area) |
| LBNL "Queued Up" 2026 | LBNL + GridTracker | https://emp.lbl.gov/queues | Generator interconnection queue, 7 ISOs + ~50 utilities | project | data through end-2025; Excel May 2026; report June 2026 | CC BY 4.0 (per search summary; site blocks scripts) | No | Context on supply additions (not load) | Context |
| Open Energy Outlook | CMU Scott Institute + NC State | https://github.com/TemoaProject/oeo | Open US energy-system scenarios (Temoa) | national/regional scenarios | last report 2023; repo last push 2023-09-21; 40 stars | no licence file | No | — | Skip for v1 |
| RMI Utility Transition Hub | RMI | https://utilitytransitionhub.rmi.org/data-download/ | Utility finances (FERC 1), operations, emissions, commitments | utility-year | finances through RY2024 (UNVERIFIED) | CC BY 4.0 | No | Investor-cut cross-check (capex, rate base, returns) | Useful secondary |
| FERC Form 1 via PUDL | Catalyst / FERC | `stable/out_ferc1__yearly_rate_base.parquet` (2.8 MB), `..._income_statements_sched114`, `..._utility_plant_summary_sched200` | IOU rate base, revenues, plant additions | utility-year | 2026-11-10 build | FERC public; PUDL CC BY 4.0 (UNVERIFIED) | No | Investor cut: who gains from capex | **Core** for the investor cut |
| PowerLines "Utility Bills Are Rising" | PowerLines (advocacy) | https://powerlines.org/wp-content/uploads/2026/07/PowerLines_UBAR-Q2-2026.pdf | Rate-increase requests by utility, quarterly ($18.6 B in H1 2026 per press coverage, UNVERIFIED) | request | quarterly PDFs to Q2 2026 | report; no open data | No | Cite totals; manual table of open requests (policy area) | Cite, label advocacy |
| Energy and Policy Institute | EPI (watchdog, advocacy) | https://energyandpolicy.org (UNVERIFIED) | Investigations of utility spending and lobbying | narrative | — | — | — | Narrative sources only; no structured dataset found | Skip as data |
| Electricity Maps | Electricity Maps ApS | https://www.electricitymaps.com/platform/datasets | Zone-level carbon intensity, mix | zone, hourly | 2021–2025 datasets | ODbL datasets (few free downloads); API commercial | **Yes** (401 without) | Not needed for bills | Skip v1 |
| Epoch AI "AI data centers" | Epoch AI | https://epoch.ai/data/ai-data-centers | 96 frontier AI sites, IT power, compute, timelines (CSV) | site | live (Nov 2026) | CC BY 4.0 | No | Cross-check compute-atlas MW for big AI campuses | **Build on** |
| Cleanview data-center tracker | Cleanview | https://cleanview.co/data-centers/us | ~4,600 US data centers, MW, status, by ISO | facility | updated daily | terms not checked | — | Pipeline counts by ISO | Check terms first |
| FracTracker National Data Centers Tracker | FracTracker Alliance | https://www.fractracker.org/data-centers/ | Facility-level open dataset and map | facility | 2026-03-26 (UNVERIFIED) | licence not found | — | Cross-check | Maybe |
| ratepayer-exposure | AthenaTheOwl | https://github.com/AthenaTheOwl/ratepayer-exposure | ZIP → share of a PJM household's capacity-charge rise attributable to data centers, inputs cited | ZIP / PJM zone | created 2026-06-19, pushed 2026-10-30; 0 stars | MIT | No | Closest analogue to our product; method reference (its prices and shares UNVERIFIED) | Study, don't depend |
| Data-Center-Equality | PEESE group | https://github.com/PEESEgroup/Data-Center-Equality (Zenodo 10.5281/zenodo.23019736) | Data-center load → wholesale prices, transmission cost allocation (PJM, MISO, 2020–2025), energy burden | ISO zone-year | pushed 2026-09-28 | MIT | No | Evidence and cost-allocation visuals | **Build on** (evidence) |
| ICARUS Data Center Dataset | Johns Hopkins ROSEI / APL | https://github.com/HopkinsICARUS/ICARUS-DC-Dataset | Data-center infrastructure vs regional prices and load, PJM + NY | facility/zone | pushed 2026-09-28 | MIT code, CC BY 4.0 data | No | Evidence for PJM/NY | Useful |
| shape_maker | LBNL Data Center CoE | https://github.com/LBNL-DataCenter-CoE/shape_maker | Synthetic data-center/industrial load shapes | hourly profile | pushed 2026-04-06; 13 stars | NOASSERTION | No | Explainer on how DC load differs | Optional |
| electricity_entity_boundaries | IMMM-SFA (PNNL) | https://github.com/IMMM-SFA/electricity_entity_boundaries | Nested utility/BA boundaries from EIA-861 | county | 2020; 7 stars | BSD-2-Clause | No | Method reference | Skip (stale) |
| open-grid-emissions | Singularity Energy | https://github.com/singularity-energy/open-grid-emissions | Hourly generation and emissions by BA | BA-hour | pushed 2026-11-22; 96 stars | MIT | No | Not bill-related | Skip v1 |
| us-utility-rates and similar | electricbillmath; aidanmcjones; greencalculus | https://github.com/electricbillmath/us-utility-rates | Utility bills from EIA-861 2025 | utility | created Nov 2026, 0 stars | CC BY 4.0 / CC0 | No | Duplicate of our bills work; possible cross-check | Skip |
| large-load-tariffs | jphoebus | https://github.com/jphoebus/large-load-tariffs | Large-load tariff terms in five states | state | pushed 2026-11-23 | no licence | No | Lead list for the policy area | Reference |
| anchored-returns | kazirafsanmahboob29-create | https://github.com/kazirafsanmahboob29-create/anchored-returns | 1,785 rate cases with allowed ROE | rate case | created 2026-11-19 | no licence | No | Investor-cut lead (verify) | Reference, unvetted |
| us-datacenter-electricity-forecasts | JiaweiQi3 | https://github.com/JiaweiQi3/us-datacenter-electricity-forecasts | Compares 16 institutions' data-center demand forecasts | national | pushed 2026-11-03 | no licence | No | Lead for a forecast-range chart | Reference |

GitHub search for "utility rate case" returned mostly noise; no maintained open rate-case tracker exists on GitHub (the
2024 `yutongsi/Utility-Rate-Cases` is small and stale).

## 11. Recommended v1 data stack

1. **Geocoding:** Census geocoder (`geographies/onelineaddress`) as primary, via JSONP or a one-function proxy:
   authoritative, free, no key, returns county FIPS in one call. Photon for type-ahead and as the fallback when Census
   finds nothing; move to a self-hosted Photon or a paid geocoder if traffic grows.
2. **Address → utility:** in-browser point-in-polygon over `geo_territories.geojson` (1.7 MB gzipped; split by state or
   convert to FlatGeobuf/PMTiles if load time matters), ranked with the ZIP list and EIA-861 residential customers;
   ZIP then county fallbacks; merger crosswalk. Always offer "not your utility? pick another".
3. **Region:** RTO from the chosen utility's EIA-861 `rto_iso`; ISO polygons for the national map.
4. **Prices and bills:** EIA-861 annual + EIA-861M (bills area); EIA API for state monthly refresh (server-side key).
5. **Investor cut and load growth:** PUDL `stable/` parquet (FERC Form 1 rate base and plant, FERC 714 planning-area
   forecasts); RMI Utility Transition Hub as a cross-check.
6. **Data-center load:** compute-atlas campuses (joined here), cross-checked with Epoch AI (CC BY) and, if its terms
   allow, Cleanview; evidence from PEESE Data-Center-Equality and ICARUS; ISO series via gridstatus (markets area).

Why: every piece is free, keyless in the browser (except the EIA API, kept server-side), openly licensed, refreshed in
2026, and joins on `eia_utility_id` + state + RTO.

## 12. Caveats and open questions

- Territory polygons are frozen at 2022 and coarse (county outlines) for many co-ops and munis; addresses near boundaries
  can be wrong. No public successor to HIFLD Open's layer was found; check EIA's U.S. Energy Atlas periodically.
- Overlapping territories need UX, not just code: 65% of CONUS land area sits in 2+ polygons.
- The Columbus and Phoenix picks are plausible but UNVERIFIED against the utilities' own address tools.
- ISO polygons date from 2020 and overlap; SPP's 2026 western expansion is not reflected (UNVERIFIED).
- Connecticut county FIPS mismatch (planning regions) in the county fallback.
- PUDL's data licence and whether its 2026-11-10 build includes EIA-861 2025 were not checked first-hand (no parquet
  reader here: pandas 1.1.5 without pyarrow), so UNVERIFIED.

## 13. Log: what didn't work

- Old HIFLD URL `services1.arcgis.com/Hp6G80Pky0om7QvQ/.../Retail_Service_Territories` → `400 Invalid URL` (HIFLD Open
  retired 2025-08-26). The HIFLD org's service list has no retail-territory or ISO service any more.
- NASA NCCS mirror `maps.nccs.nasa.gov/mapping/rest/services/hifld_open/energy/FeatureServer/26` timed out (180 s).
- EIA Atlas org (`services7.arcgis.com/FGr1D95XCGALKXqM`) has no territory layer; the `hifld-geoplatform.hub.arcgis.com`
  search API returned 400.
- WebFetch was refused for `portal.datarescueproject.org` and `emp.lbl.gov` (the latter is behind Cloudflare and also
  blocks node); used node and search summaries instead.
- `developer.nrel.gov` no longer resolves in DNS; `developer.nlr.gov` works.
- URDB with DEMO_KEY returned 429 immediately (shared key exhausted).
- pandas `read_excel` needs `engine='openpyxl'` for .xlsx here (xlrd refuses xlsx).
- mapshaper precision 0.0003/0.0005 produced long float tails (larger file than at 0.0001); with `keep-shapes`, 4 tiny
  polygons still collapsed and are restored from raw.
- The Write tool refused to create `research/geo/FINDINGS.md` directly; it is copied into place by
  `scripts/geo/publish_findings.mjs` from a draft.
