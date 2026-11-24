"""Build EIA-861 (2025) lookups for the geo join layer.

Run:  python3 -I scripts/geo/build_eia861_lookup.py   (from the ai-power-tax folder or anywhere)

Inputs (untouched downloads):
  data/raw/geo/eia861_2025/f8612025.zip              https://www.eia.gov/electricity/data/eia861/zip/f8612025.zip
  data/raw/geo/census_county_codes/national_county2020.txt   https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt
Outputs:
  data/processed/geo_eia861_utilities.csv   one row per (eia_utility_id, state): name, ownership, RTO flags (EIA-861 Utility_Data 2025)
  data/processed/geo_county_to_utility.csv  one row per (county, utility): county FIPS + EIA-861 Service_Territory 2025
"""
import io
import os
import re
import sys
import unicodedata
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ZIP = os.path.join(ROOT, 'data/raw/geo/eia861_2025/f8612025.zip')
CNTY = os.path.join(ROOT, 'data/raw/geo/census_county_codes/national_county2020.txt')
OUT_UTIL = os.path.join(ROOT, 'data/processed/geo_eia861_utilities.csv')
OUT_CNTY = os.path.join(ROOT, 'data/processed/geo_county_to_utility.csv')
YEAR = 2025

z = zipfile.ZipFile(ZIP)


def read_sheets(name):
    x = pd.ExcelFile(io.BytesIO(z.read(name)), engine='openpyxl')
    return x


# ---------- Utility_Data: ownership + RTO participation ----------
x = read_sheets('Utility_Data_%d.xlsx' % YEAR)
frames = []
for s in x.sheet_names:
    d = pd.read_excel(x, sheet_name=s, header=1)
    frames.append(d)
ud = pd.concat(frames, ignore_index=True)
ud = ud[pd.to_numeric(ud['Utility Number'], errors='coerce').notna()].copy()
ud['eia_utility_id'] = ud['Utility Number'].astype(int)
# RTO columns: second 'SPP' is the RTO flag (pandas renames it SPP.1)
rto_cols = {'CAISO': 'CAISO', 'ERCOT': 'ERCOT', 'PJM': 'PJM', 'NYISO': 'NYISO', 'SPP.1': 'SPP', 'MISO': 'MISO', 'ISONE': 'ISO-NE'}


def rtos(row):
    return ';'.join(v for k, v in rto_cols.items() if k in row and str(row[k]).strip().upper() == 'Y')


ud['rto_iso'] = ud.apply(rtos, axis=1)
util = ud[['eia_utility_id', 'Utility Name', 'State', 'Ownership Type', 'NERC Region', 'rto_iso', 'Distribution', 'Bundled', 'Retail Marketing']].rename(columns={
    'Utility Name': 'utility_name', 'State': 'state', 'Ownership Type': 'ownership', 'NERC Region': 'nerc_region',
    'Distribution': 'does_distribution', 'Bundled': 'bundled_service', 'Retail Marketing': 'retail_marketing'})
util['in_utility_data'] = True
# Frame lists every respondent (incl. short-form utilities missing from Utility_Data) with ownership
fr = pd.read_excel(read_sheets('Frame_%d.xlsx' % YEAR), sheet_name=0)
fr = fr[pd.to_numeric(fr['Utility Number'], errors='coerce').notna()].copy()
fr['eia_utility_id'] = fr['Utility Number'].astype(int)
sf = pd.read_excel(read_sheets('Short_Form_%d.xlsx' % YEAR), sheet_name=0)
sf_state = dict(zip(pd.to_numeric(sf['Utility Number'], errors='coerce'), sf['State']))
extra = fr[~fr.eia_utility_id.isin(util.eia_utility_id)]
extra = pd.DataFrame({'eia_utility_id': extra.eia_utility_id, 'utility_name': extra['Utility Name'],
                      'state': extra.eia_utility_id.map(sf_state), 'ownership': extra['Ownership'], 'in_utility_data': False})
util = pd.concat([util, extra], ignore_index=True, sort=False)
util.insert(0, 'year', YEAR)
util = util.sort_values(['eia_utility_id', 'state'])
util.to_csv(OUT_UTIL, index=False)
print('utilities rows', len(util), 'unique ids', util.eia_utility_id.nunique())

# ---------- Service_Territory: utility x county ----------
x = read_sheets('Service_Territory_%d.xlsx' % YEAR)
st = pd.concat([pd.read_excel(x, sheet_name=s) for s in x.sheet_names], ignore_index=True)
st = st[pd.to_numeric(st['Utility Number'], errors='coerce').notna()].copy()
st['eia_utility_id'] = st['Utility Number'].astype(int)


def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()
    s = s.replace('&', 'and')
    s = re.sub(r'\b(county|parish|borough|city and borough|census area|municipality|municipio|planning region)\b', ' ', s)
    s = re.sub(r'\bsaint\b', 'st', s)
    s = re.sub(r'\bste\b', 'ste', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s


c = pd.read_csv(CNTY, sep='|', dtype=str)
c['county_fips'] = c.STATEFP + c.COUNTYFP
c['key'] = c.STATE + '|' + c.COUNTYNAME.map(norm)
# independent cities: 'X city' vs county 'X County' in same state -> keep 'city' suffix distinguishable
c['is_city'] = c.COUNTYNAME.str.lower().str.endswith(' city')
c.loc[c.is_city, 'key'] = c.loc[c.is_city, 'key'] + 'city'
lut = dict(zip(c.key, c.county_fips))
name_lut = dict(zip(c.county_fips, c.COUNTYNAME))


def fips_for(state, county):
    raw = str(county)
    k = state + '|' + norm(raw)
    if raw.lower().strip().endswith(' city'):
        # EIA writes e.g. 'Richmond City'; norm() keeps 'city' in the string already
        k2 = state + '|' + norm(raw[:-5]) + 'city'
        if k2 in lut:
            return lut[k2]
    if k in lut:
        return lut[k]
    # EIA sometimes drops 'city' for independent cities with no same-named county
    if k + 'city' in lut:
        return lut[k + 'city']
    return None


st['county_fips'] = [fips_for(s, cn) for s, cn in zip(st.State, st.County)]
st['county_name_census'] = st.county_fips.map(name_lut)
out = st[['State', 'county_fips', 'County', 'county_name_census', 'eia_utility_id', 'Utility Name', 'Short Form']].rename(columns={
    'State': 'state', 'County': 'county_name_eia', 'Utility Name': 'utility_name', 'Short Form': 'short_form'})
own = util.drop_duplicates(['eia_utility_id', 'state']).set_index(['eia_utility_id', 'state'])['ownership']
out['ownership'] = [own.get((i, s)) for i, s in zip(out.eia_utility_id, out.state)]
out.insert(0, 'year', YEAR)
out = out.sort_values(['state', 'county_fips', 'eia_utility_id'])
out.to_csv(OUT_CNTY, index=False)
miss = out[out.county_fips.isna()]
print('county rows', len(out), 'unmatched county names', len(miss), 'unique counties', out.county_fips.nunique())
if len(miss):
    print(miss.groupby(['state', 'county_name_eia']).size().head(60).to_string())
