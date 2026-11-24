"""Build finance_roe.csv and finance_rate_cases.csv from EEI's quarterly Rate Review workbook.

Source: EEI Financial Analysis Dept, "Rate Review 2026 Q3" (data: S&P Global Market Intelligence / RRA),
downloaded by scripts/finance/fetch.mjs into data/raw/finance/eei_rate_review_2026q3/.
Run:  python3 -I scripts/finance/build_roe.py
"""
import io
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'data/raw/finance/eei_rate_review_2026q3/2026_Q3_Rate_Review.xlsx')
SRC_URL = ('https://www.eei.org/-/media/Project/EEI/Documents/Issues-and-Policy/Finance-And-Tax/'
           'Quarterly-Financial-Updates/2026_Q3_Rate_Review_XLSX.xlsx')
OUT_ROE = os.path.join(ROOT, 'data/processed/finance_roe.csv')
OUT_CASES = os.path.join(ROOT, 'data/processed/finance_rate_cases.csv')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

COLS = ['status', 'state', 'company', 'ticker', 'docket', 'service', 'case_type',
        'request_date', 'requested_increase_musd', 'requested_ror_pct', 'requested_roe_pct',
        'requested_equity_ratio_pct', 'requested_rate_base_musd',
        'decision_date', 'authorized_increase_musd', 'authorized_ror_pct', 'authorized_roe_pct',
        'authorized_equity_ratio_pct', 'authorized_rate_base_musd', 'lag_months']

raw = pd.read_excel(SRC, 'All Rate Cases 2026Q3', header=None, engine='openpyxl')
raw = raw.dropna(how='all').dropna(axis=1, how='all')
df = raw.iloc[2:, :len(COLS)].copy()
df.columns = COLS
for c in ['request_date', 'decision_date']:
    df[c] = pd.to_datetime(df[c], errors='coerce')
num = [c for c in COLS if c.endswith(('_musd', '_pct')) or c == 'lag_months']
for c in num:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['ticker'] = df['ticker'].astype(str).str.rstrip('.').replace('nan', '')
df['state_name'] = df['state']

# ---- annual series --------------------------------------------------------------------------
dec = df[df.status == 'Settled'].copy()
dec['year'] = dec.decision_date.dt.year
req = df.copy()
req['year'] = req.request_date.dt.year

rows = []
for y in range(2000, 2027):
    d = dec[(dec.year == y)]
    roe_all = d[d.authorized_roe_pct.notna()]
    roe_gen = roe_all[roe_all.case_type != 'Limited-Issue Rider']
    roe_vi = roe_all[roe_all.case_type == 'Vertically Integrated']
    roe_dist = roe_all[roe_all.case_type == 'Distribution']
    r = req[req.year == y]
    rows.append({
        'year': y,
        'period': 'Q1-Q3' if y == 2026 else 'full year',
        'avg_authorized_roe_pct_all_cases': round(roe_all.authorized_roe_pct.mean(), 3) if len(roe_all) else None,
        'n_roe_all_cases': len(roe_all),
        'avg_authorized_roe_pct_ex_riders': round(roe_gen.authorized_roe_pct.mean(), 3) if len(roe_gen) else None,
        'median_authorized_roe_pct_ex_riders': round(roe_gen.authorized_roe_pct.median(), 3) if len(roe_gen) else None,
        'n_roe_ex_riders': len(roe_gen),
        'avg_authorized_roe_pct_vertically_integrated': round(roe_vi.authorized_roe_pct.mean(), 3) if len(roe_vi) else None,
        'avg_authorized_roe_pct_distribution': round(roe_dist.authorized_roe_pct.mean(), 3) if len(roe_dist) else None,
        'avg_requested_roe_pct_filed': round(r[r.requested_roe_pct.notna()].requested_roe_pct.mean(), 3) if r.requested_roe_pct.notna().any() else None,
        'avg_authorized_equity_ratio_pct': round(roe_all.authorized_equity_ratio_pct.mean(), 2) if roe_all.authorized_equity_ratio_pct.notna().any() else None,
        'n_cases_decided': len(d),
        'authorized_increase_usd_total': round(d.authorized_increase_musd.sum() * 1e6) if len(d) else None,
        'n_cases_filed': len(r),
        'requested_increase_usd_total': round(r.requested_increase_musd.sum() * 1e6) if len(r) else None,
    })
annual = pd.DataFrame(rows)

