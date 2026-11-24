"""Crude PDF text extractor (no third-party libs). Run: python3 -I scripts/policy/pdf_text.py <file.pdf> [out.txt]
Decompresses FlateDecode streams, maps glyphs through ToUnicode CMaps when present,
and pulls text from Tj/TJ operators. Good enough to read numbers out of reports."""
import re
import sys
import zlib

src = sys.argv[1]
data = open(src, 'rb').read()

# collect objects
objs = {}
for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj(.*?)endobj', data, re.S):
    objs[int(m.group(1))] = m.group(3)


def stream_of(body):
    m = re.search(rb'stream\r?\n(.*?)\r?\nendstream', body, re.S)
    if not m:
        m = re.search(rb'stream\r?\n(.*)endstream', body, re.S)
        if not m:
            return None
    raw = m.group(1)
    if b'FlateDecode' in body[:m.start()]:
        try:
            return zlib.decompress(raw)
        except Exception:
            try:
                return zlib.decompressobj().decompress(raw)
            except Exception:
                return None
    return raw


# expand object streams (/Type /ObjStm) so font dicts stored inside them are visible
for num, body in list(objs.items()):
    if b'/ObjStm' not in body[:400]:
        continue
    s = stream_of(body)
    if not s:
        continue
    mN = re.search(rb'/N\s+(\d+)', body[:400])
    mF = re.search(rb'/First\s+(\d+)', body[:400])
    if not (mN and mF):
        continue
    n, first = int(mN.group(1)), int(mF.group(1))
    nums = list(map(int, s[:first].split()))
    pairs = [(nums[i], nums[i + 1]) for i in range(0, min(len(nums), 2 * n), 2)]
    for i, (onum, off) in enumerate(pairs):
        end = pairs[i + 1][1] if i + 1 < len(pairs) else len(s) - first
        objs.setdefault(onum, s[first + off:first + end])


# parse ToUnicode cmaps
cmaps = {}
for num, body in objs.items():
    if b'/Image' in body[:600] or b'/FontFile' in body[:600] or b'/Length1' in body[:600]:
        continue
    if len(body) > 200_000:
        continue
    s = stream_of(body)
    if s and b'beginbfchar' in s or (s and b'beginbfrange' in s):
        cmap = {}
        for blk in re.findall(rb'beginbfchar(.*?)endbfchar', s, re.S):
            for a, b in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
                try:
                    cmap[int(a, 16)] = bytes.fromhex(b.decode()).decode('utf-16-be', 'ignore')
                except Exception:
                    pass
        for blk in re.findall(rb'beginbfrange(.*?)endbfrange', s, re.S):
            for a, b, c in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
                lo, hi, start = int(a, 16), int(b, 16), int(c, 16)
                for i in range(lo, min(hi, lo + 5000) + 1):
                    try:
                        cmap[i] = chr(start + i - lo)
                    except Exception:
                        pass
        cmaps[num] = cmap

# font name -> cmap via font dicts
font_cmap = {}
for num, body in objs.items():
    m = re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', body)
    if m and int(m.group(1)) in cmaps:
        font_cmap[num] = cmaps[int(m.group(1))]

# resource name -> font obj (global, approximate)
res_font = {}
for num, body in objs.items():
    for fm in re.finditer(rb'/Font\s*<<(.*?)>>', body, re.S):
        for name, ref in re.findall(rb'/([A-Za-z0-9_+.-]+)\s+(\d+)\s+0\s+R', fm.group(1)):
            res_font.setdefault(name, int(ref))


def decode_str(raw, cmap, hexmode):
    if hexmode:
        raw = bytes.fromhex(re.sub(rb'\s', b'', raw).decode() + ('0' if len(re.sub(rb'\s', b'', raw)) % 2 else ''))
    else:
        raw = re.sub(rb'\\([nrtbf()\\])', lambda m: {b'n': b'\n', b'r': b'', b't': b'\t', b'b': b'', b'f': b'', b'(': b'(', b')': b')', b'\\': b'\\'}[m.group(1)], raw)
        raw = re.sub(rb'\\([0-7]{1,3})', lambda m: bytes([int(m.group(1), 8) & 255]), raw)
    if cmap:
        # try 2-byte codes first
        if len(raw) % 2 == 0 and any(k > 255 for k in cmap):
            return ''.join(cmap.get((raw[i] << 8) | raw[i + 1], '') for i in range(0, len(raw), 2))
        return ''.join(cmap.get(b, chr(b)) for b in raw)
    return raw.decode('latin-1')


out = []
for num, body in sorted(objs.items()):
    head = body[:600]
    if b'/Image' in head or b'/XObject' in head and b'/Form' not in head or b'/FontFile' in head or b'/Length1' in head:
        continue
    s = stream_of(body)
    if not s or (b'Tj' not in s and b'TJ' not in s) or b'BT' not in s:
        continue
    if len(s) > 3_000_000:
        continue
    cur = None
    line = []
    for tok in re.finditer(rb'/([A-Za-z0-9_+.-]+)\s+[\d.]+\s+Tf|\[(.*?)\]\s*TJ|\((.*?)(?<!\\)\)\s*Tj|<([0-9A-Fa-f\s]+)>\s*Tj|(T\*|Td|TD|ET)', s, re.S):
        if tok.group(1):
            ref = res_font.get(tok.group(1))
            cur = font_cmap.get(ref)
        elif tok.group(2) is not None:
            parts = re.findall(rb'\((.*?)(?<!\\)\)|<([0-9A-Fa-f\s]*)>|(-?[\d.]+)', tok.group(2), re.S)
            for a, b, n in parts:
                if a:
                    line.append(decode_str(a, cur, False))
                elif b:
                    line.append(decode_str(b, cur, True))
                elif n and float(n) < -200:
                    line.append(' ')
        elif tok.group(3) is not None:
            line.append(decode_str(tok.group(3), cur, False))
        elif tok.group(4) is not None:
            line.append(decode_str(tok.group(4), cur, True))
        elif tok.group(5):
            if line:
                out.append(''.join(line))
                line = []
    if line:
        out.append(''.join(line))

text = '\n'.join(l for l in out if l.strip())
if len(sys.argv) > 2:
    open(sys.argv[2], 'w', encoding='utf-8').write(text)
else:
    sys.stdout.buffer.write(text.encode('utf-8'))
