# Load: sources

All raw downloads are under `data/raw/load/<folder>/` (git-ignored). Extracted text is under `data/raw/load/_text/`. Download with `node scripts/load/fetch.mjs <url> <out>`; for SEC, set `FETCH_UA` to a generic research UA.
The "Verified" column means the number was read in this copy during this session.

## Primary reports and statistics

| # | Name | Publisher | URL | Date | Licence / terms | Granularity | Local folder (size) | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | United States Data Center Energy Usage Report: 2025 Update (LBNL-2001758) | Lawrence Berkeley National Laboratory (DOE) | https://doi.org/10.71468/P1RP4F (PDF https://escholarship.org/content/qt33m6w3x0/qt33m6w3x0.pdf) | June 2026 | CC BY 4.0 | US annual 2017–2030; 2030 scenarios | `lbnl_2025_update/` (4.3 MB) | 2024 = 192 TWh, 4.7%; 2030 ref 649 TWh (521–843). Excludes crypto. Verified. |
| 2 | 2024 United States Data Center Energy Usage Report (Shehabi et al.) | LBNL | https://escholarship.org/uc/item/32d6m0d1 (PDF https://escholarship.org/content/qt32d6m0d1/qt32d6m0d1.pdf) | Dec 2024 | LBNL/eScholarship open access | US annual 2014–2028 (chart), text points | `lbnl_2024_report/` (4.2 MB) | 2014–16 ~60 TWh; 2018 76 TWh (1.9%); 2023 176 TWh (4.4%); 2028 325–580 TWh (6.7–12%). Verified. |
| 3 | Powering Intelligence: Analyzing AI and Data Center Energy Consumption (3002028905) | EPRI | https://www.epri.com/research/products/000000003002028905 (PDF https://restservice.epri.com/publicdownload/000000003002028905/0/Product) | May 2024 | EPRI public download; cite, no redistribution of PDF | 44 states: 2023 MWh and % of state consumption, plus four 2030 growth scenarios (Table A1) | `epri_2024_powering_intelligence/` (3.4 MB) | Virginia 25.59%. 2030 values are national growth rates applied to the state 2023 base. Verified. |
| 4 | Powering Intelligence 2026: Updated Scenarios of U.S. Data Center Electricity Use (3002034696) | EPRI | https://www.epri.com/research/products/000000003002034696 (PDF https://restservice.epri.com/publicdownload/000000003002034696/0/Product) | Feb 2026 | EPRI public download | State nominal IT MW 2021–2024 and 2030 (Table 2); US TWh; state shares only in charts | `epri_2026_powering_intelligence/` (6.0 MB) | 2024 177–192 TWh incl. crypto; 2030 383/596/793 TWh; Virginia 25%→39–57%. Verified. |
| 5 | EIA-861 Annual Electric Power Industry Report, 2019–2025 (final; 2025 released 2026-10-07 per `bills`) | U.S. EIA | https://www.eia.gov/electricity/data/eia861/ (zips `.../zip/f861<year>.zip`) | Annual | Public domain (US Gov) | Utility × state × year; sales MWh, revenue, customers by sector; Parts A–D; Delivery_Companies (TX TDUs) from 2020 | Read from `data/raw/bills/eia861_<year>/f861<year>.zip` (downloaded by `bills`; ~20–30 MB each) | Used read-only. Behind-the-meter third-party sellers and Texas REPs are excluded from the utility ranking. |
| 6 | Today in Energy: "Commercial electricity sales have soared in Virginia, driven by data centers" | EIA | https://www.eia.gov/todayinenergy/detail.php?id=67664 | 5 May 2026 | Public domain | State, PJM DOM zone | `eia_tie_67664/` | VA commercial +~30.0 million MWh 2019–2025 (prelim); DOM summer peak 23,905 MW (2025). Verified. |
| 7 | Today in Energy: "Commercial electricity demand grew fastest in states with rapid computing facility growth" | EIA | https://www.eia.gov/todayinenergy/detail.php?id=62409 | 28 Jun 2024 | Public domain | State | `eia_tie_62409/` | 2019–2023: VA +14 BkWh, TX +13 BkWh commercial; ND +37%. Context. |
| 8 | Today in Energy: "After more than a decade of little change, U.S. electricity consumption is rising again" | EIA | https://www.eia.gov/todayinenergy/detail.php?id=65264 | 13 May 2025 | Public domain | US | `eia_tie_65264/` | Context only. |
| 9 | Data Centres Metered Electricity Consumption 2025 (and 2024 edition) | Central Statistics Office Ireland | https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/ | 7 Jul 2026 | CSO re-use policy (CC BY 4.0) | Ireland annual 2015–2025, quarterly | `cso_ie_dcmec_2025*/`, `cso_ie_dcmec_2024/` | 23% in 2025 (7,663 GWh of 32,986). Verified. |
| 10 | "Data centres consume 5 percent of the Netherlands' electricity" | Statistics Netherlands (CBS) | https://www.cbs.nl/en-gb/news/2026/47/data-centres-consume-5-percent-of-the-netherlands-electricity | 18 Nov 2026 | CBS open data (CC BY 4.0) | NL annual 2017–2025; EU-country table 2024 (Eurostat) | `cbs_nl_dc_2026/` | NL 5.0% (2025 prov.), 5,664 GWh; EU 2024: IE 21.3, NL 4.6, DE 4.2. Verified. |
| 11 | Energy Trends special article: Data centre electricity consumption in Great Britain, 2020–2024 | DESNZ (UK) | https://assets.publishing.service.gov.uk/media/6a3e9f25da47783d87723bf2/Data_centre_electricity_consumption_in_Great_Britain__2020_to_2024.pdf | 30 Jun 2026 | Open Government Licence v3 | GB, regions, local authorities | `desnz_gb_dc_2020_2024/` | 4.5 TWh (2%) in 2024; Slough 65%; NESO 7.6 vs meter 4.1 TWh (2023). Official Statistics in Development. Verified. |
| 12 | Opening remarks by SMS Janil Puthucheary, ATxSummit Digital Sustainability Forum | Ministry of Digital Development and Information, Singapore | https://www.mddi.gov.sg/newsroom/opening-by-sms-janil-puthucheary-at-atxsummit-digital-sustainability-forum/ | 30 May 2024 | Singapore Gov terms | National | `mddi_sg_atx_speech/` | Data centres = "7% of Singapore's total electricity consumption" (reference year not stated). |
| 13 | Green Data Centre Roadmap | IMDA Singapore | https://www.imda.gov.sg/assets/c99c4fa7-8fe9-4082-9969-1e86f69375e4.pdf | 2024 | IMDA copyright | National | `imda_sg_green_dc_roadmap/` (5.8 MB) | No consumption share in it; +300 MW capacity aim. |
| 14 | Written reply to PQ on data-centre electricity consumption | MTI/METI Singapore | https://www.mti.gov.sg/newsroom/written-reply-to-pq-on-electricity-consumption-when-data-centres--capacities-rise-by-a-third-and-impact-on-singapore-s-greenhouse-emissions/ | 7 Jan 2025 | Singapore Gov terms | National | `mti_sg_pq_2025/` | No numeric share; not used for numbers. |
| 15 | Analyseforudsætninger til Energinet 2025 – Datacentre (background note) | Energistyrelsen (Danish Energy Agency) | https://ens.dk/media/7603/download | Nov 2025 | Free to cite | Denmark, projections 2025–2050 | `ens_dk_media_7603/` | 6.0 TWh 2030, 26.8 TWh 2040; ~60% capacity utilisation in 2023. No realized TWh. |
| 16 | DDI consultation response on AF25 (industry) | Danish Data Center Industry (advocacy) | https://ens.dk/media/7629/download | 10 Oct 2025 | — | — | `ens_dk_media_7629/` | Utilisation assumptions only. The "7% of Danish electricity" claim comes from a DDI report seen only in a search snippet: UNVERIFIED. |
| 17 | Energistatistik 2024 | Energistyrelsen | https://ens.dk/media/7426/download | 2025 | Free to cite | Denmark | `ens_dk_media_7426/` (2.7 MB) | No data-centre split (checked). |
| 18 | Key questions on energy and AI (slides, N. Kauf) | IEA (hosted by ADB Asia Clean Energy Forum) | https://asiacleanenergyforum.adb.org/wp-content/uploads/2026/06/Key-questions-on-energy-and-AI.pdf | 11 Jun 2026 | IEA terms (CC BY 4.0 for most IEA material) | Global | `iea_key_questions_energy_ai_2026/` | "data centre electricity demand grew by almost 20% in 2025". iea.org itself is blocked (403/Cloudflare). |

