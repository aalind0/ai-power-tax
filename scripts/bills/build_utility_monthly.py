"""Build data/processed/bills_utility_monthly.csv from EIA-861M utility-level files (2024-01 -> latest month).

Run from project root: python3 -I scripts/bills/build_utility_monthly.py
Inputs : data/raw/bills/eia861m_utility_<year>/sales_ult_cust_<year>.xlsx (2024, 2025 archive; 2026 current, preliminary)
Notes  : EIA-861M utility rows are BUNDLED (full-service) sales only - verified: 2025 monthly sums for PECO, BGE,
         ComEd, PG&E equal the EIA-861 annual Part A bundled revenue to the dollar. Delivery-only (Texas TDUs,
         shopping customers) are not in this file. EIA-861M is a sample (~all large utilities); small utilities
         are folded into 'State Adjustment' rows (utility number 0), which are dropped here.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.getcwd()
OUT = os.path.join(ROOT, 'data/processed/bills_utility_monthly.csv')
COLS = ['year', 'month', 'eia_utility_id', 'utility_name', 'state', 'ownership', 'data_status']
SEC = ['res', 'com', 'ind', 'trans', 'tot']
MET = ['revenue_thousand_usd', 'sales_mwh', 'customers']
frames = []
for y in [2024, 2025, 2026]:
    f = os.path.join(ROOT, f'data/raw/bills/eia861m_utility_{y}/sales_ult_cust_{y}.xlsx')
    d = pd.read_excel(f, engine='openpyxl', sheet_name=0, header=None, skiprows=3)
    d = d.iloc[:, :22]
    d.columns = COLS + [f'{s}_{m}' for s in SEC for m in MET]
    d = d[pd.to_numeric(d['eia_utility_id'], errors='coerce').notna()].copy()
    frames.append(d)
d = pd.concat(frames, ignore_index=True)
for c in ['year', 'month', 'eia_utility_id']:
    d[c] = d[c].astype(int)
for c in [f'{s}_{m}' for s in SEC for m in MET]:
    d[c] = pd.to_numeric(d[c].replace('.', np.nan), errors='coerce')
d = d[(d['eia_utility_id'] != 0) & (d['ownership'] != 'Behind the Meter')]
d = d.groupby(COLS[:5] + ['ownership', 'data_status'], as_index=False)[[f'{s}_{m}' for s in ['res', 'com', 'ind'] for m in MET]].sum()
d['date'] = d['year'].astype(str) + '-' + d['month'].astype(str).str.zfill(2)
for s in ['res', 'com', 'ind']:
    d[f'{s}_price_cents_kwh'] = np.where(d[f'{s}_sales_mwh'] > 0, d[f'{s}_revenue_thousand_usd'] / d[f'{s}_sales_mwh'] * 100, np.nan)
d['res_avg_monthly_bill_usd'] = np.where(d['res_customers'] > 0, d['res_revenue_thousand_usd'] * 1000 / d['res_customers'], np.nan)
d['res_avg_monthly_kwh'] = np.where(d['res_customers'] > 0, d['res_sales_mwh'] * 1000 / d['res_customers'], np.nan)
d = d.sort_values(['eia_utility_id', 'state', 'date'])
cols = ['date', 'year', 'month', 'eia_utility_id', 'utility_name', 'state', 'ownership', 'data_status',
        'res_revenue_thousand_usd', 'res_sales_mwh', 'res_customers', 'res_price_cents_kwh', 'res_avg_monthly_bill_usd', 'res_avg_monthly_kwh',
        'com_price_cents_kwh', 'ind_price_cents_kwh', 'com_sales_mwh', 'ind_sales_mwh']
d = d[cols].round({'res_price_cents_kwh': 3, 'com_price_cents_kwh': 3, 'ind_price_cents_kwh': 3, 'res_avg_monthly_bill_usd': 2, 'res_avg_monthly_kwh': 1})
d.to_csv(OUT, index=False)
print('wrote', OUT, len(d), 'rows;', d['eia_utility_id'].nunique(), 'utilities;', d['date'].min(), '->', d['date'].max())
