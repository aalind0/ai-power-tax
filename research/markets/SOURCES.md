# Markets: sources
Raw files: data/raw/markets/<name>/ (73 MB total, largest 8.5 MB). Text extracts: data/raw/markets/_text/ (derived; rebuild with scripts/markets/fetch_all.mjs).
Scripts: fetch.mjs (downloader), fetch_all.mjs (manifest), pdf2txt.js (PDFKit/JXA), html2txt.py, build_capacity_prices.py, build_wholesale_components.py, build_utility_dc_load.py.

| Source | Publisher | URL | Date | Terms | Granularity | Notes |
|---|---|---|---|---|---|---|
| BRA reports 2019/20–2028/29 | PJM | pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/... (see fetch_all.mjs) | 2016–2026-07-14 | "For Public Use", pjm.com terms | RTO and LDA, delivery year | Primary for prices, cleared MW, $bn |
| Load Forecast Reports 2025, 2026 | PJM | .../library/reports-notices/load-forecast/2025-load-report.pdf, 2026-load-report.pdf | 2025-01, 2026-01 | Public | RTO and zone, annual, 20-yr | Detailed Excel tables not downloaded |
| State of the Market 2018 Sec 5; 2025 Sec 1/5/12; 2026 Q3 Sec 1 | Monitoring Analytics (IMM) | monitoringanalytics.com/reports/PJM_State_of_the_Market/... | 2019-03, 2026-03, 2026-11 | Copyright IMM, public | LDA, zone, delivery year; $/MWh by component | Tables 5-21/23/24/26, 1-9/1-10 |
| BRA analyses: 2025/26 Part G Rev and H; 2026/27 A and B; 2027/28 A and B; 2028/29 A | Monitoring Analytics | monitoringanalytics.com/reports/Reports/2025/2026/... | 2025-06 to 2026-10-30 | Copyright IMM, public | Auction-level counterfactuals | Data-center attribution series |
| FCA 18 order (ER24-1290) | FERC / ISO-NE | iso-ne.com/static-assets/documents/100012/er24-1290-000.pdf | 2024 | Public | System | $3.580/kW-month |
| FCA 10–17 press releases and filings | ISO-NE | URLs in CSV | 2016–2023 | Public | Capacity zone | Read via search snippets |
| PRA 2023/24–2026/27 | MISO via Utility Dive, APPA, Enel, mgrid | URLs in CSV | 2023–2026 | Press | Zone and season | Secondary |
| ICAP spot | Modo Energy | modoenergy.com/research/nyiso-capacity-prices-record-summer-2026 | 2026 | Paywalled | Locality, monthly | Secondary, unverified |
| Senate panel deck; IGA update | ERCOT | ercot.com/files/docs/2026/07/29/...; .../2026/09/17/... | 2026-07, 2026-09 | Public | System | 474 GW requests; 205 GW Batch Zero |
| US Data Center Energy Usage Report: 2025 Update | LBNL / DOE | energy.gov/documents/united-states-data-center-energy-usage-report-2025-update | 2026 | CC BY 4.0 | National, annual | 192 TWh (2024); 649 TWh (2030) |
| 2024 Data Center Energy Usage Report | LBNL / DOE | eta-publications.lbl.gov/publications/2024-lbnl-data-center-energy-usage-report | 2024-12 | Public | National | Via DOE release (LBL PDF 403) |
| Factors Impacting Retail Electricity Prices | LBNL & Brattle | archive.legmt.gov/.../5.Retail-Price-Trends-Drivers_Jan2026.pdf (mirror); emp.lbl.gov/retail-electricity-price-trends-and-drivers | 2026-01 | Public | State | LBL originals 403 |
| Data center growth could increase bills 8% | CMU / NC State OEO | cmu.edu/work-that-matters/energy-innovation/data-center-growth-could-increase-electricity-bills | 2025-07 | Public | National and regional | ERL paper not accessed |
| Connection Costs brief, release, blog | UCS | ucs.org/media/13772; ucs.org/about/news/billions-dollars-unreported-data-center-costs-pjm | 2025-09-15 | Copyright UCS | State, 2024 | Appendix ucs.org/media/13773 not downloaded |
| Extracting Profits from the Public | Harvard ELI | eelp.law.harvard.edu/wp-content/uploads/2025/03/Harvard-ELI-Extracting-Profits-from-the-Public.pdf | 2025-03 | Copyright Harvard | Qualitative | |
| Ratepayer Study (Amazon); Rate Drivers (DCC); Large Load Tariff whitepaper | E3 | ethree.com/wp-content/uploads/2025/12/RatepayerStudy.pdf; .../2026/05/... (two files) | 2025-12, 2026-05 | Copyright E3 | Facility, PJM | Industry-funded |
| Data Centers in Virginia (presentation) | JLARC / E3 | jlarc.virginia.gov/pdfs/presentations/JLARC%20Virginia%20Data%20Center%20Study_FINAL_12-09-2024.pdf | 2024-12-09 | Public | Dominion | Full report: Rpt598.pdf |
| RTEP cost-allocation complaint; CAPS presentation | Maryland OPC | opc.maryland.gov/Portals/0/Files/Publications/Others/... (two files) | 2026-05-07, 2026-05-13 | Public | MD class and utility | Advocacy |
| PJM Board press release | NRDC | nrdc.org/press-releases/pjm-board-decide-higher-bills-67-million-americans-due-data-centers | 2025-10 | Public | PJM | Advocacy |
| Retail rate trends (for EEI); Ratepayer pledge statement | CRA / EEI | media.crai.com/.../Retail-rate-trends-in-the-US-EEI-CRA.pdf; eei.org/News/news/All/2026-white-house-ratepayer-protection-pledge | 2026-02, 2026-07-23 | Public | State | Industry |
| Load growth literature review | Columbia CGEP | energypolicy.columbia.edu/publications/the-effects-of-load-growth-on-electricity-prices-in-the-united-states-a-literature-review/ | 2026-06-23 | Public | National | Funded by Google.org |
| How the AI Data Center Boom Costs | Sens. Warren, Van Hollen, Blumenthal | warren.senate.gov/wp-content/uploads/2026/10/471703-ai-data-center-boom-cost-Digital-8.5x11.pdf | 2026-10 | Public | National | Partisan staff report |
| atlas.json (US campuses) | compute-atlas (internal) | ../compute-atlas/data/atlas.json | 2026-11 | Internal | Campus | 105 US campuses |
| Secondary / unverified | Bloomberg (2025-09-29), PolitiFact (2026-06-11), EPRI (2026-06), Sierra Club (2025-03), Wood Mackenzie, utility earnings coverage (Zacks, DCD, GuruFocus, Finviz, Nasdaq, Utility Dive, Baxtel, T&D World, KJZZ), MISO and SPP forecast summaries | URLs in the JSON files | 2025–2026 | Various / paywalled | Various | verified=false |
