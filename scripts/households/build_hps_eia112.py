"""Build two intermediate tables used in data/processed/households_arrears_shutoffs.json:

1. Census Household Pulse Survey (HPS) Phase 4.2 Cycle 09 (Aug 20 - Sep 16, 2024; the final HPS cycle),
   Housing Table 4 "Household Energy Use and Spending in the last 12 Months", one sheet per state.
   Share of adults (18+) whose household, in the last 12 months, was unable to pay an energy bill
   (in full) in at least one month; reduced/forwent necessities to pay an energy bill; kept the home at
   an unsafe temperature. Denominator excludes "Did not report". Also for household income < $50k.
   -> data/processed/households_hps_energy_insecurity_state.csv

2. EIA Form EIA-112 Residential Utility Disconnections Survey, reporting year 2024 (released Apr 14, 2026):
   utility-level and state-level electric final notices, disconnections, reconnections, avg customers.
   -> data/processed/households_eia112_disconnections_2024.csv (utility rows + 'State Total'/'State Adjustment')
   EIA-112 has no utility id; eia_utility_id is matched by normalized name+state against
   data/processed/geo_eia861_utilities.csv (geo area), then by name only within the same state's bills file.

Run: python3 -I scripts/households/build_hps_eia112.py
"""
import json
import os
import re

import openpyxl

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
RAW = os.path.join(ROOT, 'data', 'raw', 'households')


def num(x):
    if x is None or x == '-' or x == '':
        return 0.0
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


# ---------------- HPS ----------------
wb = openpyxl.load_workbook(os.path.join(RAW, 'census_hps_c09', 'housing4_cycle09.xlsx'), read_only=True)
LOWINC = ('Less than $25,000', '$25,000 - $34,999', '$35,000 - $49,999')
# column blocks: 1 total; 2-6 reduced necessities; 7-11 unsafe temp; 12-16 unable to pay
BLOCKS = {'forwent_necessities': 2, 'unsafe_temperature': 7, 'unable_to_pay': 12}


def shares(rows):
    out = {}
    for k, s in BLOCKS.items():
        every, some, one_two, never, nr = [sum(num(r[s + i]) for r in rows) for i in range(5)]
        resp = every + some + one_two + never
        out[k + '_pct'] = round(100 * (every + some + one_two) / resp, 1) if resp else None
        out[k + '_almost_every_month_pct'] = round(100 * every / resp, 1) if resp else None
    out['adults_responding'] = int(sum(num(r[12 + i]) for r in rows for i in range(4)))
    return out


hps = {}
for name in wb.sheetnames:
    if len(name) != 2:
        continue  # skip metro sheets
    rows = list(wb[name].iter_rows(values_only=True))
    total = [r for r in rows if r[0] and str(r[0]).strip() == 'Total']
    low = [r for r in rows if r[0] and str(r[0]).strip() in LOWINC]
    rec = shares(total[:1])
    lo = shares(low)
    rec.update({'lt50k_' + k: v for k, v in lo.items()})
    hps[name] = rec
import csv
PROC = os.path.join(ROOT, 'data', 'processed')
cols = ['state', 'unable_to_pay_pct', 'unable_to_pay_almost_every_month_pct', 'forwent_necessities_pct',
        'forwent_necessities_almost_every_month_pct', 'unsafe_temperature_pct', 'unsafe_temperature_almost_every_month_pct',
        'adults_responding', 'lt50k_unable_to_pay_pct', 'lt50k_forwent_necessities_pct', 'lt50k_unsafe_temperature_pct',
        'lt50k_adults_responding']
