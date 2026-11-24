"""Parse PowerLines 'Utility Bills Are Rising' appendix tables (rate increase requests by utility).

Run (from ai-power-tax/):
  for each report:  python3 -I scripts/policy/pdf_text.py data/raw/policy/<folder>/<file>.pdf <txt>
  then:             python3 -I scripts/policy/parse_powerlines.py <txtdir> data/processed/policy_rate_requests_powerlines.csv

<txtdir> holds <folder>.raw.txt files produced by pdf_text.py (folder = powerlines_q1_2025 ...).
Amounts in the PowerLines appendices are in billions of dollars rounded to 0.1, so rows below $50M show as 0.0.
"""
import csv
import os
import re
import sys

txtdir, out = sys.argv[1], sys.argv[2]

STATES = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
          'District of Columbia', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas',
          'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
          'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
          'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island',
          'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
          'West Virginia', 'Wisconsin', 'Wyoming']
ABBR = dict(zip(STATES, ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
                         'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM',
                         'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA',
                         'WV', 'WI', 'WY']))
NOISE = re.compile(r'^(BT|ET|EMC|Q|q|/P|en-US|[-0-9. ]+(scn|SCN|Tc|Tm|Tw|Tf|TL|re|cm|f|W n|w|m|l|c|v|y|M|Tr|J|j|d|gs)?|S|f|n|W n|h|B|\d+ Tr|.*BDC.*|.*Artifact.*|.*MCID.*|/[A-Za-z0-9_]+ (gs|cs|CS|Do|sh)|/[A-Za-z0-9_]+ \d+ Tf|.*Tm|q .*|.* cm|.* (re|W n|Tr|M|w|J|j|d)|\d+ [Tt]r|/[A-Za-z0-9_]+ (cs|CS))$')


def tokens(path):
    raw = open(path, 'rb').read().decode('utf-8', 'ignore')
    out = []
    for line in raw.split('\n'):
        line = re.sub(r'\)-?[0-9.]+ \(', '', line)
        line = re.sub(r'^\[?\(', '', line)
        line = re.sub(r'\)\]?TJ$', '', line)
        line = re.sub(r'(/[A-Za-z0-9_]+ \d+ Tf|[-0-9.]+ (Tc|Tw) |[-0-9. ]+ Tm)', '', line)
        line = line.replace('\\', '').strip()
        if not line or (NOISE.match(line) and not re.match(r'^\d+\.\d$', line)):
            continue
        out.append(line)
    return out


REGIONS = {'South', 'West', 'Midwest', 'Northeast'}
TYPES = re.compile(r'^(Electric(?: and Gas| & Gas)?|Gas|Steam|Electric/Gas)$')
WHEN = re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}$')
CUST = re.compile(r'^[\d,]+$')
AMT = re.compile(r'^\$?\d+\.\d+$')


def match_state(toks, j):
    """Return (state, start_index) if a state name ends at toks[j] (names may be split across 2 tokens)."""
    for k in (1, 2):
        if j - k + 1 < 0:
            continue
        cand = ' '.join(t.strip() for t in toks[j - k + 1:j + 1])
        cand = re.sub(r'\s+', ' ', cand).strip()
        if cand in ABBR:
            return cand, j - k + 1
    return None, None


rows = []
for fn in sorted(os.listdir(txtdir)):
    if not fn.endswith('.raw.txt') or 'onepager' in fn or '2026' not in fn:
        continue  # 2025 reports use different appendix layouts; only 2026 quarterly appendices are parsed
    report = fn.replace('.raw.txt', '')
    T = [t.strip() for t in tokens(os.path.join(txtdir, fn))]
    for i in range(1, len(T) - 4):
        if T[i] not in REGIONS:
            continue
        if not (CUST.match(T[i + 1]) and TYPES.match(T[i + 2]) and WHEN.match(T[i + 3]) and AMT.match(T[i + 4])):
            continue
        util_toks, state = [], None
        j = i - 1
        while j >= 0 and len(util_toks) < 4:
            st, st_start = match_state(T, j)
            if st and util_toks:
                state = st
                break
            util_toks.insert(0, T[j])
            j -= 1
        if not state:
            continue
        rows.append({
            'report': report,
            'state': ABBR[state],
            'utility': ' '.join(util_toks),
            'region': T[i],
            'customers': int(T[i + 1].replace(',', '')),
            'type': T[i + 2],
            'when_requested': T[i + 3],
            'requested_increase_busd': float(T[i + 4].lstrip('$')),
            'source_as_listed': ' '.join(T[i + 5:i + 7])[:120],
        })

# de-duplicate rows that repeat across reports (later report wins)
seen = {}
for r in rows:
    key = (r['state'], r['utility'], r['type'], r['when_requested'], r['requested_increase_busd'])
    seen[key] = r
rows = list(seen.values())
rows.sort(key=lambda r: (-r['requested_increase_busd'], r['state']))
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows ->', out)
by = {}
for r in rows:
    by[r['report']] = by.get(r['report'], 0) + 1
print(by)
