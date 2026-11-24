# Policy area: sources

Access date for all items: 2026-11-23 unless noted. "Raw" = local copy under `data/raw/policy/`. Advocacy and industry sources are labelled.
Licence/terms: government documents are public records; news, think-tank and trade-association items are copyrighted and used for facts and short citations only.

## Datasets and reports downloaded

| Name | Publisher (type) | URL | Date | Granularity | Raw copy / notes |
|---|---|---|---|---|---|
| Rate Review 2026 Q3 workbook ("All Rate Cases" sheet) | Edison Electric Institute, data from S&P Global RRA (industry) | https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/Quarterly-Financial-Updates/2026_Q3_Rate_Review_XLSX.xlsx | as of 2026-09-30 | case-level: state, company, docket, case type, request/decision dates, $M, ROE | `eei_rate_review_2026q3/` (912 KB). Backbone of `policy_rate_cases.json`. EEI terms of use apply. |
| Large Load Projects and Tariffs | EEI (industry) | https://www.eei.org/-/media/Project/EEI/Documents/Issues%20and%20Policy/List%20of%20Large%20Customer%20Projects%20and%20Tariffs | updated 2026-10-09 | state/utility tariff list + example projects | `eei_large_load_tariff_list/` (PDF). Main source for tariff status by state; industry framing. |
| Electricity Rate Designs for Large Loads: 2026 Update | Lawrence Berkeley National Lab & Brattle (government/consultant) | https://eta-publications.lbl.gov/sites/default/files/2026-08/rate_designs_large_loads_2026.08.10.pdf | Aug 2026 | tariff design elements across ~55 tariffs | `lbnl_large_load_rate_designs_2026/`. Median threshold 25 MW; median contract 5 -> 12 years. |
| Utility Bills Are Rising: Q1 2025, Q2 2025, Q3 2025, 2025 Review (Q4), Q1 2026, Q2 2026, Q3 2026 + Q4 2025 one-pager | PowerLines (consumer-advocacy nonprofit) | https://powerlines.org/reports/ (PDF links in `_fetch_log.json` of each folder) | Apr 2025 - Oct 2026 | national/regional totals; per-request appendices | `powerlines_q*_20*/` (1-33 MB each). 2026 appendices parsed to `policy_rate_requests_powerlines.csv`. |
| 2026 State Bills to Restrict Data Center Subsidies (map) | Center on Budget and Policy Priorities (progressive think tank) | https://www.cbpp.org/blog/states-began-scaling-back-expensive-subsidies-for-data-centers-in-this-years-legislative | 2026-08-07 | state: passed / failed / active | `cbpp_2026_dc_subsidy_map/` (PNG, read visually). |
| PUC / advocate link check | this project | `scripts/policy/check_urls.mjs` | 2026-11-23 | URL status codes | `url_check/url_check.json` |

## Web pages and documents read (not downloaded)

National / multi-state
- Good Jobs First, "Cloudy with a Loss of Spending Control" (Apr 2025; advocacy) - state cost table (TX $1.0156B FY25, VA $732.8M FY24 state-only, IL $370.6M 2023, GA $296M FY25, IA $151.1M 2020, NV $140.0M FY24, OH $127.4M, MN $114.2M, WA $112.1M, TN $103.6M) - https://goodjobsfirst.org/cloudy-with-a-loss-of-spending-control-how-data-centers-are-endangering-state-budgets/
- S&P Global, "Where states stand on data center sales tax exemptions ahead of US midterms" (2026-09-11) - https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/091126-where-states-stand-on-data-center-sales-tax-exemptions-ahead-of-us-midterms
- PowerLines Q3 2026 press release (2026-10-07) - https://powerlines.org/utilities-request-23-1-billion-in-rate-increases-through-third-quarter-of-2026/
- Utility Dive, "US electric, gas utility rate requests spike to $4.5B in Q3" (2026-10-09) - https://www.utilitydive.com/news/q3-electric-gas-rate-requests-powerlines-analysis/832609/
- E&E News, "Utilities sought a record $31B in rate increases last year" (2026-01-29) - https://www.eenews.net/articles/utilities-sought-a-record-31b-in-rate-increases-last-year/
- NASUCA member directory (consumer advocates by state) - https://www.nasuca.org/members/
- Cited via the markets area (verified there, same session): UCS PJM connection-costs brief (Sept 2025, advocacy) https://www.ucs.org/sites/default/files/2025-09/PJM%20Data%20Center%20Issue%20Brief%20-%20Sep%202025.pdf ;
  Harvard ELI "Extracting Profits from the Public" (Mar 2025, academic) https://eelp.law.harvard.edu/wp-content/uploads/2025/03/Harvard-ELI-Extracting-Profits-from-the-Public.pdf ;
  E3/Amazon "Tailored for Scale" (Dec 2025, industry-funded) https://www.ethree.com/wp-content/uploads/2025/12/RatepayerStudy.pdf ;
  LBNL/Brattle retail price drivers (Jan 2026) https://archive.legmt.gov/content/Committees/Interim/2025-2026/ETIC/January-2026/5.Retail-Price-Trends-Drivers_Jan2026.pdf

