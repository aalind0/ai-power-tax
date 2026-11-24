"""Write data/processed/bills_ba_codes.csv: EIA balancing-authority codes used in bills_utility_prices.csv (ba_code) with names,
states and the RTO/ISO mapping used. Source: EIA-861 Balancing_Authority_2025.xlsx. Run: python3 -I scripts/bills/build_ba_codes.py"""
import os
import pandas as pd
ROOT = os.getcwd()
f = os.path.join(ROOT, 'data/raw/bills/eia861_2025/extracted/Balancing_Authority_2025.xlsx')
d = pd.read_excel(f, engine='openpyxl', header=0)
d.columns = ['year', 'ba_id', 'ba_code', 'state', 'ba_name']
RTO = {'PJM': 'PJM', 'MISO': 'MISO', 'ERCO': 'ERCOT', 'SWPP': 'SPP', 'CISO': 'CAISO', 'NYIS': 'NYISO', 'ISNE': 'ISO-NE'}
g = d.groupby(['ba_code', 'ba_id', 'ba_name'])['state'].agg(lambda s: ';'.join(sorted(set(s)))).reset_index().rename(columns={'state': 'states'})
g['rto_iso'] = g['ba_code'].map(RTO).fillna('none')
u = pd.read_csv(os.path.join(ROOT, 'data/processed/bills_utility_prices.csv'), usecols=['year', 'ba_code', 'res_customers'])
used = u[u.year == 2025].assign(ba_code=u['ba_code'].astype(str).str.split(';')).explode('ba_code').groupby('ba_code')['res_customers'].sum()
g['res_customers_2025_bundled'] = g['ba_code'].map(used)
g.sort_values('ba_code').to_csv(os.path.join(ROOT, 'data/processed/bills_ba_codes.csv'), index=False)
print('wrote bills_ba_codes.csv', len(g))
