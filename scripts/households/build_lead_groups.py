"""National (50 states + DC, excl. PR) energy burden by income group, tenure and heating fuel from DOE LEAD 2022.
Same ratio-of-averages definition as build_lead_county.py.
Output: data/processed/households_burden_national_by_group.csv
Run: python3 -I scripts/households/build_lead_groups.py
"""
import glob
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'data', 'raw', 'households', 'lead2022_ami_counties_all')
SUMS = ['UNITS', 'HINCP*UNITS', 'ELEP*UNITS', 'GASP*UNITS', 'FULP*UNITS', 'HINCP UNITS', 'ELEP UNITS', 'GASP UNITS', 'FULP UNITS']
parts = []
for f in sorted(glob.glob(os.path.join(SRC, '*', '*_AMI_Counties_2022.csv'))):
    if os.path.basename(f).startswith('PR'):
        continue
    df = pd.read_csv(f, usecols=['AMI150', 'TEN', 'TEN-HFL'] + SUMS)
    for c in SUMS:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
    df['HFL'] = df['TEN-HFL'].str.replace(r'^(OWNER|RENTER) ', '', regex=True)
    parts.append(df.groupby(['AMI150', 'TEN', 'HFL'])[SUMS].sum().reset_index())
a = pd.concat(parts).groupby(['AMI150', 'TEN', 'HFL'])[SUMS].sum().reset_index()


def row(kind, label, g):
    inc = g['HINCP*UNITS'].sum() / g['HINCP UNITS'].sum()
    ele = g['ELEP*UNITS'].sum() / g['ELEP UNITS'].sum()
    gas = g['GASP*UNITS'].sum() / g['GASP UNITS'].sum()
    oth = g['FULP*UNITS'].sum() / g['FULP UNITS'].sum()
    return {'group_type': kind, 'group': label, 'households': round(g['UNITS'].sum()),
            'avg_household_income_usd': round(inc), 'avg_annual_elec_cost_usd': round(ele),
            'avg_annual_energy_cost_usd': round(ele + gas + oth),
            'energy_burden_pct': round(100 * (ele + gas + oth) / inc, 2), 'elec_burden_pct': round(100 * ele / inc, 2)}


rows = [row('all', 'All households', a)]
for b in ['0-30%', '30-60%', '60-80%', '80-100%', '100-150%', '150%+']:
    rows.append(row('ami_bin', b + ' AMI', a[a['AMI150'] == b]))
rows.append(row('ami_group', '<=80% AMI (low income)', a[a['AMI150'].isin(['0-30%', '30-60%', '60-80%'])]))
rows.append(row('ami_group', '>80% AMI', a[~a['AMI150'].isin(['0-30%', '30-60%', '60-80%'])]))
for t, lab in [('OWN', 'Owners'), ('REN', 'Renters')]:
    rows.append(row('tenure', lab, a[a['TEN'] == t]))
    rows.append(row('tenure_low_income', lab + ' <=80% AMI', a[(a['TEN'] == t) & a['AMI150'].isin(['0-30%', '30-60%', '60-80%'])]))
for h in ['ELECTRICITY', 'UTILITY GAS', 'BOTTLED GAS', 'FUEL OIL']:
    rows.append(row('heating_fuel', h.title(), a[a['HFL'] == h]))
    rows.append(row('heating_fuel_low_income', h.title() + ' <=80% AMI', a[(a['HFL'] == h) & a['AMI150'].isin(['0-30%', '30-60%', '60-80%'])]))
out = pd.DataFrame(rows)
out['source'] = 'DOE LEAD Tool 2022 update (ACS 2018-2022 5-yr PUMS calibrated to 2022 EIA-861/176), 50 states + DC'
out.to_csv(os.path.join(ROOT, 'data', 'processed', 'households_burden_national_by_group.csv'), index=False)
pd.set_option('display.width', 200)
print(out.drop(columns='source').to_string())
