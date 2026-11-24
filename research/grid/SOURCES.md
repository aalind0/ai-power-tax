# Grid (T&D): sources

All accessed 2026-11-23. Raw copies are in `data/raw/grid/<folder>/` (git-ignored). Text extracts are in `data/raw/grid/_text/`, and parquet converted to CSV is in `data/raw/grid/_derived_csv/`.
Labels: **primary** = regulator, grid operator, market monitor or government; **advocacy** = consumer advocate, NGO or industry-funded; **press** = news.

## Datasets used in processed files
| Name | Publisher | URL | Date | Licence / terms | Granularity | Notes |
|---|---|---|---|---|---|---|
| FERC Form 1 plant in service (sched. 204) | FERC via Catalyst Cooperative PUDL (stable) | https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc1__yearly_plant_in_service_sched204.parquet | PUDL build 2026-11-10; data 1994-2025 | PUDL data CC-BY-4.0; FERC data public domain | Respondent x year x FERC account | 5.9 MB. "additions" = T&D capex. Folder `pudl_core_ferc1__yearly_plant_in_service_sched204` |
| FERC Form 1 O&M expenses (sched. 320) | FERC via PUDL | https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc1__yearly_operating_expenses_sched320.parquet | same | same | Respondent x year x expense type | 3.4 MB |
| PUDL utility crosswalks | PUDL | .../stable/core_pudl__assn_ferc1_pudl_utilities.parquet and .../core_pudl__assn_eia_pudl_utilities.parquet | same | CC-BY-4.0 | FERC1 id / EIA id -> PUDL id | 76% of 2015-25 respondents matched to an EIA id |
| PUDL rate base, utility plant summary (downloaded, not used) | PUDL | .../stable/out_ferc1__yearly_rate_base.parquet; core_ferc1__yearly_utility_plant_summary_sched200.parquet | same | CC-BY-4.0 | | For future rate-base-by-function work |
| Annual Energy Outlook Table 8, "Prices by Service Category" | EIA (primary) | https://www.eia.gov/outlooks/aeo/excel/aeotab8.xlsx (AEO2026); https://www.eia.gov/outlooks/archive/aeo{14..25}/excel/aeotab_8.xlsx or aeotab8.xlsx | AEO2014-AEO2026 (none for 2024) | Public domain | US all-sector c/kWh: generation / transmission / distribution | Base-year values are model estimates (NEMS). AEO2026 scenario label is "Counterfactual Baseline" |
| CPI-U annual average | BLS via `data/processed/bills_cpi_monthly.csv` (bills area) | see research/bills | 2005-2026 | Public domain | Annual | 2025 average has 11 months |
| ATRR and NITS rates postings | PJM (primary) | https://www.pjm.com/markets-and-operations/billing-settlements-and-credit; files .../markets-ops/settlements/network-integration-trans-service-{2021..2025}.pdf, -january-2026-xls.xlsx, -june-2026-xls.xlsx, -october-2026-xls.xlsx | 2021 - Oct 2026 | PJM site terms (public posting) | Zone x posting date, $/MW-yr + ATRR | 2021 PDF layout not parsed; ETCC was used for <=2021 |
| PJM NITS rate history 2015-2024 | Electricity Transmission Competition Coalition (advocacy, pro-competitive transmission) | https://electricitytransmissioncompetitioncoalition.org/wp-content/uploads/PJM-Transmission-Rates-History-20215-2024.pdf | ~2024 | Public PDF | Zone x year | Compiled from TO formula-rate filings; matches PJM postings 2022-24; AECO 2017 truncated |
| Network service peak loads 2026 (downloaded, not used) | PJM | .../settlements/network-service-peak-loads-2026.pdf | 2026 | public | Zone MW | For converting rates to $ |
| Transmission enhancement worksheet Oct 2026 (downloaded, not parsed) | PJM | https://www.pjm.com/-/media/DotCom/committees-groups/subcommittees/mss/postings/2026/transmission-enhancement-worksheet-october-2026.xlsx | Oct 2026 | public | Project x zone TEC allocation | 1.2 MB. Next step for project-level zone shares |

