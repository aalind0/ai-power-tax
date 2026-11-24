"""Overlap of household energy burden with data-center hotspots, plus a state summary table.

Inputs (all already built):
  data/processed/households_energy_burden_county.csv          (build_lead_county.py)
  data/processed/households_hps_energy_insecurity_state.csv   (build_hps_eia112.py)
  data/processed/households_eia112_disconnections_2024.csv    (build_hps_eia112.py)
  data/raw/households/census_geocoder_campuses/campus_counties.json (geocode_campuses.mjs; compute-atlas US campuses)
Outputs:
  data/processed/households_dc_county_overlap.csv   one row per county hosting >=1 compute-atlas US campus
  data/processed/households_state_summary.csv       one row per state (burden, insecurity, shutoffs, DC campuses)
  prints summary statistics quoted in research/households/FINDINGS.md
Run: python3 -I scripts/households/build_overlap_state.py
"""
import json
import os

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
P = os.path.join(ROOT, 'data', 'processed')
county = pd.read_csv(os.path.join(P, 'households_energy_burden_county.csv'), dtype={'county_fips': str})
camp = json.load(open(os.path.join(ROOT, 'data', 'raw', 'households', 'census_geocoder_campuses', 'campus_counties.json'),
                      encoding='utf-8'))['campuses']
cdf = pd.DataFrame(camp)
ACTIVE = {'operational', 'construction', 'partial', 'planned', 'announced'}
cdf['active'] = cdf['status'].isin(ACTIVE)
cdf['mw'] = cdf['powerMW'].fillna(cdf['powerMWNow'])

g = cdf.groupby('county_fips').agg(
    dc_campuses=('id', 'count'),
    dc_campuses_active=('active', 'sum'),
    dc_power_mw_disclosed=('mw', 'sum'),
    dc_campus_ids=('id', lambda s: ';'.join(sorted(s))),
    dc_statuses=('status', lambda s: ';'.join(sorted(set(s)))),
).reset_index()
ov = county.merge(g, on='county_fips', how='inner')
cols = ['county_fips', 'county', 'state', 'dc_campuses', 'dc_campuses_active', 'dc_power_mw_disclosed', 'dc_statuses',
        'dc_campus_ids', 'households', 'avg_energy_burden_pct', 'low_income_burden_pct', 'avg_elec_burden_pct',
        'low_income_elec_burden_pct', 'avg_annual_elec_cost_usd', 'avg_annual_elec_cost_2025_est_usd',
        'avg_household_income_usd', 'low_income_share_pct', 'quality_flag']
ov = ov[cols].sort_values('low_income_burden_pct', ascending=False)
ov.to_csv(os.path.join(P, 'households_dc_county_overlap.csv'), index=False)


def wstats(df):
    hh = df['households']
    lh = df['low_income_households']
    return {
        'counties': len(df), 'households': int(hh.sum()),
        'energy_burden_pct': round((df['avg_annual_energy_cost_usd'] * hh).sum() / (df['avg_household_income_usd'] * hh).sum() * 100, 2),
        'low_income_burden_pct': round((df['low_income_avg_annual_energy_cost_usd'] * lh).sum() / (df['low_income_avg_household_income_usd'] * lh).sum() * 100, 2),
        'avg_income_usd': round((df['avg_household_income_usd'] * hh).sum() / hh.sum()),
        'avg_elec_cost_usd': round((df['avg_annual_elec_cost_usd'] * hh).sum() / hh.sum()),
        'low_income_share_pct': round(100 * lh.sum() / hh.sum(), 1),
    }


us = county[county['state'] != 'PR']
host = set(cdf.loc[cdf['active'], 'county_fips'])
print('ACTIVE DC host counties', json.dumps(wstats(us[us['county_fips'].isin(host)])))
print('Other US counties     ', json.dumps(wstats(us[~us['county_fips'].isin(host)])))
print('All US                ', json.dumps(wstats(us)))
lb = us['low_income_burden_pct']
print('counties where low-income burden >= 10%:', int((lb >= 10).sum()), 'households in them', int(us.loc[lb >= 10, 'low_income_households'].sum()))
print('DC host counties w/ low-income burden >=10%:',
      ov[(ov['low_income_burden_pct'] >= 10) & (ov['dc_campuses_active'] > 0)][['county', 'state', 'low_income_burden_pct', 'dc_campus_ids']].to_string())

