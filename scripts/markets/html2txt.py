"""Crude HTML -> text for reading downloaded pages (run with python3 -I).
Usage: python3 -I scripts/markets/html2txt.py <in.html> <out.txt>
"""
import io
import re
import sys
import html

src, dst = sys.argv[1], sys.argv[2]
t = io.open(src, encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', t)
t = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>', '\n', t)
t = re.sub(r'(?i)<a [^>]*href="([^"]+)"[^>]*>', r' [\1] ', t)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'[ \t\r\f\v]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
io.open(dst, 'w', encoding='utf-8').write(t)
print(len(t))
