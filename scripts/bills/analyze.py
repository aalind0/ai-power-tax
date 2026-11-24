"""Compute headline statistics for research/bills/FINDINGS.md and write
   data/processed/bills_state_annual.csv  (state x year residential price, nominal + real, from EIA-861M monthly sums)
   data/processed/bills_summary.json      (headline numbers the site can show)
Run from project root after the build_* scripts:  python3 -I scripts/bills/analyze.py
"""
import json
import os

import numpy as np
import pandas as pd

ROOT = os.getcwd()
P = lambda *a: os.path.join(ROOT, 'data', 'processed', *a)
pd.set_option('display.width', 220)
pd.set_option('display.max_columns', 30)

cpi = pd.read_csv(P('bills_cpi_monthly.csv'))
cpi_ann = cpi.dropna(subset=['cpi_u_all_items_nsa']).groupby('year')['cpi_u_all_items_nsa'].agg(['mean', 'count'])
cpi_ann = cpi_ann[cpi_ann['count'] >= 11]['mean']
elec_ann = cpi.dropna(subset=['cpi_u_electricity_nsa']).groupby('year')['cpi_u_electricity_nsa'].mean()

# ---------------- state annual (calendar years, 861M monthly sums) ----------------
sm = pd.read_csv(P('bills_state_monthly.csv'))
full_years = sm.groupby('year')['month'].nunique()
full_years = full_years[full_years == 12].index.tolist()
sa = sm[sm['year'].isin(full_years)].groupby(['state', 'year'])[['res_revenue_thousand_usd', 'res_sales_mwh', 'res_customers']].agg(
    {'res_revenue_thousand_usd': 'sum', 'res_sales_mwh': 'sum', 'res_customers': 'mean'}).reset_index()
sa['res_price_cents_kwh'] = sa['res_revenue_thousand_usd'] / sa['res_sales_mwh'] * 100
sa['res_avg_monthly_bill_usd'] = sa['res_revenue_thousand_usd'] * 1000 / sa['res_customers'] / 12
sa['res_avg_monthly_kwh'] = sa['res_sales_mwh'] * 1000 / sa['res_customers'] / 12
sa['cpi_u_annual_avg'] = sa['year'].map(cpi_ann)
base = cpi_ann[2025]
sa['res_price_real2025_cents_kwh'] = sa['res_price_cents_kwh'] * base / sa['cpi_u_annual_avg']
sa['res_bill_real2025_usd'] = sa['res_avg_monthly_bill_usd'] * base / sa['cpi_u_annual_avg']
# trailing-12-month to latest month (Sep 2025-Aug 2026) as a "2026 TTM" row
latest = sm['date'].max()
ttm = sm[sm['state'] == 'US'].sort_values('date').tail(1)
ttm_rows = sm[sm['date'] == latest][['state', 'res_price_ttm_cents_kwh', 'res_price_ttm_yoy_pct', 'res_price_yoy_pct', 'res_price_cents_kwh']]
sa = sa.round({'res_price_cents_kwh': 3, 'res_avg_monthly_bill_usd': 2, 'res_avg_monthly_kwh': 1, 'cpi_u_annual_avg': 3,
               'res_price_real2025_cents_kwh': 3, 'res_bill_real2025_usd': 2, 'res_revenue_thousand_usd': 1, 'res_sales_mwh': 1, 'res_customers': 0})
sa.to_csv(P('bills_state_annual.csv'), index=False)
print('wrote bills_state_annual.csv', len(sa), 'rows; years', min(full_years), '-', max(full_years))

