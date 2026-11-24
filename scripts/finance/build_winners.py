"""Build data/processed/finance_winners.json: who profits from scarcity and capacity prices.

Facts are hand-curated from primary SEC 8-K exhibits (downloaded by scripts/finance/fetch_edgar_8k.mjs into
data/raw/finance/edgar_8k_*), company/hyperscaler newsrooms and trade press. Stock moves are merged from
data/processed/finance_stock_moves.csv (scripts/finance/build_stock_moves.py).
Every fact carries source_url + verified (True = read in that source during this session, 2026-11-23).
Run: python3 -I scripts/finance/build_winners.py
"""
import csv
import io
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.join(ROOT, 'data/processed/finance_winners.json')
E = 'https://www.sec.gov/Archives/edgar/data/'

stock = {}
with io.open(os.path.join(ROOT, 'data/processed/finance_stock_moves.csv'), encoding='utf-8') as f:
    for r in csv.DictReader(f):
        stock[r['ticker']] = {k: (float(v) if k.startswith(('close', 'pct', 'peak_close')) and v not in ('', None) else v)
                              for k, v in r.items() if k not in ('source', 'retrieved')}


def fact(metric, value, unit, period, url, verified=True, note=''):
    d = dict(metric=metric, value=value, unit=unit, period=period, source_url=url, verified=verified)
    if note:
        d['note'] = note
    return d


CEG_Q3 = E + '1868275/000186827526000116/ceg-20261109991.htm'
CEG_Q3D = E + '1868275/000186827526000116/ceg-20261109992.htm'
CEG_FY24 = E + '1868275/000186827525000020/ceg-20250218991.htm'
CEG_FY25 = E + '1868275/000186827526000029/ceg-20260224991.htm'
CEG_FY23 = E + '1868275/000186827524000010/ceg-20240227991.htm'
VST_Q3 = E + '1692819/000169281926000023/vistra-20260930xearningsre.htm'
VST_COG = E + '1692819/000114036126042013/ef20084950_ex99-1.htm'
VST_FY23 = E + '1692819/000119312524049124/d784050dex991.htm'
VST_FY24 = E + '1692819/000119312525037636/d126557dex991.htm'
VST_FY25 = E + '1692819/000119312526073364/d21122dex991.htm'
TLN_Q3 = E + '1622536/000162253626000084/a20261103q32026earningsrel.htm'
TLN_FY24 = E + '1622536/000162828025008641/a20250227q42024earningsrel.htm'
TLN_FY25 = E + '1622536/000162253626000014/a20260226q42025earningsrel.htm'
TLN_AMZN = E + '1622536/000162828025030559/a20250611pressreleasebusin.htm'
NRG_Q3 = E + '1013871/000101387126000022/nrgq32026ex991.htm'
NRG_FY23 = E + '1013871/000101387124000003/ex991-q42023.htm'
NRG_FY24 = E + '1013871/000101387125000004/ex991-q42024.htm'
NRG_FY25 = E + '1013871/000101387126000002/ex991-q42025.htm'
NRG_LSP = E + '1013871/000110465925047007/tm2514561d1_ex99-1.htm'
NEE_Q325 = E + '753308/000075330825000055/neeq32025exhibit99.htm'
NEE_Q326 = E + '753308/000075330826000077/neeq32026exhibit99.htm'
NEE_D = E + '753308/000110465926063001/tm2614888d1_ex99-1.htm'
META = 'https://about.fb.com/news/2026/01/meta-nuclear-energy-projects-power-american-ai-leadership/'
ANS = 'https://www.ans.org/news/article-7666/meta-strikes-deals-with-vistra-oklo-terrapower'

