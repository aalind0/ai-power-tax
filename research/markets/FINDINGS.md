# Markets: findings (wholesale/capacity markets, transmission, load growth, data-center attribution)

Research date 2026-11-23. Every number has a link. UNVERIFIED = not read in a primary document this session.
Sources and licences: SOURCES.md.

## Outputs
| File | Rows | Content |
|---|---|---|
| data/processed/markets_capacity_prices.csv | 447 | PJM BRA by LDA, 2015/16 to 2028/29 (215 rows: RTO, MAAC, APS, PPL, EMAAC, SWMAAC, DPL-SOUTH, PSEG, PSEG-NORTH, PEPCO, ATSI, COMED, BGE, DEOK, DOM, PECO; plus ATSI-CLEVELAND, DAY, JCPL for 2028/29). PJM zone prices averaged across all auctions (184 rows, 23 zones; 2018/19 to 2021/22 and 2024/25 to 2027/28). MISO PRA (27). ISO-NE FCA (16). NYISO (5, secondary). Columns: market, delivery_year, zone_or_lda, price_usd_mw_day, total_cost_usd, cleared_mw, notes, source_url, verified. |
| data/processed/markets_attribution_studies.json | 26 | 14 say raises-bills, 5 mixed, 7 lowers-or-neutral. 19 verified. Brief's fields plus id and notes (funder, caveats). |
| data/processed/markets_load_growth.json | 5 + 10 + 11 | LBNL 2024 and 2025 estimates; PJM forecast vintages and data-center MW per auction; ERCOT, MISO, SPP; utility pipelines (Dominion, Georgia Power, AEP, Entergy, Oncor, Duke, NIPSCO, Xcel, APS, PG&E, ComEd). |
| data/processed/markets_utility_dc_load.csv | 105 | Atlas US campuses mapped to utility and RTO. 84 from the atlas energy field; 21 inferred from location (UNVERIFIED). Extra columns: is_market_cluster, pjm_zone_or_note, mapping_basis, lat, lng, atlas_energy_text. |
| data/processed/markets_pjm_wholesale_cost_components.csv | 27 | PJM wholesale $/MWh split into energy, capacity, transmission and other; 2001 to 2025 plus Jan to Sep 2025 and 2026 (IMM). Use it for the "what a bill is made of" panel. |

PJM zone codes and their utilities: BGE=Baltimore Gas & Electric; PEPCO=Pepco; DOM=Dominion; COMED=ComEd; PSEG=PSE&G; PECO (inside EMAAC); PPL; JCPL; AECO=Atlantic City Electric; DPL=Delmarva; METED/PENELEC=FirstEnergy PA; ATSI=FirstEnergy Ohio; AEP; APS=Allegheny; DEOK=Duke Ohio/Kentucky; DAY=AES Ohio; DLCO=Duquesne; RECO=Rockland.