w = sa.pivot(index='state', columns='year', values='res_price_cents_kwh')
wr = sa.pivot(index='state', columns='year', values='res_price_real2025_cents_kwh')
cpi_2020_2025 = (cpi_ann[2025] / cpi_ann[2020] - 1) * 100
cpi_2024_2025 = (cpi_ann[2025] / cpi_ann[2024] - 1) * 100
cpi_2019_2025 = (cpi_ann[2025] / cpi_ann[2019] - 1) * 100
st = pd.DataFrame({
    'p2015': w[2015], 'p2019': w[2019], 'p2020': w[2020], 'p2024': w[2024], 'p2025': w[2025],
    'nom_2020_2025_pct': (w[2025] / w[2020] - 1) * 100,
    'real_2020_2025_pct': (wr[2025] / wr[2020] - 1) * 100,
    'nom_2024_2025_pct': (w[2025] / w[2024] - 1) * 100,
    'real_2015_2025_pct': (wr[2025] / wr[2015] - 1) * 100,
}).join(ttm_rows.set_index('state'))
print('\nCPI-U change 2020->2025 %.1f%%, 2024->2025 %.1f%%, 2019->2025 %.1f%%' % (cpi_2020_2025, cpi_2024_2025, cpi_2019_2025))
print('Electricity CPI 2020->2025 %.1f%%' % ((elec_ann[2025] / elec_ann[2020] - 1) * 100))
print('\nUS row:\n', st.loc['US'].round(2).to_string())
s50 = st.drop('US')
print('\nTop 12 states real 2020->2025:\n', s50.sort_values('real_2020_2025_pct', ascending=False).head(12).round(1).to_string())
print('\nBottom 8 states real 2020->2025:\n', s50.sort_values('real_2020_2025_pct').head(8).round(1).to_string())
print('\nStates real decline 2020->2025:', int((s50['real_2020_2025_pct'] < 0).sum()), 'of', len(s50))
print('States nominal 2024->2025 >= 10%:', s50[s50['nom_2024_2025_pct'] >= 10].index.tolist())
print('States nominal 2024->2025 above CPI:', int((s50['nom_2024_2025_pct'] > cpi_2024_2025).sum()))
print('\nTop 12 states TTM (Sep25-Aug26 vs Sep24-Aug25):\n', s50.sort_values('res_price_ttm_yoy_pct', ascending=False).head(12)[['p2025', 'res_price_ttm_cents_kwh', 'res_price_ttm_yoy_pct']].round(1).to_string())
print('States TTM yoy >=10%:', int((s50['res_price_ttm_yoy_pct'] >= 10).sum()), '; above latest CPI yoy:', int((s50['res_price_ttm_yoy_pct'] > 3.4).sum()), '; falling:', int((s50['res_price_ttm_yoy_pct'] < 0).sum()))
print('Latest month (%s) yoy: states >=10%%: %d' % (latest, int((s50['res_price_yoy_pct'] >= 10).sum())))

# US monthly series check
us = sm[sm['state'] == 'US'].set_index('date')
print('\nUS latest:', us.loc[latest, ['res_price_cents_kwh', 'res_price_yoy_pct', 'res_price_ttm_cents_kwh', 'res_price_ttm_yoy_pct', 'cpi_u_all_items_yoy_pct']].to_dict())
yrs = {}
for y in full_years:
    yrs[y] = sa[(sa.state == 'US') & (sa.year == y)].iloc[0][['res_price_cents_kwh', 'res_price_real2025_cents_kwh', 'res_avg_monthly_bill_usd', 'res_avg_monthly_kwh']].to_dict()
print(pd.DataFrame(yrs).T.round(2).to_string())

