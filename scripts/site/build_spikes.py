"""Prototype data for the lab spike-map hero: per-area monthly cost change vs 2020 at constant usage."""
import io, json, glob, os
from collections import defaultdict, Counter

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
A = lambda p: os.path.join(ROOT, p)
L = lambda p: json.load(io.open(A(p), encoding='utf-8'))
YEARS = list(range(2020, 2027))
DC_CENTS = 7.27e9 / 7.93e11 * 100  # IMM 2026/27 data-center attribution / PJM kWh -> cents per kWh

index = {u['id']: u for u in L('assets/data/utilities_index.json')}
utils = {}
for f in glob.glob(A('assets/data/utilities/*.json')):
    for u in json.load(io.open(f, encoding='utf-8')):
        rows = {r[0]: r for r in (u.get('a') or [])}
        if 2020 not in rows or 2025 not in rows:
            continue
        kwh = [rows[y][4] for y in range(2020, 2026) if y in rows and rows[y][4]]
        if not kwh:
            continue
        kref = sum(kwh) / len(kwh)
        price = {y: rows[y][1] for y in range(2020, 2026) if y in rows and rows[y][1]}
        ix = index.get(u['id'], {})
        ytd = ix.get('ytd', u.get('ytd'))
        if ytd is not None and 2025 in price:
            price[2026] = price[2025] * (1 + ytd / 100.0)
        d = []
        for y in YEARS:
            p = price.get(y)
            if p is None:  # carry last known forward
                p = d and (price.get(y - 1)) or price[2020]
                price[y] = p
            d.append(round((price[y] - price[2020]) / 100 * kref, 1))
        dc = round(DC_CENTS / 100 * kref, 1) if u.get('r') == 'PJM' else 0
        utils[u['id']] = dict(id=u['id'], n=u['n'], st=u['st'], r=u.get('r'), c=u.get('c') or 0, k=round(kref), d=d, dc=dc, ytd=ytd is not None)

zips, zcta = L('assets/data/zip.json'), L('assets/data/zcta.json')
cells = defaultdict(list)
for z, ids in zips.items():
    pt = zcta.get(z)
    if not pt or pt[0] is None:
        continue
    cand = [i for i in ids if i in utils]
    if not cand:
        continue
    uid = max(cand, key=lambda i: utils[i]['c'])
    lat, lon = pt[0], pt[1]
    cells[(round(lat / 0.16), round(lon / 0.2))].append((lat, lon, uid))

order, uix, pts = [], {}, []
for pts_ in cells.values():
    cnt = Counter(p[2] for p in pts_)
    uid = max(cnt, key=lambda i: (cnt[i], utils[i]['c']))
    if uid not in uix:
        uix[uid] = len(order); order.append(uid)
    lat = sum(p[0] for p in pts_) / len(pts_); lon = sum(p[1] for p in pts_) / len(pts_)
    pts.append([round(lon, 2), round(lat, 2), uix[uid], len(pts_)])

U = [utils[i] for i in order]
def wavg(rows, f):
    w = sum(u['c'] for u in rows)
    return round(sum(u['c'] * f(u) for u in rows) / w, 1) if w else 0
allu = [u for u in utils.values() if u['c']]
pjm = [u for u in allu if u['r'] == 'PJM']
out = dict(
    years=YEARS, dcCents=round(DC_CENTS, 3),
    us=[wavg(allu, lambda u, i=i: u['d'][i]) for i in range(len(YEARS))],
    pjm=[wavg(pjm, lambda u, i=i: u['d'][i]) for i in range(len(YEARS))],
    pjmDc=wavg(pjm, lambda u: u['dc']),
    u=[[u['n'], u['st'], u['r'], u['d'], u['dc'], u['k']] for u in U],
    z=pts,
    dcs=[[c['lng'], c['lat'], c.get('mw'), c['n'], c['st'], c.get('s')] for c in L('assets/data/grid.json')['campuses'] if c.get('lat')],
)
io.open(A('assets/data/spikes.json'), 'w', encoding='utf-8').write(json.dumps(out, separators=(',', ':'), ensure_ascii=False))
print('utilities', len(U), 'cells', len(pts), 'campuses', len(out['dcs']))
print('US weighted', out['us']); print('PJM weighted', out['pjm'], 'PJM dc', out['pjmDc'], 'dc cents', out['dcCents'])
