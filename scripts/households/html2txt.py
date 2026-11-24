"""Convert a downloaded HTML file to plain text (stdout as utf-8). Usage: python3 -I html2txt.py <file> [start_marker] [max_chars]"""
import html
import re
import sys

path = sys.argv[1]
start = sys.argv[2] if len(sys.argv) > 2 else ''
maxc = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
t = open(path, encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style|noscript|svg|nav|footer|header)[^>]*>.*?</\1>', ' ', t)
t = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>', '\n', t)
t = re.sub(r'(?i)</td>|</th>', ' | ', t)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
t = re.sub(r'[ \t\r\f\v]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
i = t.find(start) if start else 0
sys.stdout.buffer.write(t[max(i, 0):max(i, 0) + maxc].encode('utf-8'))
