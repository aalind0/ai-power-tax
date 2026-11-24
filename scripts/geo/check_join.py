"""Join-rate check: HIFLD territory ids vs EIA-861 utility ids (and the bills agent's utility price table).

Run: python3 -I scripts/geo/check_join.py
Reads data/raw/geo/hifld_retail_territories/*.geojson, data/raw/geo/eia861_2025/f8612025.zip,
data/processed/bills_utility_prices.csv (bills area, read-only). Prints rates; writes nothing.
"""
import io
import json
import os
import zipfile

import pandas as pd

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/'
with open(R + 'data/raw/geo/hifld_retail_territories/electric_retail_service_territories.geojson', encoding='utf-8') as fh:
    g = json.load(fh)
rows = [(f['properties']['ID'], f['properties']['NAME'], f['properties']['STATE'], f['properties']['TYPE'], f['properties']['CUSTOMERS']) for f in g['features']]
h = pd.DataFrame(rows, columns=['id', 'name', 'state', 'type', 'cust'])
h = h[h.id.str.isdigit()].copy()
h['id'] = h.id.astype(int)
h['cust'] = h.cust.fillna(0).clip(lower=0)
z = zipfile.ZipFile(R + 'data/raw/geo/eia861_2025/f8612025.zip')


def ids(n, _hdr=None):
    """All utility ids in every sheet of an EIA-861 workbook (header row located automatically)."""
    x = pd.ExcelFile(io.BytesIO(z.read(n)), engine='openpyxl')
    s = set()
    for sh in x.sheet_names:
        top = pd.read_excel(x, sheet_name=sh, header=None, nrows=6)
        hdr = next((i for i in range(len(top)) if top.iloc[i].astype(str).str.contains('Utility Number').any()), None)
        if hdr is None:
            continue
        d = pd.read_excel(x, sheet_name=sh, header=hdr)
        col = [c for c in d.columns if 'Utility Number' in str(c)][0]
        s |= set(pd.to_numeric(d[col], errors='coerce').dropna().astype(int))
    return s


U = ids('Utility_Data_2025.xlsx', 1)
S = ids('Short_Form_2025.xlsx', 0)
SA = ids('Sales_Ult_Cust_2025.xlsx', 2)
ST = ids('Service_Territory_2025.xlsx', 0)
FR = ids('Frame_2025.xlsx', 0)
sets = [('EIA-861 2025 Utility_Data', U), ('EIA-861 2025 Short_Form', S), ('EIA-861 2025 Sales_Ult_Cust', SA),
        ('EIA-861 2025 Service_Territory', ST), ('EIA-861 2025 Frame', FR), ('UtilData|ShortForm|Sales 2025', U | S | SA)]
bp = R + 'data/processed/bills_utility_prices.csv'
b = None
if os.path.exists(bp):
    b = pd.read_csv(bp)
    sets += [('bills_utility_prices any year', set(b.eia_utility_id.dropna().astype(int))),
             ('bills_utility_prices 2024', set(b[b.year == 2024].eia_utility_id.astype(int))),
             ('bills_utility_prices 2025', set(b[b.year == 2025].eia_utility_id.astype(int)))]
xw = pd.read_csv(R + 'data/processed/geo_utility_id_crosswalk.csv')
xmap = dict(zip(xw.territory_eia_utility_id, xw.current_eia_utility_id))
h['id_current'] = h.id.map(lambda i: xmap.get(i, i))
tot = len(h)
tc = h.cust.sum()
print('HIFLD US features with numeric id:', tot, ' customers (HIFLD 2022):', int(tc))
for nm, s in sets:
    m = h.id.isin(s)
    m2 = h.id_current.isin(s)
    print('%-34s ids %4d/%d = %5.1f%%  cust-weighted %5.1f%%  | with merger crosswalk %4d = %5.1f%%, cust-weighted %5.1f%%  (set size %d)' % (
        nm, m.sum(), tot, 100 * m.mean(), 100 * h.cust[m].sum() / tc, m2.sum(), 100 * m2.mean(), 100 * h.cust[m2].sum() / tc, len(s)))
allset = U | S | SA | FR
print('\nHIFLD ids not in any EIA-861 2025 file (largest by customers):')
print(h[~h.id.isin(allset)].sort_values('cust', ascending=False).head(12).to_string(index=False))
if b is not None:
    for yr in (2024, 2025):
        by = b[(b.year == yr) & (b.res_customers > 0)]
        r = by.eia_utility_id.astype(int).isin(set(h.id)).values
        print('\nReverse, bills %d utilities with residential customers found in HIFLD: %d/%d (%.1f%%), residential-customer weighted %.1f%%' % (
            yr, r.sum(), len(r), 100 * r.mean(), 100 * by.res_customers[r].sum() / by.res_customers.sum()))
        print(by[~r].sort_values('res_customers', ascending=False)[['eia_utility_id', 'utility_name', 'state', 'ownership', 'basis', 'res_customers']].head(12).to_string(index=False))
