"""Build data/processed/grid_transmission_rates.csv: PJM zonal Network Integration Transmission Service (NITS)
rates, $/MW-year, 2015-2026 (+ latest posting Oct 2026).

Sources:
  2015-2021: Electricity Transmission Competition Coalition (ETCC) table compiled from PJM transmission owners'
             annual formula-rate informational filings (values typed from the PDF; checked against PJM postings
             for 2021-2024 where both exist). ETCC is an advocacy coalition (pro-competitive transmission).
  2022-2026: PJM 'ATRR and NITS Rates' postings (billing-settlements-and-credit page), PDF text + xlsx.
Annual value = rate in effect on 1 July of that year (after both January and June annual updates) — the same
convention as the ETCC table. Run: python3 -I scripts/grid/build_transmission_rates.py
"""
import re
import pandas as pd

# ---- ETCC 2015-2024 (zone label in ETCC -> PJM zone code) ----
ETCC = """AECO 40731 36810 NA 53775 56171 45693 66741 79876 91559 103398 June
AEP 41438 41438 56991 59818 65923 80306 95598 110857 123925 125467 January
APS 17895 17895 17895 17895 17895 17895 13930 18162 16760 17115 January
ATSI 37014 43391 45058 54689 55185 57482 66399 67421 66479 87624 January
BGE 25237 27285 32851 35762 29860 31311 40962 45531 46400 55851 June
ComEd 31470 35544 34392 34516 33116 34280 37749 36069 39796 38531 June
DAY 13296 13296 13296 13296 12561 14456 19203 18410 18687 32782 January
DEOK 17039 19881 20055 24077 25840 32143 35136 37718 40717 45820 June
DUQ 38880 50695 47892 51954 49200 53072 51001 60851 63330 63699 June
DOM 42902 41245 47376 52457 47471 54914 61729 62645 64053 68235 January
DPL 34807 30298 32938 42812 44803 33000 46184 49476 55166 61897 June
EKPC 25753 21334 26424 24441 30251 23763 26038 28271 34784 30818 June
JCPL 15112 15112 23232 23597 22588 24354 27327 27008 27304 37937 January
ME 15112 15112 22612 25132 28796 37083 50128 45113 52088 73260 January
PECO 20942 20942 20942 19093 18922 16022 19517 22998 25648 25611 June
PENELEC 15112 15112 22612 25132 28796 37083 50128 45113 52088 73260 January
PEPCO 26521 23232 25229 31304 33874 28022 31497 37199 42675 54821 Jan/Jun
PPL 34595 41952 61792 58865 68031 75204 90836 88606 95644 104055 Jan/Jun
PSEG 96521 110916 120931 130535 119736 156503 172190 159248 164719 180898 January
RECO 32114 32114 49695 44799 42548 42548 42458 51530 51530 53766 STATED"""
YEARS = list(range(2015, 2025))
etcc = {}
for line in ETCC.splitlines():
    p = line.split()
    for y, v in zip(YEARS, p[1:11]):
        etcc[(p[0], y)] = None if v == 'NA' else float(v)
etcc_eff = {line.split()[0]: line.split()[-1] for line in ETCC.splitlines()}

# ---- PJM postings ----
ORDER_2023 = ['AECO', 'AEP', 'APS', 'ATSI', 'BGE', 'ComEd', 'DAY', 'DEOK', 'DOM', 'DOM_UG', 'DPL', 'DUQ', 'EKPC', 'JCPL',
              'ME', 'PENELEC', 'OVEC', 'PECO', 'PEPCO', 'PPL', 'PSEG', 'RECO']
ORDER_2022 = ['AECO', 'AEP', 'APS', 'ATSI', 'BGE', 'ComEd', 'DAY', 'DEOK', 'DUQ', 'DOM', 'DOM_UG', 'DPL', 'EKPC', 'JCPL',
              'ME', 'PENELEC', 'OVEC', 'PECO', 'PEPCO', 'PPL', 'PSEG', 'RECO']
num = re.compile(r'\d{1,3}(?:,\d{3})*\.\d{2}')
pjm = {}  # (zone, as_of) -> rate
for yr in [2022, 2023, 2024, 2025]:
    t = open('data/raw/grid/_text/pjm_nits_%d.txt' % yr, encoding='utf-8').read()
    for page in t.split('=== PAGE ')[1:]:
        m = re.search(r'As of\s+(\d{1,2})/(\d{1,2})/(\d{4})', page)
        if not m:
            continue
        asof = '%s-%02d-%02d' % (m.group(3), int(m.group(1)), int(m.group(2)))
        rates = [float(v.replace(',', '')) for v in num.findall(page) if float(v.replace(',', '')) < 300000]
        order = ORDER_2022 if yr == 2022 else ORDER_2023
        if len(rates) != len(order):
            print('skip', yr, asof, len(rates))
            continue
        for z, r in zip(order, rates):
            pjm[(z, asof)] = r
