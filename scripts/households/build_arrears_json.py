"""Build data/processed/households_arrears_shutoffs.json.

Combines (a) curated figures read this session from NEADA, LIHEAP Clearinghouse, EIA, EPI, Utility Dive documents
(downloaded under data/raw/households/...), and (b) computed tables from:
  data/processed/households_eia112_disconnections_2024.csv
  data/processed/households_hps_energy_insecurity_state.csv
Run after build_hps_eia112.py:  python3 -I scripts/households/build_arrears_json.py
"""
import csv
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'data', 'processed')

NEADA = 'https://neada.org/'
neada_series = [
    {"as_of": "2020-12-31", "total_arrears_usd_bn": 20.2, "households_in_arrears_m": 23.0, "avg_arrears_usd": 879,
     "source_title": "NEADA Arrearage and Moratorium Update, 1/20/22", "url": "https://neada.org/wp-content/uploads/2022/01/arrearagesjan2022.pdf",
     "method_note": "NEADA national projection from selected state data (electric + gas).", "verified": True},
    {"as_of": "2021-12-31", "total_arrears_usd_bn": 22.3, "households_in_arrears_m": 21.0, "avg_arrears_usd": 1060,
     "source_title": "NEADA Arrearage and Moratorium Update, 1/20/22", "url": "https://neada.org/wp-content/uploads/2022/01/arrearagesjan2022.pdf",
     "method_note": "Same method as 2020 point.", "verified": True},
    {"as_of": "2022-01-31", "total_arrears_usd_bn": 15.9, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA press release: End of Winter Energy Update (2023-04-17)", "url": "https://neada.org/press-release-neada-releases-end-of-winter-energy-update/",
     "method_note": "Later NEADA series; not comparable with the $22.3B Dec-2021 projection above (different method/sample). Feb-2026 NEADA report gives $15.4B for Jan 2022 in the same later series.", "verified": True},
    {"as_of": "2023-01-31", "total_arrears_usd_bn": 17.8, "households_in_arrears_m": 20.5, "avg_arrears_usd": None,
     "source_title": "NEADA press release: End of Winter Energy Update (2023-04-17)", "url": "https://neada.org/press-release-neada-releases-end-of-winter-energy-update/",
     "method_note": "20.5M households behind on ELECTRIC bills (19.0M a year earlier); ~13M behind on gas. NEADA Jan-2024 release restates Jan 2023 as $17.7B.", "verified": True},
    {"as_of": "2023-03-31", "total_arrears_usd_bn": 19.5, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA: Utility Arrearages Rise After Winter Shutoff Moratoriums End (2023-05-24)", "url": "https://neada.org/wp-content/uploads/2023/05/arrearagesmay2023.pdf",
     "method_note": "", "verified": True},
    {"as_of": "2023-12-31", "total_arrears_usd_bn": 20.3, "households_in_arrears_m": 21.2, "avg_arrears_usd": None,
     "source_title": "NEADA press release 01/23/2024 (States Call for Congress to Restore Funding for LIHEAP)", "url": "https://neada.org/wp-content/uploads/2024/01/pr-recordhhbehind.pdf",
     "method_note": "16% of U.S. households behind. CONFLICT: NEADA's Aug-2024 release says debt rose 8.4% 'since December 2023' to $17.4B, which implies ~$16.0B at Dec 2023, not $20.3B. Treat levels as NEADA estimates with method changes.", "verified": True},
    {"as_of": "2024-06 (approx; NEADA Q3 2024 report)", "total_arrears_usd_bn": 17.4, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA press release: As LIHEAP Funding Runs Dry, Utility Debt Increases by 8.4% to $17.4 Billion (embargoed to 2024-08-28)",
     "url": "https://neada.org/wp-content/uploads/2024/08/August-Arrearages-Press-Release-8.26.24.pdf",
     "method_note": "Spread across 17.4M electric and 11M gas households (overlapping). Exact as-of month not stated.", "verified": True},
    {"as_of": "2025-03-31", "total_arrears_usd_bn": 21.4, "households_in_arrears_m": 21.5, "avg_arrears_usd": None,
     "source_title": "NEADA Energy Hardship Report, February 2026 (slide 11)", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx",
     "method_note": "'Outstanding utility debt jumped from $15.4 billion in January 2022 to $21.4 billion at the end of March 2025'; 21.5M households (~1 in 6) behind (household count as of the Feb-2026 report).", "verified": True},
    {"as_of": "2025-12 (NEADA estimate)", "total_arrears_usd_bn": 23.0, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA: Winter Heating Costs Expected to Jump 9.2% (2025-12-16)", "url": "https://neada.org/wp-content/uploads/2025/12/winterheatingdec25PR.pdf",
     "method_note": "'one in six U.S. households is already behind on energy bills, owing utilities a combined $23 billion'.", "verified": True},
    {"as_of": "2026-03/04 (NEADA estimate)", "total_arrears_usd_bn": 25.0, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA: President's FY2027 Budget Eliminates Federal Funding for LIHEAP (2026-04-03); NEADA letter to HHS (2026-03-20)",
     "url": "https://neada.org/wp-content/uploads/2026/04/PresidentBudget2027Response.pdf",
     "method_note": "'approximately $25 billion—the highest level since 2021 and a 30 percent increase since the end of 2023'. NEADA's June-2026 update instead frames ~$25B as a projection for end-2026.", "verified": True},
    {"as_of": "2026-12-31 (projection)", "total_arrears_usd_bn": 25.0, "households_in_arrears_m": None, "avg_arrears_usd": None,
     "source_title": "NEADA June Price Update (2026-06-09)", "url": "https://neada.org/summer-cooling-costs-projected-to-hit-record-highs-as-household-electric-bills-rise-10-5-june-price-update/",
     "method_note": "'Total utility debt is projected to reach approximately $25 billion by the end of 2026.' Projection, not a measurement.", "verified": True},
]

