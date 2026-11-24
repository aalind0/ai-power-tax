# Load: how much electricity data centers use today

Area owner: `load`. Scope: realized data-center consumption (not pipelines; `markets` covers forecasts and queues).
Status: complete for this pass (2026-11-23). Every number below was read in a primary document this session unless marked **UNVERIFIED**.

## The 10 most important insights

1. **US data centers used about 192 TWh in 2024, or 4.7% of US electricity.** That is up 14% from 2023 and roughly 3x the flat ~60 TWh of 2014–2016.
   LBNL's June 2026 update ([LBNL 2025 Update](https://doi.org/10.71468/P1RP4F)) puts 2024 at 192 TWh (4.7%). EPRI, using an independent method based on site development and including crypto mining, gets 177–192 TWh, or 4–5% ([EPRI Powering Intelligence 2026](https://www.epri.com/research/products/000000003002034696)).
   LBNL's 2024 report had 2018 at 76 TWh (1.9%) and 2023 at 176 TWh (4.4%) ([LBNL 2024](https://escholarship.org/uc/item/32d6m0d1)). The 2025 update revised 2023 down to about 168 TWh (derived from the "+14% 2023→2024" statement).

2. **The forward range is wide, and the latest central estimates sit above the middle of earlier ranges.**
   - 2028: LBNL 2024 gave 325–580 TWh (6.7–12.0%). LBNL's 2025 Reference Case gives 464 TWh.
   - 2030: the LBNL Reference Case is 649 TWh (11.8%), with a compounded range of 521–843 TWh (9.5–15.3%). EPRI 2026 gives 383 / 596 / 793 TWh (9–17%).
   - LBNL's Reference Case has data centers making up 33% of all US load growth from 2024 to 2030.
   - These are projections; `markets` owns pipelines and queues.