# ---------------- state summary ----------------
c = us.copy()
c['cost_sum'] = c['avg_annual_energy_cost_usd'] * c['households']
c['elec_sum'] = c['avg_annual_elec_cost_usd'] * c['households']
c['elec25_sum'] = c['avg_annual_elec_cost_2025_est_usd'] * c['households']
c['inc_sum'] = c['avg_household_income_usd'] * c['households']
c['lcost_sum'] = c['low_income_avg_annual_energy_cost_usd'] * c['low_income_households']
c['linc_sum'] = c['low_income_avg_household_income_usd'] * c['low_income_households']
s = c.groupby('state')[['households', 'low_income_households', 'cost_sum', 'elec_sum', 'elec25_sum', 'inc_sum', 'lcost_sum', 'linc_sum']].sum()
st = pd.DataFrame({
    'households': s['households'].round(0).astype('int64'),
    'avg_energy_burden_pct': (100 * s['cost_sum'] / s['inc_sum']).round(2),
    'low_income_burden_pct': (100 * s['lcost_sum'] / s['linc_sum']).round(2),
    'avg_elec_burden_pct': (100 * s['elec_sum'] / s['inc_sum']).round(2),
    'avg_annual_elec_cost_usd_lead2022': (s['elec_sum'] / s['households']).round(0),
    'avg_annual_elec_cost_2025_est_usd': (s['elec25_sum'] / s['households']).round(0),
    'low_income_share_pct': (100 * s['low_income_households'] / s['households']).round(1),
})
hps = pd.read_csv(os.path.join(P, 'households_hps_energy_insecurity_state.csv')).set_index('state')
st = st.join(hps[['unable_to_pay_pct', 'forwent_necessities_pct', 'unsafe_temperature_pct', 'lt50k_unable_to_pay_pct']]
             .add_prefix('hps2024_'))
e = pd.read_csv(os.path.join(P, 'households_eia112_disconnections_2024.csv'))
tot = e[e['utility_name'] == 'State Total'].set_index('state')
st['eia112_elec_disconnections_2024'] = tot['disconnections']
st['eia112_elec_final_notices_2024'] = tot['final_notices']
st['eia112_disconnections_per_100_customers'] = tot['disconnections_per_100_customers']
dc = cdf.copy()
dc['state'] = dc['county_fips'].str[:2]
fips2st = county.drop_duplicates('state').assign(sf=lambda d: d['county_fips'].str[:2]).set_index('sf')['state']
dc['state'] = dc['state'].map(fips2st)
st['dc_campuses_active_atlas'] = dc[dc['active']].groupby('state')['id'].count()
st['dc_power_mw_disclosed_atlas'] = dc[dc['active']].groupby('state')['mw'].sum()
st = st.fillna({'dc_campuses_active_atlas': 0})
st.reset_index().to_csv(os.path.join(P, 'households_state_summary.csv'), index=False)
pd.set_option('display.width', 250)
print(st.sort_values('eia112_disconnections_per_100_customers', ascending=False).head(12).to_string())
print(st.sort_values('low_income_burden_pct', ascending=False).head(10)[['low_income_burden_pct', 'avg_energy_burden_pct', 'hps2024_unable_to_pay_pct']].to_string())
print(st.sort_values('dc_power_mw_disclosed_atlas', ascending=False).head(10)[['dc_campuses_active_atlas', 'dc_power_mw_disclosed_atlas', 'low_income_burden_pct', 'hps2024_unable_to_pay_pct', 'eia112_disconnections_per_100_customers']].to_string())
print('corr (states) dc MW vs low_income_burden', round(st['dc_power_mw_disclosed_atlas'].corr(st['low_income_burden_pct']), 2),
      'vs disconnect rate', round(st['dc_power_mw_disclosed_atlas'].corr(st['eia112_disconnections_per_100_customers']), 2))
