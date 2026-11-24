"""Builds the compact JSON assets the website reads, from data/processed/*.
Run from the repo root:  python3 -I scripts/site/build_site_data.py
Writes assets/data/*.json (+ per-state utility shards in assets/data/utilities/).
"""
import csv, json, os, re, collections, math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
P = os.path.join(ROOT, 'data', 'processed')
OUT = os.path.join(ROOT, 'assets', 'data')
os.makedirs(os.path.join(OUT, 'utilities'), exist_ok=True)


def rows(name):
    with open(os.path.join(P, name), newline='', encoding='utf-8') as h:
        return list(csv.DictReader(h))


def num(v, d=None):
    try:
        x = float(v)
        return None if math.isnan(x) else (round(x, d) if d is not None else x)
    except (TypeError, ValueError):
        return None


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as h:
        json.dump(obj, h, separators=(',', ':'), ensure_ascii=False)
    return os.path.getsize(path)


sizes = {}
truthy = lambda v: str(v).strip().lower() in ('true', '1', 'yes')

# ---------------------------------------------------------------- PJM zone mapping (by utility name)
ZONES = [
    ('AECO', r'atlantic city electric', None), ('AEP', r'appalachian power|ohio power|indiana michigan power|kentucky power|wheeling power|kingsport power', None),
    ('APS', r'potomac edison|monongahela power|west penn power', None), ('ATSI', r'ohio edison|cleveland electric|toledo edison|pennsylvania power co', None),
    ('BGE', r'baltimore gas', None), ('ComEd', r'commonwealth edison', None), ('DAY', r'dayton power|aes ohio', None),
    ('DEOK', r'duke energy ohio|duke energy kentucky', None), ('DOM', r'virginia electric', None), ('DPL', r'delmarva', None),
    ('DUQ', r'duquesne light', None), ('EKPC', r'east kentucky', None), ('JCPL', r'jersey central', None),
    ('ME', r'metropolitan edison', None), ('PECO', r'^peco', None), ('PENELEC', r'^pennsylvania electric co', None),
    ('PEPCO', r'potomac electric power', None), ('PPL', r'ppl electric', None), ('PSEG', r'public service elec.*gas', 'NJ'),
    ('RECO', r'rockland electric', None),
]
# capacity price lookup order for each transmission zone (LDA names as in markets_capacity_prices.csv)
CAP_LDA = {
    'BGE': ['BGE', 'SWMAAC', 'MAAC', 'RTO'], 'PEPCO': ['PEPCO', 'SWMAAC', 'MAAC', 'RTO'], 'DOM': ['DOM', 'RTO'], 'ComEd': ['COMED', 'RTO'],
    'PSEG': ['PSEG', 'EMAAC', 'MAAC', 'RTO'], 'PECO': ['PECO (zone in EMAAC)', 'EMAAC', 'MAAC', 'RTO'], 'PPL': ['PPL', 'MAAC', 'RTO'],
    'JCPL': ['JCPL', 'EMAAC', 'MAAC', 'RTO'], 'AECO': ['EMAAC', 'MAAC', 'RTO'], 'DPL': ['EMAAC', 'MAAC', 'RTO'], 'RECO': ['EMAAC', 'MAAC', 'RTO'],
    'ME': ['MAAC', 'RTO'], 'PENELEC': ['MAAC', 'RTO'], 'ATSI': ['ATSI', 'RTO'], 'DEOK': ['DEOK', 'RTO'], 'DAY': ['DAY', 'RTO'], 'APS': ['APS', 'RTO'],
    'AEP': ['RTO'], 'DUQ': ['RTO'], 'EKPC': ['RTO'],
}


def zone_for(name, state):
    n = (name or '').lower()
    for z, pat, st in ZONES:
        if re.search(pat, n) and (st is None or st == state):
            return z
    return None