liheap = [
    # LIHEAP Clearinghouse (NCAT, ACF-funded) "LIHEAP Funding for States and Territories", last updated 10/21/2026.
    {"fiscal_year": 2018, "total_released_usd": 3637316000, "notes": "Regular funds (page mislabels total as FY 2020)."},
    {"fiscal_year": 2019, "total_released_usd": None, "notes": "~$3.65B regular released 2018-10-26; total not itemised on page."},
    {"fiscal_year": 2020, "total_released_usd": 4637316000, "notes": "Includes $900M CARES Act supplemental."},
    {"fiscal_year": 2021, "total_released_usd": 8209300960, "notes": "Includes $4.5B American Rescue Plan supplemental."},
    {"fiscal_year": 2022, "total_released_usd": 3876220260, "notes": "Includes $99.5M IIJA."},
    {"fiscal_year": 2023, "total_released_usd": 6090400000, "notes": "Includes $1B supplemental (CR) + $1B Consolidated Appropriations Act 2023 + IIJA $100M."},
    {"fiscal_year": 2024, "total_released_usd": 4115400000, "notes": "Regular + IIJA $100M; ~$2B lower than FY2023."},
    {"fiscal_year": 2025, "total_released_usd": 4115508197, "notes": "Full-year CR; final $401.5M released 2025-05-01 (after the April 2025 staff layoff)."},
    {"fiscal_year": 2026, "total_released_usd": 4130596037, "notes": "$3.714B released 2025-11-28 after the Oct 1-Nov 12 2025 shutdown; final $421.5M on 2026-04-17 under the Consolidated Appropriations Act, 2026 (H.R. 7148)."},
    {"fiscal_year": 2027, "total_released_usd": 3631860000, "notes": "PARTIAL: released 2026-10-09 under the Continuing Appropriations and Extensions Act, 2027 (H.R. 6500). Full-year level not yet set."},
]
for r in liheap:
    r.update({"scope": "states and territories (excludes tribal grants)", "source_url": "https://liheapch.ncat.org/node/62", "verified": True})

