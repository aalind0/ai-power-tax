"""Fallback downloader (python stdlib, normal TLS verification). Usage: python3 -I scripts/bills/fetch.py <url> <outfile>"""
import os
import sys
import urllib.request

url, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.dirname(out), exist_ok=True)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research-downloader)', 'Accept': '*/*'})
with urllib.request.urlopen(req, timeout=120) as r, open(out, 'wb') as f:
    f.write(r.read())
    print('OK', r.status, url, '->', out, os.path.getsize(out), r.headers.get('Content-Type'))
