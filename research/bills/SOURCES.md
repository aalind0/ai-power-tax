# Bills: sources

Accessed 2026-11-23 unless noted. US federal data (EIA, BLS, LBNL/DOE, OpenEI/NREL) are public domain or open
(OpenEI content is CC0). State commission pages are public records. News and advocacy sources are cited, not redistributed.

## Datasets (downloaded; raw copies in `data/raw/bills/`)

| Name | Publisher | URL | Date / version | Licence | Granularity | Notes |
|---|---|---|---|---|---|---|
| Form EIA-861 annual detailed data, 2013-2025 (`Sales_Ult_Cust`, `Delivery_Companies`, `Balancing_Authority`, `Short_Form`) | US EIA | https://www.eia.gov/electricity/data/eia861/ (zips: `archive/zip/f861YYYY.zip`; 2025 `zip/f8612025.zip`) | 2025 final data released 2026-10-07; 2024 file updated 2025-12-03 | Public domain | utility x state x part (A bundled, B energy-only, C delivery-only, D bundled REP/other), by sector | 3-6 MB per zip. `Delivery_Companies` (2020+) holds the Texas TDUs. Short-form filers report totals only. Raw: `data/raw/bills/eia861_YYYY/` |
| Form EIA-861M state sales & revenue (`sales_revenue.xlsx`) | US EIA | https://www.eia.gov/electricity/data/eia861m/xls/sales_revenue.xlsx | released 2026-10-23 with Aug 2026 data; 2026 preliminary | Public domain | state x month, 1990-2026-08, by sector | 2.3 MB. Raw: `data/raw/bills/eia861m_sales_revenue/` |
| Form EIA-861M utility-level (`sales_ult_cust_2024/2025/2026.xlsx`) | US EIA | https://www.eia.gov/electricity/data/eia861m/ (archive/xls/ for 2024-2025, xls/ for 2026) | 2026 through Aug (preliminary) | Public domain | utility x state x month, bundled only | Sample of ~all large utilities; small ones folded into state adjustment rows. Raw: `data/raw/bills/eia861m_utility_YYYY/` |
| CPI-U all items (CUUR0000SA0), CPI electricity NSA (CUUR0000SEHF01) and SA (CUSR0000SEHF01) | US BLS | https://api.bls.gov/publicAPI/v2/timeseries/data/ | through Oct 2026; Oct 2025 not published | Public domain | US monthly | Fetched with `scripts/bills/fetch_bls_cpi.mjs`. Raw JSON: `data/raw/bills/bls_cpi_api/` |
| Retail Electricity Price Trends and Drivers: July 2026 briefing + data file | Lawrence Berkeley National Laboratory (Wiser et al.) | https://emp.lbl.gov/retail-electricity-price-trends-and-drivers ; data file https://emp.lbl.gov/sites/default/files/2026-07/Retail%20Price%20Trends_2026%20edition_%20JulyUpdate_Data%20File.xlsx | July 2026 update | Public (DOE lab) | national/state/ISO; some utility lists | Tabs used: Primary drivers, PJM capacity prices/auction prices, State growth vs prices, Storm recovery, Wildfire mitigation, Distribution/Transmission price estimates, Rate requests/approvals, Load growth benefits. The 10.5 MB briefing PDF was downloaded but could not be text-extracted (no PDF tooling). Raw: `data/raw/bills/lbnl_retail_price_trends_2026jul*/` |
| OpenEI Utility Rate Database (URDB) residential tariffs | OpenEI / National Laboratory of the Rockies (NREL), DOE | https://api.openei.org/utility_rates (DEMO_KEY) ; record pages https://apps.openei.org/IURDB/rate/view/<label> | records effective 2025-01 to 2026-04 | CC0 | utility x rate schedule | Transcribed tariffs with "rate" + "adjustments" (riders listed in comments). API rate-limited after 9 utilities. Raw: `data/raw/bills/openei_urdb_2026-11-23/` |
| USURDB bulk download (all approved rates) | OpenEI | https://apps.openei.org/USURDB/download/usurdb.csv.gz | downloaded 2026-11-23 (58,920 rates) | CC0 | utility x rate schedule, tiers/periods/schedules flattened | 12 MB gz. Used for Dominion Sch. 1 (2026-01-01), Pepco DC Sch. R (2025-08-01), PSE&G RS (2026-04-01), PG&E E-1 region X baseline. Raw: `data/raw/bills/openei_usurdb_bulk_2026-11-23/` |

## Tariffs, commission and utility documents (bill anatomy)