liheap_events = [
    {"date": "2025-04", "event": "HHS reduction in force removed the federal LIHEAP program staff (~two dozen people).",
     "source": "Utility Dive, 2026-02-04", "url": "https://www.utilitydive.com/news/federal-energy-assistance-programs-survive-budget-gauntlet/811389/", "verified": True},
    {"date": "2025-05-02", "event": "President's FY2026 budget proposed $0 for LIHEAP (eliminating ~$4B serving ~6M households); rationale: state shutoff protections make it 'unnecessary'.",
     "source": "NEADA; Utility Dive", "url": "https://neada.org/wp-content/uploads/2025/05/Presidents-FY-26-Budget-LIHEAP-1-1.pdf", "verified": True},
    {"date": "2025-10-01/2025-11-12", "event": "Federal shutdown delayed release of FY2026 LIHEAP funds; NEADA asked utilities to suspend shutoffs (2025-10-21). Some states (e.g., PA) delayed program start.",
     "source": "NEADA; PBS/AP", "url": "https://neada.org/wp-content/uploads/2025/10/PRshutdownshutoffs.pdf", "verified": True},
    {"date": "2025-11-28", "event": "$3.71B of FY2026 LIHEAP block grant released.", "source": "LIHEAP Clearinghouse", "url": "https://liheapch.ncat.org/node/62", "verified": True},
    {"date": "2026-02-03", "event": "Consolidated Appropriations Act, 2026 signed; LIHEAP funded at about $4.05B for FY2026 (slight increase over FY2025).",
     "source": "Utility Dive, 2026-02-04", "url": "https://www.utilitydive.com/news/federal-energy-assistance-programs-survive-budget-gauntlet/811389/", "verified": True},
    {"date": "2026-04-03", "event": "President's FY2027 budget again proposes eliminating LIHEAP (~$4B, ~6M households).",
     "source": "NEADA", "url": "https://neada.org/wp-content/uploads/2026/04/PresidentBudget2027Response.pdf", "verified": True},
    {"date": "2026-04-16", "event": "NEADA asks Congress for $7B in FY2027 ($6B base + $1B contingency); says funds reach ~1 in 5 eligible households.",
     "source": "NEADA testimony", "url": "https://neada.org/wp-content/uploads/2026/07/housetestimonyFY27.pdf", "verified": True},
    {"date": "2026-07-23", "event": "NEADA asks for a $3.0B emergency anomaly in the FY2027 CR as crude reaches $100/bbl (Iran war) and heating oil spikes.",
     "source": "NEADA", "url": "https://neada.org/neada-increases-emergency-liheap-funding-request-to-3-billion-as-crude-oil-reaches-100-per-barrel/", "verified": True},
    {"date": "2026-10-09", "event": "$3.63B of FY2027 funds released under a CR.", "source": "LIHEAP Clearinghouse", "url": "https://liheapch.ncat.org/node/62", "verified": True},
]
liheap_households_served = [
    {"fiscal_year": 2022, "households_m": 5.8, "source": "NEADA press release 2024-01-23", "url": "https://neada.org/wp-content/uploads/2024/01/pr-recordhhbehind.pdf", "verified": True},
    {"fiscal_year": 2023, "households_m": 7.3, "source": "NEADA press release 2024-01-23 (record; table total 7.2M est.)", "url": "https://neada.org/wp-content/uploads/2024/01/pr-recordhhbehind.pdf", "verified": True},
    {"fiscal_year": 2024, "households_m": 6.0, "source": "Utility Dive 2026-02-04 ('about 6 million households in 2024')", "url": "https://www.utilitydive.com/news/federal-energy-assistance-programs-survive-budget-gauntlet/811389/", "verified": True},
]

# ---------------- EIA-112 ----------------
rows = list(csv.DictReader(open(os.path.join(P, 'households_eia112_disconnections_2024.csv'))))


def f(x):
    return float(x) if x not in ('', None) else None


