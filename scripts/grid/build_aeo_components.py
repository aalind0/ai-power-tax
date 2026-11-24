"""Build a generation / transmission / distribution price-component trend (all sectors, nominal cents/kWh) from
EIA Annual Energy Outlook Table 8 ("Prices by Service Category"), editions AEO2014-AEO2026 (no AEO2024 was published).
For every edition we keep the columns for years <= edition-1 (history or the edition's base-year estimate); for each
calendar year the most recent edition wins. Output: data/raw/grid/_derived_csv/aeo_components.csv
Run: python3 -I scripts/grid/build_aeo_components.py"""
import glob
import re
import pandas as pd

recs = []
for f in sorted(glob.glob('data/raw/grid/eia_aeo20??_tab8/*.xlsx')):
    ed = int(re.search(r'aeo(20\d\d)_tab8', f).group(1))
    x = pd.read_excel(f, header=None, engine='openpyxl').astype(str)
    # locate label column + header row
    lab_col, hdr = None, None
    for i in range(len(x)):
        for c in range(3):
            if 'Supply, Disposition, Prices' in x.iat[i, c] and hdr is None and any(re.match(r'^20\d\d', v) for v in x.iloc[i].values):
                lab_col, hdr = c, i
    years = {}
    for c in range(lab_col + 1, x.shape[1]):
        m = re.match(r'^(20\d\d)(\.0)?$', x.iat[hdr, c].strip())
        if m:
            years[c] = int(m.group(1))
    # rows under 'Prices by Service Category': first block = real (base-year $), second block = nominal
    start = [i for i in range(len(x)) if 'Prices by Service Category' in x.iat[i, lab_col]][0]
    block = {}
    for i in range(start, start + 12):
        lab = x.iat[i, lab_col].strip()
        if lab in ('Generation', 'Transmission', 'Distribution'):
            block.setdefault(lab, []).append(i)
    # 'All Sectors Average' rows: first = real, last = nominal
    avg_rows = [i for i in range(len(x)) if x.iat[i, lab_col].strip() == 'All Sectors Average']
    for c, yr in years.items():
        if yr > ed - 1:
            continue
        def val(i):
            try:
                return round(float(x.iat[i, c]), 3)
            except ValueError:
                return None
        recs.append(dict(year=yr, aeo_edition=ed,
                         generation_cents_kwh=val(block['Generation'][-1]),
                         transmission_cents_kwh=val(block['Transmission'][-1]),
                         distribution_cents_kwh=val(block['Distribution'][-1]),
                         all_sectors_avg_cents_kwh=val(avg_rows[-1]) if avg_rows else None,
                         basis='estimate (edition base year)' if yr == ed - 1 else 'history'))
df = pd.DataFrame(recs).sort_values(['year', 'aeo_edition'])
best = df.groupby('year').tail(1).copy()
s = best.generation_cents_kwh + best.transmission_cents_kwh + best.distribution_cents_kwh
best['transmission_share_pct'] = (best.transmission_cents_kwh / s * 100).round(1)
best['distribution_share_pct'] = (best.distribution_cents_kwh / s * 100).round(1)
best['td_share_pct'] = ((best.transmission_cents_kwh + best.distribution_cents_kwh) / s * 100).round(1)
print(df.to_string())
print(best.to_string())
best.to_csv('data/raw/grid/_derived_csv/aeo_components.csv', index=False)