# ---------------------------------------------------------------- utilities (annual + monthly)
annual = collections.defaultdict(list)
meta = {}
price_rows = rows('bills_utility_prices.csv')
# Texas wires companies: the source carries one statewide retail all-in price. Split it into a statewide energy
# part (all-in minus the customer-weighted average delivery rate) plus each company's own delivery rate.
tx_energy = {}
_acc = collections.defaultdict(lambda: [0.0, 0.0, None])
for r in price_rows:
    if r['state'] == 'TX' and r['basis'] == 'delivery_only' and num(r['res_delivery_only_price_cents_kwh']) and num(r['res_delivery_only_customers']):
        a = _acc[int(r['year'])]
        a[0] += num(r['res_delivery_only_price_cents_kwh']) * num(r['res_delivery_only_customers'])
        a[1] += num(r['res_delivery_only_customers'])
        a[2] = num(r['tx_rep_all_in_price_cents_kwh']) or a[2]
for y, (pc, c, allin) in _acc.items():
    if c and allin:
        tx_energy[y] = allin - pc / c
cpi_by_year = {}
for r in price_rows:
    if num(r['cpi_u_annual_avg']):
        cpi_by_year[int(r['year'])] = num(r['cpi_u_annual_avg'])
for r in price_rows:
    y = int(r['year'])
    if y < 2013:
        continue
    key = (r['eia_utility_id'], r['state'])
    price = num(r['res_all_in_price_cents_kwh'], 2) or num(r['res_price_cents_kwh'], 2)
    real = num(r['res_all_in_price_real2025_cents_kwh'], 2) or num(r['res_price_real2025_cents_kwh'], 2)
    if r['state'] == 'TX' and r['basis'] == 'delivery_only' and y in tx_energy and num(r['res_delivery_only_price_cents_kwh']):
        price = round(tx_energy[y] + num(r['res_delivery_only_price_cents_kwh']), 2)
        if cpi_by_year.get(y) and cpi_by_year.get(2025):
            real = round(price * cpi_by_year[2025] / cpi_by_year[y], 2)
    bill = num(r['res_all_in_avg_monthly_bill_usd'], 1) or num(r['avg_monthly_bill_usd'], 1)
    # delivery-only utilities (e.g. Texas wires companies) report customers in the delivery-only columns
    cust = num(r['res_customers']) or num(r['res_delivery_only_customers'])
    if price is None or not cust:
        continue
    annual[key].append([y, price, real, bill, num(r['res_all_in_avg_monthly_kwh'], 0) or num(r['avg_monthly_kwh'], 0),
                        1 if truthy(r['res_all_in_is_estimate']) else 0])
    m = meta.get(key)
    if not m or y >= m['y']:
        meta[key] = {'y': y, 'name': r['utility_name'], 'own': r['ownership'], 'rto': (r['rto_iso'] or 'none').split(';')[0],
                     'cust': int(cust), 'basis': r['basis'], 'ba': r['ba_code']}

monthly = collections.defaultdict(list)
ytd = collections.defaultdict(lambda: collections.defaultdict(lambda: [0.0, 0.0, set()]))  # key -> year -> [rev, sales, months]
for r in rows('bills_utility_monthly.csv'):
    key = (r['eia_utility_id'], r['state'])
    p = num(r['res_price_cents_kwh'], 2)
    if p is None:
        continue
    monthly[key].append([r['date'], p, num(r['res_avg_monthly_bill_usd'], 1)])
    rev, sales = num(r['res_revenue_thousand_usd']), num(r['res_sales_mwh'])
    if rev and sales:
        acc = ytd[key][int(r['year'])]
        acc[0] += rev
        acc[1] += sales
        acc[2].add(int(r['month']))


def ytd_change(key):
    a, b = ytd[key].get(2026), ytd[key].get(2025)
    if not a or not b:
        return None
    months = sorted(a[2])
    # compare like-for-like months only
    rev25 = sales25 = 0.0
    if a[2] != b[2] and not a[2] <= b[2]:
        return None
    # recompute 2025 for the same months
    return months


