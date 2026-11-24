"""Rank every US utility by commercial + industrial (C&I) sales added 2019 -> 2025 (EIA-861 final).

Run from the project root:  python3 -I scripts/load/build_top_ci_growth.py
Output: data/processed/load_utility_ci_growth_rank.csv  (top 60 utilities by C&I TWh added, utility x state)

Same EIA-861 conventions as build_utility_sales_growth.py (Parts A+C+D; Texas TDUs from Delivery_Companies, base 2020),
excluding retail power marketers, behind-the-meter third-party sellers and EIA 'Adjustment' rows.
This is where new large load (data centers, crypto mining, manufacturing, oil & gas electrification) physically landed;
it does NOT isolate data centers. Use alongside utility disclosures.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.getcwd(), 'scripts', 'load'))
from build_utility_sales_growth import read_member  # noqa: E402

OUT = os.path.join(os.getcwd(), 'data', 'processed', 'load_utility_ci_growth_rank.csv')


def load(year):
    fr = [read_member(year, 'Sales_Ult_Cust', 'States')]
    d = read_member(year, 'Delivery_Companies', 0)
    if d is not None:
        fr.append(d)
    x = pd.concat(fr, ignore_index=True, sort=False)
    x = x[x.part.isin(['A', 'C', 'D'])]
    # drop Texas retail power marketers (their kWh are also counted by the TDU), third-party behind-the-meter sellers,
    # and EIA's statewide 'Adjustment' rows
    x = x[~x.ownership.isin(['Retail Power Marketer', 'Behind the Meter'])]
    x = x[~x.utility_name.astype(str).str.startswith('Adjustment')]
    g = x.groupby(['eia_utility_id', 'state']).agg(utility_name=('utility_name', 'last'), ba_code=('ba_code', 'last'),
                                                    com=('com_sales_mwh', 'sum'), ind=('ind_sales_mwh', 'sum'),
                                                    res=('res_sales_mwh', 'sum'), tot=('tot_sales_mwh', 'sum')).reset_index()
    g['year'] = year
    return g


def main():
    a19, a20, a25 = load(2019), load(2020), load(2025)
    base = a19.set_index(['eia_utility_id', 'state'])
    b20 = a20.set_index(['eia_utility_id', 'state'])
    end = a25.set_index(['eia_utility_id', 'state'])
    rows = []
    for k, e in end.iterrows():
        if k in base.index:
            b, by = base.loc[k], 2019
        elif k in b20.index:
            b, by = b20.loc[k], 2020
        else:
            continue
        ci_b, ci_e = b.com + b.ind, e.com + e.ind
        rows.append(dict(eia_utility_id=int(k[0]), state=k[1], utility_name=e.utility_name, ba_code=e.ba_code, base_year=by,
                         ci_sales_mwh_base=ci_b, ci_sales_mwh_2025=ci_e, ci_added_twh=round((ci_e - ci_b) / 1e6, 3),
                         ci_growth_pct=round(100 * (ci_e / ci_b - 1), 1) if ci_b else None,
                         com_added_twh=round((e.com - b.com) / 1e6, 3), ind_added_twh=round((e.ind - b.ind) / 1e6, 3),
                         res_growth_pct=round(100 * (e.res / b.res - 1), 1) if b.res else None,
                         tot_sales_mwh_2025=e.tot, tot_growth_pct=round(100 * (e.tot / b.tot - 1), 1) if b.tot else None))
    df = pd.DataFrame(rows).sort_values('ci_added_twh', ascending=False)
    us_ci_added = df.ci_added_twh.sum()
    df['rank'] = range(1, len(df) + 1)
    top = df.head(60).copy()
    top['source'] = 'EIA-861 final 2019/2020 and 2025 (Sales_Ult_Cust, Delivery_Companies); https://www.eia.gov/electricity/data/eia861/'
    top['method'] = 'Parts A+C+D (bundled + delivery-only); energy-only marketers excluded; Texas TDUs base year 2020.'
    top.to_csv(OUT, index=False)
    print('C&I added, sum over all ranked utilities:', round(us_ci_added, 1), 'TWh; top-10 share', round(100 * df.head(10).ci_added_twh.sum() / us_ci_added, 1), '%', file=sys.stderr)
    pd.set_option('display.width', 250)
    sys.stdout.buffer.write(top.head(30)[['rank', 'utility_name', 'state', 'base_year', 'ci_added_twh', 'ci_growth_pct', 'com_added_twh',
                                          'ind_added_twh', 'res_growth_pct', 'tot_growth_pct']].to_string().encode('utf-8'))


if __name__ == '__main__':
    main()
