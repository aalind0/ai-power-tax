"""Regional data-center bill estimates (outside PJM) -> assets/data/dc_regional.json.
Input: data/processed/markets_dc_regional.json (targeted research: official estimates or channel inputs per region)."""
import io, json, os

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
src = json.load(io.open(os.path.join(ROOT, 'data/processed/markets_dc_regional.json'), encoding='utf-8'))
LABEL = {'ERCOT': 'Texas (ERCOT)', 'CAISO': 'California (CAISO)', 'MISO': 'the Midwest grid (MISO)', 'SPP': 'the Southwest Power Pool',
         'ISO-NE': 'New England', 'NYISO': 'New York', 'Southeast': 'the Southeast', 'West': 'the West'}
# plain-language basis shown on the bill (the research notes stay in the processed file)
BASIS = {
    'ERCOT': 'Texas is building a roughly $33B high-voltage grid for oil-field and data-center demand, shared by all ERCOT customers. Little is in rates yet; the range shows its data-center share once built.',
    'CAISO': 'Little is in rates yet. Over $2B of new South Bay power lines for data centers will be shared by all California grid customers as they come online; PG&E says big new loads can lower rates.',
    'MISO': 'Midwest capacity prices jumped about tenfold in 2025, partly on data-center demand, but most utilities here own their plants, so little reaches home bills directly.',
    'SPP': 'Kansas and Missouri approved large-load rates in 2025 designed to make data centers cover their own costs instead of households.',
    'ISO-NE': 'New England\'s grid operator says data centers are not yet a major driver of demand; only a few hundred megawatts are in study.',
    'NYISO': 'Few large data centers are connected in New York yet, so the effect on today\'s bills is near zero.',
    'Southeast': 'Georgia approved a big data-center power build-out in Dec 2025 on condition it not add a projected $20/month to home bills through 2031. Other Southern utilities haven\'t published a figure.',
    'West': 'Arizona\'s APS has proposed raising data-center rates about 45% versus about 14% for homes so households don\'t subsidize them; the case is still pending.',
}
out = {}
for key, r in src['regions'].items():
    key = key.replace(' non-RTO', '')
    rec = r.get('recommended') or {}
    if rec.get('central') is None:
        continue
    off = r.get('official_estimate') or {}
    url = (r.get('checked') or {}).get('url') or off.get('url') or next((c.get('url') for c in r.get('channels') or [] if c.get('url')), None)
    out[key] = dict(low=rec.get('low', 0) or 0, central=rec['central'], high=rec.get('high', rec['central']),
                    confidence=rec.get('confidence'), basis=BASIS.get(key, rec.get('one_line_basis')), url=url, label=LABEL.get(key, key))
io.open(os.path.join(ROOT, 'assets/data/dc_regional.json'), 'w', encoding='utf-8').write(
    json.dumps({'as_of': src.get('as_of'), 'regions': out}, ensure_ascii=False, separators=(',', ':')))
for k, v in out.items():
    print(f"{k:10} {v['low']:.3f} / {v['central']:.3f} / {v['high']:.3f} c/kWh  {v['confidence']}")
