"""Build data/processed/markets_capacity_prices.csv  (run: python3 -I scripts/markets/build_capacity_prices.py)

PJM rows are parsed from text extracted (scripts/markets/pdf2txt.js) from primary PDFs saved in data/raw/markets/:
  * IMM 2018 State of the Market, Sec. 5, Table 5-23  -> BRA LDA prices 2015/16-2021/22
  * IMM 2025 State of the Market, Sec. 5, Table 5-21  -> BRA LDA prices 2021/22-2027/28 (adds DEOK, DOM)
  * IMM 2025 SOM Table 5-23 / 2018 SOM Table 5-24       -> zonal cleared-MW-weighted average prices (all auctions)
  * IMM 2025 SOM Table 5-24 / 5-26                     -> RPM revenue by delivery year, cost to load
  * PJM 2019/20 BRA report Table 1                      -> RTO price + cleared UCAP 2007/08-2019/20; 2019/20 LDA prices
  * PJM 2020/21 BRA report                              -> DEOK 2020/21
  * PJM 2028/29 BRA report Table 2 + LDA table          -> RTO price, cleared UCAP, $bn 2018/19-2028/29; 2028/29 LDAs
MISO / ISO-NE / NYISO rows are entered by hand from press releases and RTO filings found this session (see
research/markets/SOURCES.md). Each row has verified=true only if the number was read from a live source this session.
"""
import csv
import io
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TXT = os.path.join(ROOT, 'data', 'raw', 'markets', '_text')
OUT = os.path.join(ROOT, 'data', 'processed', 'markets_capacity_prices.csv')

U_SOM18 = 'https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2018/2018-som-pjm-sec5.pdf'
U_SOM25 = 'https://www.monitoringanalytics.com/reports/PJM_State_of_the_Market/2025/2025-som-pjm-sec5.pdf'
U_BRA1920 = 'https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2019-2020-base-residual-auction-report.ashx'
U_BRA2021 = 'https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2020-2021-base-residual-auction-report.ashx'
U_BRA2829 = 'https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2028-2029/2028-2029-bra-results-report.pdf'
U_BRA2728 = 'https://www.pjm.com/-/media/DotCom/markets-ops/rpm/rpm-auction-info/2027-2028/2027-2028-bra-report.pdf'
U_IMM2829A = 'https://www.monitoringanalytics.com/reports/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf'


def read(name):
    return io.open(os.path.join(TXT, name), encoding='utf-8').read()


def money(s):
    return float(s.replace('$', '').replace(',', ''))


def short_dy(dy):  # '2015/2016' -> '2015/16'
    a, b = dy.split('/')
    return a + '/' + b[-2:]


rows = []


def add(market, dy, zone, price, total=None, mw=None, notes='', url='', verified=True):
    rows.append({
        'market': market, 'delivery_year': dy, 'zone_or_lda': zone,
        'price_usd_mw_day': '' if price is None else round(price, 2),
        'total_cost_usd': '' if total is None else int(round(total)),
        'cleared_mw': '' if mw is None else mw,
        'notes': notes, 'source_url': url, 'verified': 'true' if verified else 'false'})


# ---------------------------------------------------------------- PJM BRA LDA prices
H18 = ['RTO', 'MAAC', 'APS', 'PPL', 'EMAAC', 'SWMAAC', 'DPL-SOUTH', 'PSEG', 'PSEG-NORTH', 'PEPCO', 'ATSI', 'COMED', 'BGE']
H25 = H18 + ['DEOK', 'DOM']
lda_prices = {}  # (dy, lda) -> (price, url, note)

som18 = read('2018-som-pjm-sec5.txt')
for m in re.finditer(r'^(\d{4}/\d{4}) BRA (Annual|Capacity Performance) ((?:\$[\d,.]+ ?)+)$', som18, re.M):
    dy = short_dy(m.group(1))
    if dy < '2015/16' or dy > '2020/21':
        continue
    vals = re.findall(r'\$[\d,.]+', m.group(3))
    if len(vals) != len(H18):
        continue
    prod = 'Annual product (pre-Capacity Performance)' if m.group(2) == 'Annual' else 'Capacity Performance'
    for h, v in zip(H18, vals):
        lda_prices[(dy, h)] = (money(v), U_SOM18, 'BRA resource clearing price, ' + prod + '; IMM SOM 2018 Table 5-23')