with open(os.path.join(PROC, 'households_hps_energy_insecurity_state.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(cols + ['survey', 'period', 'unit'])
    for st in sorted(hps, key=lambda x: (x != 'US', x)):
        w.writerow([st] + [hps[st].get(c) for c in cols[1:]] +
                   ['Census Household Pulse Survey Phase 4.2 Cycle 09, Housing Table 4', '2024-08-20/2024-09-16 (last 12 months)',
                    'adults 18+ (household-level question)'])
print('HPS states', len(hps), 'US unable_to_pay', hps['US']['unable_to_pay_pct'], 'lt50k', hps['US']['lt50k_unable_to_pay_pct'])

# ---------------- EIA-112 ----------------
wb = openpyxl.load_workbook(os.path.join(RAW, 'eia112_2024', '112_electric_utility_level_data_2024.xlsx'), read_only=True)
sheets = {'final_notices': 'Final notices', 'disconnections': 'Disconnections', 'reconnections': 'Reconnections',
          'customers': 'Number of customers'}
data = {}
for key, sh in sheets.items():
    for r in wb[sh].iter_rows(values_only=True):
        if not r or not r[0] or not r[1] or str(r[0]).startswith('State abbreviation'):
            continue
        st = str(r[0]).strip()
        if not re.fullmatch(r'[A-Z]{2}', st):
            continue
        months = [num(x) if x is not None else None for x in r[2:14]]
        name = str(r[1]).strip()
        d = data.setdefault((st, name), {})
        vals = [m for m in months if m is not None]
        d[key + '_months_reported'] = len(vals)
        if key == 'customers':
            d['avg_customers'] = round(sum(vals) / len(vals)) if vals else None
        else:
            d[key] = int(sum(vals)) if vals else None
        d[key + '_monthly'] = months

rows = []
for (st, name), d in data.items():
    disc, cust = d.get('disconnections'), d.get('avg_customers')
    rows.append({
        'state': st, 'utility_name': name,
        'final_notices': d.get('final_notices'), 'disconnections': disc, 'reconnections': d.get('reconnections'),
        'avg_residential_customers': cust,
        'disconnections_per_100_customers': round(100 * disc / cust, 2) if disc is not None and cust else None,
        'months_reported': d.get('disconnections_months_reported'),
        'disconnections_monthly': d.get('disconnections_monthly'),
    })
def norm(x):
    x = x.lower().replace('&', ' and ')
    x = re.sub(r'\(.*?\)', ' ', x)
    x = re.sub(r'[^a-z0-9 ]', ' ', x)
    x = re.sub(r'\b(inc|llc|co|corp|corporation|company|the|of|dba)\b', ' ', x)
    return re.sub(r'\s+', ' ', x).strip()


lk_state, lk_name = {}, {}
with open(os.path.join(PROC, 'geo_eia861_utilities.csv'), newline='') as f:
    for r in csv.DictReader(f):
        lk_state.setdefault((r['state'], norm(r['utility_name'])), r['eia_utility_id'])
        lk_name.setdefault(norm(r['utility_name']), set()).add(r['eia_utility_id'])
with open(os.path.join(PROC, 'bills_utility_prices.csv'), newline='') as f:
    for r in csv.DictReader(f):
        lk_state.setdefault((r['state'], norm(r['utility_name'])), r['eia_utility_id'])
        lk_name.setdefault(norm(r['utility_name']), set()).add(r['eia_utility_id'])
matched = 0
for r in rows:
    if r['utility_name'] in ('State Total', 'State Adjustment'):
        r['eia_utility_id'], r['id_match'] = None, 'n/a'
        continue
    n = norm(r['utility_name'])
    uid = lk_state.get((r['state'], n))
    how = 'name+state'
    if uid is None and len(lk_name.get(n, ())) == 1:
        uid, how = next(iter(lk_name[n])), 'name_only'
    r['eia_utility_id'], r['id_match'] = uid, (how if uid else 'unmatched')
    matched += uid is not None
cols = ['state', 'utility_name', 'eia_utility_id', 'id_match', 'final_notices', 'disconnections', 'reconnections',
        'avg_residential_customers', 'disconnections_per_100_customers', 'months_reported']
with open(os.path.join(PROC, 'households_eia112_disconnections_2024.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(cols + ['year'])
    for r in sorted(rows, key=lambda r: (r['state'], r['utility_name'] in ('State Total', 'State Adjustment'), r['utility_name'])):
        w.writerow([r[c] for c in cols] + [2024])
print('matched ids', matched, 'of', sum(1 for r in rows if r['utility_name'] not in ('State Total', 'State Adjustment')))
names = sorted(set(r['utility_name'] for r in rows if r['utility_name'].lower().startswith(('state', 'total'))))
print('EIA-112 rows', len(rows), 'special names:', names[:10])