ipps = [
    dict(ticker='CEG', name='Constellation Energy', fleet='~55 GW (nuclear, gas, geothermal, hydro, wind, solar) after Calpine',
         earnings=[
             fact('Adjusted (non-GAAP) operating EPS', 6.28, 'USD/share', '2023', CEG_FY24),
             fact('Adjusted (non-GAAP) operating EPS', 8.67, 'USD/share', '2024', CEG_FY24),
             fact('Adjusted (non-GAAP) operating EPS', 9.39, 'USD/share', '2025', CEG_FY25),
             fact('Adjusted operating EPS guidance (raised Nov-2026)', [12.50, 12.80], 'USD/share range', '2026', CEG_Q3),
             fact('Adjusted EBITDA (metric reported for 2023)', 4025e6, 'USD', '2023', CEG_FY23),
             fact('GAAP EPS', 11.89, 'USD/share', '2024', CEG_FY24),
             fact('GAAP EPS', 7.40, 'USD/share', '2025', CEG_FY25),
             fact('Q3 adjusted operating EPS', 5.06, 'USD/share', 'Q3-2026 (vs 3.04 in Q3-2025)', CEG_Q3),
         ],
         capacity_revenue=[fact('Q3-2026 drivers', 'Contribution from Calpine; strong commercial performance; higher capacity revenue', 'text', 'Q3-2026', CEG_Q3D)],
         shareholder_returns=[fact('Share repurchases YTD', 3.0e9, 'USD (approx., ~11M shares)', '2026 YTD', CEG_Q3D, note='Buyback authorization $5.0B; ~$2.0B remaining.')],
         contracts=[fact('Long-term agreements signed', 8500, 'MW', '2026 YTD', CEG_Q3D)]),
    dict(ticker='VST', name='Vistra', fleet='~50 GW incl. Cogentrix (closed Oct-2026), Energy Harbor nuclear (Mar-2024), Lotus gas (Oct-2025)',
         earnings=[
             fact('Ongoing Operations Adjusted EBITDA', 4140e6, 'USD', '2023', VST_FY23),
             fact('Ongoing Operations Adjusted EBITDA', 5656e6, 'USD', '2024', VST_FY24),
             fact('Ongoing Operations Adjusted EBITDA', 5912e6, 'USD', '2025', VST_FY25),
             fact('Ongoing Operations Adjusted EBITDA guidance (narrowed Nov-2026)', [7.1e9, 7.5e9], 'USD range', '2026', VST_Q3),
             fact('Ongoing Operations Adjusted EBITDA guidance (initiated Nov-2026)', [7.7e9, 8.5e9], 'USD range', '2027', VST_Q3),
             fact('Q3 Ongoing Operations Adjusted EBITDA', 2378e6, 'USD', 'Q3-2026 (>50% y/y)', VST_Q3),
         ],
         capacity_revenue=[fact('Q3-2026 drivers', 'Higher realized energy and capacity prices; Lotus plants; Martin Lake 1 return', 'text', 'Q3-2026', VST_Q3)],
         shareholder_returns=[fact('Cumulative share repurchases since Nov-2021', 6.7e9, 'USD', 'to 2026-11-02', VST_Q3, note='+$1.5B new authorization; ~$2.5B remaining through 2028.')],
         contracts=[fact('Meta 20-yr PPAs (Perry + Davis-Besse) plus uprate energy', 2176, 'MW', 'announced 2026-01-09', META, note='Uprates +433 MW across Perry, Davis-Besse, Beaver Valley by early 2030s.'),
                    fact('Hedged share of expected generation', [100, 98, 78], 'percent for 2026/2027/2028', 'as of 2026-10-30', VST_Q3)]),
    dict(ticker='TLN', name='Talen Energy', fleet='Susquehanna nuclear + PJM gas incl. Freedom & Guernsey CCGTs (+~2.8 GW, closed 2025-11-25)',
         earnings=[
             fact('Adjusted EBITDA', None, 'USD', '2023', '', False, 'Emerged from bankruptcy May-2023; not collected.'),
             fact('Adjusted EBITDA', 770e6, 'USD', '2024', TLN_FY24),
             fact('Adjusted EBITDA', 1035e6, 'USD', '2025', TLN_FY25),
             fact('Adjusted EBITDA guidance (reaffirmed Nov-2026)', [2050e6, 2200e6], 'USD range', '2026', TLN_Q3),
             fact('Adjusted EBITDA guidance (initiated)', [2500e6, 2850e6], 'USD range', '2027', TLN_Q3),
         ],
         capacity_revenue=[fact('PJM capacity monetization', 1.5e9, 'USD of future PJM capacity cash flows sold (2027/28 + 2028/29 delivery years) for $1.3B net proceeds, closed 2026-10-01; proceeds funded a $1.5B accelerated share repurchase', '2027/28-2028/29', TLN_Q3)],
         shareholder_returns=[fact('Share repurchases since start of 2024 (on ASR completion)', 4.0e9, 'USD (~19.5M shares)', '2024-2026', TLN_Q3)],
         contracts=[fact('Amazon PPA (front-of-meter) at full quantity', 1920, 'MW through 2042', 'announced 2025-06-11', TLN_AMZN,
                         note='~$18B lifetime revenue at full quantity per Talen investor presentation (as reported by Utility Dive / POWER; not read in primary).')]),
    dict(ticker='NRG', name='NRG Energy', fleet='~25 GW after LS Power portfolio (closed 2026-01-30), less 4.9 GW being sold back to LS Power',
         earnings=[
             fact('Adjusted EBITDA', 3282e6, 'USD', '2023', NRG_FY23),
             fact('Adjusted EBITDA', 3752e6, 'USD', '2024', NRG_FY24, note='Derived: 2023 + $470M improvement stated in FY2024 release.'),
             fact('Adjusted EBITDA', 4050e6, 'USD', '2025', NRG_FY25, note='Derived: 2024 + $298M improvement stated in FY2025 release.'),
             fact('Adjusted EPS', 4.72, 'USD/share', '2023', NRG_FY24, note='Derived: $6.83 - $2.11.'),
             fact('Adjusted EPS', 6.83, 'USD/share', '2024', NRG_FY24),
             fact('Adjusted EPS', 8.24, 'USD/share', '2025', NRG_FY25),
             fact('Adjusted EBITDA guidance', [5325e6, 5825e6], 'USD range', '2026', NRG_Q3),
             fact('Adjusted EPS guidance', [7.90, 9.90], 'USD/share range', '2026', NRG_Q3),
             fact('Adjusted EBITDA guidance (initiated)', [5500e6, 6000e6], 'USD range', '2027', NRG_Q3),
         ],
         capacity_revenue=[fact('East segment Adjusted EBITDA (PJM/Northeast)', 1547e6, 'USD (+$867M y/y)', '9M-2026', NRG_Q3,
                                note='Q3-2026 East $614M, +$507M y/y; segment is where PJM capacity-price exposure sits (attribution to capacity prices is our inference).')],
         shareholder_returns=[fact('Planned share repurchases 2026-2027', 3.0e9, 'USD', '2026-2027', NRG_Q3, note='Funded partly by $4.0B sale of 4.9 GW to LS Power (agreed 2026-11-09).')],
         contracts=[fact('Bring-your-own-power data-center project', 1200, 'MW', 'on track (Q3-2026)', NRG_Q3)]),
]
for p in ipps:
    p['stock'] = stock.get(p['ticker'])