# 10-year Treasury (monthly, sheet V of the same workbook) -> annual average; ROE spread over Treasuries
ust = pd.read_excel(SRC, 'V. 10-Year Treasury', header=None, engine='openpyxl').iloc[26:, [2, 3]].dropna()
ust.columns = ['d', 'y10']
ust['d'] = pd.to_datetime(ust.d, errors='coerce')
ust = ust.dropna()
ust['y10'] = ust.y10.astype(float)
ust_y = ust.groupby(ust.d.dt.year).y10.mean().round(3)
annual['ust10y_avg_pct'] = annual.year.map(ust_y)
annual['roe_spread_over_ust10y_pp'] = (annual.avg_authorized_roe_pct_ex_riders - annual.ust10y_avg_pct).round(3)
# share of requested $ granted, settled non-rider cases with both values, by decision year
m = dec[dec.requested_increase_musd.notna() & dec.authorized_increase_musd.notna() & (dec.case_type != 'Limited-Issue Rider')]
gr = m.groupby('year').agg(req=('requested_increase_musd', 'sum'), auth=('authorized_increase_musd', 'sum'))
annual['authorized_share_of_requested_increase_pct_ex_riders'] = annual.year.map((gr.auth / gr.req * 100).round(1))

# EEI-published headline numbers (as printed in the EEI 2025 Financial Review, p.40) for cross-check
annual['eei_published_avg_awarded_roe_pct'] = annual.year.map({2024: 9.73, 2025: 9.71})
annual['record_type'] = 'annual_average'
annual['source'] = 'EEI Rate Review 2026 Q3 workbook (S&P Global Market Intelligence/RRA data), case-level; computed'
annual['source_url'] = SRC_URL
annual['verified'] = True

# ---- recent authorized ROEs at major utility holding companies --------------------------------
MAJOR = ['D', 'SO', 'AEP', 'DUK', 'NEE', 'EXC', 'PEG', 'ETR', 'XEL', 'SRE', 'CNP', 'PPL', 'FE', 'NI',
         'EVRG', 'WEC', 'AEE', 'PNW', 'DTE', 'CMS', 'ED', 'ES', 'EIX', 'PCG', 'AES', 'OGE', 'LNT', 'TXNM', 'PNM']
recent = dec[(dec.decision_date >= '2024-01-01') & dec.authorized_roe_pct.notna() & dec.ticker.isin(MAJOR)].copy()
recent = recent.sort_values(['ticker', 'decision_date'])
recent_out = pd.DataFrame({
    'record_type': 'recent_case',
    'year': recent.decision_date.dt.year,
    'decision_date': recent.decision_date.dt.strftime('%Y-%m-%d'),
    'ticker': recent.ticker,
    'company': recent.company,
    'state': recent.state_name,
    'docket': recent.docket,
    'case_type': recent.case_type,
    'requested_roe_pct': recent.requested_roe_pct,
    'authorized_roe_pct': recent.authorized_roe_pct,
    'authorized_equity_ratio_pct': recent.authorized_equity_ratio_pct,
    'authorized_rate_base_usd': (recent.authorized_rate_base_musd * 1e6).round(),
    'authorized_increase_usd': (recent.authorized_increase_musd * 1e6).round(),
    'source': 'EEI Rate Review 2026 Q3 workbook (S&P Global Market Intelligence/RRA data)',
    'source_url': SRC_URL,
    'verified': True,
})

out = pd.concat([annual, recent_out], ignore_index=True, sort=False)
lead = ['record_type', 'year', 'period', 'decision_date', 'ticker', 'company', 'state', 'docket', 'case_type',
        'avg_authorized_roe_pct_all_cases', 'avg_authorized_roe_pct_ex_riders', 'median_authorized_roe_pct_ex_riders',
        'eei_published_avg_awarded_roe_pct', 'requested_roe_pct', 'authorized_roe_pct']
out = out[lead + [c for c in out.columns if c not in lead]]
out.to_csv(OUT_ROE, index=False)

# ---- full case list (2015+) for the site: pending cases = "what you can do" -------------------
cases = df[(df.request_date >= '2015-01-01') | (df.status == 'Pending')].copy()
cases['request_date'] = cases.request_date.dt.strftime('%Y-%m-%d')
cases['decision_date'] = cases.decision_date.dt.strftime('%Y-%m-%d')
cases = cases.drop(columns=['state_name'])
cases['source_url'] = SRC_URL
cases.sort_values(['status', 'request_date'], ascending=[True, False]).to_csv(OUT_CASES, index=False)

print(annual[['year', 'avg_authorized_roe_pct_all_cases', 'avg_authorized_roe_pct_ex_riders', 'n_roe_ex_riders',
              'avg_requested_roe_pct_filed', 'requested_increase_usd_total', 'authorized_increase_usd_total',
              'n_cases_filed', 'n_cases_decided']].to_string())
print('recent major-utility cases:', len(recent_out), ' all cases written:', len(cases),
      ' pending:', int((cases.status == 'Pending').sum()))