atrr = {}
for f, sheet, asof in [('january-2026', 'January 2026 (updated)', '2026-01-01'), ('june-2026', 'June 2026', '2026-06-01'),
                       ('october-2026', 'October 2026', '2026-10-01')]:
    path = 'data/raw/grid/pjm_network-integration-trans-service-%s-xls/network-integration-trans-service-%s-xls.xlsx' % (f, f)
    x = pd.read_excel(path, sheet_name=sheet, header=None, engine='openpyxl')
    z = None
    for i, r in x.iterrows():
        c0 = str(r[0]).strip()
        if c0 != 'nan' and not c0.startswith(('Annual', 'Transmission Zone', 'As of', '*')):
            z = c0
        if str(r[4]) != 'nan' and 'Rate' not in str(r[4]):
            zz = {'DOM': 'DOM'}.get(z, z)
            if z == 'DOM' and float(r[4]) < 2000:
                zz = 'DOM_UG'
            pjm[(zz, asof)] = round(float(r[4]), 2)
            if str(r[3]) != 'nan':
                atrr[(zz, asof)] = float(r[3])

ZONES = {
    'AECO': ('Atlantic City Electric', 'NJ'), 'AEP': ('AEP East (Appalachian Power, Ohio Power, Indiana Michigan, Kentucky Power, Wheeling, Kingsport + AEP transcos)', 'OH;WV;VA;IN;MI;KY;TN'),
    'APS': ('Allegheny Power (Potomac Edison, Mon Power, West Penn)', 'PA;MD;WV;VA'), 'ATSI': ('American Transmission Systems (FirstEnergy Ohio + Penn Power)', 'OH;PA'),
    'BGE': ('Baltimore Gas and Electric', 'MD'), 'ComEd': ('Commonwealth Edison', 'IL'), 'DAY': ('Dayton Power & Light (AES Ohio)', 'OH'),
    'DEOK': ('Duke Energy Ohio/Kentucky', 'OH;KY'), 'DOM': ('Dominion Energy Virginia (Virginia Electric and Power)', 'VA;NC'),
    'DPL': ('Delmarva Power & Light', 'DE;MD;VA'), 'DUQ': ('Duquesne Light', 'PA'), 'EKPC': ('East Kentucky Power Cooperative', 'KY'),
    'JCPL': ('Jersey Central Power & Light', 'NJ'), 'ME': ('Met-Ed (FirstEnergy PA; MAIT)', 'PA'), 'PENELEC': ('Penelec (FirstEnergy PA; MAIT)', 'PA'),
    'OVEC': ('Ohio Valley Electric Corp', 'OH;IN'), 'PECO': ('PECO Energy', 'PA'), 'PEPCO': ('Potomac Electric Power', 'DC;MD'),
    'PPL': ('PPL Electric Utilities', 'PA'), 'PSEG': ('Public Service Electric & Gas', 'NJ'), 'RECO': ('Rockland Electric', 'NJ'),
}
rows = []
for z, (name, st) in ZONES.items():
    for y in range(2015, 2027):
        rate, asof, src, note = None, None, None, ''
        if y >= 2022:
            cands = sorted(k[1] for k in pjm if k[0] == z and k[1] <= '%d-07-01' % y)
            if cands and cands[-1][:4] == str(y) or (cands and y >= 2022):
                asof = cands[-1] if cands else None
                rate = pjm[(z, asof)] if asof else None
                src = 'PJM ATRR & NITS rates posting'
            e = etcc.get((z, y))
            if e is not None and rate is not None and abs(e - rate) > 2:
                note = 'ETCC table shows %d' % e
        else:
            rate = etcc.get((z, y))
            src = 'ETCC compilation of PJM TO formula-rate filings'
            asof = '%d (%s update)' % (y, etcc_eff.get(z, '?'))
            if z == 'AECO' and y == 2017:
                note = 'value truncated in ETCC source PDF'
        if z == 'OVEC' and y < 2022:
            continue
        rows.append(dict(iso='PJM', zone=z, zone_name=name, states=st, year=y, period='mid-year (in effect 1 Jul)', nits_rate_usd_per_mw_yr=rate,
                         usd_per_kw_month=None if rate is None else round(rate / 1000 / 12, 2),
                         as_of=asof, zonal_atrr_usd=atrr.get((z, asof)), source=src, verified=rate is not None, note=note))
    # latest posting
    if (z, '2026-10-01') in pjm:
        r = pjm[(z, '2026-10-01')]
        rows.append(dict(iso='PJM', zone=z, zone_name=name, states=st, year=2026, period='latest (posting as of 2026-10-01)', nits_rate_usd_per_mw_yr=r,
                         usd_per_kw_month=round(r / 12000, 2), as_of='2026-10-01', zonal_atrr_usd=atrr.get((z, '2026-10-01')),
                         source='PJM ATRR & NITS rates posting (latest)', verified=True, note=''))
df = pd.DataFrame(rows)
# growth columns
base = df[(df.year == 2015)].set_index('zone').nits_rate_usd_per_mw_yr
df['pct_change_vs_2015'] = df.apply(lambda r: None if pd.isna(r.nits_rate_usd_per_mw_yr) or pd.isna(base.get(r.zone)) else round((r.nits_rate_usd_per_mw_yr / base[r.zone] - 1) * 100, 1), axis=1)
df.to_csv('data/processed/grid_transmission_rates.csv', index=False)
w = df[df.year.isin([2015, 2020, 2024, 2025, 2026]) & df.period.str.startswith('mid')].pivot_table(index='zone', columns='year', values='nits_rate_usd_per_mw_yr')
w['x2015_2026'] = (w[2026] / w[2015]).round(2)
print(w.round(0).to_string())
print(df[df.note != ''][['zone', 'year', 'nits_rate_usd_per_mw_yr', 'note']].to_string())
print(len(df))