deals = [
    dict(buyer='Microsoft', seller='Constellation', asset='Crane Clean Energy Center (Three Mile Island Unit 1 restart), PA (PJM)',
         mw=835, mw_note='"more than 800 MW"; unit was 837 MW before 2019 retirement (835 MW widely reported)', term_years=20,
         announced='2024-09-20', start='2028 at announcement (later reported accelerated to 2027 - UNVERIFIED)',
         price='not disclosed', structure='PPA; DOE guarantee up to $1B for restart loan (Nov-2025)',
         source_url=E + '1868275/000186827524000058/ceg-202409208kexh991.htm', verified=True),
    dict(buyer='Amazon (AWS)', seller='Talen', asset='Susquehanna nuclear, PA (PJM)', mw=1920, term_years=17,
         announced='2025-06-11 (expanded; original Mar-2024 Cumulus campus sale)', start='ramping: 840-1,200 MW by 2029, 1,680-1,920 MW by 2032 (Utility Dive)',
         price='~$18B lifetime revenue at full quantity (Talen deck via trade press)', structure='front-of-meter PPA through 2042; Talen as retail supplier, PPL Electric delivers',
         source_url=TLN_AMZN, verified=True, note='MW/term verified in 8-K; $18B and ramp from trade press.'),
    dict(buyer='Meta', seller='Constellation', asset='Clinton Clean Energy Center, IL (MISO)', mw=1121, term_years=20,
         announced='2025-06-03', start='2027-06', price='not disclosed', structure='virtual PPA; supports relicensing after Illinois ZEC expires 2027',
         source_url='https://www.utilitydive.com/news/meta-constellation-illinois-clinton-nuclear-ppa-support-ai-goals/749992/', verified=True,
         note='Verified via trade press (Utility Dive/The Register); CEG 8-K not retrieved.'),
    dict(buyer='Google', seller='NextEra Energy Resources', asset='Duane Arnold Energy Center restart, IA (MISO)', mw=615, term_years=25,
         announced='2025-10-27', start='no later than Q1-2029 (possibly Q4-2028)', price='not disclosed',
         structure='PPA; CIPCO buys 50 MW on same terms; NEE to buy 30% minority stakes; up to $0.16/yr adjusted EPS avg first 10 years',
         source_url=NEE_Q325, verified=True),
    dict(buyer='Meta', seller='Vistra', asset='Perry + Davis-Besse (OH) existing output; uprates incl. Beaver Valley (PA), PJM', mw=2176,
         mw_note='plus 433 MW of uprates by early 2030s', term_years=20, announced='2026-01-09', start='not stated',
         price='not disclosed', structure='PPAs; enable subsequent license renewals', source_url=META, verified=True),
    dict(buyer='Meta', seller='TerraPower', asset='2 Natrium units (+ rights to 6 more, ~2.1 GW)', mw=690, term_years=None,
         announced='2026-01-09', start='as early as 2032; options by 2035', price='not disclosed', structure='development funding + offtake rights',
         source_url=META, verified=True),
    dict(buyer='Meta', seller='Oklo', asset='Pike County, OH advanced-nuclear campus (PJM)', mw=1200, term_years=None,
         announced='2026-01-09', start='as early as 2030; full 1.2 GW by 2034', price='not disclosed', structure='prepayment/development support',
         source_url=ANS, verified=True),
    dict(buyer='Amazon', seller='Constellation', asset='Calvert Cliffs, MD (PJM)', mw=690, mw_note='+190 MW expansion 2030-2032', term_years=20,
         announced='2026-09', start='not stated', price='not disclosed', structure='PPA + retail supply agreement; enables >$3B investment',
         source_url=CEG_Q3, verified=True),
    dict(buyer='Google', seller='Constellation', asset='Uprates at 11 nuclear units in IL, PA, NJ (PJM)', mw=890, term_years=20,
         announced='2026-10', start='first uprate 2028', price='not disclosed',
         structure='PPA enabling >$4.3B uprate investment; plus 15-yr financial load-following agreement for 2,700 MW in PJM',
         source_url=CEG_Q3, verified=True),
    dict(buyer='undisclosed', seller='NextEra Energy Resources', asset='Point Beach nuclear, WI', mw=1000, term_years=20,
         announced='Q3-2026', start='', price='"competitive price"', structure='PPA, subject to PSC of Wisconsin approval',
         source_url=NEE_Q326, verified=True),
    dict(buyer='Google', seller='Kairos Power', asset='fleet of SMRs (incl. Hermes 2 via TVA)', mw=500, term_years=None,
         announced='2024-10-14', start='first by 2030, full by 2035', price='not disclosed', structure='SMR offtake agreement; Aug-2025 step: Hermes 2 (Oak Ridge) to supply up to 50 MW to TVA grid serving Google sites from 2030',
         source_url='https://www.axios.com/2024/10/14/google-nuclear-deal-power-ai', verified=True,
         note='Verified via trade press (Axios, TechCrunch, Fox Business); 500 MW vs 50 MW refer to the full deal vs the TVA/Hermes 2 phase.'),
    dict(buyer='Amazon', seller='X-energy (first project with Energy Northwest)', asset='Xe-100 SMRs', mw=5000, term_years=None,
         announced='2024-10', start='by 2039 (target)', price='Amazon anchored ~$500M X-energy financing round',
         structure='equity + deployment target (not contracted capacity); first project 4 units/320 MW in WA, expandable to 960 MW',
         source_url='https://techcrunch.com/2024/10/14/google-signed-a-deal-to-power-data-centers-with-nuclear-micro-reactors-from-kairos-but-the-2030-timeline-is-very-optimistic', verified=True,
         note='Verified via search snippets of trade press only; 5 GW is a collaboration target.'),
]