## Documents used for projects and findings
| Name | Publisher | URL | Date | Type | Notes |
|---|---|---|---|---|---|
| 2022 RTEP Window 3 Reliability Analysis Report | PJM TEAC | https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2023/20231205/20231205-2022-rtep-window-3-reliability-analysis-report.pdf | 2023-12-05 | primary | $5,142.98M; N. Va DC cluster $1,418.3M; MPRP (proposal 637) $447.5M; West cluster $940.85M |
| 2024 RTEP Window 1 Reliability Analysis Report | PJM TEAC | https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2025/20250107/20250107-2024-rtep-window-1-reliability-analysis-report.pdf | 2025-01-07 | primary | ~$5.9B; Joshua Falls-Yeat $1,109.89M; Amos-Welton Spring-Rocky Point $1,945.05M; Kraken $704.33M |
| 2025 RTEP Window 1 Reliability Analysis Report | PJM TEAC | https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2026/20260106/20260106-2025-rtep-window-1-reliability-analysis-report.pdf | 2026-01-06 | primary | ~$11.8B ($9.4B regional + $2.39B zonal) |
| 2025 W1 reliability analysis update (slides) | PJM TEAC | https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2026/20260106/20260106-item-09---reliability-analysis-update.pdf | 2026-01-06 | primary | 68.7 MB (kept, not mined) |
| PJM Board whitepaper Nov 2025 | PJM | https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2025/20251104/20251104-pjm-board-whitepaper-november-2025.pdf | 2025-11 | primary | downloaded, skimmed only |
| PJM Board approves 2024 RTEP W1 | PJM Inside Lines | https://insidelines.pjm.com/pjm-board-approves-new-transmission-projects-to-support-grid-reliability/ | 2025-02-26 | primary | Read in browser (blocks scripts). ~$6B; Brandon Shores revised to $1,513.96M |
| PJM Board approves 2025 RTEP W1 | PJM Inside Lines | https://insidelines.pjm.com/pjm-board-approves-transmission-improvements-needed-for-grid-reliability/ | 2026-02-13 | primary | Read in browser. ~$11.8B; 134 proposals |
| PJM answer to MD OPC complaint, EL26-63 | PJM | https://www.pjm.com/-/media/DotCom/documents/ferc/filings/2026/20260727-el26-63-000.pdf | 2026-07-27 | primary (party position) | Beneficiary-pays defence; MD imports ~40% |
| Complaint, EL26-63, with Nelson/Eiden affidavit and Synapse report | Maryland Office of People's Counsel | https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf | 2026-05-07 | advocacy (state consumer advocate) | Text reused from the markets area's download (`data/raw/markets/md_opc_rtep_complaint_may2026`), not re-downloaded |
| OPC bulletin: FERC rejects Valley Link rate proposal | MD OPC | https://content.govdelivery.com/accounts/MDOPC/bulletins/3e0a691 | 2025-05-15 | advocacy | $3B, 417 miles; FERC order ER25-1633 |
| OPC bulletin: response to opposition | MD OPC | https://content.govdelivery.com/accounts/MDOPC/bulletins/429daf6 | 2026 | advocacy | |
| 2025 State of the Market, sec. 12 Planning | Monitoring Analytics (PJM IMM) | https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec12.pdf | 2026-03 | primary (market monitor) | Text reused from the markets area. Data Center Alley $1.4B; supplemental project counts |
| Order No. 92606, Case 9773 (MPRP) | Maryland PSC | https://psc.maryland.gov/wp-content/uploads/2026/08/Order_RevProcSched-9773.pdf | 2026-08-27 | primary | Revised schedule; intervenors |
| FERC large-load show cause orders | FERC | https://www.ferc.gov/news-events/news/ferc-launches-aggressive-targeted-action-speed-large-load-integration | 2026-06-18 | primary | Read in browser (blocks scripts) |
| Today in Energy: spending to produce and deliver electricity | EIA | https://www.eia.gov/todayinenergy/detail.php?id=63724 | 2024-11-18 | primary | Cross-check: 2023 distribution $50.9B, transmission $27.7B |
| Earlier EIA T&D spending articles | EIA | ids 47316 (2021, transmission), 48136 (2021, distribution), 55639 (2023), 36675 (2018), 34892 (2018) at https://www.eia.gov/todayinenergy/detail.php?id=... | 2018-2023 | primary | Context and definitions |
| Factors Impacting Retail Electricity Prices | LBNL & Brattle | https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf | 2026-01 | primary (national lab) | Read from the markets area's download |
| Understanding the Drivers of Rising Electricity Rates and the Role of Data Centers | E3 (funded by Data Center Coalition) | https://www.ethree.com/wp-content/uploads/2026/05/Understanding-the-Drivers-of-Rising-Electricity-Rates-and-the-Role-of-Data-Centers_E3-2026.pdf | 2026-05 | industry-funded | Read from the markets area's download |
| Data Centers in Virginia (presentation) | JLARC / E3 | https://jlarc.virginia.gov/pdfs/presentations/JLARC%20Virginia%20Data%20Center%20Study_FINAL_12-09-2024.pdf | 2024-12-09 | primary (state legislative auditor) | Read from the markets area's download |
| UCS: Billions in unreported data center costs (PJM) | Union of Concerned Scientists | https://www.ucs.org/about/news/billions-dollars-unreported-data-center-costs-pjm | 2025-09-15 | advocacy | Read from the markets area's download |
| Why Northern Virginians will help pay for... transmission line | WTOP | https://wtop.com/virginia/2026/07/why-northern-virginians-will-help-pay-for-controversial-transmission-line-project-in-rural-neighborhoods/ | 2026-07 | press | Valley Link spokesman quotes |
| Growing county government opposition to Valley Link | WMRA/WHRO | https://www.whro.org/2026-08-25/the-growing-county-government-opposition-to-valley-link | 2026-08-25 | press | |
| Valley Link revised routes | Cardinal News | https://cardinalnews.org/2026/06/02/valley-link-says-its-new-transmission-line-plan-would-impact-fewer-people-opponents-vow-to-continue-fighting-it/ | 2026-06-02 | press | |
| Spanberger: data centers should pay for Valley Link | WJLA | https://wjla.com/news/local/governor-abigail-spanberger-data-centers-should-pay-for-major-electrical-infrastructure-like-valley-link-electrical-company-cost-august-2026 | 2026-08 | press | Dominion statement on SCC direct-connect ruling |
| Texas regulators approve Permian Basin reliability plan | Utility Dive | https://www.utilitydive.com/news/texas-regulators-approve-permian-basin-reliability-plan/728269/ | 2024-09-27 | press | $13.8B vs $12.95B; 26 GW by 2038 |
| PUCT approves two 765 kV lines | Texas Tribune | https://www.texastribune.org/2026/08/28/transmission-lines-texas-energy/ | 2026-08-28 | press | Oncor CCNs; opposition |

## Tried but not used
- KERA 765 kV protest article (403), Maryland Matters MPRP article (403), Inside Climate News (403).
- EIA electricity price explainer (`data/raw/grid/eia_explained_prices`): the chart data is not in the page.
- `eia.gov/outlooks/aeo/excel/aeotab_8.xlsx`: returns AEO2021. It is kept in `eia_aeo2021_tab8_staleurl`, and the archived AEO2021 copy is used instead.
- Search results seen but not opened: IEEFA West Virginia Valley Link/MARL cost ($440M+, UNVERIFIED), Texas SB 6, MISO Tranche 2.1, SPP 765 kV.
