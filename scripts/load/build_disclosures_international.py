"""Write hand-curated tables from primary documents read this session.

Run from the project root:  python3 -I scripts/load/build_disclosures_international.py
Outputs:
  data/processed/load_utility_dc_disclosures.csv   utility-reported data-center sales / share / contracted load
  data/processed/load_international.json           international comparison points (data-center share of electricity)

Every value was read from the cited document (raw copies under data/raw/load/, text under data/raw/load/_text/)
unless verified=False, in which case it comes from a secondary report or search snippet and is marked UNVERIFIED.
"""
import csv
import json
import os

ROOT = os.getcwd()
OUT_CSV = os.path.join(ROOT, 'data', 'processed', 'load_utility_dc_disclosures.csv')
OUT_JSON = os.path.join(ROOT, 'data', 'processed', 'load_international.json')

D_10K = 'https://www.sec.gov/Archives/edgar/data/715957/000119312526063120/d-20251231.htm'
D_10Q = 'https://www.sec.gov/Archives/edgar/data/715957/000119312526440697/d-20260930.htm'
SO_10K = 'https://www.sec.gov/Archives/edgar/data/92122/000009212226000006/so-20251231.htm'
SO_10Q = 'https://www.sec.gov/Archives/edgar/data/92122/000009212226000069/so-20260930.htm'
AEP_10K = 'https://www.sec.gov/Archives/edgar/data/4904/000000490426000013/aep-20251231.htm'
AEP_10Q = 'https://www.sec.gov/Archives/edgar/data/4904/000000490426000072/aep-20260930.htm'
PNW_10K = 'https://www.sec.gov/Archives/edgar/data/764622/000076462226000011/pnw-20251231.htm'
PNW_10Q = 'https://www.sec.gov/Archives/edgar/data/764622/000076462226000050/pnw-20260930.htm'
ETR_10K = 'https://www.sec.gov/Archives/edgar/data/65984/000006598426000174/etr-20251231.htm'
ETR_10Q = 'https://www.sec.gov/Archives/edgar/data/65984/000006598426000325/etr-20260930.htm'
DUK_10K = 'https://www.sec.gov/Archives/edgar/data/1326160/000132616026000014/duk-20251231.htm'
EXC_10K = 'https://www.sec.gov/Archives/edgar/data/1109357/000110935726000018/exc-20251231.htm'
PCG_10K = 'https://www.sec.gov/Archives/edgar/data/1004980/000100498026000009/pcg-20251231.htm'
ONC_10K = 'https://www.sec.gov/Archives/edgar/data/1193311/000119331126000007/c311-20251231x10k.htm'
BHE_10K = 'https://www.sec.gov/Archives/edgar/data/1081316/000108131626000003/bhe-20251231.htm'
EIA_VA = 'https://www.eia.gov/todayinenergy/detail.php?id=67664'

COLS = ['utility', 'eia_utility_id', 'state', 'parent', 'period', 'metric', 'value', 'unit', 'kind', 'quote_or_basis',
        'source', 'source_url', 'verified']