ma = [
    dict(deal='Constellation acquires Calpine', announced='2025-01-10', status='completed (reported in CEG FY2025 release, 2026-02-24)',
         value_usd=26.6e9, value_note='net purchase price; equity $16.4B (50M CEG shares at $237.98 VWAP + $4.5B cash) + ~$12.7B net debt; 7.9x 2026 EV/EBITDA',
         assets='~27 GW (79 facilities): gas + geothermal', source_url=E + '1868275/000186827525000006/ceg-202501108kxexh991.htm', verified=True),
    dict(deal='NRG acquires LS Power gas portfolio + CPower', announced='2025-05-12', status='closed 2026-01-30',
         value_usd=12.0e9, value_note='enterprise value; 7.5x 2026 EV/EBITDA; ~50% of new-build replacement cost',
         assets='13 GW gas (18 plants, 9 states) + CPower ~6 GW C&I demand response', source_url=NRG_LSP, verified=True),
    dict(deal='NRG sells six gas plants back to LS Power', announced='2026-11-09', status='definitive agreement',
         value_usd=4.0e9, value_note='cash; proceeds to fund $3B buybacks 2026-27 and debt reduction', assets='4.9 GW gas', source_url=NRG_Q3, verified=True),
    dict(deal='Vistra acquires Cogentrix Energy (from Quantum)', announced='2026-01-05', status='closed Oct-2026',
         value_usd=4.0e9, value_note='net purchase price (~$2.3B cash + 5M VST shares at $185 + assumed debt); ~$730/kW; ~7.25x 2027 EBITDA',
         assets='~5,500 MW gas (PJM, ISO-NE, ERCOT)', source_url=E + '1692819/000119312526002589/d62722dex991.htm', verified=True),
    dict(deal='Vistra acquires Lotus Infrastructure gas plants', announced='2025', status='closed Oct-2025', value_usd=None,
         value_note='price not collected', assets='7 gas plants, >2,300 MW', source_url=VST_COG, verified=True),
    dict(deal='Talen acquires Freedom (PA) and Guernsey (OH) CCGTs', announced='2025', status='closed 2025-11-25', value_usd=None,
         value_note='price not collected (~$3.5B reported - UNVERIFIED)', assets='~2.8 GW gas', source_url=TLN_FY25, verified=True),
    dict(deal='Constellation agrees to acquire Rhode Island State Energy Center', announced='Q3-2026', status='agreement', value_usd=None,
         value_note='price not collected', assets='609 MW CCGT', source_url=CEG_Q3, verified=True),
    dict(deal='NextEra Energy + Dominion Energy all-stock combination', announced='2026-05-18', status='pending regulatory approvals',
         value_usd=None, value_note='0.8138 NEE share per D share; NEE holders 74.5% / D holders 25.5%; $360M one-time cash to D holders; '
         '$2.25B proposed bill credits for Dominion customers (VA, NC, SC), residential credits extended from 2 to 4 years in Sept-2026; combined rate base $138B growing ~11%/yr to 2032; >130 GW large-load pipeline',
         assets='~10M utility accounts (FL, VA, NC, SC); 110 GW generation', source_url=NEE_D, verified=True),
    dict(deal='Blackstone Infrastructure acquires TXNM Energy (PNM, TNMP)', announced='2025-05', status='pending: PUCT approved 2026-02-06 ($45M rate credits); FERC/FCC/HSR cleared; NMPRC and NRC pending; outside date extended to 2027-05-31 (as of Jul-2026)',
         value_usd=11.5e9, value_note='$61.25/share cash; enterprise value', assets='NM + TX wires/vertically integrated utilities',
         source_url='https://www.abqjournal.com/business/txnm-blackstone-extend-115-billion-sale-deadline-after-regulatory-setback/3084994', verified=True,
         note='Secondary sources (Albuquerque Journal, Barchart/PR). Status after Jul-2026 not checked.'),
    dict(deal='CenterPoint sells Ohio gas LDC', announced='2025-10', status='announced', value_usd=2.62e9,
         value_note='gross; ~1.9x 2024 rate base and ~26x 2024 earnings - a market price for regulated rate base',
         assets='gas distribution (Ohio)', source_url=E + '1130310/000110465926118963/tm2628051d1_ex99-2.htm', verified=True),
]

