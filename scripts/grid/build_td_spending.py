"""Build data/processed/grid_td_spending.csv: transmission & distribution spending by FERC Form 1 respondents
(major investor-owned utilities + FERC-jurisdictional transmission companies), 2005-latest, plus EIA AEO
generation/transmission/distribution price components (share-of-bill proxy).

Inputs (all produced by scripts in scripts/grid/):
  data/raw/grid/_derived_csv/core_ferc1__yearly_plant_in_service_sched204.csv   (parquet2csv.mjs of PUDL stable)
  data/raw/grid/_derived_csv/core_ferc1__yearly_operating_expenses_sched320.csv (parquet2csv.mjs of PUDL stable)
  data/raw/grid/_derived_csv/aeo_components.csv                                  (build_aeo_components.py)
  data/processed/bills_cpi_monthly.csv                                           (bills area, BLS CPI-U)
Run: python3 -I scripts/grid/build_td_spending.py
"""
import pandas as pd

D = 'data/raw/grid/_derived_csv/'
p = pd.read_csv(D + 'core_ferc1__yearly_plant_in_service_sched204.csv', low_memory=False)
o = pd.read_csv(D + 'core_ferc1__yearly_operating_expenses_sched320.csv', low_memory=False)
aeo = pd.read_csv(D + 'aeo_components.csv')
cpi = pd.read_csv('data/processed/bills_cpi_monthly.csv')

B = 1e9
tot = p[p.ferc_account_label.isin(['transmission_plant', 'distribution_plant', 'production_plant', 'electric_plant_in_service'])]
add = tot.pivot_table(index='report_year', columns='ferc_account_label', values='additions', aggfunc='sum') / B
bal = tot.pivot_table(index='report_year', columns='ferc_account_label', values='ending_balance', aggfunc='sum') / B
n = tot[tot.ferc_account_label == 'electric_plant_in_service'].groupby('report_year').utility_id_ferc1.nunique()

ox = o[o.expense_type.isin(['transmission_expenses', 'transmission_of_electricity_by_others', 'distribution_expenses'])]
om = ox.pivot_table(index='report_year', columns='expense_type', values='dollar_value', aggfunc='sum') / B

df = pd.DataFrame({
    'n_ferc1_respondents': n,
    'transmission_capex_busd': add['transmission_plant'],
    'distribution_capex_busd': add['distribution_plant'],
    'production_capex_busd': add['production_plant'],
    'total_electric_capex_busd': add['electric_plant_in_service'],
    # own O&M = total transmission O&M minus payments to other parties for wheeling (account 565), which would
    # double count across utilities (one utility's payment is another's transmission revenue)
    'transmission_om_own_busd': om['transmission_expenses'] - om['transmission_of_electricity_by_others'],
    'transmission_paid_to_others_busd': om['transmission_of_electricity_by_others'],
    'distribution_om_busd': om['distribution_expenses'],
    'transmission_plant_in_service_busd': bal['transmission_plant'],
    'distribution_plant_in_service_busd': bal['distribution_plant'],
})
df.index.name = 'year'
df = df.loc[2005:].reset_index()
df['td_capex_busd'] = df.transmission_capex_busd + df.distribution_capex_busd
df['td_share_of_capex_pct'] = (df.td_capex_busd / df.total_electric_capex_busd * 100).round(1)

ann = cpi.groupby('year').agg(cpi=('cpi_u_all_items_nsa', 'mean'), months=('cpi_u_all_items_nsa', 'count')).reset_index()
df = df.merge(ann, on='year', how='left')
base = float(ann.loc[ann.year == 2025, 'cpi'])
for c in ['transmission_capex_busd', 'distribution_capex_busd', 'td_capex_busd']:
    df[c.replace('_busd', '_busd_real2025')] = (df[c] * base / df.cpi).round(2)
df = df.rename(columns={'cpi': 'cpi_u_annual_avg', 'months': 'cpi_months'})

a = aeo.rename(columns={'generation_cents_kwh': 'aeo_generation_cents_kwh', 'transmission_cents_kwh': 'aeo_transmission_cents_kwh',
                        'distribution_cents_kwh': 'aeo_distribution_cents_kwh', 'all_sectors_avg_cents_kwh': 'aeo_all_sectors_price_cents_kwh',
                        'transmission_share_pct': 'aeo_transmission_share_pct', 'distribution_share_pct': 'aeo_distribution_share_pct',
                        'td_share_pct': 'aeo_td_share_pct', 'basis': 'aeo_basis'})
df = df.merge(a, on='year', how='left')
df['source'] = 'FERC Form 1 via Catalyst PUDL stable (sched 204 additions; sched 320 O&M); EIA AEO Table 8 for aeo_* columns'
df['verified'] = True
num = df.select_dtypes('number').columns
df[num] = df[num].round(3)
df.to_csv('data/processed/grid_td_spending.csv', index=False)
print(df[['year', 'n_ferc1_respondents', 'transmission_capex_busd', 'distribution_capex_busd', 'td_capex_busd_real2025',
          'transmission_om_own_busd', 'distribution_om_busd', 'td_share_of_capex_pct', 'aeo_transmission_cents_kwh', 'aeo_td_share_pct']].to_string())