## Utility filings (SEC EDGAR; `scripts/load/fetch_sec_filings.mjs`)

| Filer (CIK) | Documents | URL | Filed | Local folder | Used for |
|---|---|---|---|---|---|
| Dominion Energy (715957) | 2025 10-K; Q3 2026 10-Q; Q3 2026 8-K ex-99 | https://www.sec.gov/Archives/edgar/data/715957/000119312526063120/d-20251231.htm ; https://www.sec.gov/Archives/edgar/data/715957/000119312526440697/d-20260930.htm | 2026-02-23; 2026-10-30 | `sec_dominion_10k_2025/` (17 MB), `sec_dominion_10q_2026q3/` (12 MB), `sec_dominion_8k_20261030/` | DC = 26% / 28% of Virginia Power sales; high-load revenue; PJM DOM 5.4%/yr |
| Southern Company (92122) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/92122/000009212226000006/so-20251231.htm ; https://www.sec.gov/Archives/edgar/data/92122/000009212226000069/so-20260930.htm | 2026-02-19; 2026-11-05 | `sec_so_*` | Georgia Power commercial +4.1% (2025), +9.3% YTD 2026; ~9 → ~16 GW large-load contracts |
| American Electric Power (4904) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/4904/000000490426000013/aep-20251231.htm ; https://www.sec.gov/Archives/edgar/data/4904/000000490426000072/aep-20260930.htm | 2026-02-12; 2026-10-28 | `sec_aep_*` | AEP Texas LOAs 36 → 49 GW; Piketon 10.4 GW; data-processing load drives C&I sales |
| Pinnacle West / APS (764622) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/764622/000076462226000011/pnw-20251231.htm ; https://www.sec.gov/Archives/edgar/data/764622/000076462226000050/pnw-20260930.htm | 2026-02-25; 2026-11-03 | `sec_pnw_*` | Sales growth guidance 8–10% (2026), 5–7 pts from DC/manufacturing |
| Entergy (65984) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/65984/000006598426000174/etr-20251231.htm ; https://www.sec.gov/Archives/edgar/data/65984/000006598426000325/etr-20260930.htm | 2026-02-19; 2026-11-02 | `sec_etr_*` | Meta (LA), AWS (MS), Google (AR) agreements; no MWh |
| Duke Energy (1326160) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/1326160/000132616026000014/duk-20251231.htm | 2026-02-26; 2026-11-05 | `sec_duk_*` | Qualitative only |
| Exelon / ComEd (1109357) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/1109357/000110935726000018/exc-20251231.htm | 2026-02-12; 2026-10-30 | `sec_exc_*` | Qualitative only |
| PG&E Corp (1004980) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/1004980/000100498026000009/pcg-20251231.htm | 2026-02-12; 2026-10-22 | `sec_pcg_*` | Qualitative only |
| Oncor Electric Delivery (1193311) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/1193311/000119331126000007/c311-20251231x10k.htm | 2026-02-26; 2026-11-05 | `sec_oncor_*` | ERCOT 2031 peak forecast 159 GW vs 85.5 GW record |
| Berkshire Hathaway Energy (1081316) | 2025 10-K; Q3 2026 10-Q | https://www.sec.gov/Archives/edgar/data/1081316/000108131626000003/bhe-20251231.htm | 2026-03-02; 2026-11-09 | `sec_bhe_*` | MidAmerican "electronic data storage"; NV Energy has no DC disclosure |

