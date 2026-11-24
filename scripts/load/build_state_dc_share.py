"""Build data-center share of electricity consumption by state + US totals.

Run from the project root:  python3 -I scripts/load/build_state_dc_share.py

Inputs (downloaded with scripts/load/fetch.mjs, text extracted with scripts/load/pdf2txt.js):
  data/raw/load/_text/epri_2024.txt   EPRI (May 2024) Powering Intelligence, Table A1 (2023 state load + 2030 scenarios)
      PDF: https://restservice.epri.com/publicdownload/000000003002028905/0/Product
  data/raw/load/_text/epri_2026.txt   EPRI (Feb 2026) Powering Intelligence 2026, Table 2 (state nominal IT capacity, MW)
      PDF: https://restservice.epri.com/publicdownload/000000003002034696/0/Product
  data/processed/load_utility_sales_growth.csv (built by build_utility_sales_growth.py; EIA-861 state totals for cross-check)
Outputs:
  data/processed/load_state_dc_share.csv
  data/processed/load_state_dc_capacity_mw.csv
"""
import io
import os
import re
import sys

import pandas as pd

ROOT = os.getcwd()
TXT = os.path.join(ROOT, 'data', 'raw', 'load', '_text')
OUT = os.path.join(ROOT, 'data', 'processed', 'load_state_dc_share.csv')
OUT_CAP = os.path.join(ROOT, 'data', 'processed', 'load_state_dc_capacity_mw.csv')
EIA = os.path.join(ROOT, 'data', 'processed', 'load_utility_sales_growth.csv')

EPRI24_URL = 'https://www.epri.com/research/products/000000003002028905'
EPRI26_URL = 'https://www.epri.com/research/products/000000003002034696'
LBNL24_URL = 'https://escholarship.org/uc/item/32d6m0d1'
LBNL25_URL = 'https://doi.org/10.71468/P1RP4F'
DOM_10K_URL = 'https://www.sec.gov/Archives/edgar/data/715957/000119312526063120/d-20251231.htm'

ABBR = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
        'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
        'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
        'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
        'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
        'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
        'Wisconsin': 'WI', 'Wyoming': 'WY'}

ROWS = []


def row(**k):
    base = dict(state=None, state_name=None, year=None, scenario=None, is_projection=False, dc_twh=None, dc_twh_low=None,
                dc_twh_high=None, total_twh=None, dc_share_pct=None, dc_share_pct_low=None, dc_share_pct_high=None,
                includes_crypto=None, source=None, source_url=None, method=None, verified=True, notes=None)
    base.update(k)
    ROWS.append(base)


def epri_2024():
    t = io.open(os.path.join(TXT, 'epri_2024.txt'), encoding='utf-8').read()
    a = t.find('Table A1. Projections to 2030')
    b = t.find('APPENDIX B', a)
    seg = t[a:b]
    names = '|'.join(sorted(ABBR, key=len, reverse=True))
    pair = r' ([\d,]+) ([\d.]+)%'
    pat = re.compile(r'^(' + names + r')' + pair * 5 + r'$', re.M)
    scen = [('2023_estimate', 2023, False, None), ('epri2024_low_3.71pct_cagr', 2030, True, 'Low growth (3.71%/yr)'),
            ('epri2024_moderate_5pct_cagr', 2030, True, 'Moderate growth (5%/yr)'),
            ('epri2024_high_10pct_cagr', 2030, True, 'High growth (10%/yr)'),
            ('epri2024_higher_15pct_cagr', 2030, True, 'Higher growth (15%/yr)')]
    n = 0
    for m in pat.finditer(seg):
        n += 1
        name = m.group(1)
        g = m.groups()[1:]
        for i, (sc, yr, proj, label) in enumerate(scen):
            mwh = float(g[2 * i].replace(',', ''))
            pct = float(g[2 * i + 1])
            row(state=ABBR[name], state_name=name, year=yr, scenario=sc, is_projection=proj,
                dc_twh=round(mwh / 1e6, 4), total_twh=round(mwh / 1e6 / (pct / 100), 3) if pct else None,
                dc_share_pct=pct, includes_crypto=False,
                source='EPRI (May 2024), Powering Intelligence: Analyzing Artificial Intelligence and Data Center Energy Consumption, Table A1',
                source_url=EPRI24_URL,
                method=('EPRI 2023 state data-center load (MWh/yr) and % of total state electricity consumed (%EC). '
                        'total_twh is implied (dc_twh / share), not published.' +
                        ('' if not proj else ' 2030 = national growth scenario applied to the state\'s 2023 load (' + label + '); not a state-specific forecast.')),
                notes='EPRI lists 44 states with significant data-center load in 2023; states not listed have no estimate (not zero).')
    assert n >= 40, n
    print('EPRI 2024 Table A1 states parsed:', n, file=sys.stderr)
    return n