3. **Virginia's "~25%" holds up.** Three independent checks agree.
   - EPRI Table A1 puts Virginia data centers at **33.85 TWh, or 25.59% of the state's 2023 consumption**. EPRI's implied denominator (132.3 TWh) matches EIA-861 Virginia retail sales for 2023 exactly.
   - Dominion's 2025 10-K says data centers were **26% (2024) and 28% (2025) of Virginia Power's electricity sales** ([10-K](https://www.sec.gov/Archives/edgar/data/715957/000119312526063120/d-20251231.htm)).
   - EPRI 2026 says Virginia "exceeds 25%" and is the only state above 20%, rising to 39–57% by 2030.
   - A derived lower bound using Dominion alone (excluding co-op-served data centers) gives 17.8% of statewide sales in 2024 and 19.1% in 2025. NOVEC's commercial class would add about 8 more points.

4. **Below Virginia, there is a second tier of small states where data centers already take 7–15% of all power.** EPRI's 2023 figures:
   - Shares: ND 15.4%, NE 11.7%, IA 11.4%, OR 11.4%, WY 11.3%, NV 8.7%, UT 7.7%, AZ 7.4%.
   - Largest absolute users: VA 33.9 TWh, TX 21.8 TWh, CA 9.3 TWh, IL 7.5 TWh.
   - EPRI 2026 nominal IT capacity (2024, medium): **TX 7.3 GW is now above VA 6.4 GW** (EPRI counts crypto mining), followed by OR 3.0, OH 2.1, AZ 1.9, GA 1.8 and IA 1.7 GW.
   - EPRI expects OR, IA, NE, NV, WY, AZ and IN to pass 20% by 2030 in its Medium scenario.

5. **The new load is visible in EIA sales and is highly concentrated** (EIA-861 final, 2019→2025, state totals Parts A+B+D).
   - US commercial sales rose 142 TWh (+10.5%) and total retail sales rose 269 TWh (+7.1%).
   - **Virginia (+32.6 TWh) and Texas (+32.7 TWh) together account for 46% of all US commercial-sector growth.**
   - Virginia's total sales rose 29.2 TWh while its residential sales rose only 0.5 TWh.
   - EIA's own analysis agrees: Virginia commercial sales rose "nearly 30.0 million MWh" from 2019 to 2025, "largely driven by" data centers ([EIA TIE, 5 May 2026](https://www.eia.gov/todayinenergy/detail.php?id=67664)).

6. **Growth at hotspot utilities is large in percentage terms** (`load_utility_sales_growth.csv`; C&I = commercial + industrial).
   - **NOVEC: total sales 5.9 → 14.6 TWh (+150%)**; commercial is now 84% of its sales.
   - Dominion VA: C&I +18.4 TWh (+36%), total +23%, residential +0.6%.
   - Oncor: +40.8 TWh since 2020 (+31%).
   - AEP Ohio: commercial +82%, total +28%.
   - Omaha PPD: commercial +110%, total +39%.
   - MidAmerican (IA): total +28%.
   - APS: +23%. SRP: +19%.
   - AEP Texas North: +118%. Data centers, crypto and oil & gas are not separable there.
   - Ranking every utility by C&I TWh added (`load_utility_ci_growth_rank.csv`), the top 10 equal 63% of the net national C&I gain among utilities. The top 10 are Oncor, Dominion, CenterPoint, AEP Ohio, NOVEC, TNMP, AEP Texas North, FPL, Umatilla EC (OR) and AEP Texas Central.

7. **Some "hotspots" do not yet show it in their sales.**
   - ComEd C&I: −1.7%.
   - Duke Energy Carolinas and Duke Energy Progress C&I: −0.5% to −2.7%. Duke Energy Indiana C&I: −3.9%.
   - PG&E total: −8.6% (CCA delivery included; rooftop solar effect).
   - Georgia Power C&I: only +5.9% over 2019–2025, but its 10-K/10-Q show weather-adjusted commercial sales **+4.1% in 2025 and +9.3% YTD 2026, "largely driven by data centers"**. Georgia statewide commercial sales grew +20%, much of it at EMCs and munis.
   - Takeaway: in many regions, data-center load is still mostly *contracted* rather than *consumed*, or other C&I losses offset it.

8. **Signed commitments far exceed realized load.**
   - Southern's contracts with data centers and other large loads grew from ~9 GW (FY2025) to **~16 GW (Q3 2026)**.
   - AEP Texas holds Letters of Agreement for **~49 GW by 2031**. A single 10.4 GW campus is planned at Piketon, OH (AEP Ohio).
   - Dominion reports ~54.9 GW "in various stages of contracting" (Sept 2026, **UNVERIFIED** secondary). For scale, the PJM Dominion zone's entire summer peak was 23.9 GW in 2025 (+23% vs 2019; winter peak +45%) per EIA.
   - On realized revenue, Dominion's "high load" class went from $1.31B (2023) to $1.81B (2025), and +65% YTD 2026.

9. **Internationally, only Ireland is comparable to Virginia.**
   - Ireland: **23% of metered electricity in 2025** (7.66 TWh), up from 5% in 2015 ([CSO, 7 Jul 2026](https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/)). Data centers there now use more than all urban households combined (18%).
   - Netherlands: 5.0% (2025, provisional, CBS).
   - Germany: 4.2% (2024, 20 TWh, Eurostat via CBS).
   - Great Britain: 2% (2024, 4.5 TWh, DESNZ meter-based), but Slough is at 65% and Hillingdon at 28%.
   - Singapore: ~7% (government statement, year not stated).
   - Denmark: no official realized figure.
   - The US national share (4.7%) is already above every EU country except Ireland, and level with the Netherlands.

10. **Measurement is the biggest weakness: nobody meters US data centers as a category.**
    - Every US number is modeled: LBNL from server shipments, EPRI from site capacity.
    - EIA records data centers as commercial *or* industrial depending on tariff, and reclassification is visible. NOVEC's data-center load moved from industrial to commercial in 2022; EPRI flags the same for Oregon and Virginia.
    - Methods disagree by up to ~2x. For 2023 GB, the capacity-based NESO estimate is 7.6 TWh versus 4.1 TWh from DESNZ meters. Crypto alone was ~70 TWh in 2023 (EIA bottom-up, cited by LBNL); EPRI includes crypto and LBNL excludes it.
    - Capacity is not consumption. Grid interconnection utilization is ~50% (LBNL). EPRI facility data show peak at 62–80% of nameplate. Denmark's data centers used ~60% of their capacity in 2023 (Energistyrelsen AF25).

## Counter-evidence and balance (for the "data centers raise bills" debate)
- **Data centers are still a small share nationally:** 4–5% of US electricity. US load growth since 2019 also came from residential (+79 TWh) and industrial (+48 TWh) sales (EIA-861). In Texas, industrial growth (+56 TWh, partly oil & gas and crypto) exceeds commercial growth.
- **EPRI's cross-check:** comparing modeled data-center load with EIA C&I sales, EPRI concludes that the estimates "could not be significantly higher and still be consistent with observed total electricity sales". This argues against inflated claims of current data-center use.
- **LBNL revised its history down.** The 2024 figure sits at the low end of the 2024 report's range because GPU shipments for 2023–24 were lower than assumed.
- **Residential sales were flat where data-center load grew.** For example, Dominion residential was +0.6% from 2019 to 2025 while C&I was +36%. Spreading fixed costs over more kWh *can* lower average rates if new costs are assigned to the new loads; this is the industry argument (see `markets`/`policy` for LBNL/E3/EEI rate-driver work).
  - A contrary data point from Dominion's revenue table: Virginia Power residential revenue rose from $3.86B (2023) to $4.63B (2025), +20%, while residential kWh rose ~10% (EIA-861). The causes (fuel, riders, base rates, weather) are not separated here; this is for `bills`/`markets` to attribute.
- **Utility guidance and contracts are not consumption.** Many announced GW will not be built, or will ramp slowly (EPRI assumes 20%/yr ramp).

## Caveats
- **Definitions differ.**
  - LBNL: servers, storage, network and infrastructure; excludes crypto.
  - EPRI: small and large data centers *plus* crypto mining.
  - DESNZ: colocation, managed hosting and hyperscale only; excludes enterprise data centers.
  - CSO Ireland: metered sites identified by name and size.
  - CBS: ~200 sites; excludes in-house data centers (est. 142 GWh).
- **Behind-the-meter / co-located load** (on-site gas turbines, nuclear co-location) does not appear in EIA-861 retail sales or in grid-meter statistics. As on-site generation grows, retail-sales proxies will *understate* data-center use. None of the sources here quantify it.
- **EIA-861 caveats.**
  - The Texas TDU volumes (Delivery_Companies table) start in 2020, so Oncor, CenterPoint and AEP Texas use base year 2020. 2020 was a COVID-affected year, which overstates growth slightly.
  - State totals follow EIA's A+B+D convention. The utility rows sum A+C+D.
  - C&I growth is *not* data-center growth. It includes manufacturing, crypto and oil-field electrification.
- **EPRI 2024 2030 state values are mechanical.** They apply national growth scenarios (3.71%/5%/10%/15%) to 2023 state load and are not state forecasts.
- **EPRI 2026 numeric state shares are only in charts.** Only the Virginia range and the "states above 20%" list are in the text.
- **Derived rows** (LBNL 2023/2025/2026 values, Dominion-based Virginia lower bound) are marked `verified=false` with the method spelled out.

## Datasets produced (all in `data/processed/`)

| File | Rows | What | Key columns |
|---|---|---|---|
| `load_state_dc_share.csv` | 253 | Data-center share by state: EPRI 2024 (44 states, 2023 plus four 2030 scenarios); EPRI 2026 text points; US totals from LBNL 2024, LBNL 2025 and EPRI 2026; derived Virginia cross-check | `state, year, scenario, is_projection, dc_twh(_low/_high), total_twh, dc_share_pct(_low/_high), includes_crypto, source, source_url, method, verified, notes` |
| `load_state_dc_capacity_mw.csv` | 450 | EPRI 2026 Table 2 nominal IT capacity (MW) by state, 2021–2024 plus 2030 low/medium/high | `state, year, scenario, nominal_it_capacity_mw, is_projection` |
| `load_utility_sales_growth.csv` | 325 | EIA-861 2019–2025 sales for 26 hotspot utility×state rows, 20 states and the US, with growth vs base year | `entity_type, eia_utility_id, label, state, ba_code, year, base_year, res/com/ind/ci/tot_sales_mwh, *_growth_pct_vs_base, ci_added_twh_vs_base, ci_yoy_pct` |
| `load_utility_ci_growth_rank.csv` | 60 | Top 60 utilities nationally by C&I TWh added, 2019 (or 2020) → 2025 | `rank, eia_utility_id, state, ci_added_twh, ci_growth_pct, com_added_twh, ind_added_twh, tot_growth_pct` |
| `load_utility_dc_disclosures.csv` | 28 | Utility-reported data-center share, revenue, contracts and guidance from 10-K/10-Q and EIA, with quotes and links | `utility, eia_utility_id, period, metric, value, unit, kind (realized/commitment/guidance), quote_or_basis, source_url, verified` |
| `load_international.json` | 10 points | IE, NL, DE, EU table, GB, SG, DK, US, US-VA, World | `country, year, dc_twh, dc_share_pct, series, basis, source_url, verified` |

Join keys: `eia_utility_id`, `state` (2-letter), `year`.

To rebuild (from the project root):
1. `node scripts/load/fetch.mjs <url> <out>` for each PDF/page listed in SOURCES.md.
2. `FETCH_UA="<generic UA>" node scripts/load/fetch_sec_filings.mjs`.
3. `osascript -l JavaScript scripts/load/pdf2txt.js` / `python3 -I scripts/load/html2txt.py` to produce text.
4. `python3 -I scripts/load/build_utility_sales_growth.py`, then `build_state_dc_share.py`, `build_top_ci_growth.py` and `build_disclosures_international.py`.

## Open questions
- What is realized 2025 data-center consumption by state? There is no official source. EIA's pilot data-center survey and the EPRI 2026 Figure 10 values are the best targets.
- How much behind-the-meter data-center load is there, and how fast is it growing?
- How much of Texas C&I growth is data centers versus crypto versus Permian electrification? ERCOT large-load reports may help (`grid`/`markets`).
- Which NOVEC, Mecklenburg EC (VA) and Umatilla EC (OR) sales are data centers? Their commercial jumps (+243% to +932%) fit known hyperscale campuses, but this is **UNVERIFIED** by disclosure.

## Log: what did not work
- WebFetch was denied for datacenterdynamics.com, fool.com, iea.org and euronews.com. iea.org also returned a Cloudflare challenge in the browser, which was not bypassed. The IEA 415 TWh (2024) / ~485 TWh (2025) global figures therefore remain **UNVERIFIED**. The IEA "almost 20% growth in 2025" figure was taken from an IEA slide deck hosted by ADB.
- SEC www returned 403 for a browser UA. A generic research UA (env `FETCH_UA`) works.
- The EIA-861 2019 zip has no Delivery_Companies table, so the Texas TDUs start in 2020.
- AEP's sales-by-class percentage table in the Q3 2026 10-Q is an image and was not extracted.
- Bug found and fixed: `Series.replace('.', None)` in pandas 1.1 pad-fills values instead of blanking them. This doubled some sales and was caught by sanity checks. The `bills` scripts use `np.nan` and are not affected.
- There is no Danish official realized data-center consumption figure. Statistics Denmark and Energistyrelsen Energistatistik 2024 do not split out data centers.