State primary and secondary sources
- Ohio: AEP Ohio Data Center Tariff page (terms, PUCO order 7/9/2025) https://www.aepohio.com/company/about/rates/data-center-tariff ; WOSU on DeWine pause and $1.4B underestimate (2026-05-27) https://www.wosu.org/2026-05-27/gov-dewine-freezes-controversial-data-center-tax-break-for-now
- Virginia: SCC final order PUR-2025-00058 (2025-11-25) https://npr.brightspotcdn.com/b6/ac/706130b64d2b8eee6a9832b97e48/20251125-virginiascc-dominionenergyruling.pdf ; Utility Dive on SCC Rider T-1 order (2026-08-12) https://www.utilitydive.com/news/dominion-energy-scc-transmission-costs-data-center/827693/ ; Virginia Mercury via Patch, 2026 session bills (2026-03-17) https://patch.com/virginia/across-va/data-center-bills-dominated-years-general-assembly-heres-what-passed ; Bloomberg Law on HB 30 energy tax (2026-06-22) https://news.bloomberglaw.com/environment-and-energy/virginia-lawmakers-approve-data-center-energy-tax-in-budget-deal ; Cardinal News on base-rate impact https://cardinalnews.org/2025/11/26/regulators-approve-dominion-energy-rate-increase/
- Maryland: PSC PC72 notice https://www.psc.state.md.us/wp-content/uploads/Notice_LargeLoadCust-PC72.pdf ; HB 1532 (Ch. 353, 2026) https://mgaleg.maryland.gov/2026RS/Chapters_noln/CH_353_hb1532e.pdf ; SB 937 (Ch. 625, 2025) https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_625_sb0937e.pdf ; OPC RTEP complaint (2026-05-07) https://opc.maryland.gov/Portals/0/Files/Publications/Others/20260507%20-%20RTEP%20complaint%20-%20FINAL%20932.pdf (search snippets; documents not opened)
- Pennsylvania: PUC final order on model large-load tariff (2026-05-13) https://www.puc.pa.gov/press-release/2026/puc-releases-final-order-establishing-first-of-its-kind-large-load-model-tariff-framework-05132026 (search snippet)
- New Jersey: Governor's office (2026-07-07) https://www.nj.gov/governor/news/2026/20260707a.shtml ; New Jersey Monitor https://newjerseymonitor.com/2026/07/07/sherrill-signs-three-bills-to-lower-nj-electricity-costs/ (search snippets)
- Illinois: CBS Chicago on Pritzker pause https://www.cbsnews.com/chicago/news/gov-jb-pritzker-suspends-data-center-tax-breaks/ (search snippet)
- Indiana: IURC orders 46322/46362 (2026-06-17) https://www.in.gov/iurc/files/ord_46322_061726.pdf ; 46183 (2025-09-24) https://www.in.gov/iurc/files/ord_46183_092425.pdf ; I&M settlement coverage https://www.utilitydive.com/news/indiana-iurc-large-load-interconnection-data-center-aep-amazon-google/740452/ ; IURC hearing lists (Oct 2026) (search snippets)
- Georgia: PSC data-center rule advisory (2025-01-23) https://psc.ga.gov/site/assets/files/8617/media_advisory_data_centers_rule_1-23-2025.pdf ; AJC (2026-02) https://www.ajc.com/business/2026/02/georgia-regulators-wont-revisit-approval-of-new-power-plants-for-data-centers ; PSC storm/fuel stipulation advisory (2026-05-28) https://psc.ga.gov/site/assets/files/9488/media_advisory_5_28_26_fuel_storm_stip_approval.pdf ; Inside Climate News on Helene costs https://insideclimatenews.org/news/26022026/hurricane-helene-recovery-georgia-power-bills/
- Texas: Utility Dive on Abbott audit (2026-08-05) https://www.utilitydive.com/news/texas-hits-pause-data-center-interconnections/827046/ ; White & Case on PUCT rule (search snippet) https://www.whitecase.com/insight-alert/puct-sets-financial-commitments-data-center-interconnection-governor-pauses-permit
- Oregon: OPUC Order 26-154 https://apps.puc.state.or.us/orders/2026ords/26-154.pdf (search snippet)
- New York: Utility Dive on Hochul EO and A11560 (2026-07-28) https://www.utilitydive.com/news/behind-the-new-york-data-center-pause-is-legislation-that-could-impact-exis/826369/
- North Carolina: Axios Raleigh on NCUC Duke order (2026-11-17) https://www.axios.com/local/raleigh/2026/11/17/nc-regulators-approve-duke-energy-rate-increase
- Arizona: ACC "What's next in the APS rate case" (2026-07-10) https://azcc.gov/news/home/2026/07/10/what-s-next-in-the-aps-rate-case ; KOLD on TEP decision https://kold.com/2026/11/18/tep-customers-pay-more-after-acc-approves-rate-increase
- Michigan: MPSC Consumers data-center tariff (2025-11-06) https://www.michigan.gov/mpsc/commission/news-releases/2025/11/06/mpsc-approves-terms-of-service-between-consumers-energy-and-data-centers ; MPSC DTE order (2026-02-19) https://www.michigan.gov/mpsc/commission/news-releases/2026/02/19/commission-approves-additional-242m-for-dte-electric-grid-upgrades ; AG Nessel on U-22046 (2026-08-28) https://www.michigan.gov/ag/news/press-releases/2026/08/28/ag-nessel-seeks-to-slash-dtes-474-million-rate-hike-request-by-71
- Missouri: PSC large-load tariff page https://psc.mo.gov/General/Utility_Tariffs_for_Large_Load_Customers ; Ameren release (2026-06-26) https://ameren.mediaroom.com/2026-06-26-Storm-hardening,-electric-grid-upgrades-and-new-generation-underpin-request-to-update-electric-rates-in-mid-2027
- Wisconsin: PSC release on We Energies VLC (2026-04-24) https://content.govdelivery.com/accounts/WIPSC/bulletins/4147a70 ; Wisconsin Watch on 5-UR-112 (2026-11) https://wisconsinwatch.org/2026/11/wisconsin-we-energies-customers-another-rate-hike-but-smaller-public-service-commission-regulators-utility/
- Oklahoma: PSO order coverage (2026-11) https://gcn.com/?p=23300 (search snippet)
- Washington: PSE 2026 GRC page https://www.pse.com/en/pages/rates/pending-utc-filings/2026-general-rate-case (search snippet)
- Louisiana: Louisiana Illuminator on LPSC Meta approval (2025-08-20) https://lailluminator.com/2025/08/20/entergy-meta/ (search snippet)
- Maine / Nebraska: Brownstein data-center tracker https://www.bhfs.com/data-center-tracker/maine/ (search snippet)
- Minnesota: EY tax alert on HF 9 (2025-06-24) https://taxnews.ey.com/news/2025-1349 ; HF 5125 (2026) https://www.revisor.mn.gov/bills/94/2026/0/HF/5125/

## Verification levels
- Opened and read in a browser this session: AEP Ohio tariff page; NASUCA members; GJF report; CBPP blog + map; S&P article; Utility Dive (Q3 PowerLines, Dominion Rider T-1, Texas pause, NY pause);
  PowerLines reports page and Q3 press release; E&E News; Patch/Virginia Mercury; Bloomberg Law (lede only); Axios NC; ACC APS page; WOSU; RI PUC site.
- Downloaded and parsed: EEI workbook, EEI large-load list, LBNL brief, PowerLines PDFs, CBPP map.
- Search-snippet only (marked as such above): treat as secondary until the primary document is opened.