# second pass for like-for-like YTD (needs per-month values)
per_month = collections.defaultdict(dict)
for r in rows('bills_utility_monthly.csv'):
    rev, sales = num(r['res_revenue_thousand_usd']), num(r['res_sales_mwh'])
    if rev and sales:
        per_month[(r['eia_utility_id'], r['state'])][(int(r['year']), int(r['month']))] = (rev, sales)


def like_for_like(key):
    pm = per_month.get(key, {})
    months = [m for (y, m) in pm if y == 2026 and (2025, m) in pm]
    if len(months) < 3:
        return None, 0
    r26 = sum(pm[(2026, m)][0] for m in months); s26 = sum(pm[(2026, m)][1] for m in months)
    r25 = sum(pm[(2025, m)][0] for m in months); s25 = sum(pm[(2025, m)][1] for m in months)
    if not s26 or not s25:
        return None, 0
    return round(((r26 / s26) / (r25 / s25) - 1) * 100, 1), max(months)


index, shards = [], collections.defaultdict(list)
zone_hits = collections.defaultdict(list)
for key, series in annual.items():
    series.sort()
    m = meta[key]
    if m['y'] < 2023:
        continue
    by_year = {s[0]: s for s in series}
    base = by_year.get(2020)
    last = series[-1]
    ch20 = round((last[2] / base[2] - 1) * 100, 1) if base and base[2] and last[2] else None
    nom20 = round((last[1] / base[1] - 1) * 100, 1) if base and base[1] else None
    ytd_pct, ytd_m = like_for_like(key)
    zone = zone_for(m['name'], key[1]) if m['rto'] == 'PJM' else None
    if zone:
        zone_hits[zone].append(f"{m['name']} ({key[1]})")
    entry = {'id': int(key[0]), 'st': key[1], 'n': m['name'], 'o': m['own'], 'r': m['rto'], 'c': m['cust'], 'y': last[0],
             'p': last[1], 'b': last[3], 'ch': ch20, 'chn': nom20, 'ytd': ytd_pct, 'ytdm': ytd_m, 'z': zone}
    index.append(entry)
    shards[key[1]].append({**entry, 'a': series, 'mo': sorted(monthly.get(key, []))})

index.sort(key=lambda e: -e['c'])
sizes['utilities_index.json'] = dump('utilities_index.json', index)
for st, lst in shards.items():
    sizes[f'utilities/{st}.json'] = dump(f'utilities/{st}.json', lst)
print('PJM zone matches:', {z: len(v) for z, v in zone_hits.items()})
for z in ('PSEG', 'PENELEC', 'ATSI', 'APS'):
    print('  ', z, zone_hits.get(z))

# ---------------------------------------------------------------- states & US
st_annual = collections.defaultdict(list)
for r in rows('bills_state_annual.csv'):
    # [year, price, real price, avg bill, residential customers (homes), residential sales MWh]
    st_annual[r['state']].append([int(r['year']), num(r['res_price_cents_kwh'], 2), num(r['res_price_real2025_cents_kwh'], 2), num(r['res_avg_monthly_bill_usd'], 1),
                                  num(r['res_customers'], 0), num(r['res_sales_mwh'], 0)])
summary = json.load(open(os.path.join(P, 'bills_summary.json'), encoding='utf-8'))
# [year, price, real price, avg bill, avg monthly kWh]
us_annual = [[int(y), v['res_price_cents_kwh'], v['res_price_real2025_cents_kwh'], v['res_avg_monthly_bill_usd'], v.get('res_avg_monthly_kwh')] for y, v in summary['us'].items() if y.isdigit()]
st_month = collections.defaultdict(dict)
latest_ttm = {}
for r in rows('bills_state_monthly.csv'):
    st, y, mth = r['state'], int(r['year']), int(r['month'])
    rev, sales = num(r['res_revenue_thousand_usd']), num(r['res_sales_mwh'])
    if rev and sales:
        st_month[st][(y, mth)] = (rev, sales)
    if r['res_price_ttm_yoy_pct']:
        latest_ttm[st] = (r['date'], num(r['res_price_ttm_yoy_pct'], 1), num(r['cpi_u_all_items_yoy_pct'], 1))