def epri_2026_capacity():
    """Parse Table 2 (nominal IT capacity MW) - text extraction lists most state codes first, then the rows in order."""
    t = io.open(os.path.join(TXT, 'epri_2026.txt'), encoding='utf-8').read()
    a = t.find('Table 2. State-level data center nominal IT capacity (MW)')
    b = t.find('U.S. Total', a)
    seg = t[a:b + 200]
    lines = [l.strip() for l in seg.splitlines()]
    code_line = [l for l in lines if l.startswith('AZ CA CO')][0]
    codes = code_line.split()[:]
    # first numeric row is glued to the end of the code line
    num_tail = [x for x in code_line.split() if re.match(r'^[\d,.]+$', x)]
    codes = [x for x in code_line.split() if re.match(r'^[A-Z]{2}$', x)]
    explicit = {}
    numeric_rows = [num_tail]
    for l in lines:
        m = re.match(r'^([A-Z]{2})\s?([\d,.\s–-]+)$', l)
        if m and m.group(1) not in ('MW',):
            vals = re.findall(r'[\d,.]+|–', m.group(2))
            explicit[m.group(1)] = vals
            continue
        if re.match(r'^[\d,.]+( [\d,.]+){8}$', l):
            numeric_rows.append(l.split())
    # explicit lines that are full rows: AL, AK, AR, DE, ME, MS, MT, VT
    ordered = codes
    assert len(ordered) == len(numeric_rows), (len(ordered), len(numeric_rows))
    data = dict(zip(ordered, numeric_rows))
    for k, v in explicit.items():
        if k not in data:
            data[k] = v
    tot = re.search(r'U\.S\. Total ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+) ([\d,]+)', seg)
    cols = [(2021, 'point'), (2022, 'point'), (2023, 'point'), (2024, 'low'), (2024, 'medium'), (2024, 'high'),
            (2030, 'low'), (2030, 'medium'), (2030, 'high')]

    def num(x):
        if x in ('–', '-'):
            return None
        x = x.replace(',', '')
        if x.count('.') == 1 and len(x.split('.')[1]) == 3:  # '1.866' typo for 1,866 in source
            x = x.replace('.', '')
        return float(x)

    out = []
    for st, vals in data.items():
        v = [num(x) for x in vals]
        if len(v) == 6:  # rows printed with '–' for 2021-2023 collapse to 6 numbers + 3 dashes
            v = [None, None, None] + v
        if len(v) != 9:
            print('skip', st, vals, file=sys.stderr)
            continue
        for (yr, sc), x in zip(cols, v):
            out.append(dict(state=st, year=yr, scenario=sc, nominal_it_capacity_mw=x, is_projection=yr == 2030))
    cap = pd.DataFrame(out)
    us = [num(x) for x in tot.groups()]
    for (yr, sc), x in zip(cols, us):
        cap = cap.append(dict(state='US', year=yr, scenario=sc, nominal_it_capacity_mw=x, is_projection=yr == 2030), ignore_index=True)
    # check: state sum vs published US total (medium 2024)
    chk = cap[(cap.state != 'US') & (cap.year == 2024) & (cap.scenario == 'medium')].nominal_it_capacity_mw.sum()
    print('EPRI 2026 Table 2 states:', cap.state.nunique() - 1, '| sum of 2024 medium', chk, 'vs US total', us[4], file=sys.stderr)
    cap['includes_crypto'] = True
    cap['source'] = 'EPRI (Feb 2026), Powering Intelligence 2026, Table 2: State-level data center nominal IT capacity (MW)'
    cap['source_url'] = EPRI26_URL
    cap['notes'] = ('Nominal IT capacity (not grid draw, not energy). Includes small and large data centers and cryptocurrency mining. '
                    '2024 low/high = min/avg across commercial data sources; 2030 = pipeline completion scenarios (projection). '
                    'Parsed from PDF text; state sums match the published U.S. total for every column except 2023 '
                    '(states sum to 24,881 MW vs published 25,547 MW; IA 2023 = 160 MW between 707 MW in 2022 and 1,530 MW in 2024 looks like a source typo).')
    cap['verified'] = True
    cap.to_csv(OUT_CAP, index=False)
    return cap


