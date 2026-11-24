"""Summarise stock moves 2023 -> latest for IPPs and utilities from Nasdaq.com historical quotes.

Input : data/raw/finance/nasdaq_prices_<date>/<SYM>.json (from scripts/finance/fetch_prices.mjs)
Output: data/processed/finance_stock_moves.csv
Run   : python3 -I scripts/finance/build_stock_moves.py
Closes are NOT dividend-adjusted (price return only). The feed IS split-adjusted (checked: ETR 2:1 Dec 2024 shows
no break; XLU history is on the post-split basis), so SPLITS stays empty.
TLN history starts 2023-06-02 (OTC after emerging from bankruptcy in May 2023; Nasdaq listing July 2024).
"""
import glob
import io
import json
import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
dirs = sorted(glob.glob(os.path.join(ROOT, 'data/raw/finance/nasdaq_prices_*')))
SRC = dirs[-1]

GROUP = {'CEG': 'IPP', 'VST': 'IPP', 'TLN': 'IPP', 'NRG': 'IPP',
         'OKLO': 'nuclear developer', 'SMR': 'nuclear developer', 'GEV': 'equipment (turbines/grid)',
         'XLU': 'benchmark: S&P 500 utilities ETF', 'SPY': 'benchmark: S&P 500 ETF'}
# Split factors to apply to closes BEFORE the split date if the feed is unadjusted (filled in after inspection).
SPLITS = {}


def load(sym):
    j = json.load(io.open(os.path.join(SRC, sym + '.json'), encoding='utf-8'))
    rows = j['data']['tradesTable']['rows']
    d = pd.DataFrame(rows)
    d['date'] = pd.to_datetime(d['date'], format='%m/%d/%Y')
    d['close'] = d['close'].str.replace(r'[$,]', '', regex=True).astype(float)
    d = d.sort_values('date')[['date', 'close']]
    for (dt, f) in SPLITS.get(sym, []):
        d.loc[d.date < dt, 'close'] = d.loc[d.date < dt, 'close'] / f
    return d


def close_on_or_before(d, dt):
    s = d[d.date <= pd.Timestamp(dt)]
    return (None, None) if s.empty else (s.iloc[-1].close, s.iloc[-1].date)


def first_on_or_after(d, dt):
    s = d[d.date >= pd.Timestamp(dt)]
    return (None, None) if s.empty else (s.iloc[0].close, s.iloc[0].date)


out = []
for f in sorted(glob.glob(os.path.join(SRC, '*.json'))):
    sym = os.path.basename(f)[:-5]
    d = load(sym)
    base, base_dt = close_on_or_before(d, '2022-12-30')
    if base is None:
        base, base_dt = first_on_or_after(d, '2023-01-01')
    e23, _ = close_on_or_before(d, '2023-12-29')
    e24, _ = close_on_or_before(d, '2024-12-31')
    e25, _ = close_on_or_before(d, '2025-12-31')
    last, last_dt = d.iloc[-1].close, d.iloc[-1].date
    pk = d.loc[d.close.idxmax()]
    pct = lambda a, b: None if (a is None or b is None) else round((b / a - 1) * 100, 1)
    out.append({
        'ticker': sym, 'group': GROUP.get(sym, 'regulated utility holding co.'),
        'base_date': base_dt.strftime('%Y-%m-%d'), 'close_base': base,
        'close_2023_end': e23, 'close_2024_end': e24, 'close_2025_end': e25,
        'latest_date': last_dt.strftime('%Y-%m-%d'), 'close_latest': last,
        'peak_close': pk.close, 'peak_date': pk.date.strftime('%Y-%m-%d'),
        'pct_2023': pct(base, e23), 'pct_2024': pct(e23, e24), 'pct_2025': pct(e24, e25),
        'pct_2026_ytd': pct(e25, last), 'pct_base_to_latest': pct(base, last),
        'pct_latest_vs_peak': pct(pk.close, last),
        'price_basis': 'close, not dividend-adjusted',
        'source': 'Nasdaq.com historical quotes API', 'source_url':
            'https://api.nasdaq.com/api/quote/%s/historical?assetclass=%s' % (sym, 'etf' if sym in ('XLU', 'SPY') else 'stocks'),
        'retrieved': os.path.basename(SRC).split('_')[-1],
    })
res = pd.DataFrame(out)
res.to_csv(os.path.join(ROOT, 'data/processed/finance_stock_moves.csv'), index=False)
print(res[['ticker', 'base_date', 'close_base', 'close_2024_end', 'close_2025_end', 'close_latest', 'peak_close',
           'peak_date', 'pct_2023', 'pct_2024', 'pct_2025', 'pct_2026_ytd', 'pct_base_to_latest',
           'pct_latest_vs_peak']].to_string())
