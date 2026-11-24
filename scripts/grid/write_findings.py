# -*- coding: utf-8 -*-
"""Writes research/grid/FINDINGS.md (report text kept here so it is reproducible alongside the data scripts).
Run: python3 -I scripts/grid/write_findings.py"""
import io

TEXT = u"""# Grid (transmission and distribution): findings

Scope: what utilities spend on wires, what share of the price that is, how PJM zonal transmission rates moved,
and which transmission projects are being built for data-center load. Who pays, explained in plain English.
Capacity auctions and bill-attribution studies are covered by `research/markets/` and are not repeated here.
Every number below was read from the cited document in this session unless it is marked UNVERIFIED.

## Processed outputs

| File | Rows | What it is |
|---|---|---|
| `data/processed/grid_td_spending.csv` | 21 (2005-2025) | National T&D capital additions, O&M and plant in service for all FERC Form 1 respondents (major investor-owned utilities plus FERC-jurisdictional transmission companies), nominal and real 2025 $. Also includes the EIA AEO split of the average price into generation, transmission and distribution (2011-2025, `aeo_*` columns). |
| `data/processed/grid_td_spending_by_utility.csv` | 2,050 (222 respondents, 2015-2025) | The same numbers per FERC respondent, with `eia_utility_id` from the PUDL crosswalk (76% matched; Oncor and PPL Electric are among those unmatched). |
| `data/processed/grid_transmission_rates.csv` | 266 | PJM zonal Network Integration Transmission Service (NITS) rates, $/MW-yr and $/kW-month, 21 zones, 2015-2026, plus the latest posting (1 Oct 2026, `period = latest...`). Also carries the zonal annual revenue requirement (ATRR) where PJM posts it. |
| `data/processed/grid_dc_projects.json` | 20 records (3 PJM window packages, 15 projects, 2 aggregates) | Transmission projects driven by data-center load: cost, purpose, the data-center link and how it is stated, cost allocation, status, local opposition and sources. Use `level` so a package is not added to its own components. |

Column notes:
- `*_capex_busd` = FERC Form 1 schedule 204 "additions" to plant in service for that function. This is capital put into service, not cash spent.
- `transmission_om_own_busd` excludes account 565 (payments to others for transmission). Account 565 is in `transmission_paid_to_others_busd`; it would double count across utilities.
- `*_real2025` uses the BLS CPI-U annual average from `bills_cpi_monthly.csv`. 2025 has 11 months because October 2025 was not published.
- The AEO columns use the latest AEO edition that covers each year. `aeo_basis` marks whether the year was history or that edition's base-year estimate. These are NEMS model splits, not accounting data: distribution swings (2.48 c in 2021, 3.25 c in 2020) are partly modelling artefacts. Use them for the trend, not year-to-year changes.
- NITS `year` value = the rate in effect on 1 July (after the January and June annual updates), the same convention as the ETCC table. For 2015-2021 the source is ETCC. For 2022-2026 it is PJM's own postings, which match ETCC for 2022-2024 within $2 except DOM 2023, PEPCO 2022 and RECO 2022 (noted in `note`).

## Key insights

1. **Utilities now spend most of their capital on wires, and the pace sped up after 2022.**
   - Capital put into service by FERC Form 1 utilities on transmission and distribution (T&D) rose from $18.5B (2005) to $43.1B (2015) to $100.1B (2025): 5.4x in nominal terms and 3.3x after inflation.
   - In 2025, transmission was $35.6B and distribution $64.5B. Both are up about 50% since 2022.
   - T&D was 68% of all electric plant added in 2025, against 58% in 2005. Generation was $30.6B.
   - Transmission plant in service went from $202B (2015) to $446B (2025). Distribution went from $400B to $762B.
   - Cross-check: EIA's FERC-based figures for 2023 are $50.9B distribution capital and $27.7B transmission. Our PUDL figures are $50.9B and $27.1B ([EIA, Nov 2024](https://www.eia.gov/todayinenergy/detail.php?id=63724)).
   - Other side: most distribution growth is replacement, storm and wildfire hardening, and supply-chain inflation, not data centers. EIA attributes 2023 distribution spending to aging equipment and extreme weather ([EIA](https://www.eia.gov/todayinenergy/detail.php?id=63724)). LBNL/Brattle name aging assets (over $10B/yr just for transmission), hardening and supply chains as the T&D drivers ([LBNL/Brattle Jan 2026, slide 11](https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf)). Data centers mostly connect at transmission voltage, so their footprint shows up in the transmission line.

2. **The transmission slice of the average kWh roughly doubled while the total price rose about a third.**
   - EIA's AEO splits the all-sector average price as follows. Transmission went from 0.93 c/kWh (2013) to 1.89 c (2025, AEO2026 estimate), and its share from 9% to 14%.
   - Distribution went from 2.57 c to 4.05 c (about 30% of the price). The total price went from 10.06 c to 13.54 c (+35%).
   - T&D together are about 44% of the 2025 average price ([AEO2026 Table 8](https://www.eia.gov/outlooks/aeo/excel/aeotab8.xlsx); archived editions for earlier years).
   - Caveat: these are model allocations for all sectors. Residential bills carry a larger distribution share.

3. **PJM zonal transmission rates roughly doubled between 2015 and 2026, with wide variation by zone.**
   - The median zone rose 2.2x (2015 to mid-2026), against +40% for CPI.
   - Rises by zone:
     - AEP: $41,438 -> $138,849/MW-yr (3.4x)
     - PPL: 3.3x
     - Dominion: $42,902 -> $85,191 (2.0x)
     - BGE: 2.3x
     - Pepco: 2.3x
     - Met-Ed/Penelec (FirstEnergy PA): 6.4x
     - Dayton: 4.1x
   - EKPC (1.0x), PECO (1.4x) and ComEd (1.5x) barely moved.
   - Total PJM transmission revenue requirement: $10.55B (Jan 2023) -> $12.65B (Jan 2025) -> $14.05B (Jun 2026), +33% in 3.5 years ([PJM ATRR & NITS postings](https://www.pjm.com/markets-and-operations/billing-settlements-and-credit)).
   - Translation: Dominion's 2026 rate is $7.10 per kW of a customer's share of the zone's annual peak, per month.
   - Other side: much of the 2015-2021 rise predates the data-center wave. It came from local "supplemental" and end-of-life projects, which the IMM says jumped from about 20 a year (1998-2007) to 241 a year (2008-2025) ([IMM SOM 2025 sec. 12](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec12.pdf)). The data-center-driven RTEP windows mostly enter service in 2027-2032, so most of their bill effect is still ahead. Maryland's share starts in 2029 and peaks in 2033 ([MD OPC complaint](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).

4. **PJM's own planning reports say its last three big transmission packages are driven mainly by data centers: about $23B.**
   - 2022 RTEP Window 3: $5.14B. PJM wrote that "data center loads within northern Virginia have been increasing at an unprecedented rate". It modelled about 5,700 MW of data-center load in Dominion and 1,500 MW in APS ([PJM TEAC Dec 2023](https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2023/20231205/20231205-2022-rtep-window-3-reliability-analysis-report.pdf)).
   - 2024 Window 1: about $5.9B. The forecast grew by 10 GW (2029) and 15 GW (2032), "attributed primarily to data centers" ([PJM TEAC Jan 2025](https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2025/20250107/20250107-2024-rtep-window-1-reliability-analysis-report.pdf)).
   - 2025 Window 1: about $11.8B. The forecast grew by 10 GW (2030) and 28 GW (2032), "primarily attributed to data centers", with "substantial data center load additions in the AEP, PPL and Dominion zones" ([PJM TEAC Jan 2026](https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2026/20260106/20260106-2025-rtep-window-1-reliability-analysis-report.pdf); approved 12 Feb 2026, [Inside Lines](https://insidelines.pjm.com/pjm-board-approves-transmission-improvements-needed-for-grid-reliability/)).
   - Other side: the same reports also name generator retirements, delayed New Jersey offshore wind and new generation in southern Virginia:
     - 2022 W3: about 11,100 MW of announced deactivations.
     - 2024 W1: over 2 GW of deactivations.
     - 2025 W1: about 3 GW of deactivations.

     PJM publishes no facility-by-facility attribution and says it plans "holistically". Not every big project is data-center driven: the $1.51B Brandon Shores Deactivation Project exists to retire a coal plant ([PJM, Feb 2025](https://insidelines.pjm.com/pjm-board-approves-new-transmission-projects-to-support-grid-reliability/)).

5. **How "who pays" works in PJM, in plain English.**
   - (a) PJM decides a new line is needed for reliability (a "baseline" project).
   - (b) Lines of 500 kV and above: half the cost is split across every PJM zone by its share of PJM's peak load (a "postage stamp", like everyone paying the same stamp regardless of distance). The other half goes to the zones whose power flows actually use the line, a computer power-flow test called DFAX. Smaller baseline lines go 100% by DFAX. PJM reruns DFAX every year.
   - (c) "Supplemental" local projects, including most single-data-center hookups, are not reviewed by the PJM Board. They are paid 100% by the zone where they sit.
   - (d) Each utility recovers its zone's share through a FERC formula rate, turned into a $/MW-yr NITS charge plus transmission enhancement charges (TECs).
   - (e) The state commission then splits that cost among residential, commercial and industrial classes, usually by contribution to peak. It appears on the bill as a transmission charge, often in c/kWh on the supply side.
   - Example: from the three windows, Maryland zones are assigned $2.0B of capital ($1.32B by DFAX and $0.68B by load-ratio share). That becomes $1.62B of revenue requirement over 10 years, about $345 per residential customer ([MD OPC complaint, Tables 1-2](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
   - Rule of thumb from Synapse: customers pay 3-4x a project's capital cost over its 30-40-year life, once return, O&M and taxes are included.

6. **Single-data-center hookups are mostly socialized within the host utility.**
   - The IMM says the $1.4B of 2022 W3 "Data Center Alley" baseline upgrades "are assigned to all retail customers and not solely to the customers requesting interconnection". Supplemental hookups go 100% to the host zone ([IMM SOM 2025 sec. 12](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec12.pdf)).
   - UCS (advocacy) counted 130 data-center connection projects approved in 2024 in 7 PJM states, worth $4.3B. Over 95% passed all their costs to customers ([UCS, Sep 2025](https://www.ucs.org/about/news/billions-dollars-unreported-data-center-costs-pjm)).
   - Dominion's IRP lists 88 transmission projects driven mainly by data-center connections ($2.44B), or $5.77B including multi-driver projects. This is cited via MD OPC; the IRP was not opened this session.
   - Other side, things are changing:
     - Virginia's SCC ruled in 2026 that "direct connect" transmission for large loads is charged to those customers ([WJLA, Aug 2026](https://wjla.com/news/local/governor-abigail-spanberger-data-centers-should-pay-for-major-electrical-infrastructure-like-valley-link-electrical-company-cost-august-2026)).
     - FERC accepted ComEd and PECO "transmission security agreements" that require data centers to make minimum payments and exit fees ([MD OPC complaint sec. II.B](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
     - E3 (funded by the Data Center Coalition) argues dedicated facilities can and should be assigned directly, while shared lines bring broad benefits that are hard to assign ([E3, May 2026](https://www.ethree.com/wp-content/uploads/2026/05/Understanding-the-Drivers-of-Rising-Electricity-Rates-and-the-Role-of-Data-Centers_E3-2026.pdf)).
     - Gap the critics stress: the SCC ruling does not cover backbone lines such as Valley Link (Dominion's own statement). TSAs cap minimum payments at 80% of committed load and last 8-10 years, against 40-year assets (FERC Commissioner Chang, quoted by MD OPC).

7. **The core dispute: "built for data centers but billed to everyone" against "the grid is shared and everyone benefits".**
   - Against the current rules:
     - Maryland's People's Counsel filed a complaint at FERC (EL26-63, 7 May 2026) asking that data-center-driven regional costs go to the host zones, or straight to the data centers, as with generators under Order 2003.
     - The IMM says PJM's benefit/cost tests are biased because they rely on unverified data-center forecasts.
   - For the current rules:
     - PJM's answer (27 Jul 2026) says the hybrid method implements FERC's "beneficiary pays" rule. Because DFAX is updated yearly, data centers' flows get reflected as they connect.
     - PJM also argues that Maryland imports about 40% of its energy and relies on the same backbone, and that states already have authority to load more cost onto large retail customers. It adds that the cost-allocation rules belong to the transmission owners' filing rights ([PJM answer](https://www.pjm.com/-/media/DotCom/documents/ferc/filings/2026/20260727-el26-63-000.pdf)).
     - Dominion says Valley Link "provide[s] a reliability benefit to all customers".
   - FERC has not ruled on the complaint. On 18 Jun 2026 it ordered all six RTOs to justify or reform their large-load rules, including "preventing cost shifting and requiring transparency into transmission costs". PJM's response was due 16 Nov 2026 ([FERC](https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration)).
   - JLARC/E3 (Virginia, 2024) found no historic cost shift from data centers in Dominion's rates so far ([JLARC](https://jlarc.virginia.gov/pdfs/presentations/JLARC%20Virginia%20Data%20Center%20Study_FINAL_12-09-2024.pdf)).

8. **The new 765 kV/HVDC backbone is large, and opposed where it runs.**
   - Valley Link is a Dominion, FirstEnergy and Transource (AEP and Evergy) joint venture: about $3B and 417 miles across VA, WV and MD ([MD OPC bulletin](https://content.govdelivery.com/accounts/MDOPC/bulletins/3e0a691)). It has two lines:
     - Joshua Falls-Yeat, 765 kV, about 115 miles, $1.11B (PJM). Valley Link's spokesman said "data centers are the lead" ([WTOP, Jul 2026](https://wtop.com/virginia/2026/07/why-northern-virginians-will-help-pay-for-controversial-transmission-line-project-in-rural-neighborhoods/)).
     - Amos-Welton Spring-Rocky Point ("Valley North"), about 260 miles, $1.95B.
   - Opposition: Buckingham, Louisa and Goochland counties each set aside up to $250,000, and a nine-county coalition has formed. Four West Virginia county commissions formally oppose the project ([WHRO](https://www.whro.org/2026-08-25/the-growing-county-government-opposition-to-valley-link)).
   - FERC granted construction-period (CWIP) and abandoned-plant incentives, so customers pay during construction and even if a line is cancelled. It set Valley Link's return on equity (ROE) for hearing. Chair Christie dissented on the incentives.
   - The 2025 package adds:
     - A $4.83B Dominion HVDC portfolio. PJM chose it although it is about $2B more than the next option; Dominion's zone pays about 50%.
     - $2.77B of central-Ohio 765 kV lines (the AEP Columbus load pocket).
     - $1.79B of 765 kV into the eastern PJM region (MAAC, the Mid-Atlantic area).
   - MPRP (PSEG, 500 kV, about 67 miles, $447.5M) will not get a Maryland decision before about July 2027 (hearings 11-21 May 2027). Its original in-service date was June 2027. Opponents include StopMPRP, the Maryland Farm Bureau and two counties ([MD PSC Order 92606](https://psc.maryland.gov/wp-content/uploads/2026/08/Order_RevProcSched-9773.pdf)).

9. **Forecast risk decides who is left holding the bill.**
   - Speculative requests: AEP Ohio's data-center queue fell from over 30 GW (90 sites) to 13 GW (36 sites) after a take-or-pay tariff. ComEd reports 28 GW of requests while Exelon gave PJM 14 GW (MD OPC). PJM itself told FERC there is "growing uncertainty" about forward forecasts.
   - Transmission sized for load that never arrives stays in rates for decades. Under DFAX, a host zone whose load fails to show can shift costs to neighbours: the "hot potato" in MD OPC's words.
   - Other side: if the load does arrive, fixed transmission costs are spread over more MW. APS's NITS rate stayed flat for years, possibly because of load growth (Synapse, speculative), and NITS is a $/MW rate.
   - The markets area covers the LBNL evidence that load growth has historically lowered prices.

10. **Outside PJM: Texas socializes a $13.8B 765 kV build that is mostly for oil and gas, partly for data centers.**
    - ERCOT's Permian plan costs $13.8B for the 765 kV option, against $12.95B for 345 kV, to serve about 26 GW by 2038 ([Utility Dive](https://www.utilitydive.com/news/texas-regulators-approve-permian-basin-reliability-plan/728269/)).
    - The PUCT approved the 765 kV paths in April 2025 and two Oncor 765 kV certificates on 28 Aug 2026. It tabled Howard-Solstice amid landowner protests and an Attorney General brief urging a pause ([Texas Tribune](https://www.texastribune.org/2026/08/28/transmission-lines-texas-energy/)).
    - Oncor was the largest transmission spender among all FERC Form 1 respondents in 2025: $2.54B.
    - Recovery is statewide postage stamp by 4CP (UNVERIFIED this session).

## Maryland residential bill context
Transmission is about 10% of Maryland residential bills (16% of supply), about the same as capacity. Pepco, BGE and Delmarva retail transmission rates rose 5-6x since 2010, about 4x after inflation. Potomac Edison's was flat (Synapse for MD OPC, Attachment B to the complaint). Synapse projects Maryland could take on another $5.4B of transmission capital for projects built 2031-2035. Maryland bore $7.1B over 2010-2030.

## Open questions and caveats
- PJM's Project Status & Cost Allocation tool has per-project zonal allocations, but it is a JavaScript application and was not scraped. Zone shares for individual RTEP projects (other than Maryland totals and Dominion's about 50% of HVDC) are therefore missing.
- Residential transmission charges in $/month are not compiled. Missing: Dominion Rider T1, AEP Ohio's transmission rider (BTCR), BGE and Pepco retail transmission riders.
- Non-PJM transmission rates (MISO and SPP zonal rates, ERCOT transmission cost of service and 4CP) are not compiled. MISO Tranche 2.1 and SPP's 765 kV plans are not in the project list.
- The FERC Form 1 universe includes transmission-only companies and changes slightly each year (206-219 respondents). 2025 is the first year of XBRL-only filings in PUDL, so check for later revisions.
- Facility-level data-center attribution is not published by PJM. `dc_link_type` distinguishes facility-level from package-level statements.
- Unverified: the MidAtlantic Resiliency Link branding; the ERCOT 4CP mechanism; the Dominion IRP figures (cited via OPC).

## Log: what did not work
- No pyarrow or fastparquet on Python 3.6, so PUDL parquet is read with the pure-JS `hyparquet` reader (`scripts/grid/parquet2csv.mjs`, npm in `scripts/grid`). The 3.4 GB `pudl.sqlite.zip` was avoided.
- `insidelines.pjm.com` and `ferc.gov` block scripts and WebFetch, so they were read in our own browser tab. `pjm.com/-/media/...` PDFs and xlsx downloaded fine with node.
- marylandmatters.org, keranews.org and insideclimatenews.org returned 403 to scripts.
- `eia.gov/outlooks/aeo/excel/aeotab_8.xlsx` (underscore) is a stale AEO2021 file. The current file is `aeotab8.xlsx`, and archived editions are under `/outlooks/archive/aeoYY/`.
- The EIA "prices and factors" explainer loads its components chart from a script. The data was not in the page, so AEO Table 8 was used instead.
- The ETCC table truncates AECO 2017 (shown as "$ 50,96"), so it is set to null. PJM's 2021 NITS PDF layout did not parse cleanly, so ETCC was used for 2015-2021.
- A search for Dominion Rider T1 residential $/month found nothing usable.

## Reproduce
```
node scripts/grid/fetch.mjs <PUDL parquet url> data/raw/grid/pudl_<table>/<table>.parquet   # 5 PUDL tables, see SOURCES.md
(cd scripts/grid && npm install && node parquet2csv.mjs <in.parquet> <out.csv>)            # -> data/raw/grid/_derived_csv/
zsh scripts/grid/fetch_aeo_tab8.sh && python3 -I scripts/grid/build_aeo_components.py
python3 -I scripts/grid/build_td_spending.py && python3 -I scripts/grid/build_td_by_utility.py
zsh scripts/grid/fetch_pjm_nits.sh && osascript -l JavaScript scripts/grid/pdf2txt.js <pdf> <txt>   # NITS PDFs -> data/raw/grid/_text/
python3 -I scripts/grid/build_transmission_rates.py
python3 -I scripts/grid/build_dc_projects.py
python3 -I scripts/grid/write_findings.py && python3 -I scripts/grid/write_sources.py
```
"""

io.open('research/grid/FINDINGS.md', 'w', encoding='utf-8').write(TEXT)
print('wrote research/grid/FINDINGS.md', len(TEXT))
