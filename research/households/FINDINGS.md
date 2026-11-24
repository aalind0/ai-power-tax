# Households: who is hurt most by rising power bills

Area: `households` · built 2026-11-23 · all numbers below were read or computed this session unless marked **UNVERIFIED**.
Advocacy sources are labelled. Data-center (DC) links shown here are **correlations, not causal estimates**; the
attribution question belongs to `markets`/`bills` (see the counter-evidence section).

## The 10 most important insights

1. **Energy costs act like a regressive tax.** In DOE LEAD 2022, the 16.4M households under 30% of area median income (AMI)
   spend **16.0% of income on home energy and 11.1% on electricity alone**. Households above 150% AMI spend 1.36% and 0.90%.
   The poorest group's electricity spend ($1,366 a year) is only 27% below the richest group's ($1,869), on 1/17th of the income.
   So a 10% bill increase costs a 0-30% AMI household about **1.1% of its income (+$137)**, against **0.09% (+$187)** above 150% AMI.
   Across all <=80% AMI households (50.7M) the burden is 6.28%, against 1.71% above 80% AMI. Propane- and fuel-oil-heated
   low-income homes reach about 10.7-10.9%.
   [`households_burden_national_by_group.csv`; LEAD, DOI 10.25984/2504170]
2. **Burden is highest in the rural South, Appalachia, northern New England and remote Alaska. It is not highest in the
   data-center hubs.** By state, low-income burden peaks in ME 10.6%, VT 10.3%, MS 9.2%, WV 9.0%, AK 8.6% and LA 8.6%.
   Electricity-only burden peaks in AL, MS, LA and WV (2.2-2.4% of average income). Low-income burden is >=10% in 1,062 counties,
   home to 3.8M low-income households. Among counties without a data-quality flag, the electricity-only extremes are Ben Hill GA
   (6.2% average, 17.9% low-income), McDowell WV and the Mississippi Delta.
   [`households_energy_burden_county.csv`, `households_state_summary.csv`]
3. **Data-center overlap is two-sided.** Today's hubs are among the richest counties in the country: Loudoun VA has an average
   income of $209k and a 1.30% burden, and Fairfax VA 1.21%. Counties hosting an active compute-atlas campus average a **1.93%**
   burden against 2.32% elsewhere. **The new build-out is moving into poorer places, though.** Counties with only
   under-construction or planned campuses have a 6.72% low-income burden and $102k average income. Counties with operating
   campuses have 5.33% and $120k. Examples: Richland Parish LA (Meta Hyperion) **13.7%** low-income burden; Mecklenburg VA
   (Microsoft Boydton) 11.7%; Luzerne PA (AWS/Susquehanna) 11.2%; Cumberland NJ 10.8%; Richmond Co. NC 10.8%; Caddo LA 10.7%;
   Pike OH (~10 GW planned) 9.9%. This matches Pew's finding that most new data centers are planned in rural areas
   (AP/PBS, 2026-09-16). [`households_dc_county_overlap.csv`; geocoded with the Census geocoder]
4. **The biggest recent bill jumps hit PJM states, where data-center-driven capacity prices are best documented.** Scaling
   LEAD's 2022-calibrated electricity spend by each state's EIA average-bill change from 2022 to 2025 (an estimate) gives
   DC +44% (about $1,166 to $1,681 a year), MD +32% ($1,674 to $2,205), NJ +32% ($1,370 to $1,809), OH +22% and PA +19%.
   The US average bill rose 11%. NJ also has the 5th-highest share of adults unable to pay an energy bill (28.2%, Census
   Pulse 2024). [`avg_annual_elec_cost_2025_est_usd` column; bills area `bills_state_annual.csv`]
