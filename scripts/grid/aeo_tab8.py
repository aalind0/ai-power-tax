"""Extract 'Prices by Service Category' (generation / transmission / distribution, cents/kWh) from an
EIA AEO table-8 xlsx. Usage: python3 -I scripts/grid/aeo_tab8.py <aeotab8.xlsx>
Prints edition, column years, and the real + nominal G/T/D rows."""
import sys
import pandas as pd
x = pd.read_excel(sys.argv[1], header=None, engine='openpyxl')
hdr = None
for i, r in x.iterrows():
    s = ' '.join(str(v) for v in r.values[:4])
    if 'Annual Energy Outlook' in s or 'Release Date' in s:
        print('META', [str(v) for v in r.values[:6] if str(v) != 'nan'])
    if hdr is None and 'Supply, Disposition' in str(r[1]):
        hdr = [str(v) for v in r.values]
        print('YEARS', hdr[2:9], '...')
    lab = str(r[0])
    if any(k in lab for k in ['_Generation', '_Transmission', '_Distribution', 'AllSectorsAv']) and ('ka_' in lab or 'nom_' in lab or 'ja_' in lab):
        print(lab, [round(float(v), 3) if str(v) not in ('nan', '- -') else None for v in r.values[2:9]], str(r[1]).strip())