som25 = read('2025-som-pjm-sec5.txt')
for m in re.finditer(r'^(\d{4}/\d{4}) BRA Capacity Performance ((?:\$[\d,.]+ ?)+)$', som25, re.M):
    dy = short_dy(m.group(1))
    vals = re.findall(r'\$[\d,.]+', m.group(2))
    if len(vals) != len(H25):
        continue
    for h, v in zip(H25, vals):
        lda_prices[(dy, h)] = (money(v), U_SOM25, 'BRA resource clearing price, Capacity Performance; IMM SOM 2025 Table 5-21')

# 2019/20 CP: page break in SOM 2018 text, so take PJM's own report (constrained LDAs: EMAAC, COMED, BGE)
b1920 = read('pjm_bra_2019_20.txt')
m = re.search(r'Capacity Type Rest of RTO EMAAC PEPCO COMED BGE\s+Capacity Performance ((?:\$[\d,.]+ ?)+)', b1920)
cp = dict(zip(['RTO', 'EMAAC', 'PEPCO', 'COMED', 'BGE'], [money(v) for v in re.findall(r'\$[\d,.]+', m.group(1))]))
parent = {'MAAC': 'RTO', 'APS': 'RTO', 'PPL': 'RTO', 'SWMAAC': 'RTO', 'DPL-SOUTH': 'EMAAC', 'PSEG': 'EMAAC',
          'PSEG-NORTH': 'EMAAC', 'ATSI': 'RTO'}
for h in H18:
    if h in cp:
        lda_prices[('2019/20', h)] = (cp[h], U_BRA1920, 'BRA CP resource clearing price; PJM 2019/20 BRA report')
    else:
        lda_prices[('2019/20', h)] = (cp[parent[h]], U_BRA1920,
                                      'BRA CP price; LDA not separately constrained so equals parent (' + parent[h] + ') price per PJM report')

# DEOK 2020/21 (constrained that year)
b2021 = read('pjm_bra_2020_21.txt')
m = re.search(r'Capacity Type Rest of RTO MAAC EMAAC COMED DEOK\s+Capacity Performance ((?:\$[\d,.]+ ?)+)', b2021)
lda_prices[('2020/21', 'DEOK')] = (money(re.findall(r'\$[\d,.]+', m.group(1))[4]), U_BRA2021, 'BRA CP price; DEOK constrained LDA')

# 2028/29 LDA table (all at $325 cap)
b2829 = read('pjm_bra_2028_29.txt')
lda_mw_2829 = {}
for m in re.finditer(r'^([A-Z][A-Z\-]+) ([\d,.]+) ([\d,.]+) \$([\d,.]+) \$([\d,.]+) \$([\d,.]+)$', b2829, re.M):
    name = {'COMED': 'COMED', 'DOM': 'DOM', 'ATSI-CLEVELAND': 'ATSI-CLEVELAND'}.get(m.group(1), m.group(1))
    lda_prices[('2028/29', name)] = (money(m.group(6)), U_BRA2829,
                                     'BRA CP price; all LDAs cleared at the $325.00/MW-day cap (uncapped simulation: $554.72)')
    lda_mw_2829[name] = float(m.group(3).replace(',', ''))

# RTO cleared MW and BRA $ (cleared MW x price) from PJM 2028/29 report Table 2 (2018/19+) and 2019/20 report Table 1
rto_mw, rto_bn = {}, {}
for m in re.finditer(r'^(\d{4}/\d{2})\d? \$([\d,.]+) ([\d,.]+) [\d.]+% [\d.]+% [\d.]+% \$([\d.]+)$', b2829, re.M):
    # setdefault: the report appendix repeats 2028/29 for the uncapped simulation ($554.72, $29.7bn); keep Table 2 value
    rto_mw.setdefault(m.group(1), float(m.group(3).replace(',', '')))
    rto_bn.setdefault(m.group(1), float(m.group(4)))