SEC filings are public. Omaha PPD, NOVEC and SRP do not file with the SEC; for them only EIA-861 is used.

## Secondary sources (not used as verified numbers)
- Zacks / earnings-call coverage of Dominion Q3 2026: ~54.9 GW contracted pipeline (12.2 GW ESAs, 9.8 GW CLOAs, 32.8 GW engineering). https://www.zacks.com/stock/news/3019744/ . **UNVERIFIED**.
- Eco-Business: Singapore data centres ~6.5 TWh in 2024 (~11%). **UNVERIFIED**.
- IEA Energy and AI (Apr 2025): ~415 TWh global in 2024 (~1.5%), US ~45%; IEA 2026 update ~485 TWh (2025). iea.org blocked. **UNVERIFIED**.

## Other areas' files read (not modified)
- `data/raw/bills/eia861_*` (EIA-861 zips) and `scripts/bills/build_utility_prices.py` (conventions).
- `data/raw/markets/_text/doe_lbnl_dc_2025_update.txt` and `jlarc_dc_study_presentation_2024.txt` (initial read; then downloaded our own LBNL copy).

## Scripts (`scripts/load/`)
- `fetch.mjs`: generic downloader (env `FETCH_UA` optional).
- `fetch_sec_filings.mjs`: latest 10-K and 10-Q for 10 utility holding companies.
- `pdf2txt.js` (macOS PDFKit via JXA) and `html2txt.py`: text extraction.
- `build_utility_sales_growth.py`: writes `load_utility_sales_growth.csv`.
- `build_top_ci_growth.py`: writes `load_utility_ci_growth_rank.csv`.
- `build_state_dc_share.py`: writes `load_state_dc_share.csv` and `load_state_dc_capacity_mw.csv`.
- `build_disclosures_international.py`: writes `load_utility_dc_disclosures.csv` and `load_international.json`.