# kind: realized = measured sales/revenue/share; commitment = signed contracts/pipeline (not consumption); guidance = company forecast
DISC = [
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', 2024, 'data_center_share_of_sales', 26, 'pct', 'realized',
     'Data centers represent 28% and 26% of Virginia Power\'s electricity sales for the years ended December 31, 2025 and 2024', 'Dominion Energy 2025 Form 10-K (filed 2026-02-23)', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', 2025, 'data_center_share_of_sales', 28, 'pct', 'realized',
     'same sentence as above', 'Dominion Energy 2025 Form 10-K (filed 2026-02-23)', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', 2023, 'high_load_class_revenue', 1308, 'million_usd', 'realized',
     'Regulated electric sales, High load (customers in VA incl. certain data centers, >=25 MW and >=75% load factor)', 'Dominion Energy 2025 Form 10-K, Note 3 Operating Revenue', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', 2024, 'high_load_class_revenue', 1362, 'million_usd', 'realized',
     'as above', 'Dominion Energy 2025 Form 10-K, Note 3', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', 2025, 'high_load_class_revenue', 1811, 'million_usd', 'realized',
     'as above (residential revenue at Virginia Power: 3,863 / 4,133 / 4,631 $M in 2023/2024/2025)', 'Dominion Energy 2025 Form 10-K, Note 3', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', '2026 Jan-Sep', 'high_load_class_revenue', 2156, 'million_usd', 'realized',
     'YTD Sept 2026 vs 1,308 YTD Sept 2025 (+65%); Virginia Power residential YTD 4,287 vs 3,494 (+23%)', 'Dominion Energy Q3 2026 Form 10-Q, Note 3', D_10Q, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', '2026-2035', 'pjm_dom_zone_peak_growth_forecast', 5.4, 'pct_per_year', 'guidance',
     'PJM has projected a 5.4% average peak annual load growth over the next ten years for the PJM DOM Zone', 'Dominion Energy 2025 Form 10-K', D_10K, True),
    ('Dominion Energy Virginia (Virginia Power)', 19876, 'VA', 'Dominion Energy', '2026-09', 'data_center_contracted_capacity_pipeline', 54.9, 'GW', 'commitment',
     '~54.9 GW in various stages of contracting (12.2 GW ESAs, 9.8 GW construction letters of authorization, 32.8 GW engineering letters); +6.3 GW vs Dec 2025',
     'Q3 2026 earnings coverage (Zacks / call summaries) - not read in a primary document this session', 'https://www.zacks.com/stock/news/3019744/dominion-energy%27s-q3-earnings-top-estimates,-revenues-increase-y/y', False),
    ('Virginia statewide', None, 'VA', None, '2019-2025', 'commercial_sales_added', 30.0, 'million_MWh', 'realized',
     'Commercial electricity sales in Virginia increased by nearly 30.0 million MWh between 2019 and 2025 ... largely driven by a concentration of data centers (EIA used preliminary 2025 data)',
     'EIA Today in Energy, 5 May 2026', EIA_VA, True),
    ('Virginia statewide', None, 'VA', None, '2025', 'pjm_dom_zone_summer_peak', 23905, 'MW', 'realized',
     'Summer peak load in PJM\'s Dominion zone was 23,905 MW in 2025, 23% higher than in 2019; winter peak 25,413 MW in 2025-26, 45% higher than 2019-20', 'EIA Today in Energy, 5 May 2026', EIA_VA, True),
    ('Georgia Power', 7140, 'GA', 'Southern Company', 2025, 'weather_adjusted_commercial_sales_growth', 4.1, 'pct_yoy', 'realized',
     'Weather-adjusted commercial KWH sales increased 4.1% primarily due to additional sales from new and existing data centers', 'Southern Company 2025 Form 10-K (Georgia Power MD&A)', SO_10K, True),
    ('Georgia Power', 7140, 'GA', 'Southern Company', '2026 Jan-Sep', 'weather_adjusted_commercial_sales_growth', 9.3, 'pct_yoy', 'realized',
     'Weather-adjusted commercial KWH sales increased 10.2% and 9.3% in the third quarter and year-to-date 2026 ... largely driven by data centers (Georgia Power section; attribution inferred from section context)',
     'Southern Company Q3 2026 Form 10-Q', SO_10Q, True),
    ('Southern Company traditional electric operating companies', None, 'GA/AL/MS', 'Southern Company', '2023-2025', 'large_load_contracts', 9, 'GW', 'commitment',
     'Since 2023 ... contracted with new data centers and other large load customers covering approximately nine GWs of electric load (each >100 MW)', 'Southern Company 2025 Form 10-K', SO_10K, True),
    ('Southern Company traditional electric operating companies', None, 'GA/AL/MS', 'Southern Company', '2023-2026-09', 'large_load_contracts', 16, 'GW', 'commitment',
     'Since 2023 ... contracts with new data centers and other large load customers covering approximately 16 GWs of electric load', 'Southern Company Q3 2026 Form 10-Q', SO_10Q, True),
    ('AEP Texas', None, 'TX', 'American Electric Power', 'by 2030', 'letters_of_agreement_load', 36, 'GW', 'commitment',
     'AEP Texas has signed Letters of Agreement for an incremental 36 gigawatts of load by 2030', 'AEP 2025 Form 10-K', AEP_10K, True),
    ('AEP Texas', None, 'TX', 'American Electric Power', 'by 2031', 'letters_of_agreement_load', 49, 'GW', 'commitment',
     'AEP Texas has executed Letters of Agreement for approximately 49 gigawatts of incremental load by 2031, including prospective load seeking consideration under ERCOT\'s Batch Zero process',
     'AEP Q3 2026 Form 10-Q', AEP_10Q, True),
    ('AEP Ohio (Ohio Power)', 14006, 'OH', 'American Electric Power', 'agreements Aug 2026', 'single_campus_contracted_load', 10.4, 'GW', 'commitment',
     'definitive agreements ... three 765 kV transmission lines ... to support the development of a proposed 10.4 GW data center campus in Piketon, Ohio (initial 800 MW on existing transmission)',
     'AEP Q3 2026 Form 10-Q', AEP_10Q, True),
    ('American Electric Power (system)', None, 'multi', 'American Electric Power', '2026 Jan-Sep', 'qualitative_sales_driver', None, None, 'realized',
     'Through the third quarter of 2026, AEP experienced higher customer demand, driven primarily by new data processing load added in the commercial and industrial customer classes (percentages in an image table not extracted)',
     'AEP Q3 2026 Form 10-Q', AEP_10Q, True),
    ('Arizona Public Service', 803, 'AZ', 'Pinnacle West', '2026', 'retail_sales_growth_guidance', '8.0-10.0', 'pct', 'guidance',
     'annual retail electricity sales in kWh will increase in the range of 8.0% to 10.0% for 2026 ... large manufacturing and data center facilities ... expected to contribute to 2026 growth in the range of 5.0% to 7.0%',
     'Pinnacle West Q3 2026 Form 10-Q', PNW_10Q, True),
    ('Arizona Public Service', 803, 'AZ', 'Pinnacle West', '2026-2030', 'retail_sales_growth_guidance', '8.0-10.0', 'pct_per_year', 'guidance',
     'average annual growth ... 8.0% to 10.0% through 2030; data centers and large manufacturing contribute 7.0% to 9.0% (Feb 2026 10-K guidance was 5-7% with 4-6% from large loads)',
     'Pinnacle West Q3 2026 Form 10-Q', PNW_10Q, True),
    ('Entergy Louisiana', 11241, 'LA', 'Entergy', '2024-2026', 'large_customer_agreements', None, None, 'commitment',
     'Service to a Meta Platforms data center in north Louisiana (LPSC approval Aug 2025); second Meta (Evest LLC) ESA signed March 2026. No MWh disclosed.', 'Entergy 2025 10-K; Q3 2026 10-Q', ETR_10Q, True),
    ('Entergy Mississippi', 12685, 'MS', 'Entergy', '2024-2026', 'large_customer_agreements', None, None, 'commitment',
     'AWS data center campuses: Madison County (Mar 2024, expanded Apr 2026), Warren County (Feb 2025), Hinds County (Apr 2026). No MWh disclosed.', 'Entergy Q3 2026 10-Q', ETR_10Q, True),
    ('Entergy Arkansas', 814, 'AR', 'Entergy', '2025', 'large_customer_agreements', None, None, 'commitment',
     'Special rate contract with Altitude LLC (Google) for a data center in West Memphis, filed Sept 2025. No MWh disclosed.', 'Entergy 2025 10-K', ETR_10K, True),
    ('Duke Energy (system)', None, 'NC/SC/IN/FL/OH/KY', 'Duke Energy', 2025, 'qualitative_sales_driver', None, None, 'realized',
     'Weather-normal sales volumes have shown growth in 2025 ... due primarily to continued residential customer growth and strength in the commercial sector including data center usage', 'Duke Energy 2025 Form 10-K', DUK_10K, True),
    ('ComEd / Exelon utilities', 4110, 'IL', 'Exelon', '2026-2029', 'capex_mention', 41, 'billion_usd', 'guidance',
     '~$41 billion over four years ... including ... new business including data centers (no data-center sales disclosed)', 'Exelon 2025 Form 10-K', EXC_10K, True),
    ('PG&E', 14328, 'CA', 'PG&E Corp', '2026+', 'qualitative_load_driver', None, None, 'guidance',
     'expects customer electric load to increase in coming years primarily as a result of data center usage, electric vehicle adoption, and building electrification (no data-center sales disclosed)', 'PG&E 2025 Form 10-K', PCG_10K, True),
    ('Oncor Electric Delivery', 44372, 'TX', 'Sempra (80%)', '2031', 'ercot_peak_forecast_context', 159000, 'MW', 'guidance',
     "ERCOT's December 2025 regional transmission plan forecasts 159,000 MW of peak demand for 2031, compared to the current peak hourly demand record of 85,508 MW (summer 2023). No data-center MWh disclosed.",
     'Oncor 2025 Form 10-K', ONC_10K, True),
    ('MidAmerican Energy', 12341, 'IA', 'Berkshire Hathaway Energy', 2025, 'qualitative', None, None, 'realized',
     'Principal industries served by MidAmerican Energy include electronic data storage (no data-center sales disclosed)', 'Berkshire Hathaway Energy 2025 Form 10-K', BHE_10K, True),
]

