"""Build data/processed/bills_state_monthly.csv from EIA-861M sales_revenue.xlsx (state x month, all sectors).

Run from project root: python3 -I scripts/bills/build_state_monthly.py
Inputs : data/raw/bills/eia861m_sales_revenue/sales_revenue.xlsx  (EIA-861M, 'Monthly-States' sheet, 1990-latest)
         data/processed/bills_cpi_monthly.csv                     (BLS CPI-U all items + electricity CPI)
Output : data/processed/bills_state_monthly.csv  Jan 2015 -> latest month; 50 states + DC + US total.
US = sum of states + DC revenue / sales (EIA's own US figure is computed the same way).
"""
import os

import numpy as np
import pandas as pd

ROOT = os.getcwd()
SRC = os.path.join(ROOT, 'data/raw/bills/eia861m_sales_revenue/sales_revenue.xlsx')
OUT = os.path.join(ROOT, 'data/processed/bills_state_monthly.csv')
START = '2015-01'

hdr = pd.read_excel(SRC, engine='openpyxl', sheet_name='Monthly-States', header=None, nrows=3)
df = pd.read_excel(SRC, engine='openpyxl', sheet_name='Monthly-States', header=None, skiprows=3)
lead = [str(v).strip() for v in hdr.iloc[2].tolist()]
names = []
k = 0
SEC = ['res', 'com', 'ind', 'trans', 'tot']
MET = ['revenue_thousand_usd', 'sales_mwh', 'customers', 'price_cents_kwh']
for h in lead:
    hl = h.lower()
    if hl == 'year':
        names.append('year')
    elif hl == 'month':
        names.append('month')
    elif hl == 'state':
        names.append('state')
    elif hl.startswith('data status'):
        names.append('data_status')
    else:
        names.append(f'{SEC[k // 4]}_{MET[k % 4]}')
        k += 1
assert k == 20, lead
df.columns = names
df = df[pd.to_numeric(df['year'], errors='coerce').notna()].copy()
df['year'] = df['year'].astype(int)
df['month'] = df['month'].astype(int)
for c in names[4:]:
    df[c] = pd.to_numeric(df[c].replace('.', np.nan), errors='coerce')
df['date'] = df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2)
df = df[df['date'] >= START]
assert 'US' not in set(df['state']), 'unexpected US row'

# US total = sum over states (+DC)
sums = df.groupby(['date', 'year', 'month'])[[c for c in names if c.endswith(('revenue_thousand_usd', 'sales_mwh', 'customers'))]].sum().reset_index()
for s in SEC:
    sums[f'{s}_price_cents_kwh'] = sums[f'{s}_revenue_thousand_usd'] / sums[f'{s}_sales_mwh'] * 100
sums['state'] = 'US'
sums['data_status'] = df.groupby('date')['data_status'].agg(lambda x: 'Preliminary' if (x == 'Preliminary').any() else x.iloc[0]).values
df = pd.concat([df, sums], ignore_index=True, sort=False)

cpi = pd.read_csv(os.path.join(ROOT, 'data/processed/bills_cpi_monthly.csv'))
df = df.merge(cpi[['date', 'cpi_u_all_items_nsa', 'cpi_u_electricity_nsa']], on='date', how='left')
# Oct 2025 CPI was never published (shutdown): fill CPI-U by linear interpolation for deflation only, flag it
cpi_i = cpi.set_index('date')['cpi_u_all_items_nsa'].interpolate()
df['cpi_u_all_items_interpolated'] = df['cpi_u_all_items_nsa'].isna() & df['date'].isin(cpi_i.index)
df['cpi_for_deflation'] = df['date'].map(cpi_i)
latest_cpi_date = cpi.dropna(subset=['cpi_u_all_items_nsa'])['date'].max()
base_date = df['date'].max() if df['date'].max() <= latest_cpi_date else latest_cpi_date
base_cpi = cpi_i[base_date]

df['res_avg_monthly_kwh'] = df['res_sales_mwh'] * 1000 / df['res_customers']
df['res_avg_monthly_bill_usd'] = df['res_revenue_thousand_usd'] * 1000 / df['res_customers']
df['res_price_real_cents_kwh'] = df['res_price_cents_kwh'] * base_cpi / df['cpi_for_deflation']
df['real_dollar_base'] = base_date
df = df.sort_values(['state', 'date'])
g = df.groupby('state')
df['res_price_yoy_pct'] = (df['res_price_cents_kwh'] / g['res_price_cents_kwh'].shift(12) - 1) * 100
df['res_price_12m_avg_cents_kwh'] = g['res_price_cents_kwh'].transform(lambda s: s.rolling(12).mean())
# 12-month trailing revenue/sales price (removes seasonality better than averaging monthly prices)
rev12 = g['res_revenue_thousand_usd'].transform(lambda s: s.rolling(12).sum())
mwh12 = g['res_sales_mwh'].transform(lambda s: s.rolling(12).sum())
df['res_price_ttm_cents_kwh'] = rev12 / mwh12 * 100
df['res_price_ttm_yoy_pct'] = (df['res_price_ttm_cents_kwh'] / df.groupby('state')['res_price_ttm_cents_kwh'].shift(12) - 1) * 100
df['cpi_u_all_items_yoy_pct'] = (df['cpi_for_deflation'] / df.groupby('state')['cpi_for_deflation'].shift(12) - 1) * 100

cols = ['date', 'year', 'month', 'state', 'data_status',
        'res_price_cents_kwh', 'res_price_yoy_pct', 'res_price_ttm_cents_kwh', 'res_price_ttm_yoy_pct', 'res_price_real_cents_kwh', 'real_dollar_base',
        'res_revenue_thousand_usd', 'res_sales_mwh', 'res_customers', 'res_avg_monthly_kwh', 'res_avg_monthly_bill_usd',
        'com_price_cents_kwh', 'ind_price_cents_kwh', 'tot_price_cents_kwh',
        'com_sales_mwh', 'ind_sales_mwh', 'tot_sales_mwh',
        'cpi_u_all_items_nsa', 'cpi_u_electricity_nsa', 'cpi_u_all_items_yoy_pct', 'cpi_u_all_items_interpolated']
out = df[cols].round({**{c: 3 for c in cols if c.endswith(('_kwh', '_pct', '_usd'))}, **{c: 1 for c in cols if c.endswith(('_thousand_usd', '_mwh'))}})
out.to_csv(OUT, index=False)
print('wrote', OUT, len(out), 'rows', out['date'].min(), '->', out['date'].max(), 'states', out['state'].nunique(), 'real base', base_date)