def us_and_va_points():
    # --- LBNL 2024 report (Shehabi et al., Dec 2024)
    L24 = 'LBNL (Dec 2024), 2024 United States Data Center Energy Usage Report (Shehabi et al.)'
    for yr in (2014, 2015, 2016):
        row(state='US', state_name='United States', year=yr, scenario='lbnl2024_historical', dc_twh=60.0, includes_crypto=False,
            source=L24, source_url=LBNL24_URL, method='Bottom-up (server shipments x power x PUE). Text: "remained stable between 2014-2016 at about 60 TWh".',
            notes='Approximate; year-by-year values only shown in Figure ES-1.')
    row(state='US', state_name='United States', year=2018, scenario='lbnl2024_historical', dc_twh=76.0, dc_share_pct=1.9,
        total_twh=4000.0, includes_crypto=False, source=L24, source_url=LBNL24_URL,
        method='Bottom-up. total_twh implied (76/1.9%).')
    row(state='US', state_name='United States', year=2023, scenario='lbnl2024_historical', dc_twh=176.0, dc_share_pct=4.4,
        total_twh=4000.0, includes_crypto=False, source=L24, source_url=LBNL24_URL,
        method='Bottom-up. total_twh implied (176/4.4%).',
        notes='Revised down to ~168 TWh in the 2025 Update (lower GPU shipments, revised inference power).')
    row(state='US', state_name='United States', year=2028, scenario='lbnl2024_range', is_projection=True,
        dc_twh_low=325.0, dc_twh_high=580.0, dc_share_pct_low=6.7, dc_share_pct_high=12.0, includes_crypto=False,
        source=L24, source_url=LBNL24_URL,
        method='Scenario range (GPU shipments, AI server operation, cooling). Equivalent to 74-132 GW at 50% utilization.')
    # --- LBNL 2025 Update (Smith et al., June 2026)
    L25 = 'LBNL (June 2026), United States Data Center Energy Usage Report: 2025 Update (Smith et al., LBNL-2001758)'
    row(state='US', state_name='United States', year=2024, scenario='lbnl2025_historical', dc_twh=192.0, dc_share_pct=4.7,
        total_twh=round(192 / 0.047, 0), includes_crypto=False, source=L25, source_url=LBNL25_URL,
        method='Bottom-up; 2024 is the last historical year. total_twh implied.')
    row(state='US', state_name='United States', year=2023, scenario='lbnl2025_historical', dc_twh=round(192 / 1.14, 1), includes_crypto=False,
        source=L25, source_url=LBNL25_URL, verified=False,
        method='DERIVED: 192 TWh / 1.14 (report: "14% increase ... between 2023 and 2024"). Not published as a number.')
    row(state='US', state_name='United States', year=2025, scenario='lbnl2025_reference', is_projection=True,
        dc_twh=round(192 * 1.22, 0), includes_crypto=False, source=L25, source_url=LBNL25_URL, verified=False,
        method='DERIVED: 192 TWh x 1.22 (report: Reference Case +22% 2024->2025; shipment data only through Q3 2025, so 2025 is partly projected).')
    row(state='US', state_name='United States', year=2026, scenario='lbnl2025_reference', is_projection=True,
        dc_twh=round(192 * 1.22 * 1.29, 0), includes_crypto=False, source=L25, source_url=LBNL25_URL, verified=False,
        method='DERIVED: 2025 value x 1.29 (report: Reference Case +29% 2025->2026).')
    row(state='US', state_name='United States', year=2028, scenario='lbnl2025_reference', is_projection=True, dc_twh=464.0,
        includes_crypto=False, source=L25, source_url=LBNL25_URL, method='Reference Case; "falls in the middle of the range presented in the 2024 Report".')
    for sc, tw, pct in [('lbnl2025_reference', 649, 11.8), ('lbnl2025_consolidated_deployment', 578, 10.5),
                        ('lbnl2025_high_asic', 664, 12.1), ('lbnl2025_low_accelerator_lifetime', 590, 10.7),
                        ('lbnl2025_high_inference_energy', 782, 14.2), ('lbnl2025_compounded_low', 521, 9.5),
                        ('lbnl2025_compounded_high', 843, 15.3)]:
        row(state='US', state_name='United States', year=2030, scenario=sc, is_projection=True, dc_twh=float(tw), dc_share_pct=pct,
            total_twh=round(tw / (pct / 100), 0), includes_crypto=False, source=L25 + ', Table 2', source_url=LBNL25_URL,
            method='Share of 2030 U.S. electricity per NERC 2025 LTRA forecast. total_twh implied.')
    # --- EPRI 2026
    E26 = 'EPRI (Feb 2026), Powering Intelligence 2026: Updated Scenarios of U.S. Data Center Electricity Use (3002034696)'
    row(state='US', state_name='United States', year=2024, scenario='epri2026_historical', dc_twh_low=177.0, dc_twh_high=192.0,
        dc_share_pct_low=4.0, dc_share_pct_high=5.0, includes_crypto=True, source=E26, source_url=EPRI26_URL,
        method='Site-development based: nominal IT capacity x PUE (1.32 fleet avg 2024) x ramp (20%/yr) x load factor. Includes crypto mining.',
        notes='Aggregate DC peak load 21-22 GW in 2024. "approximately twice the level of annual electricity use in 2021".')
    for sc, tw in [('epri2026_low', 383.0), ('epri2026_medium', 596.0), ('epri2026_high', 793.0)]:
        row(state='US', state_name='United States', year=2030, scenario=sc, is_projection=True, dc_twh=tw, includes_crypto=True,
            source=E26, source_url=EPRI26_URL, method='Pipeline completion scenarios.',
            notes='DC share of U.S. demand 9-17% in 2030 across scenarios (US-REGEN non-DC demand). Peak 45/71/94 GW.')
    row(state='VA', state_name='Virginia', year=2024, scenario='epri2026_historical', dc_share_pct_low=25.0, includes_crypto=True,
        source=E26, source_url=EPRI26_URL, method='Text: "Virginia, where the DC share exceeds 25%" / "around 25%". Numeric state shares only in Figure 10 (chart).',
        notes='Lower bound as stated in text. Virginia is "the only state where data centers consume over 20% of electricity".')
    row(state='VA', state_name='Virginia', year=2030, scenario='epri2026_range', is_projection=True, dc_share_pct_low=39.0,
        dc_share_pct_high=57.0, includes_crypto=True, source=E26, source_url=EPRI26_URL,
        method='Low-High scenarios.', notes='Medium scenario: OR, IA, NE, NV, WY, AZ, IN could also exceed 20% by 2030.')
    for st, nm in [('OR', 'Oregon'), ('IA', 'Iowa'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('WY', 'Wyoming'), ('AZ', 'Arizona'), ('IN', 'Indiana')]:
        row(state=st, state_name=nm, year=2030, scenario='epri2026_medium', is_projection=True, dc_share_pct_low=20.0,
            includes_crypto=True, source=E26, source_url=EPRI26_URL,
            method='Text only: state "could see data centers exceeding a 20% share (Medium scenario)". Exact value only in Figure 10.')
    # --- Virginia cross-check from Dominion 10-K + EIA-861
    try:
        e = pd.read_csv(EIA)
        dom = e[(e.eia_utility_id == 19876) & (e.year.isin([2024, 2025]))]
        vas = e[(e.entity_type == 'state') & (e.state == 'VA')].set_index('year')
        nc = None
        for yr, share in [(2024, 26.0), (2025, 28.0)]:
            dva = dom[dom.year == yr].tot_sales_mwh.sum() / 1e6  # VA only (Virginia Power also serves NE North Carolina)
            dc = share / 100 * dva
            tot = vas.loc[yr, 'tot_sales_mwh'] / 1e6
            row(state='VA', state_name='Virginia', year=yr, scenario='dominion_disclosure_lower_bound', dc_twh=round(dc, 2),
                total_twh=round(tot, 2), dc_share_pct=round(100 * dc / tot, 1), includes_crypto=False,
                source='Dominion Energy 2025 Form 10-K ("Data centers represent 28% and 26% of Virginia Power\'s electricity sales for 2025 and 2024") + EIA-861 final sales',
                source_url=DOM_10K_URL, verified=False,
                method=('DERIVED LOWER BOUND: Dominion share x Dominion VA retail sales (EIA-861, bundled) / VA statewide retail sales (EIA-861 A+B+D). '
                        'Excludes data centers served by co-ops (NOVEC, Rappahannock, etc.). Dominion\'s "electricity sales" denominator may differ from EIA retail sales.'),
                notes='Adding NOVEC\'s commercial class (EIA-861; largely data centers, not confirmed) would raise the statewide share by ~8 points in 2025.')
    except Exception as ex:  # noqa
        print('VA cross-check skipped:', ex, file=sys.stderr)


def main():
    epri_2024()
    us_and_va_points()
    df = pd.DataFrame(ROWS)
    # cross-check EPRI 2023 implied totals vs EIA-861 2023 state retail sales
    try:
        e = pd.read_csv(EIA)
        st = e[(e.entity_type == 'state') & (e.year == 2023)].set_index('state').tot_sales_mwh / 1e6
        m = df[(df.scenario == '2023_estimate') & df.state.isin(st.index)]
        for _, r in m.iterrows():
            print('check %s: EPRI implied total %.1f TWh vs EIA-861 2023 retail %.1f TWh' % (r.state, r.total_twh, st[r.state]), file=sys.stderr)
    except Exception as ex:  # noqa
        print('EIA check skipped', ex, file=sys.stderr)
    df = df.sort_values(['state', 'year', 'scenario']).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print('wrote', OUT, len(df), 'rows', file=sys.stderr)
    epri_2026_capacity()


if __name__ == '__main__':
    main()