INTL = {
    'description': 'Data-center share of national (or regional) electricity consumption, realized/measured where available. '
                   'Comparable only loosely: definitions (colocation/hyperscale vs enterprise), metering basis and denominators differ.',
    'generated_by': 'scripts/load/build_disclosures_international.py',
    'points': [
        {'country': 'Ireland', 'iso2': 'IE', 'year': 2025, 'dc_twh': 7.663, 'total_twh': 32.986, 'dc_share_pct': 23,
         'series': {'2015': 5, '2016': 6, '2017': 7, '2018': 8, '2019': 9, '2020': 11, '2021': 14, '2022': 18, '2023': 21, '2024': 22, '2025': 23},
         'series_dc_gwh': {'2015': 1240, '2019': 2490, '2023': 6339, '2024': 6973, '2025': 7663},
         'basis': 'Metered electricity consumption (CSO identifies data-centre meters by operator name, industry reports, high-consumption checks)',
         'source': 'Central Statistics Office (CSO), Data Centres Metered Electricity Consumption 2025, released 7 July 2026',
         'source_url': 'https://www.cso.ie/en/releasesandpublications/ep/p-dcmec/datacentresmeteredelectricityconsumption2025/keyfindings/',
         'note': 'Data centres 23% vs all urban households 18% and rural households 9%. DC use +10% in 2025 vs +2% for all other users.', 'verified': True},
        {'country': 'Netherlands', 'iso2': 'NL', 'year': 2025, 'dc_twh': 5.664, 'dc_share_pct': 5.0,
         'series': {'2017': 1.5, '2018': 2.1, '2019': 2.4, '2020': 2.8, '2021': 3.3, '2022': 4.0, '2023': 4.2, '2024': 4.6, '2025': 5.0},
         'basis': 'Electricity supplied to ~200 data centres (CBS); ~50 sites >=10 GWh/yr use ~90%. Excludes in-house DCs of universities/hospitals (est. 142 GWh).',
         'source': 'Statistics Netherlands (CBS), news release 18 Nov 2026 (2025 provisional)',
         'source_url': 'https://www.cbs.nl/en-gb/news/2026/47/data-centres-consume-5-percent-of-the-netherlands-electricity', 'verified': True},
        {'country': 'Germany', 'iso2': 'DE', 'year': 2024, 'dc_twh': 20.0, 'dc_share_pct': 4.2,
         'basis': 'Eurostat services energy consumption (data centres), as compiled by CBS', 'source': 'CBS (18 Nov 2026) citing Eurostat nrg_d_serq_n and nrg_cb_e',
         'source_url': 'https://www.cbs.nl/en-gb/news/2026/47/data-centres-consume-5-percent-of-the-netherlands-electricity', 'verified': True},
        {'country': 'EU comparison (Eurostat via CBS)', 'iso2': None, 'year': 2024,
         'shares_pct': {'Ireland': 21.3, 'Netherlands': 4.6, 'Germany': 4.2, 'Finland': 3.1, 'Sweden': 2.1, 'Belgium': 2.0, 'Norway': 1.6, 'France': 1.1, 'Czechia': 0.6, 'Spain': 0.3, 'Poland': 0.3},
         'basis': 'Eurostat; no data for Denmark, Italy, Luxembourg, Bulgaria, Croatia, Malta, Serbia',
         'source': 'CBS (18 Nov 2026) citing Eurostat', 'source_url': 'https://www.cbs.nl/en-gb/news/2026/47/data-centres-consume-5-percent-of-the-netherlands-electricity', 'verified': True},
        {'country': 'United Kingdom (Great Britain)', 'iso2': 'GB', 'year': 2024, 'dc_twh': 4.5, 'total_twh': 249.2, 'dc_share_pct': 2,
         'basis': 'Meter-level grid consumption of 2,423 matched colocation/managed-hosting/hyperscale sites; excludes enterprise DCs. Official Statistics in Development.',
         'local_extremes': {'Slough_share_pct': 65, 'Hillingdon_share_pct': 28, 'Tower_Hamlets_share_pct': 18, 'London_share_pct': 5, 'South_East_share_pct': 5},
         'growth': '2020-2024: +1.3 TWh (+41%)',
         'method_gap': 'NESO capacity-based estimate for 2023 = 7.6 TWh vs DESNZ meter-based 4.1 TWh',
         'source': 'DESNZ Energy Trends special article, 30 June 2026: Data centre electricity consumption in Great Britain, 2020-2024',
         'source_url': 'https://assets.publishing.service.gov.uk/media/6a3e9f25da47783d87723bf2/Data_centre_electricity_consumption_in_Great_Britain__2020_to_2024.pdf', 'verified': True},
        {'country': 'Singapore', 'iso2': 'SG', 'year': None, 'dc_share_pct': 7,
         'basis': 'Government statement; reference year not stated (speech of 30 May 2024)',
         'source': 'MDDI, Opening remarks by SMS Janil Puthucheary at ATxSummit Digital Sustainability Forum, 30 May 2024',
         'source_url': 'https://www.mddi.gov.sg/newsroom/opening-by-sms-janil-puthucheary-at-atxsummit-digital-sustainability-forum/',
         'note': 'Secondary reports (Eco-Business) put 2024 at ~6.5 TWh, roughly 11% of ~58 TWh national use: UNVERIFIED.', 'verified': True},
        {'country': 'Denmark', 'iso2': 'DK', 'year': None, 'dc_share_pct': 7,
         'basis': 'Industry association claim (Danish Data Center Industry, DDI), year not stated; no official realized figure found (Eurostat has no Danish DC data)',
         'source': 'DDI report (industry/advocacy) via search snippet; Danish Energy Agency AF25 projects 6.0 TWh in 2030, 26.8 TWh in 2040',
         'source_url': 'https://www.danskindustri.dk/globalassets/brancher/di-digital/ddi-rapport-final.pdf',
         'official_projection': {'source': 'Energistyrelsen, Analyseforudsaetninger til Energinet 2025 - Datacentre (Nov 2025)', 'url': 'https://ens.dk/media/7603/download',
                                 'twh': {'2030': 6.0, '2040': 26.8, '2050': 35.9}, 'capacity_utilisation_2023_pct': 60, 'verified': True},
         'verified': False},
        {'country': 'United States', 'iso2': 'US', 'year': 2024, 'dc_twh': 192, 'dc_share_pct': 4.7,
         'basis': 'LBNL bottom-up model (excludes crypto). EPRI 2026: 177-192 TWh incl. crypto, 4-5%.',
         'source': 'LBNL, US Data Center Energy Usage Report: 2025 Update (June 2026)', 'source_url': 'https://doi.org/10.71468/P1RP4F', 'verified': True},
        {'country': 'United States - Virginia', 'iso2': 'US-VA', 'year': 2023, 'dc_twh': 33.85, 'dc_share_pct': 25.59,
         'basis': 'EPRI state estimate; Dominion reports data centers = 28% of Virginia Power sales in 2025',
         'source': 'EPRI Powering Intelligence (2024), Table A1; Dominion 2025 10-K', 'source_url': 'https://www.epri.com/research/products/000000003002028905', 'verified': True},
        {'country': 'World', 'iso2': None, 'year': 2025, 'dc_growth_pct': 20,
         'basis': 'IEA: "data centre electricity demand grew by almost 20% in 2025"',
         'source': 'IEA, Key questions on energy and AI (slides, 11 June 2026, hosted by ADB Asia Clean Energy Forum)',
         'source_url': 'https://asiacleanenergyforum.adb.org/wp-content/uploads/2026/06/Key-questions-on-energy-and-AI.pdf',
         'note': 'IEA Energy and AI (Apr 2025) global ~415 TWh in 2024 (~1.5% of world electricity), US ~45% of it; 2025 ~485 TWh per IEA update: UNVERIFIED (iea.org blocked automated access).',
         'verified': True},
    ],
}


def main():
    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(COLS)
        for r in DISC:
            w.writerow(r)
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(INTL, f, indent=2, ensure_ascii=False)
    print('wrote', OUT_CSV, len(DISC), 'rows;', OUT_JSON, len(INTL['points']), 'points')


if __name__ == '__main__':
    main()
