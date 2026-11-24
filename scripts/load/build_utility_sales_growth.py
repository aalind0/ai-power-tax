"""Build data/processed/load_utility_sales_growth.csv from EIA-861 (annual, final) 2019-2025.

Run from the project root:  python3 -I scripts/load/build_utility_sales_growth.py

Inputs (READ-ONLY, downloaded by the `bills` area; we never modify them):
  data/raw/bills/eia861_<year>/f861<year>.zip   members Sales_Ult_Cust_<year>.xlsx and (2020+) Delivery_Companies_<year>.xlsx
  Source: https://www.eia.gov/electricity/data/eia861/  (zips: https://www.eia.gov/electricity/data/eia861/zip/f861<year>.zip)
  If the bills raw files are missing, download the zips with:  node scripts/load/fetch.mjs <zip url> data/raw/load/eia861_<year>/f861<year>.zip
  and set RAW_DIRS below.

Method:
  * Utility rows: for each hotspot utility x state x year, sum sales over EIA-861 Parts A (bundled), C (delivery-only) and D
    (bundled, choice states). Part B (energy-only marketers) is excluded, so the number is "kWh the utility delivered or sold
    to end users in its territory". Texas TDUs (Oncor, CenterPoint, AEP Texas) only appear in Delivery_Companies_<year>.xlsx,
    which EIA publishes from 2020; for them the base year is 2020 (2019 not available in the 861 tables).
  * State rows: EIA convention for state totals = Parts A + B + D (C would double count energy sold by marketers).
  * Growth columns compare each year with the entity's base year (2019, or 2020 where 2019 is unavailable).
  * C&I = commercial + industrial. Data centers are reported as commercial at some utilities (e.g. Dominion) and as
    industrial at others (e.g. MidAmerican, Omaha PPD, Entergy); always read C&I together.
"""
import io
import os
import sys
import zipfile

import pandas as pd

ROOT = os.getcwd()
RAW_DIRS = [os.path.join(ROOT, 'data', 'raw', 'bills'), os.path.join(ROOT, 'data', 'raw', 'load')]
OUT = os.path.join(ROOT, 'data', 'processed', 'load_utility_sales_growth.csv')
YEARS = list(range(2019, 2026))
SECTORS = ['res', 'com', 'ind', 'trans', 'tot']
METRICS = ['revenue_thousand_usd', 'sales_mwh', 'customers']

# (eia_utility_id, state, short label, hotspot / market, parent)
HOTSPOTS = [
    (19876, 'VA', 'Dominion Energy Virginia (Virginia Electric & Power)', 'Northern Virginia / PJM DOM zone', 'Dominion Energy'),
    (13640, 'VA', 'NOVEC (Northern Virginia Electric Coop)', 'Northern Virginia / PJM DOM zone', 'Cooperative'),
    (40228, 'VA', 'Rappahannock Electric Coop', 'Virginia exurbs (Culpeper/Fredericksburg) / PJM DOM zone', 'Cooperative'),
    (7140, 'GA', 'Georgia Power', 'Atlanta / Southeast (SOCO)', 'Southern Company'),
    (44372, 'TX', 'Oncor Electric Delivery (TDU)', 'Dallas-Fort Worth & West Texas / ERCOT', 'Sempra (80%)'),
    (8901, 'TX', 'CenterPoint Energy Houston Electric (TDU)', 'Houston / ERCOT', 'CenterPoint Energy'),
    (3278, 'TX', 'AEP Texas Central (TDU)', 'South Texas / ERCOT', 'American Electric Power'),
    (20404, 'TX', 'AEP Texas North (TDU)', 'West Texas (Abilene) / ERCOT', 'American Electric Power'),
    (803, 'AZ', 'Arizona Public Service (APS)', 'Phoenix / AZPS', 'Pinnacle West'),
    (16572, 'AZ', 'Salt River Project (SRP)', 'Phoenix / SRP', 'Public power'),
    (14006, 'OH', 'AEP Ohio (Ohio Power Co)', 'Columbus (New Albany) / PJM AEP zone', 'American Electric Power'),
    (9324, 'IN', 'Indiana Michigan Power (AEP)', 'Northern Indiana (New Carlisle) / PJM AEP zone', 'American Electric Power'),
    (4110, 'IL', 'ComEd (Commonwealth Edison)', 'Chicago / PJM ComEd zone', 'Exelon'),
    (11241, 'LA', 'Entergy Louisiana', 'Louisiana (Meta Hyperion, Richland Parish) / MISO', 'Entergy'),
    (814, 'AR', 'Entergy Arkansas', 'Arkansas / MISO', 'Entergy'),
    (12685, 'MS', 'Entergy Mississippi', 'Mississippi / MISO', 'Entergy'),
    (55937, 'TX', 'Entergy Texas', 'Southeast Texas / MISO', 'Entergy'),
    (5416, 'NC', 'Duke Energy Carolinas (NC)', 'Charlotte / Carolinas (DUK)', 'Duke Energy'),
    (5416, 'SC', 'Duke Energy Carolinas (SC)', 'Upstate SC / Carolinas (DUK)', 'Duke Energy'),
    (3046, 'NC', 'Duke Energy Progress (NC)', 'Raleigh / Carolinas (CPLE)', 'Duke Energy'),
    (15470, 'IN', 'Duke Energy Indiana', 'Indiana / MISO', 'Duke Energy'),
    (14328, 'CA', 'PG&E (Pacific Gas & Electric)', 'Silicon Valley (San Jose/Santa Clara) / CAISO', 'PG&E Corp'),
    (13407, 'NV', 'NV Energy - Nevada Power', 'Las Vegas / NEVP', 'Berkshire Hathaway Energy'),
    (17166, 'NV', 'NV Energy - Sierra Pacific Power', 'Reno (Tahoe-Reno Industrial Center) / NEVP', 'Berkshire Hathaway Energy'),
    (12341, 'IA', 'MidAmerican Energy (IA)', 'Des Moines / Council Bluffs / MISO', 'Berkshire Hathaway Energy'),
    (14127, 'NE', 'Omaha Public Power District', 'Omaha (Papillion, Sarpy County) / SPP', 'Public power'),
]
STATES = ['VA', 'TX', 'GA', 'AZ', 'OH', 'IN', 'IL', 'LA', 'NC', 'CA', 'NV', 'IA', 'NE', 'OR', 'ND', 'WA', 'PA', 'NJ', 'UT', 'WY']