m = re.search(r'Auction Results ((?:\d{4}/\d{4}\d? ?)+)\nResource Clearing Price ((?:\$[\d.]+ ?)+)\nCleared UCAP \(MW\) ((?:[\d,.]+ ?)+)', b1920)
yrs = [short_dy(y[:9]) for y in m.group(1).split()]
for y, mw in zip(yrs, m.group(3).split()):
    rto_mw.setdefault(y, float(mw.replace(',', '')))

# IMM RPM revenue by delivery year (all auctions) and cost to load
rev = {}
for m in re.finditer(r'^(\d{4}/\d{4}) \$([\d.]+) ([\d,.]+) (\d{3}) \$([\d,]+)$', som25, re.M):
    rev[short_dy(m.group(1))] = money(m.group(5))

capnote = {
    '2025/26': 'First BRA reflecting PJM data-center load forecast surge; BGE and DOM constrained. IMM: data-center load added $9.33bn (Part G Revised, Scenario 88).',
    '2026/27': 'Cleared at the cap from the Shapiro-PJM agreement (cap/floor ~$325/$175 per MW-day UCAP). IMM: data-center load added $7.27bn.',
    '2027/28': 'Cleared at cap; 6,516.6 MW UCAP short of reliability requirement. IMM: data-center load added $6.50bn.',
    '2028/29': 'Cleared at cap; 6,831.3 MW UCAP short; uncapped simulation $554.72. IMM: data-center load added $6.27bn.',
}

# RTO rows
for dy in sorted(set(k[0] for k in lda_prices)):
    p, url, note = lda_prices[(dy, 'RTO')]
    if dy in rto_bn:
        total, tnote = rto_bn[dy] * 1e9, 'total_cost_usd = PJM "cleared MW x clearing price" for the BRA (rounded to $0.1bn; not a cost to load)'
        turl = U_BRA2829
    else:
        total, tnote = rev.get(dy), 'total_cost_usd = IMM RPM revenue for the delivery year, all RPM auctions (BRA + incrementals)'
        turl = U_SOM25
    extra = '' if dy not in rev else '; IMM RPM revenue all auctions = $%.2fbn' % (rev[dy] / 1e9)
    n = note + '; ' + tnote + extra + ('; ' + capnote[dy] if dy in capnote else '')
    add('PJM', dy, 'RTO', p, total, rto_mw.get(dy), n, url + ' | ' + turl)

# LDA rows
for (dy, lda), (p, url, note) in sorted(lda_prices.items()):
    if lda == 'RTO':
        continue
    n = note
    if lda == 'DOM' and dy in ('2022/23', '2023/24', '2024/25'):
        n += '; Dominion zone load was under the FRR alternative (self-supplied) before 2025/26 per PJM 2025/26 BRA report, so this LDA price did not set Dominion customers\' capacity cost'
    if lda == 'DEOK':
        n += '; DEOK = Duke Energy Ohio/Kentucky (column "DUKE" in IMM table)'
    mw = lda_mw_2829.get(lda) if dy == '2028/29' else None
    if mw is not None:
        n += '; cleared_mw = LDA total incl. nested child LDAs'
    add('PJM', dy, lda, p, None, mw, n, url)

# PECO convenience rows (PECO zone sits inside EMAAC and is not a separately modeled LDA)
for (dy, lda), (p, url, note) in sorted(lda_prices.items()):
    if lda == 'EMAAC':
        add('PJM', dy, 'PECO (zone in EMAAC)', p, None, None,
            'Derived: PECO is not a modeled LDA; its BRA price equals the EMAAC price', url)

# ---------------------------------------------------------------- PJM zonal weighted average (all auctions)
ZNORM = {'ACEC': 'AECO', 'AECO': 'AECO', 'ComEd': 'COMED', 'Cleveland': 'ATSI-CLEVELAND', 'DUKE': 'DEOK', 'DUQ': 'DLCO',
         'Dominion': 'DOM', 'DPL South': 'DPL-SOUTH', 'JCPLC': 'JCPL', 'MEC': 'METED', 'Met-Ed': 'METED', 'PE': 'PENELEC',
         'Pepco': 'PEPCO', 'PSEG North': 'PSEG-NORTH', 'REC': 'RECO'}
