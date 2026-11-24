"""Build data/processed/geo_zip_to_utility.csv from NREL/NLR OpenEI 'Look-up by Zip Code (2025)'.

Run: python3 -I scripts/geo/build_zip_to_utility.py
Input : data/raw/geo/openei_zip_utility_2025/{iou,non_iou}_zipcodes_2025.csv
        (https://data.openei.org/submissions/10259, CC-BY-4.0, published 2026-11-05)
        data/processed/geo_eia861_utilities.csv (for the id join-rate check)
Output: data/processed/geo_zip_to_utility.csv
  zip (5-char string), eia_utility_id, utility_name, state, service_type, ownership,
  res_rate_usd_kwh, comm_rate_usd_kwh, ind_rate_usd_kwh  (utility-wide averages = revenue/sales from EIA-861 2025,
  NOT zip-specific; 0 in the source = no sales in that class -> written as blank), n_utilities_in_zip, source_file, data_year
"""
import os

import pandas as pd

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/'
RAW = R + 'data/raw/geo/openei_zip_utility_2025/'
frames = []
for f in ('iou_zipcodes_2025.csv', 'non_iou_zipcodes_2025.csv'):
    d = pd.read_csv(RAW + f, dtype={'zip': str})
    d['source_file'] = f
    frames.append(d)
d = pd.concat(frames, ignore_index=True)
n_in = len(d)
d['zip'] = d['zip'].str.strip().str.zfill(5)
d = d.rename(columns={'eiaid': 'eia_utility_id', 'res_rate': 'res_rate_usd_kwh', 'comm_rate': 'comm_rate_usd_kwh', 'ind_rate': 'ind_rate_usd_kwh'})
for c in ('res_rate_usd_kwh', 'comm_rate_usd_kwh', 'ind_rate_usd_kwh'):
    d[c] = pd.to_numeric(d[c], errors='coerce')
    d.loc[d[c] <= 0, c] = None
    d[c] = d[c].round(5)
d = d.drop_duplicates(['zip', 'eia_utility_id', 'service_type'])
d['n_utilities_in_zip'] = d.groupby('zip')['eia_utility_id'].transform('nunique')
d['data_year'] = 2025
cols = ['zip', 'eia_utility_id', 'utility_name', 'state', 'service_type', 'ownership', 'res_rate_usd_kwh', 'comm_rate_usd_kwh',
        'ind_rate_usd_kwh', 'n_utilities_in_zip', 'source_file', 'data_year']
d = d[cols].sort_values(['zip', 'eia_utility_id'])
d.to_csv(R + 'data/processed/geo_zip_to_utility.csv', index=False)

print('rows in', n_in, 'rows out', len(d), 'unique zips', d.zip.nunique(), 'unique utilities', d.eia_utility_id.nunique())
print('service_type', d.service_type.value_counts().to_dict())
print('ownership', d.ownership.value_counts().to_dict())
z = d.groupby('zip').eia_utility_id.nunique()
print('utilities per zip: 1 -> %.1f%%, 2 -> %.1f%%, 3+ -> %.1f%%' % (100 * (z == 1).mean(), 100 * (z == 2).mean(), 100 * (z >= 3).mean()))
print('rows with residential rate', d.res_rate_usd_kwh.notna().mean())
u = pd.read_csv(R + 'data/processed/geo_eia861_utilities.csv')
m = d.eia_utility_id.isin(set(u.eia_utility_id))
print('ids found in EIA-861 2025 Frame/Utility_Data: rows %.1f%%, unique ids %d/%d' % (100 * m.mean(), d[m].eia_utility_id.nunique(), d.eia_utility_id.nunique()))