def find_zip(year):
    for d in RAW_DIRS:
        p = os.path.join(d, f'eia861_{year}', f'f861{year}.zip')
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'f861{year}.zip not found in {RAW_DIRS}')


def read_member(year, kind, sheet=0):
    z = zipfile.ZipFile(find_zip(year))
    names = [n for n in z.namelist() if os.path.basename(n).startswith(f'{kind}_{year}')]
    if not names:
        return None
    raw = z.read(names[0])
    hdr = pd.read_excel(io.BytesIO(raw), engine='openpyxl', sheet_name=sheet, header=None, nrows=3)
    df = pd.read_excel(io.BytesIO(raw), engine='openpyxl', sheet_name=sheet, header=None, skiprows=3)
    lead = [str(v).strip() for v in hdr.iloc[2].tolist()]
    cols, k = [], 0
    for h in lead:
        hl = h.lower()
        if hl.startswith('data year'):
            cols.append('year')
        elif hl.startswith('utility number'):
            cols.append('eia_utility_id')
        elif hl.startswith('utility name'):
            cols.append('utility_name')
        elif hl == 'part':
            cols.append('part')
        elif hl.startswith('service'):
            cols.append('service_type')
        elif hl.startswith('data type'):
            cols.append('data_type')
        elif hl == 'state':
            cols.append('state')
        elif hl == 'ownership':
            cols.append('ownership')
        elif hl.startswith('ba'):
            cols.append('ba_code')
        elif hl.startswith('short form'):
            cols.append('short_form')
        else:
            cols.append(f'{SECTORS[k // 3]}_{METRICS[k % 3]}')
            k += 1
    assert k == 15, (year, kind, lead)
    df.columns = cols
    df = df[pd.to_numeric(df['year'], errors='coerce').notna()].copy()
    df['eia_utility_id'] = pd.to_numeric(df['eia_utility_id'], errors='coerce')
    for c in cols:
        if c.endswith(('_sales_mwh', '_customers', '_revenue_thousand_usd')):
            df[c] = pd.to_numeric(df[c], errors='coerce')  # '.' = not applicable -> NaN
    df['source_table'] = kind
    return df