# ---------------- utility level (EIA-861 annual) ----------------
u = pd.read_csv(P('bills_utility_prices.csv'))
b = u[u['basis'] == 'bundled']
pv = b.pivot_table(index=['eia_utility_id', 'state'], columns='year', values='res_price_cents_kwh')
cu = b.pivot_table(index=['eia_utility_id', 'state'], columns='year', values='res_customers')
meta = b.sort_values('year').groupby(['eia_utility_id', 'state']).last()[['utility_name', 'ownership', 'rto_iso', 'ba_code']]
uu = meta.join(pd.DataFrame({'p2020': pv[2020], 'p2024': pv[2024], 'p2025': pv[2025], 'c2025': cu[2025], 'c2020': cu[2020]}))
uu['nom_2024_2025_pct'] = (uu.p2025 / uu.p2024 - 1) * 100
uu['nom_2020_2025_pct'] = (uu.p2025 / uu.p2020 - 1) * 100
uu['real_2020_2025_pct'] = ((uu.p2025 / cpi_ann[2025]) / (uu.p2020 / cpi_ann[2020]) - 1) * 100
big = uu[(uu.c2025 >= 10000) & uu.p2024.notna() & uu.p2025.notna() & (uu.p2024 > 0)]
print('\nUtilities (bundled, >=10k res customers) n=%d' % len(big))
print('share 2024->2025 >=10%%: %.1f%% (n=%d); >= CPI (%.1f%%): %.1f%%; decreased: %.1f%%' % (
    (big.nom_2024_2025_pct >= 10).mean() * 100, (big.nom_2024_2025_pct >= 10).sum(), cpi_2024_2025,
    (big.nom_2024_2025_pct > cpi_2024_2025).mean() * 100, (big.nom_2024_2025_pct < 0).mean() * 100))
wavg = lambda g, c: np.average(g[c], weights=g['c2025'])
print('customer-weighted median-ish: weighted mean 2024->2025 %.1f%%' % wavg(big, 'nom_2024_2025_pct'))
big2 = big[big.p2020.notna() & (big.p2020 > 0)]
print('share real 2020->2025 increase: %.1f%%; >=20%% real: %.1f%%' % ((big2.real_2020_2025_pct > 0).mean() * 100, (big2.real_2020_2025_pct >= 20).mean() * 100))
by_own = big.groupby('ownership').apply(lambda g: pd.Series({'n': len(g), 'cust_m': g.c2025.sum() / 1e6,
    'wavg_24_25': wavg(g, 'nom_2024_2025_pct'), 'share_ge10': (g.nom_2024_2025_pct >= 10).mean() * 100}))
print(by_own.round(1).to_string())
by_rto = big2.groupby('rto_iso').apply(lambda g: pd.Series({'n': len(g), 'cust_m': g.c2025.sum() / 1e6,
    'wavg_nom_24_25': wavg(g, 'nom_2024_2025_pct'), 'wavg_real_20_25': wavg(g, 'real_2020_2025_pct'),
    'share_ge10_24_25': (g.nom_2024_2025_pct >= 10).mean() * 100}))
print(by_rto.round(1).to_string())
large = big2[big2.c2025 >= 250000]
print('\nLarge utilities (>=250k res cust) top 15 nominal 2024->2025:\n', large.sort_values('nom_2024_2025_pct', ascending=False).head(15)[['utility_name', 'rto_iso', 'c2025', 'p2024', 'p2025', 'nom_2024_2025_pct', 'real_2020_2025_pct']].round(1).to_string())
print('\nLarge utilities top 15 real 2020->2025:\n', large.sort_values('real_2020_2025_pct', ascending=False).head(15)[['utility_name', 'rto_iso', 'c2025', 'p2020', 'p2025', 'real_2020_2025_pct']].round(1).to_string())
print('\nLarge utilities bottom 10 real 2020->2025:\n', large.sort_values('real_2020_2025_pct').head(10)[['utility_name', 'rto_iso', 'c2025', 'p2020', 'p2025', 'real_2020_2025_pct']].round(1).to_string())

# ---------------- utility monthly: 2026 YTD vs 2025 YTD (EIA-861M, bundled) ----------------
um = pd.read_csv(P('bills_utility_monthly.csv'))
last_m = um[um.year == 2026]['month'].max()
ytd = um[um.month <= last_m].groupby(['eia_utility_id', 'state', 'year'])[['res_revenue_thousand_usd', 'res_sales_mwh', 'res_customers']].agg(
    {'res_revenue_thousand_usd': 'sum', 'res_sales_mwh': 'sum', 'res_customers': 'mean'})
