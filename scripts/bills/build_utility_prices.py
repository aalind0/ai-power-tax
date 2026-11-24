"""Build data/processed/bills_utility_prices.csv from EIA-861 Sales_Ult_Cust_<year> files.

Run from the project root:  python3 -I scripts/bills/build_utility_prices.py
Inputs : data/raw/bills/eia861_<year>/extracted/Sales_Ult_Cust_<year>.xls[x]   (2013-2025)
         data/raw/bills/eia861_<year>/extracted/Balancing_Authority_<year>.xls[x]
         data/processed/bills_cpi_monthly.csv  (BLS CPI-U all items NSA CUUR0000SA0; annual avg for real-dollar columns)
Output : data/processed/bills_utility_prices.csv  (one row per year x EIA utility id x state)

Conventions (EIA-861 "Part"/"Service Type"):
  A / D = Bundled  (utility sells both energy and delivery; in choice states = default/standard-offer customers)
  B     = Energy   (energy-only; retail power marketers, CCAs)
  C     = Delivery (delivery-only; wires charges for customers who buy energy from someone else)
EIA's own note: to get state totals sum Parts A-D for revenue but only A, B, D for sales and customers.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.getcwd()
RAW = os.path.join(ROOT, 'data', 'raw', 'bills')
OUT = os.path.join(ROOT, 'data', 'processed', 'bills_utility_prices.csv')
YEARS = list(range(2013, 2026))
FINAL_YEAR_STATUS = {y: 'final' for y in YEARS}  # 2025 file on EIA page is labelled "2025 final data" (released 2026-10-07)

# BA code -> RTO/ISO (balancing-authority footprint). Everything else = no organized market (vertically integrated / bilateral).
BA_TO_RTO = {
    'PJM': 'PJM', 'MISO': 'MISO', 'ERCO': 'ERCOT', 'SWPP': 'SPP', 'CISO': 'CAISO',
    'NYIS': 'NYISO', 'ISNE': 'ISO-NE',
}

SECTORS = ['res', 'com', 'ind', 'trans', 'tot']
METRICS = ['revenue_thousand_usd', 'sales_mwh', 'customers']


def engine(path):
    return 'openpyxl' if path.endswith('x') else 'xlrd'


def read_sales(year, kind='Sales_Ult_Cust', sheet='States'):
    fs = glob.glob(os.path.join(RAW, f'eia861_{year}', 'extracted', f'{kind}_{year}.xls*'))
    if not fs:
        return None
    f = fs[0]
    hdr = pd.read_excel(f, engine=engine(f), sheet_name=sheet, header=None, nrows=3)
    df = pd.read_excel(f, engine=engine(f), sheet_name=sheet, header=None, skiprows=3)
    # name the 9 leading id columns by their 3rd header row, then 15 numeric columns by position
    lead = [str(v).strip() for v in hdr.iloc[2].tolist()]
    names = []
    num_i = 0
    for i, h in enumerate(lead):
        hl = h.lower()
        if hl.startswith('data year'):
            names.append('year')
        elif hl.startswith('utility number'):
            names.append('eia_utility_id')
        elif hl.startswith('utility name'):
            names.append('utility_name')
        elif hl == 'part':
            names.append('part')
        elif hl.startswith('service'):
            names.append('service_type')
        elif hl.startswith('data type'):
            names.append('data_type')
        elif hl == 'state':
            names.append('state')
        elif hl == 'ownership':
            names.append('ownership')
        elif hl.startswith('ba'):
            names.append('ba_code')
        elif hl.startswith('short form'):
            names.append('short_form')
        else:
            sec = SECTORS[num_i // 3]
            met = METRICS[num_i % 3]
            names.append(f'{sec}_{met}')
            num_i += 1
    assert num_i == 15, (year, lead)
    df.columns = names
    df = df[pd.to_numeric(df['eia_utility_id'], errors='coerce').notna()].copy()
    df['eia_utility_id'] = df['eia_utility_id'].astype(int)
    df['year'] = int(year)
    for s in SECTORS:
        for m in METRICS:
            df[f'{s}_{m}'] = pd.to_numeric(df[f'{s}_{m}'].replace('.', np.nan), errors='coerce')
    return df


def basis_label(st):
    return {'Bundled': 'bundled', 'Energy': 'energy_only', 'Delivery': 'delivery_only'}[st]


def main():
    cpi = pd.read_csv(os.path.join(ROOT, 'data', 'processed', 'bills_cpi_monthly.csv'))
    # annual average of available months; 2025 has 11 months (Oct 2025 CPI never published, federal shutdown)
    cpi_ann = cpi.dropna(subset=['cpi_u_all_items_nsa']).groupby('year')['cpi_u_all_items_nsa'].agg(['mean', 'count'])
    cpi_ann = cpi_ann[cpi_ann['count'] >= 11]['mean']
    base_year = 2025
    assert base_year in cpi_ann.index, 'need full-year 2025 CPI'

    frames = [read_sales(y) for y in YEARS]
    raw = pd.concat(frames, ignore_index=True, sort=False)
    # Texas TDUs (Oncor, CenterPoint, AEP Texas, TNMP) are only in Delivery_Companies_<year> (2020+)
    dframes = [read_sales(y, 'Delivery_Companies', 'Delivery Companies') for y in YEARS]
    dc = pd.concat([d for d in dframes if d is not None], ignore_index=True, sort=False)
    k = ['year', 'eia_utility_id', 'state', 'part']
    seen = set(map(tuple, raw[k].values.tolist()))
    dc = dc[[tuple(v) not in seen for v in dc[k].values.tolist()]]
    print('delivery-company rows added:', len(dc))
    raw = pd.concat([raw, dc], ignore_index=True, sort=False)
    n_raw = len(raw)
    # drop EIA state adjustment rows (utility 99999) and Behind-the-Meter third-party solar owners
    raw = raw[(raw['eia_utility_id'] != 99999) & (raw['ownership'] != 'Behind the Meter')].copy()
    print(f'raw rows {n_raw}, kept {len(raw)}')

    keys = ['year', 'eia_utility_id', 'state']
    num_cols = [f'{s}_{m}' for s in ['res', 'com', 'ind'] for m in METRICS]

    # attributes per key: latest name/ownership/BA, imputed flag, service types present
    attrs = raw.groupby(keys).agg(
        utility_name=('utility_name', 'first'),
        ownership=('ownership', 'first'),
        ba_code=('ba_code', lambda s: ';'.join(sorted(set(str(x) for x in s if str(x) != 'nan')))),
        service_types=('service_type', lambda s: ';'.join(sorted(set(s)))),
        any_imputed=('data_type', lambda s: bool((s == 'I').any())),
    ).reset_index()

    by_st = raw.groupby(keys + ['service_type'])[num_cols].sum(min_count=1).reset_index()
    wide = {}
    for st in ['Bundled', 'Energy', 'Delivery']:
        part = by_st[by_st['service_type'] == st].drop(columns='service_type').set_index(keys)
        part.columns = [f'{c}__{st}' for c in part.columns]
        wide[st] = part
    w = attrs.set_index(keys).join(wide['Bundled']).join(wide['Energy']).join(wide['Delivery']).reset_index()

    # basis: bundled if any bundled residential/total sales, else energy-only, else delivery-only
    def pick_basis(r):
        st = r['service_types'].split(';')
        if 'Bundled' in st:
            return 'Bundled'
        if 'Energy' in st:
            return 'Energy'
        return 'Delivery'
    w['basis_st'] = w.apply(pick_basis, axis=1)

    out = w[keys + ['utility_name', 'ownership', 'ba_code', 'service_types', 'any_imputed']].copy()
    out['rto_iso'] = w['ba_code'].map(lambda b: ';'.join(sorted(set(BA_TO_RTO.get(x, 'none') for x in b.split(';')))) if b else None)
    out['basis'] = w['basis_st'].map(basis_label)
    for sec in ['res', 'com', 'ind']:
        for m in METRICS:
            out[f'{sec}_{m}'] = [w.at[i, f'{sec}_{m}__{st}'] if f'{sec}_{m}__{st}' in w.columns else np.nan
                                 for i, st in zip(w.index, w['basis_st'])]
        rev, mwh, cust = out[f'{sec}_revenue_thousand_usd'], out[f'{sec}_sales_mwh'], out[f'{sec}_customers']
        out[f'{sec}_price_cents_kwh'] = np.where(mwh > 0, rev * 1000 / (mwh * 1000) * 100, np.nan)
        if sec == 'res':
            out['avg_monthly_bill_usd'] = np.where(cust > 0, rev * 1000 / cust / 12, np.nan)
            out['avg_monthly_kwh'] = np.where(cust > 0, mwh * 1000 / cust / 12, np.nan)
    # Delivery-only components (shopping customers' wires charges), reported by distribution utilities
    for m in METRICS:
        out[f'res_delivery_only_{m}'] = w.get(f'res_{m}__Delivery')
    d_rev, d_mwh = out['res_delivery_only_revenue_thousand_usd'], out['res_delivery_only_sales_mwh']
    out['res_delivery_only_price_cents_kwh'] = np.where(d_mwh > 0, d_rev / d_mwh * 100, np.nan)

    # state average energy-only (retail supplier) residential price, from Part B rows
    en = raw[raw['service_type'] == 'Energy'].groupby(['year', 'state'])[['res_revenue_thousand_usd', 'res_sales_mwh']].sum()
    en['state_res_energy_only_price_cents_kwh'] = np.where(en['res_sales_mwh'] > 0, en['res_revenue_thousand_usd'] / en['res_sales_mwh'] * 100, np.nan)
    out = out.merge(en[['state_res_energy_only_price_cents_kwh']].reset_index(), on=['year', 'state'], how='left')
    # Texas: retail electric providers report ALL-IN (energy + TDU pass-through) as Part D "Bundled"
    rep = raw[(raw['state'] == 'TX') & (raw['ownership'] == 'Retail Power Marketer') & (raw['service_type'] == 'Bundled')]
    rep = rep.groupby('year')[['res_revenue_thousand_usd', 'res_sales_mwh']].sum()
    tx_rep_price = (rep['res_revenue_thousand_usd'] / rep['res_sales_mwh'] * 100).to_dict()
    out['state_res_energy_only_price_cents_kwh'] = np.where(out['state'] == 'TX', np.nan, out['state_res_energy_only_price_cents_kwh'])
    out['tx_rep_all_in_price_cents_kwh'] = np.where(out['state'] == 'TX', out['year'].map(tx_rep_price), np.nan)
    # all-in estimate: bundled/energy price as is; delivery-only = delivery price + state avg supplier energy price,
    # except TX where the statewide average REP all-in price is used (REP bills already include TDU charges)
    out['res_all_in_price_cents_kwh'] = np.where(
        out['basis'] == 'delivery_only',
        np.where(out['state'] == 'TX', out['tx_rep_all_in_price_cents_kwh'],
                 out['res_delivery_only_price_cents_kwh'] + out['state_res_energy_only_price_cents_kwh']),
        out['res_price_cents_kwh'])
    out['res_all_in_is_estimate'] = out['basis'] == 'delivery_only'
    # for delivery-only utilities, put the delivery-only quantities in the main residential columns? No: keep null
    # main columns null for delivery_only basis to avoid passing wires-only prices off as full prices
    mask = out['basis'] == 'delivery_only'
    for c in ['res_price_cents_kwh', 'avg_monthly_bill_usd', 'avg_monthly_kwh', 'res_revenue_thousand_usd',
              'res_sales_mwh', 'res_customers', 'com_price_cents_kwh', 'ind_price_cents_kwh',
              'com_revenue_thousand_usd', 'com_sales_mwh', 'com_customers',
              'ind_revenue_thousand_usd', 'ind_sales_mwh', 'ind_customers']:
        out.loc[mask, c] = np.nan
    # all-in bill estimate for delivery-only (customers & kWh from the delivery rows)
    d_cust = out['res_delivery_only_customers']
    out['res_all_in_avg_monthly_kwh'] = np.where(mask, np.where(d_cust > 0, d_mwh * 1000 / d_cust / 12, np.nan), out['avg_monthly_kwh'])
    out['res_all_in_avg_monthly_bill_usd'] = out['res_all_in_avg_monthly_kwh'] * out['res_all_in_price_cents_kwh'] / 100

    # real (2025 $) residential price using CPI-U annual average
    defl = out['year'].map(lambda y: cpi_ann.get(base_year) / cpi_ann.get(y) if y in cpi_ann.index else np.nan)
    out['cpi_u_annual_avg'] = out['year'].map(cpi_ann)
    out['res_price_real2025_cents_kwh'] = out['res_price_cents_kwh'] * defl
    out['res_all_in_price_real2025_cents_kwh'] = out['res_all_in_price_cents_kwh'] * defl
    out['avg_monthly_bill_real2025_usd'] = out['avg_monthly_bill_usd'] * defl
    out['data_status'] = out['year'].map(FINAL_YEAR_STATUS)

    rnd = {c: 3 for c in out.columns if c.endswith('cents_kwh')}
    rnd.update({c: 2 for c in out.columns if c.endswith('bill_usd') or c.endswith('_usd') and 'thousand' not in c})
    rnd.update({'avg_monthly_kwh': 1, 'res_all_in_avg_monthly_kwh': 1, 'cpi_u_annual_avg': 3})
    out = out.round(rnd)
    out = out.sort_values(['eia_utility_id', 'state', 'year'])
    cols = ['year', 'eia_utility_id', 'utility_name', 'state', 'ownership', 'ba_code', 'rto_iso', 'service_types', 'basis',
            'res_customers', 'res_sales_mwh', 'res_revenue_thousand_usd', 'res_price_cents_kwh', 'avg_monthly_bill_usd', 'avg_monthly_kwh',
            'res_delivery_only_customers', 'res_delivery_only_sales_mwh', 'res_delivery_only_revenue_thousand_usd', 'res_delivery_only_price_cents_kwh',
            'state_res_energy_only_price_cents_kwh', 'tx_rep_all_in_price_cents_kwh', 'res_all_in_price_cents_kwh', 'res_all_in_avg_monthly_kwh', 'res_all_in_avg_monthly_bill_usd', 'res_all_in_is_estimate',
            'com_customers', 'com_sales_mwh', 'com_revenue_thousand_usd', 'com_price_cents_kwh',
            'ind_customers', 'ind_sales_mwh', 'ind_revenue_thousand_usd', 'ind_price_cents_kwh',
            'cpi_u_annual_avg', 'res_price_real2025_cents_kwh', 'res_all_in_price_real2025_cents_kwh', 'avg_monthly_bill_real2025_usd',
            'any_imputed', 'data_status']
    out[cols].to_csv(OUT, index=False)
    print('wrote', OUT, len(out), 'rows;', out['eia_utility_id'].nunique(), 'utilities')


if __name__ == '__main__':
    main()