states = {}
for st, series in st_annual.items():
    pm = st_month.get(st, {})
    months = [m for (y, m) in pm if y == 2026 and (2025, m) in pm]
    ytd_pct = None
    if months:
        r26 = sum(pm[(2026, m)][0] for m in months); s26 = sum(pm[(2026, m)][1] for m in months)
        r25 = sum(pm[(2025, m)][0] for m in months); s25 = sum(pm[(2025, m)][1] for m in months)
        ytd_pct = round(((r26 / s26) / (r25 / s25) - 1) * 100, 1)
    series.sort()
    by = {s[0]: s for s in series}
    ch20 = round((by[2025][2] / by[2020][2] - 1) * 100, 1) if 2025 in by and 2020 in by else None
    states[st] = {'a': series, 'ytd': ytd_pct, 'ttm': latest_ttm.get(st), 'ch': ch20}
us_pm = st_month.get('US', {})
us_series_monthly = sorted([[f'{y}-{m:02d}', round(v[0] / v[1] * 100, 2)] for (y, m), v in us_pm.items()])
cpi = [[r['date'], num(r['cpi_u_all_items_nsa'], 3), num(r['cpi_u_electricity_nsa'], 3)] for r in rows('bills_cpi_monthly.csv') if int(r['year']) >= 2013]
sizes['prices.json'] = dump('prices.json', {'us': sorted(us_annual), 'usMonthly': us_series_monthly, 'states': states, 'cpi': cpi,
                                            'latestMonth': summary['latest_month'], 'cpiChange': summary['cpi_u_change_pct'],
                                            'usLatest': summary.get('us_latest')})

# ---------------------------------------------------------------- markets / grid / load
cap = collections.defaultdict(list)
for r in rows('markets_capacity_prices.csv'):
    v = num(r['price_usd_mw_day'], 2)
    if v is None:
        continue
    cap[r['market']].append({'dy': r['delivery_year'], 'z': r['zone_or_lda'], 'p': v, 'cost': num(r['total_cost_usd']), 'mw': num(r['cleared_mw']),
                             'note': r['notes'][:160], 'v': truthy(r['verified']), 'url': r['source_url']})
comp = [{'per': r['period'], 'e': num(r['energy_usd_mwh'], 2), 'c': num(r['capacity_usd_mwh'], 2), 't': num(r['transmission_usd_mwh'], 2),
         'o': num(r['other_usd_mwh'], 2), 'tot': num(r['total_usd_mwh'], 2)} for r in rows('markets_pjm_wholesale_cost_components.csv')]
td = [{'y': int(r['year']), 't': num(r['transmission_capex_busd_real2025'], 2), 'd': num(r['distribution_capex_busd_real2025'], 2),
       'tn': num(r['transmission_capex_busd'], 2), 'dn': num(r['distribution_capex_busd'], 2), 'g': num(r['aeo_generation_cents_kwh'], 2),
       'tc': num(r['aeo_transmission_cents_kwh'], 2), 'dc': num(r['aeo_distribution_cents_kwh'], 2), 'all': num(r['aeo_all_sectors_price_cents_kwh'], 2)}
      for r in rows('grid_td_spending.csv')]
nits = collections.defaultdict(list)
for r in rows('grid_transmission_rates.csv'):
    if r['iso'] != 'PJM' or not r['nits_rate_usd_per_mw_yr']:
        continue
    nits[r['zone']].append([int(r['year']), num(r['nits_rate_usd_per_mw_yr'], 0)])