headwinds = [
    dict(date='2026-01-16', event='White House + all PJM governors "statement of principles": Reliability Backstop Auction by Sept-2026 with 15-yr contracts for new capacity, costs allocated to load-serving entities with new data centers that did not self-procure; extended capacity price cap',
         market_reaction='CEG fell ~9.8% on 2026-01-16 (secondary, lower-reliability source)',
         source_url='https://www.utilitydive.com/news/trump-governors-pjm-emergency-auction-data-centers/809853/', verified=True),
    dict(date='2026-10', event='PJM auction delay; S&P: the four IPP stocks down ~22%-41% over prior 12 months; analysts see hyperscalers preferring utility PPAs',
         market_reaction='see stock table', source_url='https://www.spglobal.com/market-intelligence/en/news-insights/articles/2026/10/pjm-auction-delay-complicates-independent-power-producers-stock-price-recovery-106494914',
         verified=False, note='Headline + search snippet only; S&P page not readable from this session.'),
    dict(date='2026-11', event='Midterm results (Democratic gains, Texas governor) read as raising regulatory risk for merchant generators',
         market_reaction='VST about -15%, CEG about -9% (Stocktwits)', source_url='https://stocktwits.com/news-articles/markets/equity/vst-ceg-stocks-drop-as-election-outcome-hits-merchant-power-generators/cNGLkduR93x',
         verified=False, note='Search snippet only.'),
    dict(date='2025-01-27', event='DeepSeek efficiency shock', market_reaction='VST -28%, TLN -22% in one day (Utility Dive)',
         source_url='https://www.utilitydive.com/news/ipp-stocks-reel-as-low-cost-deepseek-chills-ai-load-growth-thesis/738482/', verified=False,
         note='Search snippet only.'),
]

out = dict(
    meta=dict(title='Who profits from scarcity: IPPs, hyperscaler nuclear deals, power M&A', built='2026-11-23',
              stock_source='Nasdaq.com historical quotes (close, split-adjusted, not dividend-adjusted); see data/processed/finance_stock_moves.csv',
              capacity_context='PJM capacity cost (cleared MW x price): $2.2B for 2024/25 -> $14.7B for 2025/26 -> $16.1B for 2026/27; see data/processed/markets_capacity_prices.csv (markets area)',
              caveat='Company figures are non-GAAP as reported; deals list is not exhaustive.'),
    independent_power_producers=ipps,
    benchmarks={k: stock.get(k) for k in ('XLU', 'SPY', 'GEV', 'OKLO', 'SMR')},
    hyperscaler_nuclear_deals=deals,
    m_and_a=ma,
    headwinds_2025_2026=headwinds,
)
with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(json.dumps(out, indent=1, ensure_ascii=False))
print('ipps', len(ipps), 'deals', len(deals), 'm&a', len(ma), 'headwinds', len(headwinds), '->', OUT)