| Item | Publisher | URL | Effective / date | Verified this session | Notes |
|---|---|---|---|---|---|
| PECO Rate R tariff page (Supplement 21, Tariff Electric Pa. P.U.C. No. 8) | PECO | https://azure-na-assets.contentstack.com/v3/assets/blt1b5616c79bacadb4/bltef2bb157cc587eac/695440f39dd7d11ce0542224/Pages_52_Rate_R_from_clean_up_pages_for_ICUS_FARS_Supp_no._21_eff_Jan_1_2026.pdf | eff. 2026-01-01 | Yes (text extracted): fixed $11.30; variable distribution $0.10276/kWh | Raw: `data/raw/bills/peco_rate_r_2026/` |
| PA PUC press release: June 1 2026 Price to Compare changes | Pennsylvania PUC | https://www.puc.pa.gov/press-release/2026/puc-alerts-consumers-to-june-1-electric-price-changes-and-higher-summer-energy-costs-5-20-26 | 2026-05-20 | Yes | PTC table for 11 EDCs (PECO "estimated" 11.572 c) |
| PECO default service rate filing (10.785 c/kWh GSA from 2026-06-01) | PA PUC docket | https://www.puc.pa.gov/pcdocs/1923196.pdf | 2026 | No (search snippet only; PDF blocked by TLS error) | UNVERIFIED |
| ComEd Price to Compare | Plug In Illinois (Illinois Commerce Commission) | https://plugin.illinois.gov/understanding-the-price-to-compare/price-to-compare-comed.html | Oct 1 2026 - May 31 2027 | Yes: supply 8.413 c, transmission 1.69 c, PTC 10.103 c | Summer 2026 PTC 10.399 c (search summary, UNVERIFIED) |
| NJ BPU: 2026 BGS auction results | New Jersey BPU | https://nj.gov/bpu/newsroom/2026/approved/20260212.html | 2026-02-12, rates eff. 2026-06-01 | Yes | 650 kWh bills: PSE&G $183.46->$180.23; JCP&L $135.24->$137.47; ACE; RECO |
| PUCT TDU residential delivery charges | Public Utility Commission of Texas | https://www.puc.texas.gov/industry/electric/rates/tdr/ | as of 2026-11-01 | Yes | Oncor $1.48 + $2.58 + 6.8673 c/kWh ($72.73 at 1,000 kWh); CenterPoint $70.23; AEP Central $60.15; AEP North $59.00; TNMP $85.27 |
| URDB records used (BGE Sch. R; ComEd RDS/BES; AEP Ohio RS; JCP&L RS; Georgia Power R-30; Duke Energy Carolinas RS; Entergy Louisiana RS; PECO R) | OpenEI | see `source` fields in `data/processed/bills_anatomy.json` | 2025-2026 | No (URDB transcription) | URDB's `source` points to each utility's tariff PDF |
| PG&E Electric Schedule E-1 (Advice 7921-E, D.26-04-036) incl. "Unbundling of total rates" | PG&E | https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-1.pdf | eff. 2026-06-01 | Yes (text extracted) | Tier 1 32.561 c, tier 2 40.702 c; generation 12.855, distribution 18.042, transmission 4.638 (+0.466 adj/reliability), wildfire fund 0.591, wildfire hardening 0.391, PPP 0.614, PCIA -1.011 c/kWh; base services charge $0.19713/$0.39688/$0.79343 per day by income tier; climate credit -$36.18 semiannual. Raw: `data/raw/bills/pge_e1_tariff/` |
| Dominion biennial review final order (PUR-2025-00058) | Virginia SCC (via NPR-hosted copy) | https://npr.brightspotcdn.com/b6/ac/706130b64d2b8eee6a9832b97e48/20251125-virginiascc-dominionenergyruling.pdf | 2025-11-25 | Partly (PDF text not machine-readable) | Numbers taken from the Cardinal News summary below |

## Reports and analyses

| Item | Publisher (type) | URL | Date | Notes |
|---|---|---|---|---|
| Drivers of PJM's Capacity Market Price Surge and the DC Impact | Synapse Energy Economics for DC Office of the People's Counsel (consumer advocate) | https://opc-dc.gov/wp-content/uploads/2025/05/PJM-Capacity-Market-Report-FINAL-OPC-Synapse.pdf | May 2025 | Residential +$0.017/kWh, +$10/mo, +9% from 2025/26 BRA. Raw: `data/raw/bills/opcdc_synapse_pjm_capacity_2025/` |
| "Electric bills are set to increase in June for 65 million Americans" | U.S. PIRG (advocacy) | https://pirg.org/articles/electric-bills-are-set-to-increase-in-june-for-65-million-americans-heres-why/ | 2024-12-06 | Pre-June-2025 estimates by state; context only |
| PJM 2027/28 BRA report; PJM IMM Q3 2025 State of the Market | PJM; Monitoring Analytics | https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2027-2028/2027-2028-bra-report.pdf ; https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025q3-som-pjm.pdf | 2025 | Cited via LBNL data file (not opened directly; markets area owns these) |

## News (secondary; used for facts that commission pages summarize)

| Item | Outlet | URL | Date |
|---|---|---|---|
| Regulators approve Dominion Energy rate increase | Cardinal News | https://cardinalnews.org/2025/11/26/regulators-approve-dominion-energy-rate-increase/ | 2025-11-26 |
| Search-result leads not opened (PECO PTC context, Oncor rate case, ComEd June 2026) | PhillyVoice; electricityrates.com; utilitiesformyhome.com; CUB blog | https://www.phillyvoice.com/peco-bill-increase-supply-costs/ ; https://www.citizensutilityboard.org/blog/2026/06/10/why-is-comed-price-spiking/ | 2026 | Not relied on for numbers in outputs |