nits_out = {z: {'name': next((r['zone_name'] for r in rows('grid_transmission_rates.csv') if r['zone'] == z), z), 's': sorted(v)} for z, v in nits.items()}
studies = json.load(open(os.path.join(P, 'markets_attribution_studies.json')))
studies_out = [{k: s.get(k) for k in ('id', 'title', 'author_org', 'date', 'type', 'claim', 'region', 'stance', 'url', 'verified', 'method')} |
               {'kn': s.get('key_numbers'), 'notes': s.get('notes')} for s in studies] if False else [
    dict({k: s.get(k) for k in ('id', 'title', 'author_org', 'date', 'type', 'claim', 'region', 'stance', 'url', 'verified')}, notes=s.get('notes'))
    for s in studies]
load_share = {}
us_load = []
for r in rows('load_state_dc_share.csv'):
    if r['state'] == 'US':
        us_load.append({'y': int(r['year']), 'sc': r['scenario'], 'proj': truthy(r['is_projection']), 'pct': num(r['dc_share_pct'], 2),
                        'lo': num(r['dc_share_pct_low'], 2), 'hi': num(r['dc_share_pct_high'], 2), 'twh': num(r['dc_twh'], 1), 'src': r['source'][:80]})
    elif r['scenario'] == '2023_estimate' and r['dc_share_pct']:
        load_share[r['state']] = {'pct': num(r['dc_share_pct'], 2), 'twh': num(r['dc_twh'], 2), 'src': r['source'][:90], 'url': r['source_url']}
disclosures = [{'id': num(r['eia_utility_id']), 'u': r['utility'], 'st': r['state'], 'per': r['period'], 'm': r['metric'], 'v': num(r['value'], 2),
                'unit': r['unit'], 'q': r['quote_or_basis'][:220], 'src': r['source'][:100], 'url': r['source_url'], 'ok': truthy(r['verified'])}
               for r in rows('load_utility_dc_disclosures.csv')]
campuses = [{'id': r['campus_id'], 'n': r['campus_name'], 'st': r['state'], 'u': r['utility'], 'r': r['rto'], 'mw': num(r['powerMW'], 0),
             's': r['status'], 'cl': truthy(r['is_market_cluster']), 'lat': num(r['lat'], 4), 'lng': num(r['lng'], 4)}
            for r in rows('markets_utility_dc_load.csv') if r['lat'] and r['lng']]
sizes['grid.json'] = dump('grid.json', {'capacity': cap, 'components': comp, 'td': td, 'nits': nits_out, 'capLda': CAP_LDA,
                                        'studies': studies_out, 'loadShare': load_share, 'usLoad': us_load,
                                        'disclosures': disclosures, 'campuses': campuses})

# ---------------------------------------------------------------- bill anatomy
anat = json.load(open(os.path.join(P, 'bills_anatomy.json')))
sizes['anatomy.json'] = dump('anatomy.json', {'categories': anat['categories'], 'pjm': anat.get('pjm_capacity_context'),
                                              'utilities': {str(u['eia_utility_id']): u for u in anat['utilities']}})

# ---------------------------------------------------------------- policy
pol = json.load(open(os.path.join(P, 'policy_states.json')))
pol_out = {}
for s in pol['states']:
    llt, inc = s.get('large_load_tariff') or {}, s.get('dc_tax_incentive') or {}
    pol_out[s['state']] = {
        'name': s['name'], 'rto': s.get('rto'), 'v': s.get('verified'),
        'llt': {'status': llt.get('status'), 'utilities': llt.get('utilities'), 'terms': llt.get('key_terms'), 'year': llt.get('year'), 'url': llt.get('source_url')},
        'inc': {'type': inc.get('type'), 'cost': inc.get('est_annual_cost_usd'), 'costYear': inc.get('cost_year'), 'status': inc.get('status_2026'),
                'notes': inc.get('notes'), 'url': inc.get('source_url')},
        'laws': [{'bill': l.get('bill'), 'sum': (l.get('summary') or '')[:240], 'status': l.get('status'), 'url': l.get('url')} for l in (s.get('legislation_2025_2026') or [])][:6],
        'adv': s.get('consumer_advocate'), 'puc': s.get('puc'), 'notes': (s.get('notes') or '')[:300],
    }