state_tot = [r for r in rows if r['utility_name'] == 'State Total']
util = [r for r in rows if r['utility_name'] not in ('State Total', 'State Adjustment')]
nat_disc = sum(f(r['disconnections']) or 0 for r in state_tot)
nat_fin = sum(f(r['final_notices']) or 0 for r in state_tot)
nat_rec = sum(f(r['reconnections']) or 0 for r in state_tot)
nat_cust = sum(f(r['avg_residential_customers']) or 0 for r in state_tot)
by_rate = sorted([r for r in state_tot if f(r['disconnections_per_100_customers']) is not None],
                 key=lambda r: -f(r['disconnections_per_100_customers']))
big = [r for r in util if (f(r['avg_residential_customers']) or 0) >= 100000 and f(r['disconnections_per_100_customers']) is not None]
HOT = {('VA', 'Virginia Electric & Power Co'): 'Dominion Energy Virginia (Northern Virginia data-center alley)',
       ('VA', 'Northern Virginia Elec Coop'): 'NOVEC (Loudoun/Prince William data-center co-op)',
       ('GA', 'Georgia Power Co'): 'Georgia Power (Atlanta metro data centers)',
       ('TX', 'Oncor Electric Delivery Company LLC'): 'Oncor (Dallas-Fort Worth data centers)',
       ('OH', 'Ohio Power Co'): 'AEP Ohio (Columbus/New Albany data centers)',
       ('IL', 'Commonwealth Edison Co'): 'ComEd (Chicago data centers)',
       ('NJ', 'Public Service Elec & Gas Co'): 'PSE&G (NJ; PJM capacity-price pass-through)',
       ('MD', 'Baltimore Gas & Electric Co'): 'BGE (MD; PJM capacity-price pass-through)',
       ('DC', 'Potomac Electric Power Co'): 'Pepco DC',
       ('MD', 'Potomac Electric Power Co'): 'Pepco MD',
       ('PA', 'PPL Electric Utilities Corp'): 'PPL (PA; Susquehanna/AWS campus)',
       ('LA', 'Entergy Louisiana LLC'): 'Entergy Louisiana (Meta Hyperion, Richland Parish)',
       ('NV', 'Nevada Power Co'): 'NV Energy south (Las Vegas data centers)',
       ('AZ', 'Arizona Public Service Co'): 'APS (Phoenix data centers)',
       ('AZ', 'Salt River Project'): 'SRP (Phoenix/Mesa data centers)',
       ('IN', 'Indiana Michigan Power Co'): 'Indiana Michigan Power (AEP; northern IN data centers)',
       ('IA', 'MidAmerican Energy Co'): 'MidAmerican (Council Bluffs/Des Moines data centers)'}


def urow(r, label=None):
    d = {k: r[k] for k in ('state', 'utility_name', 'eia_utility_id')}
    d.update({'disconnections': int(f(r['disconnections'])) if f(r['disconnections']) is not None else None,
              'final_notices': int(f(r['final_notices'])) if f(r['final_notices']) is not None else None,
              'avg_residential_customers': int(f(r['avg_residential_customers'])) if f(r['avg_residential_customers']) else None,
              'disconnections_per_100_customers': f(r['disconnections_per_100_customers'])})
    if label:
        d['label'] = label
    return d