ytd['p'] = ytd.res_revenue_thousand_usd / ytd.res_sales_mwh * 100
yp = ytd['p'].unstack('year')
yc = ytd['res_customers'].unstack('year')
nm = um.sort_values('date').groupby(['eia_utility_id', 'state'])[['utility_name', 'ownership']].last()
y26 = nm.join(pd.DataFrame({'ytd2025': yp.get(2025), 'ytd2026': yp.get(2026), 'cust2026': yc.get(2026)})).dropna()
y26 = y26[(y26.cust2026 >= 10000) & (y26.ytd2025 > 0)]
y26['chg'] = (y26.ytd2026 / y26.ytd2025 - 1) * 100
cpi_ytd = cpi[(cpi.month <= last_m)].groupby('year')['cpi_u_all_items_nsa'].mean()
print('\n2026 Jan-%d vs 2025 Jan-%d, utilities >=10k res cust (861M bundled) n=%d: share >=10%%: %.1f%%, share > CPI (%.1f%%): %.1f%%, falling %.1f%%, cust-weighted mean %.1f%%' % (
    last_m, last_m, len(y26), (y26.chg >= 10).mean() * 100, (cpi_ytd[2026] / cpi_ytd[2025] - 1) * 100,
    (y26.chg > (cpi_ytd[2026] / cpi_ytd[2025] - 1) * 100).mean() * 100, (y26.chg < 0).mean() * 100,
    np.average(y26.chg, weights=y26.cust2026)))
print(y26[y26.cust2026 >= 250000].sort_values('chg', ascending=False).head(20).round(1).to_string())
print(y26[y26.cust2026 >= 250000].sort_values('chg').head(8).round(1).to_string())

summary = {
    'generated_from': ['bills_state_annual.csv', 'bills_state_monthly.csv', 'bills_utility_prices.csv', 'bills_utility_monthly.csv'],
    'latest_month': latest,
    'cpi_u_change_pct': {'2019_2025': round(cpi_2019_2025, 2), '2020_2025': round(cpi_2020_2025, 2), '2024_2025': round(cpi_2024_2025, 2)},
    'us': {str(y): {k: round(v, 3) for k, v in yrs[y].items()} for y in yrs},
    'us_latest': {k: round(float(v), 3) for k, v in us.loc[latest, ['res_price_cents_kwh', 'res_price_yoy_pct', 'res_price_ttm_cents_kwh', 'res_price_ttm_yoy_pct', 'cpi_u_all_items_yoy_pct']].items()},
    'states_real_2020_2025_pct': s50['real_2020_2025_pct'].round(2).sort_values(ascending=False).to_dict(),
    'states_ttm_yoy_pct_latest': s50['res_price_ttm_yoy_pct'].round(2).sort_values(ascending=False).to_dict(),
    'utilities_2024_2025': {
        'n_utilities_ge10k_customers': int(len(big)),
        'share_ge10pct': round(float((big.nom_2024_2025_pct >= 10).mean() * 100), 1),
        'share_above_cpi': round(float((big.nom_2024_2025_pct > cpi_2024_2025).mean() * 100), 1),
        'share_decrease': round(float((big.nom_2024_2025_pct < 0).mean() * 100), 1),
    },
    'utilities_2026ytd_vs_2025ytd': {
        'months': f'Jan-{last_m}', 'n_utilities_ge10k_customers': int(len(y26)),
        'share_ge10pct': round(float((y26.chg >= 10).mean() * 100), 1),
        'customer_weighted_mean_pct': round(float(np.average(y26.chg, weights=y26.cust2026)), 2),
    },
    'by_rto_2020_2025': by_rto.round(2).reset_index().to_dict(orient='records'),
}
json.dump(summary, open(P('bills_summary.json'), 'w'), indent=1)
print('wrote bills_summary.json')