rc = json.load(open(os.path.join(P, 'policy_rate_cases.json')))
sizes['policy.json'] = dump('policy.json', {'states': pol_out, 'cases': rc['cases'], 'national': rc.get('national_rate_requests')})

# ---------------------------------------------------------------- households
burden = {}
for r in rows('households_energy_burden_county.csv'):
    burden[r['county_fips']] = [r['county'], r['state'], num(r['avg_energy_burden_pct'], 2), num(r['low_income_burden_pct'], 2),
                                num(r['avg_annual_elec_cost_usd'], 0), num(r['households'], 0), num(r['low_income_share_pct'], 1),
                                num(r['avg_annual_elec_cost_2025_est_usd'], 0)]
shut, tot_d, tot_c = {}, 0, 0
for r in rows('households_eia112_disconnections_2024.csv'):
    d, c = num(r['disconnections']), num(r['avg_residential_customers'])
    if d is not None and c:
        if r['utility_name'].strip().lower() == 'state total':  # national total = sum of EIA's state totals
            tot_d += d
            tot_c += c
        elif r['eia_utility_id']:
            shut[f"{int(float(r['eia_utility_id']))}-{r['state']}"] = [num(r['disconnections_per_100_customers'], 2), int(d), int(c)]
hh_groups = rows('households_burden_national_by_group.csv')
sizes['households.json'] = dump('households.json', {'county': burden, 'shutoffs': shut, 'shutNational': {'disc': int(tot_d), 'per100': round(tot_d / tot_c * 100, 2)},
                                                    'groups': hh_groups})

# ---------------------------------------------------------------- lookup fallbacks
zipmap = collections.defaultdict(list)
for r in rows('geo_zip_to_utility.csv'):
    if r['eia_utility_id']:
        i = int(float(r['eia_utility_id']))
        if i not in zipmap[r['zip']]:
            zipmap[r['zip']].append(i)
sizes['zip.json'] = dump('zip.json', zipmap)
# ZIP (ZCTA) centroids from the Census Gazetteer, with the ZIP's state from the OpenEI ZIP→utility table
zip_state = collections.defaultdict(collections.Counter)
for r in rows('geo_zip_to_utility.csv'):
    if r['state']:
        zip_state[r['zip']][r['state']] += 1
gaz = os.path.join(ROOT, 'data', 'raw', 'geo', 'census_zcta_gazetteer_2024', '2024_Gaz_zcta_national.txt')
if os.path.exists(gaz):
    zcta = {}
    with open(gaz, encoding='utf-8') as h:
        for i, line in enumerate(h):
            p = [x.strip() for x in line.split('\t')]
            if i == 0 or len(p) < 7:
                continue
            st = zip_state[p[0]].most_common(1)[0][0] if zip_state.get(p[0]) else None
            zcta[p[0]] = [round(float(p[5]), 4), round(float(p[6]), 4), st]
    # ZIPs without a Census area (PO boxes, single-building ZIPs like 20500) still need their state
    for z, cnt in zip_state.items():
        if z not in zcta:
            zcta[z] = [None, None, cnt.most_common(1)[0][0]]
    sizes['zcta.json'] = dump('zcta.json', zcta)
    print('ZIP centroids:', len(zcta), 'with state:', sum(1 for v in zcta.values() if v[2]))
countymap = collections.defaultdict(list)
for r in rows('geo_county_to_utility.csv'):
    if r['year'] == '2025' and r['eia_utility_id']:
        i = int(float(r['eia_utility_id']))
        if i not in countymap[r['county_fips']]:
            countymap[r['county_fips']].append(i)
