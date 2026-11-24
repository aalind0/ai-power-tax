"""Aggregate DOE LEAD 2022 (AMI cohort, county files) to one row per county.

Input : data/raw/households/lead2022_ami_counties_all/<ST>/<ST>_AMI_Counties_2022.csv
        (extracted by scripts/households/lead_zip_extract.mjs; rows = county x AMI bin x tenure x
         building age x building type x heating fuel; ~800 MB for 52 files)
Output: data/processed/households_energy_burden_county.csv

Definitions (match the LEAD methodology, "energy burden = average annual housing energy costs divided by
average annual household income"):
  avg income      = sum(HINCP*UNITS) / sum(HINCP UNITS)
  avg elec cost   = sum(ELEP*UNITS)  / sum(ELEP UNITS)      (same for GASP gas, FULP other fuels)
  energy burden   = (avg elec + avg gas + avg other fuel) / avg income
  elec burden     = avg elec / avg income
  low income      = AMI150 bins 0-30%, 30-60%, 60-80%  (<= 80% of Area Median Income)
Run: python3 -I scripts/households/build_lead_county.py
"""
import glob
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'data', 'raw', 'households', 'lead2022_ami_counties_all')
OUT = os.path.join(ROOT, 'data', 'processed', 'households_energy_burden_county.csv')

SUMS = ['UNITS', 'HINCP*UNITS', 'ELEP*UNITS', 'GASP*UNITS', 'FULP*UNITS',
        'HINCP UNITS', 'ELEP UNITS', 'GASP UNITS', 'FULP UNITS']
LOW = {'0-30%', '30-60%', '60-80%'}


def metrics(g):
    inc = g['HINCP*UNITS'].sum() / g['HINCP UNITS'].sum() if g['HINCP UNITS'].sum() else float('nan')
    ele = g['ELEP*UNITS'].sum() / g['ELEP UNITS'].sum() if g['ELEP UNITS'].sum() else float('nan')
    gas = g['GASP*UNITS'].sum() / g['GASP UNITS'].sum() if g['GASP UNITS'].sum() else 0.0
    fue = g['FULP*UNITS'].sum() / g['FULP UNITS'].sum() if g['FULP UNITS'].sum() else 0.0
    tot = ele + gas + fue
    return pd.Series({
        'households': g['UNITS'].sum(),
        'avg_income': inc,
        'elec': ele,
        'energy': tot,
        'burden': 100 * tot / inc if inc else float('nan'),
        'elec_burden': 100 * ele / inc if inc else float('nan'),
    })


frames = []
files = sorted(glob.glob(os.path.join(SRC, '*', '*_AMI_Counties_2022.csv')))
for f in files:
    df = pd.read_csv(f, usecols=['ABV', 'FIP', 'NAME', 'AMI150', 'TEN'] + SUMS, dtype={'FIP': str})
    for c in SUMS:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)
    df['low'] = df['AMI150'].isin(LOW)
    keys = ['ABV', 'FIP', 'NAME']
    agg = df.groupby(keys + ['low', 'TEN'])[SUMS].sum().reset_index()
    allm = agg.groupby(keys).apply(metrics)
    lowm = agg[agg['low']].groupby(keys).apply(metrics).add_prefix('low_')
    renm = agg[agg['TEN'] == 'REN'].groupby(keys).apply(metrics)[['households']].rename(columns={'households': 'renter_households'})
    out = allm.join(lowm, how='left').join(renm, how='left').reset_index()
    frames.append(out)
    print(os.path.basename(f), len(out))

res = pd.concat(frames, ignore_index=True)
res['county_fips'] = res['FIP'].str.zfill(5)
res = pd.DataFrame({
    'county_fips': res['county_fips'],
    'county': res['NAME'],
    'state': res['ABV'],
    'avg_energy_burden_pct': res['burden'].round(2),
    'low_income_burden_pct': res['low_burden'].round(2),
    'avg_annual_elec_cost_usd': res['elec'].round(0),
    'households': res['households'].round(0).astype('int64'),
    'avg_elec_burden_pct': res['elec_burden'].round(2),
    'low_income_elec_burden_pct': res['low_elec_burden'].round(2),
    'low_income_avg_annual_elec_cost_usd': res['low_elec'].round(0),
    'avg_annual_energy_cost_usd': res['energy'].round(0),
    'avg_household_income_usd': res['avg_income'].round(0),
    'low_income_avg_annual_energy_cost_usd': res['low_energy'].round(0),
    'low_income_avg_household_income_usd': res['low_avg_income'].round(0),
    'low_income_households': res['low_households'].round(0),
    'low_income_share_pct': (100 * res['low_households'] / res['households']).round(1),
    'renter_share_pct': (100 * res['renter_households'].fillna(0) / res['households']).round(1),
})
# LEAD labels 09120 "Hartford County"; in the 2022 Census geography it is the Greater Bridgeport Planning Region
res.loc[res['county_fips'] == '09120', 'county'] = 'Greater Bridgeport Planning Region'
# Flag likely calibration artifacts: county electricity spend > 2x its state's household-weighted mean
w = res['households']
state_mean = (res['avg_annual_elec_cost_usd'] * w).groupby(res['state']).sum() / w.groupby(res['state']).sum()
ratio = res['avg_annual_elec_cost_usd'] / res['state'].map(state_mean)
res['elec_cost_vs_state_mean'] = ratio.round(2)
res['quality_flag'] = ''
res.loc[ratio > 2.0, 'quality_flag'] = 'elec_cost_gt_2x_state_mean'
res.loc[res['households'] < 1000, 'quality_flag'] = (res['quality_flag'] + ';small_county_lt_1000_hh').str.strip(';')
# Rough 2025 update of electricity spend (ESTIMATE, not LEAD): scale the LEAD 2022-calibrated county figure by the
# state's change in EIA average residential monthly bill 2022 -> 2025 (bills area: data/processed/bills_state_annual.csv).
# Ignores changes in consumption mix within the state and income growth, so it is NOT a 2025 burden.
bills = pd.read_csv(os.path.join(ROOT, 'data', 'processed', 'bills_state_annual.csv'))
b = bills.pivot_table(index='state', columns='year', values='res_avg_monthly_bill_usd')
factor = (b[2025] / b[2022]).rename('f')
res['state_bill_change_2022_2025_pct'] = res['state'].map((100 * (factor - 1)).round(1))
res['avg_annual_elec_cost_2025_est_usd'] = (res['avg_annual_elec_cost_usd'] * res['state'].map(factor)).round(0)
res = res.sort_values('county_fips')
res.to_csv(OUT, index=False)
print('rows', len(res), '->', OUT)
