"""Print sentences from text files that match a keyword regex AND contain a number-ish token.
Usage: python3 -I scripts/finance/grep_sentences.py '<keyword regex>' file1.txt [file2.txt ...]
Env-free; reads only the given files.
"""
import io
import re
import sys

pat = re.compile(sys.argv[1], re.I)
num = re.compile(r'(billion|\$\s?\d|\d+(\.\d+)?\s?(%|percent|GW|MW|gigawatt|megawatt))', re.I)
out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
seen = set()
for f in sys.argv[2:]:
    t = io.open(f, encoding='utf-8', errors='replace').read()
    t = re.sub(r'\s+', ' ', t)
    for s in re.split(r'(?<=[.;])\s+(?=[A-Z(•])', t):
        if pat.search(s) and num.search(s):
            k = s.strip()[:300]
            if k in seen:
                continue
            seen.add(k)
            out.write('- ' + s.strip()[:600] + '\n')
