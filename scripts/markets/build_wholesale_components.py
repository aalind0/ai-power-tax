"""PJM total wholesale cost per MWh by component (IMM State of the Market, Section 1, Tables 1-9 and 1-10).
Run: python3 -I scripts/markets/build_wholesale_components.py
Output: data/processed/markets_pjm_wholesale_cost_components.csv
"""
import csv
import io
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'data', 'raw', 'markets', '_text', '2026q3-som-pjm-sec1.txt')
URL = 'https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2026/2026q3-som-pjm-sec1.pdf'
OUT = os.path.join(ROOT, 'data', 'processed', 'markets_pjm_wholesale_cost_components.csv')

t = io.open(SRC, encoding='utf-8').read()
start = t.index('Table 1-10 Total cost per MWh by category: 2001 through 2025')
block = t[start:start + 12000]
years = list(range(2001, 2026))


def row(label):
    m = re.search(r'^' + re.escape(label) + r' ((?:\(?\$[\d,.]+\)? ?){25})$', block, re.M)
    vals = re.findall(r'\(?\$[\d,.]+\)?', m.group(1))
    out = []
    for v in vals:
        neg = v.startswith('(')
        x = float(v.strip('()').replace('$', '').replace(',', ''))
        out.append(-x if neg else x)
    return out


energy = row('Energy')
capacity = row('Capacity')
trans = row('Transmission')
total = row('Total Cost ($/MWh)')
rows = []
for i, y in enumerate(years):
    rows.append({'period': str(y), 'energy_usd_mwh': energy[i], 'capacity_usd_mwh': capacity[i],
                 'transmission_usd_mwh': trans[i], 'total_usd_mwh': total[i],
                 'other_usd_mwh': round(total[i] - energy[i] - capacity[i] - trans[i], 2),
                 'notes': 'Calendar year; IMM Table 1-10 (load-weighted system average, nominal $)', 'source_url': URL})
# Jan-Sep comparison (Table 1-9) and IMM counterfactual without data-center load in capacity market
rows.append({'period': '2025 Jan-Sep', 'energy_usd_mwh': 48.47, 'capacity_usd_mwh': 10.72, 'transmission_usd_mwh': 18.32,
             'total_usd_mwh': 79.19, 'other_usd_mwh': round(79.19 - 48.47 - 10.72 - 18.32, 2),
             'notes': 'IMM Table 1-9', 'source_url': URL})
rows.append({'period': '2026 Jan-Sep', 'energy_usd_mwh': 70.89, 'capacity_usd_mwh': 19.42, 'transmission_usd_mwh': 19.16,
             'total_usd_mwh': 111.61, 'other_usd_mwh': round(111.61 - 70.89 - 19.42 - 19.16, 2),
             'notes': 'IMM Table 1-9. IMM: total would have been $101.66/MWh without data-center load in the 2025/26 and 2026/27 capacity auctions (+$9.95/MWh, +9.8%); excludes any energy or transmission effect',
             'source_url': URL})
cols = ['period', 'energy_usd_mwh', 'capacity_usd_mwh', 'transmission_usd_mwh', 'other_usd_mwh', 'total_usd_mwh', 'notes', 'source_url']
with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print('rows', len(rows))
for r in rows[-13:]:
    print(r['period'], r['energy_usd_mwh'], r['capacity_usd_mwh'], r['transmission_usd_mwh'], r['total_usd_mwh'])