ZW = [('2018-som-pjm-sec5.txt', ['2018/19', '2019/20', '2020/21', '2021/22'], U_SOM18, 'Table 5-24'),
      ('2025-som-pjm-sec5.txt', ['2024/25', '2025/26', '2026/27', '2027/28'], U_SOM25, 'Table 5-23')]
for fname, years, url, tab in ZW:
    t = read(fname)
    start = t.index('Weighted average clearing prices by zone', t.index(tab) + 5)
    block = t[start:start + 2500]
    for m in re.finditer(r'^([A-Za-z][A-Za-z\- \.]+?) ((?:\$[\d,.]+ ?){4})$', block, re.M):
        zone = m.group(1).strip()
        zone = ZNORM.get(zone, zone.upper())
        vals = [money(v) for v in re.findall(r'\$[\d,.]+', m.group(2))]
        for y, v in zip(years, vals):
            add('PJM-zonal-weighted-avg', y, zone, v, None, None,
                'IMM cleared-MW-weighted average price for the zone across all RPM auctions for the delivery year (' + tab + ')', url)

# ---------------------------------------------------------------- MISO PRA (hand-entered)
U_MISO2627 = 'https://www.utilitydive.com/news/miso-capacity-auction-nerc/818797/'
U_MISO2627b = 'https://mgrid.org/2026/04/28/miso-2026-27-capacity-auction-clears-at-126-mw-day-down-42/'
U_MISO2526 = 'https://www.publicpower.org/node/30000'
U_MISO2425 = 'https://www.enelnorthamerica.com/insights/blogs/miso-2024-capacity-auction-results'
U_MISO2324 = 'https://www.utilitydive.com/news/miso-capacity-pra-auction-missouri/714403'
U_MISOPRA = 'https://www.misoenergy.org/markets-and-operations/resource-adequacy/'
miso = [
    ('2026/27', 'Summer LRZ 1-7 (North/Central)', 424.30, True, U_MISO2627, 'Seasonal PRA, summer season; annualized N/C ~ $126/MW-day'),
    ('2026/27', 'Summer LRZ 8 & 10', 384.10, True, U_MISO2627, 'Seasonal PRA, summer season'),
    ('2026/27', 'Summer LRZ 9', 412.10, True, U_MISO2627, 'Seasonal PRA, summer season (most of Louisiana, SE Texas)'),
    ('2026/27', 'Fall (all zones)', 33.92, True, U_MISO2627b, 'Seasonal PRA; one secondary source'),
    ('2026/27', 'Winter (all zones)', 35.97, True, U_MISO2627b, 'Seasonal PRA; one secondary source'),
    ('2026/27', 'Spring (all zones)', 7.61, True, U_MISO2627b, 'Seasonal PRA; one secondary source'),
    ('2026/27', 'Annualized (range across zones)', None, True, U_MISO2627b, 'Annualized $116-$126/MW-day across 10 zones, down from $212-$217'),
    ('2025/26', 'Summer (all zones)', 666.50, True, U_MISO2526, 'Seasonal PRA, summer; record; annualized $217 N/C, $212 South'),
    ('2025/26', 'Fall LRZ 1-7 (North/Central)', 91.60, True, U_MISO2526, 'Seasonal PRA'),
    ('2025/26', 'Fall LRZ 8-10 (South)', 74.09, True, U_MISO2526, 'Seasonal PRA'),
    ('2025/26', 'Winter (all zones)', 33.20, True, U_MISO2526, 'Seasonal PRA'),
    ('2025/26', 'Spring (all zones)', 69.88, True, U_MISO2526, 'Seasonal PRA'),
    ('2024/25', 'Summer (all zones)', 30.00, True, U_MISO2425, 'Seasonal PRA; Zone 5 (Missouri) cleared ~ $720 in fall and spring'),
    ('2024/25', 'Winter (most zones)', 0.75, True, U_MISO2425, 'Seasonal PRA'),
    ('2023/24', 'Summer (most zones)', 10.00, True, U_MISO2324, 'First seasonal PRA; fall $15, winter $2, spring $10; Zone 9 fall ~$59, winter ~$19'),
    ('2023/24', 'Fall (most zones)', 15.00, True, U_MISO2324, 'Seasonal PRA'),
    ('2023/24', 'Winter (most zones)', 2.00, True, U_MISO2324, 'Seasonal PRA'),
    ('2023/24', 'Spring (most zones)', 10.00, True, U_MISO2324, 'Seasonal PRA'),
    ('2022/23', 'LRZ 1-7 (North/Central)', 236.66, False, U_MISOPRA, 'UNVERIFIED (from memory): annual PRA cleared at CONE in North/Central; South ~ $2.88'),
    ('2022/23', 'LRZ 8-10 (South)', 2.88, False, U_MISOPRA, 'UNVERIFIED (from memory)'),
    ('2021/22', 'All zones', None, False, U_MISOPRA, 'Not checked this session'),
    ('2020/21', 'Most zones', 5.00, False, U_MISOPRA, 'UNVERIFIED (from memory): Zone 7 (Michigan) $257.53'),
    ('2019/20', 'Most zones', 2.99, False, U_MISOPRA, 'UNVERIFIED (from memory): Zone 7 $24.30'),
    ('2018/19', 'Zones 2-10', 10.00, False, U_MISOPRA, 'UNVERIFIED (from memory): Zone 1 $1.00'),
    ('2017/18', 'All zones', 1.50, False, U_MISOPRA, 'UNVERIFIED (from memory)'),
    ('2016/17', 'All zones', None, False, U_MISOPRA, 'Not checked this session'),
    ('2015/16', 'Zone 4 (Ameren Illinois)', 150.00, False, U_MISOPRA, 'UNVERIFIED (from memory): other zones ~$3.48; Zone 4 result was later challenged at FERC'),
]
for dy, zone, p, ver, url, note in miso:
    add('MISO PRA', dy, zone, p, None, None, note, url, ver)