eia112 = {
    "survey": "EIA Form EIA-112 Residential Utility Disconnections Survey, calendar year 2024 (first ever national collection)",
    "released": "2026-04-14 (report); utility-level files later in 2026",
    "report_url": "https://www.eia.gov/analysis/requests/residential/utility/",
    "data_url": "https://www.eia.gov/analysis/requests/residential/utility/xls/112%20electric%20utility%20level%20data%202024.xlsx",
    "unit_note": "Counts are EVENTS, not unique households: an account can receive several final notices/disconnections a year. Texas retail-choice disconnections are reported by wires utilities (Oncor, CenterPoint) on behalf of retailers.",
    "national_2024": {
        "electric_disconnections": int(nat_disc), "electric_final_notices": int(nat_fin), "electric_reconnections": int(nat_rec),
        "electric_residential_customers_avg": int(nat_cust),
        "electric_disconnections_per_100_customers": round(100 * nat_disc / nat_cust, 2),
        "gas_disconnections_report": 1.7e6, "gas_final_notices_report": 27.1e6, "gas_reconnections_report": 1.2e6,
        "response_rate_weighted_electric_pct": 93.5, "response_rate_weighted_gas_pct": 96.1,
        "peak_month_electric_disconnections": "October (1.5M)", "verified": True},
    "states_by_disconnection_rate": [urow(r) for r in by_rate],
    "top_utilities_by_count": [urow(r) for r in sorted(util, key=lambda r: -(f(r['disconnections']) or 0))[:15]],
    "top_large_utilities_by_rate_min100k_customers": [urow(r) for r in sorted(big, key=lambda r: -f(r['disconnections_per_100_customers']))[:15]],
    "data_center_hotspot_utilities": [urow(r, HOT[(r['state'], r['utility_name'])]) for r in util if (r['state'], r['utility_name']) in HOT],
    "full_table": "data/processed/households_eia112_disconnections_2024.csv",
}

epi = {
    "publisher": "Energy and Policy Institute (EPI) - advocacy/watchdog",
    "title": "New nationwide data reveals utility-specific disconnection information",
    "date": "2026-06-22",
    "url": "https://energyandpolicy.org/new-nationwide-data-reveals-utility-specific-disconnection-information/",
    "key_points": [
        "Analysis of EIA-112 2024 data: AEP's Public Service Co. of Oklahoma had the highest IOU disconnection rate (58 per 100 customers).",
        "Oncor led IOUs in total residential electric disconnections (1,241,425); FPL second (1.23M); CenterPoint Houston third (954,139); Dominion's Virginia Electric & Power fourth; PSO fifth (290,739).",
        "By ownership: municipal utilities 12.3 disconnections per 100 customers, co-ops 7.8, investor-owned 6.3. Large munis (>100k customers) 16.4; South Kentucky RECC highest of all (~86 per 100).",
        "EEI and AGA opposed the federal survey as unnecessary and burdensome.",
    ],
    "dashboard_note": "EPI's Utility Disconnections Dashboard and Indiana University Energy Justice Lab's dashboard (energyjustice.indiana.edu/disconnection-dashboard) were not downloaded: IU site failed TLS verification from this environment; EIA-112 is used as the primary national source instead.",
    "verified": True,
}