sizes['county_utils.json'] = dump('county_utils.json', countymap)
xwalk = {r['territory_eia_utility_id']: int(r['current_eia_utility_id']) for r in rows('geo_utility_id_crosswalk.csv')}
sizes['crosswalk.json'] = dump('crosswalk.json', xwalk)

print(f"utilities: {len(index)} in {len(shards)} state shards")
for k, v in sorted(sizes.items(), key=lambda x: -x[1])[:12]:
    print(f"  {k:28s} {v/1e6:6.2f} MB")
print('total', round(sum(sizes.values()) / 1e6, 2), 'MB')

# ---------------------------------------------------------------- findings page
F = {}
# double-digit increases by year: share of utilities whose average residential price rose >=10% vs the prior year
by_key = collections.defaultdict(dict)
for r in price_rows:
    p = num(r['res_all_in_price_cents_kwh']) or num(r['res_price_cents_kwh'])
    c = num(r['res_customers']) or num(r['res_delivery_only_customers'])
    if p and c and c >= 1000:
        by_key[(r['eia_utility_id'], r['state'])][int(r['year'])] = p
dd = []
for y in range(2014, 2026):
    pairs = [(v[y], v[y - 1]) for v in by_key.values() if y in v and y - 1 in v]
    if pairs:
        dd.append({'y': str(y), 'share': round(100 * sum(1 for a, b in pairs if a / b - 1 >= 0.10) / len(pairs), 1), 'n': len(pairs)})
F['doubleDigit'] = dd
# sales growth at data-center hotspots (latest year vs base year)
sg = {}
for r in rows('load_utility_sales_growth.csv'):
    if r['entity_type'] != 'utility':
        continue
    k = (r['eia_utility_id'], r['state'])
    if k not in sg or int(r['year']) > int(sg[k]['year']):
        sg[k] = r
F['salesGrowth'] = sorted([{'u': r['label'][:46], 'st': r['state'], 'base': r['base_year'], 'y': r['year'], 'ci': num(r['ci_growth_pct_vs_base'], 1), 'res': num(r['res_growth_pct_vs_base'], 1),
                            'twh': num(r['ci_added_twh_vs_base'], 2), 'hot': r['hotspot'][:60]} for r in sg.values() if num(r['ci_growth_pct_vs_base']) is not None], key=lambda x: -(x['ci'] or 0))
F['ciRank'] = [{'u': r['utility_name'][:40], 'st': r['state'], 'ba': r['ba_code'], 'twh': num(r['ci_added_twh'], 1), 'ci': num(r['ci_growth_pct'], 1), 'res': num(r['res_growth_pct'], 1), 'base': r['base_year']}
               for r in sorted(rows('load_utility_ci_growth_rank.csv'), key=lambda r: int(r['rank']))[:14]]
F['international'] = [{k: p.get(k) for k in ('country', 'iso2', 'year', 'dc_share_pct', 'series', 'source', 'source_url', 'note')} for p in json.load(open(os.path.join(P, 'load_international.json'), encoding='utf-8'))['points']]
mlg = json.load(open(os.path.join(P, 'markets_load_growth.json'), encoding='utf-8'))
F['pipelines'] = [{k: p.get(k) for k in ('utility', 'rto', 'state', 'contracted_gw', 'contracted_definition', 'total_pipeline_gw', 'as_of', 'url', 'verified')} for p in mlg['utility_pipelines'] if p.get('total_pipeline_gw') or p.get('contracted_gw')]
F['rtoForecasts'] = mlg['rto_forecasts']
names = {'CEG': 'Constellation', 'VST': 'Vistra', 'TLN': 'Talen', 'NRG': 'NRG', 'GEV': 'GE Vernova', 'OKLO': 'Oklo', 'SMR': 'NuScale', 'SPY': 'S&P 500', 'XLU': 'Utilities index', 'D': 'Dominion', 'AEP': 'AEP',
         'EXC': 'Exelon', 'DUK': 'Duke', 'SO': 'Southern', 'NEE': 'NextEra', 'ETR': 'Entergy', 'PEG': 'PSEG', 'FE': 'FirstEnergy', 'PPL': 'PPL', 'XEL': 'Xcel', 'AEE': 'Ameren', 'CNP': 'CenterPoint',
         'EVRG': 'Evergy', 'NI': 'NiSource', 'PNW': 'Pinnacle West', 'SRE': 'Sempra', 'WEC': 'WEC Energy'}