# ---------------------------------------------------------------- ISO-NE FCA (hand-entered; $/kW-month converted)
K = 1000 * 12 / 365.0  # $/kW-month -> $/MW-day
U_FCA18 = 'https://www.iso-ne.com/static-assets/documents/100012/er24-1290-000.pdf'
isone = [
    ('2027/28', 'All zones (FCA 18)', 3.580, True, U_FCA18, 'Read from FERC order accepting FCA 18 results'),
    ('2026/27', 'Rest-of-Pool (FCA 17)', 2.590, True, 'https://www.iso-ne.com/static-assets/documents/2023/03/20230310_pr_fca17_initial_results_final.pdf', 'Preliminary result; New Brunswick $2.551'),
    ('2025/26', 'Rest-of-Pool (FCA 16)', 2.591, True, 'https://www.iso-ne.com/static-assets/documents/2022/03/20220309_pr_fca16_initial_results.pdf', 'SENE $2.639; NNE/Maine $2.531'),
    ('2025/26', 'SENE (FCA 16)', 2.639, True, 'https://www.iso-ne.com/static-assets/documents/2022/03/20220309_pr_fca16_initial_results.pdf', ''),
    ('2024/25', 'Rest-of-Pool (FCA 15)', 2.61, True, 'https://www.iso-ne.com/static-assets/documents/2021/02/20210211_pr_fca15_initial_results.pdf', 'SENE $3.98; NNE/Maine $2.48'),
    ('2024/25', 'SENE (FCA 15)', 3.98, True, 'https://www.iso-ne.com/static-assets/documents/2021/02/20210211_pr_fca15_initial_results.pdf', ''),
    ('2023/24', 'All zones (FCA 14)', 2.001, True, 'https://www.spglobal.com/platts/en/market-insights/latest-news/electric-power/021121-iso-ne-capacity-auction-prices-climb-from-record-lows-to-clear-at-248-to-398kw-m', 'Record low'),
    ('2022/23', 'Most resources (FCA 13)', 3.80, True, 'https://www.iso-ne.com/static-assets/documents/2019/02/20190206_pr_fca13_initial_results.pdf', ''),
    ('2021/22', 'SENE/NNE/RoP (FCA 12)', 4.631, True, 'https://www.iso-ne.com/static-assets/documents/2018/02/fca_12_results_filing.pdf', ''),
    ('2020/21', 'System (FCA 11)', 5.30, True, 'https://www.iso-ne.com/static-assets/documents/2021/03/a8_fca15_auction_results.pdf', 'From historical table in ISO-NE filing'),
    ('2019/20', 'System (FCA 10)', 7.030, True, 'https://portal.ct.gov/-/media/csc/1_dockets-medialibrary/docket470/nappexhibits/fagantestimonyredacted/5exh3resultsfca10summaryslidepdf.pdf', 'NY AC interface $6.26'),
    ('2018/19', 'Rest-of-Pool (FCA 9)', 9.551, False, 'https://www.iso-ne.com/markets-operations/markets/forward-capacity-market', 'UNVERIFIED (from memory); press coverage says FCA 9 "neared $10/kW-month"; SEMA/RI higher'),
    ('2017/18', 'System (FCA 8)', 15.00, False, 'https://www.iso-ne.com/markets-operations/markets/forward-capacity-market', 'UNVERIFIED (from memory): $15.00 new resources, $7.025 existing (administrative pricing)'),
    ('2016/17', 'Rest-of-Pool (FCA 7)', 3.15, False, 'https://www.iso-ne.com/markets-operations/markets/forward-capacity-market', 'UNVERIFIED (from memory); NEMA/Boston new resources $14.999'),
    ('2015/16', 'Rest-of-Pool (FCA 6)', 3.434, False, 'https://www.iso-ne.com/markets-operations/markets/forward-capacity-market', 'UNVERIFIED (from memory)'),
    ('2028/29', 'n/a', None, True, 'https://www.iso-ne.com/markets-operations/markets/forward-capacity-market', 'No FCA 19: ISO-NE delayed it while moving to a prompt/seasonal capacity auction'),
]
for dy, zone, kwmo, ver, url, note in isone:
    p = None if kwmo is None else kwmo * K
    n = ('Original price $%.3f/kW-month converted x 1000 x 12 / 365. ' % kwmo if kwmo is not None else '') + note
    add('ISO-NE FCA', dy, zone, p, None, None, n, url, ver)