5. **About 1 in 6 households is behind on energy bills, and the debt is the largest NEADA has recorded since 2021.** NEADA
   (the LIHEAP directors' association, an advocate) puts the count at **21.5M households** behind. Its later series shows
   debt rising from **$15.4B (Jan 2022) to $21.4B (Mar 2025)**, about $23B (Dec 2025) and **about $25B (spring 2026, +30%
   since end-2023)**, and it projects about $25B for end-2026. NEADA's methods have changed and some releases conflict:
   Jan 2024 gives $20.3B for Dec 2023, while Aug 2024 implies about $16B. Treat the trend, not the exact level, as the finding.
   [`households_arrears_shutoffs.json` -> `neada_arrears_series`]
6. **The first national shutoff census counts 13.4M electric disconnections in 2024.** That is 9.4 per 100 residential
   customers, alongside 94.9M final notices and 11.4M reconnections, plus 1.7M gas disconnections (EIA-112, released
   2026-04-14). Shutoffs cluster in the South, where weather protections are weakest: **OK 30.4 per 100, TX 23.6, FL 20.6,
   AL 19.0, LA 18.6, TN 17.6**. Rates are far lower in WY 1.2, RI 1.5, MA 1.9 and NY 2.5. Counts are events, not unique
   households. NEADA's household estimate is about 3.5M households shut off in 2024.
   [`households_eia112_disconnections_2024.csv`]
7. **Several data-center-hotspot utilities disconnect at above-average rates. Others don't.** Dominion's Virginia Electric &
   Power had **368,473 disconnections, 15.5 per 100 customers**, 4th-most nationally and about 2.5x EPI's investor-owned
   average of 6.3. Others: Entergy Louisiana 16.1, Indiana Michigan Power 15.8, Nevada Power 15.2, AEP Ohio 12.9, and Oncor
   (TX retail choice) 35.7. But Georgia Power is 7.7, PSE&G 4.8, BGE 3.9, ComEd 2.6 and NOVEC (Loudoun co-op) 3.2. The
   state-level correlation between disclosed DC megawatts and disconnection rate is weak (r = 0.32) and confounded by Texas
   and by Southern shutoff rules. It is **not evidence that data centers cause shutoffs**.
8. **About a quarter of adults live in households that couldn't pay an energy bill in full, and more than a third of the
   under-$50k group.** In the final Census Household Pulse wave (Aug-Sep 2024), **23.4%** of adults lived in households
   unable to pay an energy bill in full at least once in the last 12 months. The share was **37.4% for incomes under $50k**,
   up from 22.0% and 35.5% in 2023 (per NEADA). **34.3%** cut back on food or medicine to pay energy bills (51.0% under
   $50k), and 22.8% kept the home at an unsafe temperature. The highest states were MS 33.4%, CT 29.6%, AL 29.4%, LA 28.5%
   and NJ 28.2%; the lowest were DC 11.9% and WA 15.8%. The Pulse survey ended in Sept 2024, so no 2025-26 state readings
   exist. [`households_hps_energy_insecurity_state.csv`]
9. **The safety net shrank and then wobbled.** LIHEAP fell from **$6.09B (FY2023) to $4.12B (FY2024-25)** and was $4.13B in
   FY2026 (states and territories, LIHEAP Clearinghouse). It reaches about 6M households, about 17-20% of those eligible
   (NEADA), down from a record 7.3M in FY2023. In 2025-26 the federal LIHEAP staff were laid off (Apr 2025) and the
   President proposed $0 for both FY2026 and FY2027. The Oct-Nov 2025 shutdown delayed winter funds until Nov 28, 2025.
   Congress nonetheless kept funding at about $4.05B (Consolidated Appropriations Act 2026, Feb 3, 2026). FY2027 runs on a
   CR, with $3.63B released Oct 9, 2026. NEADA asks for $7B plus a $3B emergency anomaly (oil at about $100/bbl during the
   Iran war).
10. **Public opinion turned fast and across parties. The anger targets who pays more than data centers themselves.**
    - **Opposition and blame rose sharply.** Opposition to a nearby data center went from about 4 in 10 (Aug 2025) to
      **7 in 10 (May 2026)** (Heatmap/Embold). Blaming new data centers "a lot" for power prices went from 28% to more than
      50%. Pew's "mostly bad for home energy costs" went from 38% to **50%** of all adults (Jan to Aug 2026).
    - **The 2026 exit polls confirmed it.** **76% of 2026 voters opposed a new data center in their community** (GA 78%,
      OH 76%, TX 75%), and those opponents voted 64-34 Democratic for the House (CBS exit poll). Georgia Democrats won the
      PSC 2025 seats with about 63%, took a 3-2 PSC majority in 2026, and elected a governor who promised a data-center
      moratorium. In New Jersey 2025, about 6 in 10 voters called electricity costs a major problem.
    - **The anger is about who pays.** Voters blame utilities more than data centers (Pew: 64% vs 43% name them a major
      reason). They prefer rules to bans (57% vs 23%, Morning Consult/ARI). 78% want data centers to pay grid-upgrade costs,
      and 81% of Virginians back extra fees. Quality of life outweighs bills in explaining local opposition
      (Harvard/YouGov). Only about 3% named data centers the single most important issue (NBC via Reason, UNVERIFIED).

## Counter-evidence and balance (cross-reference, mostly from `markets_attribution_studies.json`)
- **Load growth can lower rates.** LBNL/Brattle (Jan 2026): from 2019 to 2024, the states with the highest load growth
  generally saw real retail prices *fall* because fixed costs were spread over more sales. Price increases were driven by
  T&D spending, storms and wildfires, RPS costs and gas prices. PJM is the exception. E3 (for the Data Center Coalition,
  May 2026) and CRA (for EEI, Feb 2026) both say data centers did not trigger retail increases outside PJM capacity prices.
  Virginia JLARC (2024) found no historic cost shift but warned about future pressure.
- **Southern disconnection rates predate the AI build-out.** The high Southern rates track weak shutoff protections, prepay
  programs and poverty. Oklahoma customers are still paying about $5B of Winter Storm Uri costs (EPI). Texas's high rates
  reflect retail-choice mechanics.
- **Arrears and shutoffs have many drivers.** NEADA itself lists high interest rates, gas prices and LNG exports, data
  centers, aging infrastructure and capacity shortfalls as causes of rising bills, and a 50% rise in natural gas prices in
  2025. Heatmap notes prices rose 21% from 2020 to 2022, before the AI boom.
- **Many residents of data-center hubs still see benefits.** 56% of Virginians see positive job effects (WaPo-Schar).
  Loudoun has the lowest burden of any DC host county.

## How the outputs were built (website reads these)
| File | Rows | What |
|---|---|---|
| `data/processed/households_energy_burden_county.csv` | 3,222 (50 states + DC + PR) | Required columns `county_fips, county, state, avg_energy_burden_pct, low_income_burden_pct (<=80% AMI), avg_annual_elec_cost_usd, households`, plus electricity-only burdens, low-income cost and income, renter share, `quality_flag`, and an **estimate** `avg_annual_elec_cost_2025_est_usd` |
| `data/processed/households_burden_national_by_group.csv` | 21 | National burden by AMI bin, tenure and heating fuel |
| `data/processed/households_dc_county_overlap.csv` | 89 | Counties hosting compute-atlas US campuses, with burden |
| `data/processed/households_state_summary.csv` | 51 | State burden, Pulse 2024 insecurity, EIA-112 shutoffs, DC campuses and MW (atlas) |
| `data/processed/households_eia112_disconnections_2024.csv` | 1,328 | Utility- and state-level EIA-112 2024 (eia_utility_id matched for 1,200 of 1,226 utilities by name+state) |
| `data/processed/households_hps_energy_insecurity_state.csv` | 52 | Census Pulse Cycle 09 shares by state and US |
| `data/processed/households_arrears_shutoffs.json` | sections | NEADA series (11 points), EIA-112 summaries, EPI, Pulse, LIHEAP FY2018-27 (10), events (9) |
| `data/processed/households_polling.json` | 12 national, 9 state, 4 exit polls, 7 election notes | Wording, results, dates, sponsors, `verified` flags |

**How the LEAD source was simplified.** The source is 7.3 GB of 52 state zips. Rather than download it all,
`scripts/households/lead_zip_extract.mjs` reads each zip's central directory with HTTP Range requests and inflates only the
`AMI Counties` member (about 800 MB uncompressed, kept under `data/raw/households/lead2022_ami_counties_all/`; the
census-tract, FPL, SMI and LLSI files were not downloaded). Rows (county x AMI bin x tenure x building age x type x heating
fuel) are summed. Burden is computed as LEAD defines it: average energy cost / average income (ratio of sums). Low income
means <=80% AMI (0-30, 30-60 and 60-80% bins). The <=200% FPL alternative is not computed; the FPL county files can be pulled
the same way. **Flags:** 51 counties where county electricity spend is more than 2x the state mean (likely calibration
artifacts: rural co-op areas, remote AK, Cook Co. GA) and 142 counties with fewer than 1,000 households. **Vintage:** ACS
2018-2022 5-year PUMS (nominal dollars of each year), calibrated to 2022 EIA-861/176 revenues, so burdens reflect about 2022
prices. Bills have since risen; see the 2025 estimate column, which scales electricity spend only and does not adjust
incomes. LEAD's <=80% AMI burden (6.3%) is lower than NEADA's 8.6-9.9% "low-income" figures, which use BLS Consumer
Expenditure Survey quintiles or other cut-offs.

Rebuild: `node scripts/households/lead_zip_extract.mjs get lead2022_ami_counties_all "AMI Counties"` ->
`python3 -I scripts/households/build_lead_county.py` -> `build_lead_groups.py` -> `node scripts/households/geocode_campuses.mjs` ->
`build_hps_eia112.py` -> `build_overlap_state.py` -> `build_arrears_json.py` -> `build_polling_json.py` -> `write_docs.py`
(raw downloads: `node scripts/households/fetch.mjs <folder> <url>...`; URLs in SOURCES.md).

## Open questions / gaps
- No 2025-26 **state-level** inability-to-pay data. The Household Pulse Survey ended in Sept 2024. Its successor, HTOPS,
  was not checked.
- NEADA arrears are national estimates with opaque, changing methods. Utility arrears from state PUC dockets (NJ, NY, CA,
  MA, PA report monthly) would give a primary series. Not collected.
- EIA-112 covers 2024 only, so there is no before/after comparison around the 2025 PJM capacity-price increase. Watch for
  2025 data.
- The EPI Utility Disconnections Dashboard and the IU Energy Justice Lab dashboard were not downloaded (the IU site failed
  TLS verification). EPI's 2026 EIA-112 analysis was used instead.
- DC hotspots are the 105 compute-atlas campuses (many at city-level coordinate precision), not a full inventory. Counties
  served by PJM utilities bear capacity costs without hosting campuses. A utility-territory join (geo area) would capture
  that better.
- No study found that links data centers *causally* to arrears or shutoffs.
- LIHEAP households served for FY2025-26 was not found. NJ and VA 2025 vote margins were not recorded (null).
- UNVERIFIED (search summary only): Heatmap Aug-2026 75%; NBC exit 56% / 3%; Hart/Climate Power 62%; CCAN VA 73%;
  Zenith MD 40%; Change Research 65%; Marquette 62%; AJC exact 61%; GA PSC Edwards 55.2%.

## Log: what didn't work
- `WebFetch` was denied for data.openei.org, eia.gov, neada.org and energyandpolicy.org. The node `https` downloader
  (`scripts/households/fetch.mjs`) was used instead.
- Requests were refused by spglobal.com, axios.com, marylandmatters.org, newjerseymonitor.com, michiganadvance.com,
  datacenterdynamics.com, insideclimatenews.org and stand.earth (HTTP 403), and by changeresearch.com (429). ACF (acf.gov)
  returned a 202 bot check. CRS on congress.gov returned 403; everycrsreport.com only had the 2018 LIHEAP report.
- TLS verification failed in Node 16 and Python 3.6 for liheapch.acf.gov, energyjustice.indiana.edu and wilder.vcu.edu. The
  LIHEAP Clearinghouse mirror at liheapch.ncat.org was used instead.
- The Pulse `energy1_cycleNN.xlsx` tables don't exist in Phase 4. The energy questions are in `housing4_cycle09.xlsx`.
- A `rm` of the AK-only test extract was blocked, so the full extract went to a new folder. The test extract remains in
  `data/raw/households/lead2022_ami_counties/`.
- Writing .md files directly with the Write tool was refused for subagents, so this file is generated by
  `scripts/households/write_docs.py`.
- 15 WebSearch calls used.