F['stocks'] = [{'t': r['ticker'], 'n': names.get(r['ticker'], r['ticker']), 'g': r['group'], 'base': r['base_date'], 'latest': r['latest_date'], 'chg': num(r['pct_base_to_latest'], 1),
                'peak': round((num(r['peak_close']) / num(r['close_base']) - 1) * 100, 1) if num(r['peak_close']) and num(r['close_base']) else None, 'peakDate': r['peak_date']} for r in rows('finance_stock_moves.csv')]
cx = rows('finance_utility_capex.csv')
F['capexIndustry'] = sorted([{'y': r['plan_period'], 'usd': num(r['capex_usd']), 'kind': 'actual' if r['record_type'] == 'eei_industry_actual' else 'projected', 'ok': truthy(r['verified'])}
                             for r in cx if r['record_type'] in ('eei_industry_actual', 'eei_industry_projection') and num(r['capex_usd'])], key=lambda x: x['y'])
F['capexPlans'] = sorted([{'c': r['company'], 'per': r['plan_period'], 'usd': num(r['capex_usd']), 'ok': truthy(r['verified']), 'dc': r['dc_related_note'][:160], 'url': r['source_url']}
                          for r in cx if r['record_type'] == 'company_plan_latest' and num(r['capex_usd'])], key=lambda x: -x['usd'])
F['roe'] = [{'y': int(r['year']), 'roe': num(r['avg_authorized_roe_pct_ex_riders'], 2), 'ust': num(r['ust10y_avg_pct'], 2), 'share': num(r['authorized_share_of_requested_increase_pct_ex_riders'], 1)}
            for r in rows('finance_roe.csv') if r['record_type'] == 'annual_average' and num(r['avg_authorized_roe_pct_ex_riders'])]
gp = json.load(open(os.path.join(P, 'grid_dc_projects.json'), encoding='utf-8'))
F['projects'] = [{k: p.get(k) for k in ('project', 'package', 'region', 'states', 'voltage_kv', 'cost_usd', 'dc_link_type', 'cost_allocation', 'status', 'in_service', 'local_opposition', 'source_url', 'verified', 'level', 'purpose')}
                 for p in gp['projects'] if p.get('cost_usd')]
F['burden'] = [{'g': r['group'], 'type': r['group_type'], 'pct': num(r['energy_burden_pct'], 2), 'inc': num(r['avg_household_income_usd'], 0), 'cost': num(r['avg_annual_energy_cost_usd'], 0)} for r in rows('households_burden_national_by_group.csv')]
pol_j = json.load(open(os.path.join(P, 'households_polling.json'), encoding='utf-8'))
F['polls'] = [{k: p.get(k) for k in ('pollster', 'field_dates', 'published', 'sample', 'question', 'results', 'url', 'verified')} for p in pol_j['national_polls']]
F['shutState'] = sorted([{'st': r['state'], 'd': int(num(r['disconnections'])), 'per100': num(r['disconnections_per_100_customers'], 2), 'cust': num(r['avg_residential_customers'], 0)}
                         for r in rows('households_eia112_disconnections_2024.csv') if r['utility_name'].strip().lower() == 'state total' and num(r['disconnections'])], key=lambda x: -(x['per100'] or 0))
sizes['findings.json'] = dump('findings.json', F)
print('findings:', {k: len(v) for k, v in F.items()})