## Mechanism, in plain words
**Capacity.** PJM buys "capacity" (promises to be available at peak) one to three years ahead.
- Forecast: data-center hookups raise PJM's peak forecast. Data centers were 7.9 GW of the 2025/26 auction forecast and 21.5 GW of the 2028/29 one ([IMM 2028/29 Part A, Table 6](https://www.monitoringanalytics.com/reports/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf)).
- Supply: barely moved. Only 525 MW of new or uprated generation cleared in 2028/29 ([PJM 2028/29 report](https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2028-2029/2028-2029-bra-results-report.pdf)).
- Price: one clearing price is paid on all ~135–138 GW, not just the new load. A few GW of new demand therefore costs everyone billions. Economists call this a pecuniary externality: market-wide, not a subsidy to one site.
- Bills: in restructured states (MD, PA, NJ, OH, IL, DE, DC), default service is bought through full-requirements auctions. The zonal capacity price passes through each June 1. Vertically integrated utilities can self-supply and are partly shielded ([LBNL/Brattle, slide 17](https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf)).
- Size: capacity was $19.42/MWh (17.4% of $111.61) in Jan to Sep 2026, against $3.61 in 2024 ([IMM SOM 2026 Q3, Tables 1-9 and 1-10](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2026/2026q3-som-pjm-sec1.pdf)). Wholesale is 55–70% of residential bills ([MD OPC/CAPS](https://opc.maryland.gov/Portals/0/Files/Publications/Others/PJM%20Annual%20Meeting%20-%20David%20Lapp%20presentation%20(5.13.2026).pdf)).
- Back-of-envelope (my arithmetic): +$15.8/MWh is about +1.6¢/kWh, or about +$13/month at 850 kWh. Residential customers often pay more per kWh than that.

**Transmission.** There are two channels.
- Local "supplemental" projects, including single-customer hookups: recovered through FERC formula rates paid by all load in the zone, with no record of who caused the cost.
- Regional RTEP baseline projects: costs for 500 kV-class facilities are allocated 50% by load-ratio share (a "postage stamp" across PJM) and 50% by DFAX; smaller ones go 100% to DFAX ([MD OPC complaint, p.15](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
- Result: lines driven by Virginia data centers are partly billed to MD, NJ and IL customers. State rate cases then split each utility's transmission cost across customer classes using old factors.

## Key insights
1. **PJM went from a record low to the price cap.**
   - RTO price, $/MW-day: $28.92 (2024/25), $269.92 (2025/26), $329.17 (2026/27), $333.44 (2027/28), $325.00 (2028/29, cap).
   - BRA cost: $2.2B, $14.7B, $16.1B, $16.4B, $16.4B.
   - Uncapped, 2028/29 would have been $554.72 and $29.7B.
   - The last two auctions were 6.5–6.8 GW (UCAP) short, with a 14.4% reserve margin against a 20% target ([PJM 2028/29, Table 2](https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2028-2029/2028-2029-bra-results-report.pdf)).
   - Charges to load: $2.50B in 2024/25 and $14.77B in 2025/26 ([IMM SOM 2025, Table 5-26](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec5.pdf)).
2. **The IMM attributes $29.37B across four auctions to data-center load.**
   - Per auction: $9.33B (2025/26), $7.27B (2026/27), $6.50B (2027/28), $6.27B (2028/29, +61.8% of revenue).
   - "There would have been no shortfall but for the forecast data center load."
   - Data centers added $9.95/MWh (+9.8%) to PJM wholesale cost in Jan to Sep 2026 ([IMM Part A](https://www.monitoringanalytics.com/reports/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf); [IMM SOM Q3](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2026/2026q3-som-pjm-sec1.pdf)).
   - Correction to the brief: 2027/28 is $6.50B (or $6.24B counting forecast growth only); $6.27B is 2028/29.
3. **Other analysts split the increase differently. Show both.**
   - E3 (funded by the Data Center Coalition): about 50% load growth, about 50% market design and retirements ([E3 2026](https://www.ethree.com/wp-content/uploads/2026/05/Understanding-the-Drivers-of-Rising-Electricity-Rates-and-the-Role-of-Data-Centers_E3-2026.pdf)).
   - The IMM's 2025/26 scenarios also found other large, non-additive effects: CC/CT summer ratings (+23–118% of revenue), the price cap (+68%), ELCC (+49%), and leaving RMR units out of supply ([LBNL slide 17](https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf)).
   - The Shapiro cap and floor cut 2028/29 revenue by $13.3B (44.8%). The floor also hid about $2.8B of the data-center effect.
4. **Part of the jump is a rebound from an abnormal low.**
   - RTO prices were $59–$165 in 2015/16 to 2021/22, with RPM revenue of $7–11B a year ([IMM Table 5-24](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec5.pdf)).
   - Capacity cost per MWh: $12.50 (2015), $13.95 (2018), $3.61 (2024), $19.42 (2026). That is about 1.5x the 2015–18 level, not 5–9x.
   - LBNL/Brattle note earlier prices may have been "too low".
5. **Location mattered in 2025/26, not since.**
   - 2025/26: BGE $466.35 and Dominion $444.26, against $269.92 elsewhere.
   - From 2026/27, every LDA clears at the cap ([IMM Table 5-21](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec5.pdf)).
   - Dominion was under FRR (self-supply) before 2025/26 ([PJM 2025/26](https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2025-2026/2025-2026-base-residual-auction-report.pdf)).
6. **Data centers are almost all of the forecast growth, and the forecast is soft.**
   - 2026 forecast: 222,106 MW summer peak in 2036, +65.7 GW or 3.6% a year ([PJM 2026 forecast](https://www.pjm.com/-/media/DotCom/library/reports-notices/load-forecast/2026-load-report.pdf)).
   - Actual peaks: 2014–24 averaged 144.5 GW; the record was 158,005 MW on 2026-07-02.
   - Data centers were 93–95% of 2025 large-load adjustments; organic load is flat ([IMM Tables 3–6](https://www.monitoringanalytics.com/reports/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf)).
   - 80% of adjustments (38.9 GW) sit in Dominion, AEP, ComEd and PPL ([OPC](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
   - The 2026 forecast cut 2028 by 4.4 GW once firm commitments were required.
7. **Transmission is the slower second channel.**
   - UCS: $4.36B of 2024 single-data-center hookups in 7 PJM states (VA $1.99B, OH $1.30B, PA $492M, IL $239M, WV $216M, MD $108M, NJ $15M); over 95% socialized ([UCS Table 1](https://www.ucs.org/sites/default/files/2025-09/PJM%20Data%20Center%20Issue%20Brief%20-%20Sep%202025.pdf)).
   - Three RTEP windows total more than $22B of baseline projects, mostly data-center driven.
   - Maryland is assigned $2.0B capital and $1.62B over 10 years; residential $823M ($345 per customer); BGE + Pepco $1.2B ([OPC](https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf)).
   - PJM transmission cost per MWh rose from $8.81 (2015) to $18.53 (2025), with many drivers.
8. **Forward estimates are large and depend on assumptions.**
   - NRDC: $163B of PJM capacity cost 2028–32 ([NRDC](https://www.nrdc.org/press-releases/pjm-board-decide-higher-bills-67-million-americans-due-data-centers)); $70/month household figure UNVERIFIED.
   - The IMM expects a similar impact from the 2029/30 auction (Dec 2026).
   - CMU/NC State: +8% US generation cost by 2030, >25% in central/northern Virginia ([CMU](https://www.cmu.edu/work-that-matters/energy-innovation/data-center-growth-could-increase-electricity-bills)).
   - JLARC: no historic cost shift, but Dominion residential G&T costs go from $114.68 to $139.37/month (real) by 2050 under unconstrained growth ([JLARC](https://jlarc.virginia.gov/pdfs/presentations/JLARC%20Virginia%20Data%20Center%20Study_FINAL_12-09-2024.pdf)).
9. **Counter-evidence: load growth usually lowered rates.**
   - LBNL/Brattle: the highest-growth states saw real price declines of more than 1¢/kWh in 2019–24; US real prices were flat (nominal +23%) ([LBNL/Brattle](https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf)).
   - EPRI: −0.4% per +10% data-center load (UNVERIFIED).
   - CRA/EEI: no data-center-driven increases except PJM ([CRA](https://media.crai.com/wp-content/uploads/2026/02/11105740/Retail-rate-trends-in-the-US-EEI-CRA.pdf)).
   - E3/Amazon: $3.4M net surplus per site ([E3](https://www.ethree.com/wp-content/uploads/2025/12/RatepayerStudy.pdf)).
   - Georgia: rate freeze through 2028 plus about a $50/yr cut ([EEI](https://www.eei.org/News/news/All/2026-white-house-ratepayer-protection-pledge)).
10. **Both can be true.**
   - Spare capacity plus a cost-covering tariff spreads fixed costs and can lower rates (ND, NE, NM, Georgia).
   - Constrained supply in a uniform-price market (PJM) puts the scarcity price on all load, and regional transmission is socialized.
   - Industry studies measure facility-level cost of service; the IMM, UCS and OPC measure market-wide effects.
   - Columbia/CGEP (funded by Google.org) and the Senate staff report say pledges miss the system-wide costs ([CGEP](https://www.energypolicy.columbia.edu/publications/the-effects-of-load-growth-on-electricity-prices-in-the-united-states-a-literature-review/); [Senate](https://www.warren.senate.gov/wp-content/uploads/2026/10/471703-ai-data-center-boom-cost-Digital-8.5x11.pdf)).
11. **Outside PJM.**
   - MISO summer: $666.50 (2025/26), then $384–424 (2026/27) as more supply was offered; annualized $116–126.
   - ISO-NE: $2.59–3.58/kW-month (about $85–118/MW-day).
   - NYISO: NYC summer 2026 about $32.5/kW-month, a record (secondary).
   - ERCOT has no capacity market; data-center effects show up in energy and transmission.
12. **Pipelines far exceed what will be built.**
   - ERCOT: 474 GW of requests (~90% data centers), but only 205 GW eligible for Batch Zero ([ERCOT](https://www.ercot.com/files/docs/2026/07/29/ERCOT-Senate-July-29-Panel-1-Assessing-The-Grid.pdf)).
   - Dominion: 54.9 GW pipeline, 12.2 GW under service agreements. AEP: 84 GW "contracted" through 2031. Southern: 21 of 75 GW signed. PG&E: 12.87 GW, ~1.8 GW expected by 2030. APS: 19 GW queue against an 8.7 GW peak. Utility figures UNVERIFIED.
   - LBNL 2025 Update: 192 TWh (4.7%) in 2024, 649 TWh (11.8%; range 9.5–15.3%) in 2030, about 1/3 of US load growth ([LBNL](https://www.energy.gov/documents/united-states-data-center-energy-usage-report-2025-update)).
   - LBNL 2024 report: 176 TWh (4.4%) in 2023; 6.7–12% by 2028.
13. **Policy is shifting fast.**
   - 38 large-load tariffs 2018–26, 30 of them in 2025–26 (E3).
   - White House Ratepayer Protection Pledge (March, expanded July 2026).
   - IMM complaint EL26-30: data centers should bring their own generation.
   - PJM Reliability Backstop Procurement.
   - Maryland OPC FERC complaint.
   - Senate report: pledges cover only site-specific infrastructure; companies opposed "but-for" cost allocation.
14. **Comparing Jan to Sep 2026 with Jan to Sep 2025:**
   - PJM wholesale cost rose $32.42/MWh: energy +$22.42 (69%), capacity +$8.70 (27%), transmission +$0.84.
   - Of the $24.47 rise in real-time load-weighted average LMP, $8.81 came from transmission-constraint penalty factors and $5.73 from fuel.
   - No study quantifies data centers' share of energy prices ([IMM Q3](https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2026/2026q3-som-pjm-sec1.pdf)).

## Caveats
- Auction revenue is not the same as cost to load (FRR, self-supply, hedges, CTR credits). Example: 2026/27 clearing price is $329.17 but the net load price is $329.43.
- PJM gives 2027/28 cleared UCAP as 134,478.1 MW in its table and 134,584.6 MW in its text; the CSV uses the table.
- IMM counterfactuals hold supply offers fixed and are not additive.
- MISO 2015/16–2022/23 and ISO-NE FCA 6–9 come from memory (verified=false). NYISO is secondary.
- 21 campus mappings are inferred. Some atlas MW are mega-project targets (PORTS-Pike 10 GW, Fermi 11 GW). Non-cluster, non-cancelled atlas MW by grid region: PJM 13.6 GW, MISO 14.0 GW, ERCOT 11.2 GW, SPP 11.0 GW.

## Open questions and gaps
- How much of each utility's default-service rate is capacity, and the June 2025 and June 2026 bill changes (PUC filings; bills area).
- No attribution study for ERCOT or the Southeast. No data-center share of energy prices.
- Still missing: NYISO official prices; MISO 2016/17 and 2021/22; PJM zone averages for 2022/23 and 2023/24; Wood Mackenzie numbers.
- The JLARC "~$40/month by 2040" press figure was not found in the deck read here.
- NC State 2026 ERL paper (6–29%) blocked by 403.

## Log: what didn't work
- WebFetch was refused for monitoringanalytics.com, pjm.com, cmu.edu and ucs.org. A Node https GET with a browser User-Agent worked, including on PJM (no HTTP 500).
- No pdftotext, PyPDF2 or poppler. Used macOS PDFKit via JXA (scripts/markets/pdf2txt.js).
- 403: eta-publications.lbl.gov, emp.lbl.gov, news.ncsu.edu, axios.com. EPRI URL returned "not found". Sierra Club returned 302. Modo Energy and Bloomberg are paywalled.
- PJM BRA reports for 2015/16–2018/19 are not at the guessed URLs. The folders data/raw/markets/pjm_bra_2015_16 to pjm_bra_2018_19 contain a PJM "not found" HTML saved as report.pdf (rm was not permitted). Ignore them; those years use IMM SOM 2018 Table 5-23.
- The 2019/20 CP row was lost at a page break in the IMM 2018 text; it was taken from PJM's 2019/20 report.