hps_rows = list(csv.DictReader(open(os.path.join(P, 'households_hps_energy_insecurity_state.csv'))))
hps_us = [r for r in hps_rows if r['state'] == 'US'][0]
hps_states = sorted([r for r in hps_rows if r['state'] != 'US'], key=lambda r: -float(r['unable_to_pay_pct']))
hps = {
    "survey": "Census Household Pulse Survey, Phase 4.2 Cycle 09 (fielded 2024-08-20 to 2024-09-16), Housing Table 4",
    "note": "Final HPS cycle; the HPS ended in Sept 2024 (succeeded by the Household Trends and Outlook Pulse Survey, which does not publish these state energy tables). So 2024 is the latest state-level reading; no 2025-26 waves exist.",
    "question": "In the last 12 months, how many months was your household unable to pay an energy bill or unable to pay the full bill amount? (also: reduced/forwent basic necessities to pay an energy bill; kept home at an unsafe/unhealthy temperature)",
    "unit": "Adults 18+ living in such households; share excludes 'did not report'.",
    "url": "https://www2.census.gov/programs-surveys/demo/tables/hhp/2024/cycle09/housing4_cycle09.xlsx",
    "national": {k: (float(v) if v not in ('', None) and k != 'state' and k not in ('survey', 'period', 'unit') else v) for k, v in hps_us.items() if k not in ('survey', 'period', 'unit')},
    "trend_from_neada": {"all_unable_to_pay_pct": {"2023": 22.0, "2024": 23.4}, "lt50k_unable_to_pay_pct": {"2023": 35.5, "2024": 37.4},
                         "source": "NEADA Energy Hardship Report Feb 2026 (citing HPS)", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx", "verified": True},
    "top10_states_unable_to_pay": [{"state": r['state'], "unable_to_pay_pct": float(r['unable_to_pay_pct']), "lt50k_unable_to_pay_pct": float(r['lt50k_unable_to_pay_pct'])} for r in hps_states[:10]],
    "bottom5_states_unable_to_pay": [{"state": r['state'], "unable_to_pay_pct": float(r['unable_to_pay_pct'])} for r in hps_states[-5:]],
    "full_table": "data/processed/households_hps_energy_insecurity_state.csv",
    "verified": True,
}

neada_context = [
    {"claim": "Low-income households' average energy burden ~8.6% vs 3.0% for others", "date": "2026 (NEADA Energy Hardship Project page)", "url": "https://neada.org/?p=8468", "verified": True},
    {"claim": "Low-income energy burden 9.1% vs 2.4% for other households (3.8x)", "date": "2026-02", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx", "verified": True},
    {"claim": "BLS Consumer Expenditure Survey: lowest income quintile spent $1,705 on electricity+gas in 2025 = 9.86% of $17,291 income (9.38% in 2024); top quintile 1.25%", "date": "2026-02", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx", "verified": True, "caveat": "NEADA slide labels both years oddly; numbers as printed."},
    {"claim": "Average monthly residential electric bill rose from ~$121 (2021) to ~$156 (2025), +29%", "date": "2026-02", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx", "verified": True, "caveat": "EIA annual average (bills area: $121.01 in 2021 -> $150.68 in 2025) is lower than NEADA's $156; NEADA likely uses a monthly peak/recent figure."},
    {"claim": "NEADA-estimated utility shutoffs (households): ~3.3M (2023), ~3.5M (2024), up to 4.0M (2025)", "date": "2026-02", "url": "https://neada.org/wp-content/uploads/2026/02/energyhardshipfeb26.pptx", "verified": True, "caveat": "Far below EIA-112's 13.4M electric disconnection EVENTS in 2024: NEADA counts households from select state data; EIA counts every disconnection event."},
    {"claim": "33 states lack summer shutoff protections", "date": "2024-08", "url": "https://neada.org/wp-content/uploads/2024/08/August-Arrearages-Press-Release-8.26.24.pdf", "verified": True},
    {"claim": "Only ~17% of eligible households receive LIHEAP", "date": "2025-12", "url": "https://neada.org/wp-content/uploads/2025/12/winterheatingdec25PR.pdf", "verified": True},
    {"claim": "Winter 2025-26 average heating cost $995 (+9.2%), electric-heat homes +12.2%; later revised to $1,011 (+11%)", "date": "2025-12 / 2026-03", "url": "https://neada.org/wp-content/uploads/2025/12/winterheatingdec25PR.pdf", "verified": True},
]

out = {
    "meta": {"area": "households", "built": "2026-11-23", "script": "scripts/households/build_arrears_json.py",
             "notes": "NEADA = National Energy Assistance Directors Association (represents state LIHEAP directors; advocacy for LIHEAP funding). Its arrears numbers are estimates extrapolated from select state/utility data and its methods have changed over time; levels are not strictly comparable across releases."},
    "neada_arrears_series": neada_series,
    "eia112_disconnections_2024": eia112,
    "epi_disconnections_analysis": epi,
    "census_household_pulse_energy_insecurity": hps,
    "liheap_funding_by_fiscal_year": liheap,
    "liheap_households_served": liheap_households_served,
    "liheap_2025_2026_events": liheap_events,
    "neada_context_figures": neada_context,
}
json.dump(out, open(os.path.join(P, 'households_arrears_shutoffs.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('wrote households_arrears_shutoffs.json; national disconnections', int(nat_disc), 'rate', round(100 * nat_disc / nat_cust, 2))
print('top states by rate', [(r['state'], r['disconnections_per_100_customers']) for r in by_rate[:8]])
print('HPS top', [(r['state'], r['unable_to_pay_pct']) for r in hps_states[:6]], 'bottom', [(r['state'], r['unable_to_pay_pct']) for r in hps_states[-4:]])
