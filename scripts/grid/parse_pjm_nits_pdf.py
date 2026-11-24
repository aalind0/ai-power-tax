"""Parse PJM 'ATRR and NITS Rates' PDF postings (text extracted with pdf2txt.js) into zone-level NITS rates.
Each PDF page is one posting ('As of M/D/YYYY'). NITS rates are the numbers < 300,000 on a page, in zone order.
Usage: python3 -I scripts/grid/parse_pjm_nits_pdf.py <txt> [<txt> ...]  -> prints CSV rows (zone,as_of,rate,src)"""
import re
import sys

ZONE_ORDER_HINTS = ['AECO', 'AEP', 'APS', 'ATSI', 'BGE', 'ComEd', 'DAY', 'DEOK', 'DOM', 'DPL', 'DUQ', 'EKPC', 'JCPL',
                    'ME', 'OVEC', 'PECO', 'PEPCO', 'PPL', 'PSEG', 'RECO']
num = re.compile(r'\d{1,3}(?:,\d{3})*\.\d{2}')
for path in sys.argv[1:]:
    t = open(path, encoding='utf-8').read()
    for page in t.split('=== PAGE ')[1:]:
        m = re.search(r'As of\s+(\d{1,2}/\d{1,2}/\d{4})', page)
        asof = m.group(1) if m else None
        # which zones appear on the page, in order of first appearance as a standalone token
        zones = [z for z in ZONE_ORDER_HINTS if re.search(r'(^|\n|\s)' + re.escape(z) + r'(\s|$)', page)]
        vals = [float(v.replace(',', '')) for v in num.findall(page)]
        rates = [v for v in vals if v < 300000]
        print('#', path.split('/')[-1], asof, 'zones', len(zones), 'rates', len(rates), rates)