def main():
    frames = []
    for y in YEARS:
        s = read_member(y, 'Sales_Ult_Cust', 'States')
        frames.append(s)
        dcomp = read_member(y, 'Delivery_Companies', 0)
        if dcomp is not None:
            frames.append(dcomp)
        print(y, 'rows', len(s), 'delivery_companies', 0 if dcomp is None else len(dcomp), file=sys.stderr)
    allr = pd.concat(frames, ignore_index=True, sort=False)
    allr['year'] = allr['year'].astype(int)
    keep = ['res_sales_mwh', 'com_sales_mwh', 'ind_sales_mwh', 'tot_sales_mwh', 'com_customers', 'ind_customers',
            'com_revenue_thousand_usd', 'ind_revenue_thousand_usd']
    out = []
    # --- utilities
    for uid, st, label, hotspot, parent in HOTSPOTS:
        sub = allr[(allr.eia_utility_id == uid) & (allr.state == st) & (allr.part.isin(['A', 'C', 'D']))]
        if sub.empty:
            print('MISSING', uid, st, label, file=sys.stderr)
            continue
        g = sub.groupby('year')[keep].sum(min_count=1).reset_index()
        parts = sub.groupby('year')['part'].apply(lambda p: '+'.join(sorted(set(p)))).reset_index()
        g = g.merge(parts, on='year')
        g['entity_type'] = 'utility'
        g['eia_utility_id'] = uid
        g['utility_name_eia'] = sub.sort_values('year')['utility_name'].iloc[-1]
        g['label'] = label
        g['hotspot'] = hotspot
        g['parent'] = parent
        g['state'] = st
        g['ba_code'] = sub.sort_values('year')['ba_code'].iloc[-1]
        g['method'] = 'EIA-861 sum of Parts ' + g['part'] + ' (bundled + delivery-only; energy-only Part B excluded)'
        out.append(g.drop(columns=['part']))
    # --- states (A+B+D)
    sts = allr[(allr.source_table == 'Sales_Ult_Cust') & (allr.part.isin(['A', 'B', 'D']))]
    for st in STATES + ['US']:
        sub = sts if st == 'US' else sts[sts.state == st]
        g = sub.groupby('year')[keep].sum(min_count=1).reset_index()
        g['entity_type'] = 'state' if st != 'US' else 'national'
        g['eia_utility_id'] = None
        g['utility_name_eia'] = None
        g['label'] = f'{st} statewide (all utilities and retailers)' if st != 'US' else 'United States (50 states + DC)'
        g['hotspot'] = None
        g['parent'] = None
        g['state'] = st
        g['ba_code'] = None
        g['method'] = 'EIA-861 state total = Parts A+B+D (EIA convention)'
        out.append(g)
    df = pd.concat(out, ignore_index=True, sort=False)
    df['ci_sales_mwh'] = df['com_sales_mwh'].fillna(0) + df['ind_sales_mwh'].fillna(0)
    df['ci_share_of_total_pct'] = (100 * df['ci_sales_mwh'] / df['tot_sales_mwh']).round(2)
    # growth vs base year
    key = ['entity_type', 'eia_utility_id', 'state', 'label']
    df['eia_utility_id'] = df['eia_utility_id'].astype('object')
    res = []
    for _, g in df.groupby(['entity_type', 'state', 'label'], sort=False):
        g = g.sort_values('year').copy()
        base = g.iloc[0]
        g['base_year'] = int(base['year'])
        for c in ['com_sales_mwh', 'ind_sales_mwh', 'ci_sales_mwh', 'res_sales_mwh', 'tot_sales_mwh']:
            b = base[c]
            g[c.replace('_sales_mwh', '_growth_pct_vs_base')] = ((g[c] / b - 1) * 100).round(2) if b and b == b and b != 0 else None
        g['ci_added_twh_vs_base'] = ((g['ci_sales_mwh'] - base['ci_sales_mwh']) / 1e6).round(3)
        g['tot_added_twh_vs_base'] = ((g['tot_sales_mwh'] - base['tot_sales_mwh']) / 1e6).round(3)
        g['com_yoy_pct'] = (g['com_sales_mwh'].pct_change() * 100).round(2)
        g['ci_yoy_pct'] = (g['ci_sales_mwh'].pct_change() * 100).round(2)
        res.append(g)
    df = pd.concat(res, ignore_index=True, sort=False)
    df['source'] = 'EIA-861 annual electric power industry report, Sales_Ult_Cust and Delivery_Companies tables (final data); https://www.eia.gov/electricity/data/eia861/'
    df['data_status'] = 'final'
    cols = ['entity_type', 'eia_utility_id', 'label', 'utility_name_eia', 'parent', 'state', 'ba_code', 'hotspot', 'year', 'base_year',
            'res_sales_mwh', 'com_sales_mwh', 'ind_sales_mwh', 'ci_sales_mwh', 'tot_sales_mwh', 'ci_share_of_total_pct',
            'com_customers', 'ind_customers',
            'com_growth_pct_vs_base', 'ind_growth_pct_vs_base', 'ci_growth_pct_vs_base', 'res_growth_pct_vs_base',
            'tot_growth_pct_vs_base', 'ci_added_twh_vs_base', 'tot_added_twh_vs_base', 'com_yoy_pct', 'ci_yoy_pct',
            'method', 'source', 'data_status']
    df = df[cols]
    df.to_csv(OUT, index=False)
    print('wrote', OUT, len(df), 'rows', file=sys.stderr)
    # summary to stdout
    last = df[df.year == df.year.max()]
    pd.set_option('display.width', 250)
    sys.stdout.buffer.write(last[['label', 'state', 'base_year', 'com_sales_mwh', 'ind_sales_mwh', 'ci_growth_pct_vs_base', 'com_growth_pct_vs_base',
                                  'res_growth_pct_vs_base', 'tot_growth_pct_vs_base', 'ci_added_twh_vs_base']].to_string().encode('utf-8'))


if __name__ == '__main__':
    main()
