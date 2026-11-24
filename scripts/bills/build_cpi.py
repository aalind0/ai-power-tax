"""Tidy BLS CPI JSON (from fetch_bls_cpi.mjs) into data/processed/bills_cpi_monthly.csv.
Run from project root: python3 -I scripts/bills/build_cpi.py
"""
import glob
import json
import os

import pandas as pd

ROOT = os.getcwd()
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data/raw/bills/bls_cpi_api/*.json'))):
    j = json.load(open(f))
    for s in j['Results']['series']:
        for d in s['data']:
            if not d['period'].startswith('M') or d['period'] == 'M13':
                continue
            v = pd.to_numeric(d['value'], errors='coerce')  # '-' = not published (e.g. Oct 2025 shutdown)
            rows.append({'series': s['seriesID'], 'year': int(d['year']), 'month': int(d['period'][1:]), 'value': v})
df = pd.DataFrame(rows).drop_duplicates(['series', 'year', 'month'])
w = df.pivot_table(index=['year', 'month'], columns='series', values='value', aggfunc='first').reset_index()
w = w.rename(columns={'CUUR0000SA0': 'cpi_u_all_items_nsa', 'CUUR0000SEHF01': 'cpi_u_electricity_nsa',
                      'CUSR0000SEHF01': 'cpi_u_electricity_sa'})
w.columns.name = None
w['date'] = pd.to_datetime(dict(year=w.year, month=w.month, day=1)).dt.strftime('%Y-%m')
w = w.sort_values('date')
full = pd.DataFrame({'date': [str(x) for x in pd.period_range(w.date.iloc[0], w.date.iloc[-1], freq='M')]})
print('months absent from BLS response:', sorted(set(full.date) - set(w.date)))
w = full.merge(w.drop(columns=['year', 'month']), on='date', how='left')
w['year'] = w.date.str[:4].astype(int)
w['month'] = w.date.str[5:7].astype(int)
for c in ['cpi_u_all_items_nsa', 'cpi_u_electricity_nsa']:
    w[c + '_yoy_pct'] = (w[c] / w[c].shift(12) - 1) * 100  # complete monthly grid assumed (checked below)
w = w.round(3)
out = os.path.join(ROOT, 'data/processed/bills_cpi_monthly.csv')
w[['date', 'year', 'month', 'cpi_u_all_items_nsa', 'cpi_u_electricity_nsa', 'cpi_u_electricity_sa',
   'cpi_u_all_items_nsa_yoy_pct', 'cpi_u_electricity_nsa_yoy_pct']].to_csv(out, index=False)
print('wrote', out, len(w), 'rows', w.date.min(), '->', w.date.max())
print('missing values:', w[w.isna().any(axis=1) & (w.year >= 2006)][['date', 'cpi_u_all_items_nsa', 'cpi_u_electricity_nsa']].to_string())