# ---------------------------------------------------------------- NYISO (secondary only)
U_MODO = 'https://modoenergy.com/research/nyiso-capacity-prices-record-summer-2026'
nyiso = [
    ('2026 (May, monthly spot)', 'NYC (Zone J)', 32.6, 'Record; secondary (Modo Energy, paywalled); more than double May 2025 (~$15)'),
    ('2026 (June, monthly spot)', 'NYC (Zone J)', 32.5, 'Secondary (Modo Energy)'),
    ('2026 (summer, monthly spot)', 'Long Island (Zone K)', 11.70, 'Secondary (Modo Energy); also a record'),
    ('2026 (summer, monthly spot)', 'Rest of State', 7.87, 'Secondary (Modo Energy); also a record'),
    ('2025 (May, monthly spot)', 'NYC (Zone J)', 15.0, 'Secondary (Modo Energy), approximate'),
]
for dy, zone, kwmo, note in nyiso:
    add('NYISO ICAP spot', dy, zone, kwmo * K, None, None,
        'Original $%.2f/kW-month (UCAP) x 1000 x 12 / 365. NYISO prices are monthly, not annual. ' % kwmo + note +
        '. Not checked against NYISO ICAP reports.', U_MODO, False)

cols = ['market', 'delivery_year', 'zone_or_lda', 'price_usd_mw_day', 'total_cost_usd', 'cleared_mw', 'notes', 'source_url', 'verified']
with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
print('rows', len(rows))
