# -*- coding: utf-8 -*-
"""Build data/processed/grid_td_spending_by_utility.csv: transmission & distribution capital additions and plant in
service by FERC Form 1 respondent, 2015-latest, with EIA utility id(s) joined through Catalyst PUDL's utility
crosswalk (FERC1 id -> PUDL id -> EIA id). A PUDL id can map to several EIA ids; we keep the first and list all.
Run: python3 -I scripts/grid/build_td_by_utility.py
"""
import pandas as pd

D = 'data/raw/grid/_derived_csv/'
p = pd.read_csv(D + 'core_ferc1__yearly_plant_in_service_sched204.csv', low_memory=False)
fu = pd.read_csv(D + 'core_pudl__assn_ferc1_pudl_utilities.csv')
eu = pd.read_csv(D + 'core_pudl__assn_eia_pudl_utilities.csv')

p = p[(p.report_year >= 2015) & p.ferc_account_label.isin(['transmission_plant', 'distribution_plant'])]
add = p.pivot_table(index=['utility_id_ferc1', 'report_year'], columns='ferc_account_label', values='additions', aggfunc='sum')
bal = p.pivot_table(index=['utility_id_ferc1', 'report_year'], columns='ferc_account_label', values='ending_balance', aggfunc='sum')
df = pd.DataFrame({
    'transmission_capex_musd': add['transmission_plant'] / 1e6,
    'distribution_capex_musd': add['distribution_plant'] / 1e6,
    'transmission_plant_in_service_musd': bal['transmission_plant'] / 1e6,
    'distribution_plant_in_service_musd': bal['distribution_plant'] / 1e6,
}).reset_index().rename(columns={'report_year': 'year'})
df = df.merge(fu, on='utility_id_ferc1', how='left')
eia = eu.dropna(subset=['utility_id_pudl']).groupby('utility_id_pudl').utility_id_eia.apply(
    lambda s: ';'.join(str(int(v)) for v in sorted(s.dropna().unique())))
df['eia_utility_ids'] = df.utility_id_pudl.map(eia)
df['eia_utility_id'] = df.eia_utility_ids.str.split(';').str[0]
df = df[['year', 'utility_id_ferc1', 'utility_name_ferc1', 'utility_id_pudl', 'eia_utility_id', 'eia_utility_ids',
         'transmission_capex_musd', 'distribution_capex_musd', 'transmission_plant_in_service_musd',
         'distribution_plant_in_service_musd']]
num = ['transmission_capex_musd', 'distribution_capex_musd', 'transmission_plant_in_service_musd', 'distribution_plant_in_service_musd']
df[num] = df[num].round(2)
df = df[(df[num].abs().sum(axis=1) > 0)]
df['source'] = 'FERC Form 1 sched 204 via Catalyst PUDL stable'
df.to_csv('data/processed/grid_td_spending_by_utility.csv', index=False)
print(len(df), 'rows;', df.utility_id_ferc1.nunique(), 'respondents;', df.eia_utility_id.notna().mean().round(3), 'share with EIA id')
top = df[df.year == df.year.max()].sort_values('transmission_capex_musd', ascending=False).head(10)
print(top[['utility_name_ferc1', 'eia_utility_id', 'transmission_capex_musd', 'distribution_capex_musd']].to_string())
