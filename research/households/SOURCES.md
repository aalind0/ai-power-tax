# Households: sources

Raw copies are under `data/raw/households/<folder>/` (each folder has `_fetch_log.json` with URL, bytes, timestamp).
"Verified" means the figure was read from the document this session.

## Datasets (primary)
| Name | Publisher | URL | Date | Licence / terms | Granularity | Raw folder / notes |
|---|---|---|---|---|---|---|
| Low-Income Energy Affordability Data (LEAD) Tool, 2022 Update | US DOE (Office of State and Community Energy Programs) via OEDI/OpenEI; DOI 10.25984/2504170 | https://data.openei.org/submissions/6219 (files `https://data.openei.org/files/6219/<ST>-2022-LEAD-data.zip`) | 2024-12 release; ACS 2018-2022 PUMS calibrated to 2022 EIA-861/176 | US government open data ("Publicly accessible"); cite DOI | State zips with AMI/FPL/SMI/LLSI x county/tract; used **AMI Counties** only | `lead2022_ami_counties_all/` (~800 MB, 52 CSVs extracted by Range requests from 7.31 GB of zips; keep fetch script, not in git). Docs: `lead2022_docs/` (Data Dictionary 2022.xlsx, Counties list, methodology PDF https://www.energy.gov/sites/default/files/2024-12/lead-methodology_122024.pdf) |
| Form EIA-112 Residential Utility Disconnections Survey, 2024 | US EIA | https://www.eia.gov/analysis/requests/residential/utility/ ; electric file `.../xls/112 electric utility level data 2024.xlsx`; gas file `.../xls/112 natural gas utility level data 2024.xlsx`; report PDF `.../pdf/Residential Utility Disconnections Report - April 2026.pdf` | Report 2026-04-14 | Public domain (US gov) | Utility x state x month (final notices, disconnections, reconnections, customers); no utility id (matched by name) | `eia112_2024/` |
| Household Pulse Survey Phase 4.2 Cycle 09, Housing Table 4 (energy use and spending) | US Census Bureau | https://www2.census.gov/programs-surveys/demo/tables/hhp/2024/cycle09/housing4_cycle09.xlsx | Fielded 2024-08-20 to 2024-09-16 (last HPS cycle) | Public domain; experimental estimates | US, 50 states + DC, 15 metros; adults 18+ | `census_hps_c09/` (also housing/spending tables 1-5 downloaded, not used) |
| LIHEAP Funding for States and Territories (FY2018-FY2027 releases) | LIHEAP Clearinghouse (NCAT, ACF-funded) | https://liheapch.ncat.org/node/62 | Last updated 2026-10-21 | Public | National totals by fiscal year and release date | `liheap_funding3/62.html` |
| US data-center campuses | compute-atlas (companion project) | `../compute-atlas/data/atlas.json` | as of 2026-11 | project data | 105 US campuses (lat/lng, status, MW) | geocoded to county via Census Geocoder (https://geocoding.geo.census.gov/geocoder/, Public_AR_Current / Current_Current, Counties layer) -> `census_geocoder_campuses/campus_counties.json` |
| Cross-area inputs (read only) | bills, geo, markets areas | `data/processed/bills_state_annual.csv`, `geo_eia861_utilities.csv`, `bills_utility_prices.csv`, `markets_attribution_studies.json` | 2026-11 | project | state-year; utility | used for 2025 bill scaling, utility-id match, counter-evidence |

## Arrears, shutoffs, LIHEAP (reports; NEADA = advocacy for LIHEAP funding)
| Name | Publisher | URL | Date | Notes |
|---|---|---|---|---|
| Arrearage and Moratorium Update | NEADA | https://neada.org/wp-content/uploads/2022/01/arrearagesjan2022.pdf | 2022-01-20 | 2020 $20.2B / 2021 $22.3B; state table (`neada_reports2/`) |
| End of Winter Energy Update press release | NEADA | https://neada.org/press-release-neada-releases-end-of-winter-energy-update/ | 2023-04-17 | $15.9B (Jan 2022) -> $17.8B (Jan 2023); 20.5M behind on electric (via WP JSON `neada_reports/posts.json`) |
| Utility Arrearages Rise After Winter Shutoff Moratoriums End | NEADA | https://neada.org/wp-content/uploads/2023/05/arrearagesmay2023.pdf | 2023-05-24 | $19.5B Mar 2023 |
| Press release: States Call for Congress to Restore Funding for LIHEAP | NEADA | https://neada.org/wp-content/uploads/2024/01/pr-recordhhbehind.pdf | 2024-01-23 | $20.3B Dec 2023; 21.2M (16%) behind; FY23 7.3M served; state served table |
| As LIHEAP Funding Runs Dry, Utility Debt Increases by 8.4% to $17.4B | NEADA | https://neada.org/wp-content/uploads/2024/08/August-Arrearages-Press-Release-8.26.24.pdf | 2024-08-28 | conflicts with Jan-2024 level |
| Winter Heating Costs Expected to Jump 9.2% | NEADA | https://neada.org/wp-content/uploads/2025/12/winterheatingdec25PR.pdf | 2025-12-16 | $23B owed; LIHEAP $3.7B released late Nov; 17% of eligible served |
| Energy Hardship Report (pptx) | NEADA | https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx | 2026-02 | 21.5M behind; $15.4B (Jan 2022) -> $21.4B (Mar 2025); shutoffs 3.3M/3.5M/4.0M; CEX quintile burden table |
| Letter to HHS: release remaining FY26 LIHEAP funds | NEADA | https://neada.org/wp-content/uploads/2026/04/LetterHHSFinalRelease2026.pdf | 2026-03-20 | $422M remaining; ~$25B debt; 9.9% low-income burden |
| President's FY2027 Budget Eliminates LIHEAP | NEADA | https://neada.org/wp-content/uploads/2026/04/PresidentBudget2027Response.pdf | 2026-04-03 | ~$25B, +30% since end-2023 |
| House testimony FY2027 | NEADA | https://neada.org/wp-content/uploads/2026/07/housetestimonyFY27.pdf | 2026-04-16 | $7B request; state EIA-112 examples |
| June Price Update | NEADA | https://neada.org/summer-cooling-costs-projected-to-hit-record-highs-as-household-electric-bills-rise-10-5-june-price-update/ | 2026-06-09 | ~$25B projected end-2026 |
| Energy Hardship Project page; Sept-2026 heating oil PR; Nov-2026 winter outlook | NEADA | https://neada.org/?p=8468 ; https://neada.org/wp-content/uploads/2026/09/NEADA-Heating-Oil-Press-Release-Sept-25-2026A-1.pdf ; https://neada.org/neada-projects-home-heating-costs-will-rise-7-1-this-winter-with-heating-oil-costs-up-70/ | 2026 | context |
| New nationwide data reveals utility-specific disconnection information | Energy and Policy Institute (watchdog/advocacy) | https://energyandpolicy.org/new-nationwide-data-reveals-utility-specific-disconnection-information/ | 2026-06-22 | EIA-112 analysis; IOU 6.3 / muni 12.3 / co-op 7.8 per 100 (`web_arrears_1/`) |
| Federal energy assistance programs survive budget gauntlet | Utility Dive | https://www.utilitydive.com/news/federal-energy-assistance-programs-survive-budget-gauntlet/811389/ | 2026-02-04 | LIHEAP ~$4.05B FY26; April 2025 staff layoff; ~6M households 2024 |
| LIHEAP: Program and Funding (RL31865) | CRS via everycrsreport.com | https://www.everycrsreport.com/reports/RL31865.html | 2018-06-22 | historical only (`liheap_funding2/`) |

## Polls and elections
| Name | Publisher | URL | Date | Notes |
|---|---|---|---|---|
| Heatmap Pro poll (Embold Research) | Heatmap News | https://heatmap.news/energy/data-centers-electricity-prices-blame | 2026-06-03 | n=4,118 RV, May 15-28 2026 |
| How Americans view data centers' impact | Pew Research Center | https://www.pewresearch.org/short-reads/2026/03/12/how-americans-view-data-centers-impact-in-key-areas-from-the-environment-to-jobs/ ; topline https://www.pewresearch.org/wp-content/uploads/sites/20/2026/03/SR_26.03.12_data-centers_topline.pdf | 2026-03-12 | n=8,512 |
| How Americans' views of data centers have changed in 2026 + topline | Pew Research Center | https://www.pewresearch.org/chart/how-americans-views-of-data-centers-have-changed-in-2026/ ; https://www.pewresearch.org/wp-content/uploads/sites/20/2026/09/SR_26.09.22_data-centers_topline.pdf | 2026-09-22 | n=10,548 |
| Many Americans hold utility companies responsible for rising bills | Pew Research Center | https://www.pewresearch.org/short-reads/2026/05/05/many-americans-hold-utility-companies-responsible-for-their-rising-home-energy-bills/ | 2026-05-06 | n=3,524 |
| AP-NORC/EPIC poll (2026) | AP via PBS | https://www.pbs.org/newshour/politics/the-one-issue-where-republicans-and-democrats-are-unified-before-the-midterms-according-to-this-poll | 2026-09-16 | n=3,424, Jul 6-24 2026; 2025 wave https://epic.uchicago.edu/?p=24727 |
| ARI national poll | Morning Consult for Americans for Responsible Innovation (advocacy) | https://ari.us/wp-content/uploads/2026/07/ARI_Poll_DataCenters_RegisteredVoters_7-21-26.pdf | 2026-07-21 | n=2,202 RV |
| On data centers, local vibes matter more than electricity prices | Harvard Salata Institute (YouGov) | https://salatainstitute.harvard.edu/on-data-centers-local-vibes-matter-more-than-electricity-prices-poll/ | 2026-04-21 | n=1,000, Nov 2025 |
| Do Americans believe banning data centers will lower prices? | Third Way / Impact Research (advocacy) | https://www.thirdway.org/memo/do-americans-believe-banning-data-centers-will-lower-electricity-prices | 2026-03-12 | n=1,000 RV |
| How Americans Want to Make Electricity Less Expensive | Center for American Progress / Blue Rose Research (advocacy) | https://www.americanprogress.org/wp-content/uploads/sites/2/2026/05/VERSION-2-Memo_CAPs-Utilities-Polling_4.15.26-259-JOL.pdf | 2026-05-18 | memo |
| America Is All In memo (GSG) | Global Strategy Group (advocacy) | https://www.americaisallin.com/sites/default/files/2026-07/AIAI%20Data%20Center%20Survey%20Memo%20FINAL.pdf | 2026-05 | context only |
| Washington Post-Schar School Virginia poll | WaPo via ADN syndication | https://www.adn.com/nation-world/2026/04/15/in-this-us-hot-spot-for-data-centers-voters-have-turned-against-them/ | 2026-04-15 | n=1,101 RV |
| Summer 2026 Commonwealth Poll | VCU Wilder School | https://news.vcu.edu/article/voters-oppose-sales-tax-exemption-for-data-centers-new-commonwealth-poll-finds | 2026-07-15 | |
| FDU New Jersey poll | Fairleigh Dickinson via InsiderNJ | https://www.insidernj.com/fdu-nj-voters-blame-utility-companies-gov-murphy-for-price-hikes | 2025-08-07 | n=806 RV |
| Stockton Poll | Stockton University | https://stockton.edu/news/2025/renewable-energy-poll.html | 2025-07-01 | |
| Electricity costs jolt New Jersey's race for governor | NBC News | https://www.nbcnews.com/politics/elections/electricity-costs-jolt-new-jerseys-race-governor-coming-midterms-rcna232118 | 2025-09-19 | Sherrill pledge; Quinnipiac 42-40 |
| UMBC Maryland poll | WMAR | https://www.wmar2news.com/news/national-politics/america-votes/maryland-voters-see-higher-electric-bills-other-downsides-from-data-centers-in-new-umbc-poll | 2026-10-08 | |
| AJC/UGA SPIA Georgia poll | Atlanta Journal-Constitution | https://www.ajc.com/business/2026/10/poll-georgians-government-regulation-of-ai/ | 2026-10-22 | n=1,000 LV |
| 2025 exit polls (NJ/VA) | NBC, CBS, ABC | https://www.nbcnews.com/politics/elections/nbc-news-exit-poll-voters-disapprove-trump-new-jersey-virginia-rcna241693 ; https://www.cbsnews.com/news/exit-poll-2025-new-york-new-jersey-virginia-california ; https://www.goodmorningamerica.com/news/story/economy-top-mind-voters-races-preliminary-abc-news-127141841 | 2025-11-04/05 | |
| Georgia PSC 2025 results | PBS/AP | https://www.pbs.org/newshour/politics/georgia-democrats-win-big-over-gop-incumbents-in-2-statewide-utility-regulator-races | 2025-11-05 | |
| Voter anger over electricity bills could affect 2026 midterms | MPR/AP | https://www.mprnews.org/story/2025/11/08/voter-anger-over-electricity-bills-data-centers-could-affect-2026-midterms | 2025-11-08 | |
| VA data-center politics | E&E News | https://www.eenews.net/articles/with-data-center-fights-tearing-apart-towns-virginians-cast-ballots | 2025-11 | |
| How rising electric rates could affect the 2026 midterms | Brookings | https://www.brookings.edu/articles/how-rising-electric-rates-could-affect-the-2026-midterms | 2026-03-20 | |
| Data centers were not winners in the 2026 elections (exit polls) + chart PNGs | CBS News | https://www.cbsnews.com/news/exit-polls-data-centers-2026-election | 2026-11-06 | charts in `cbs_exit_2026_charts/` |
| It Was a Data Center Election After All | Reason (opinion) | https://reason.com/2026/11/04/it-was-a-data-center-election-after-all/ | 2026-11-04 | 41 local measures; NBC 3% |
| Georgia PSC 2026 results | Ballotpedia News | https://news.ballotpedia.org/?p=52280 | 2026-11 | D 3-2 majority |
| From boom to backlash: Ga. election brings a reckoning for data centers | WRDW | https://www.wrdw.com/2026/11/06/election-may-bring-reckoning-data-centers-georgia/ | 2026-11-06 | Bottoms moratorium pledge |

## Seen only in search summaries (UNVERIFIED; pages blocked or not fetched)
Heatmap Aug-2026 75% (the-decoder/TechSpot); NBC exit 56% (datacenterdynamics.com, 403); Hart/Climate Power 62% (michiganadvance.com, 403);
CCAN Action Fund VA 73% (ccanactionfund.org); Zenith MD 40% (marylandmatters.org, 403); Change Research 65% (429);
Marquette 62% (cited in WaPo); AJC 61% exact figure; GA PSC Edwards 55.2%; S&P Global arrears/midterm pieces (403); CBS News arrears story.
