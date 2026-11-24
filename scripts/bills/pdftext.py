"""Minimal stdlib-only PDF text extractor (no poppler/pdfminer available in this environment).
Usage: python3 -I scripts/bills/pdftext.py <in.pdf> <out.txt>
Handles FlateDecode content streams, Tj/TJ/'/" text operators, literal and hex strings, and
ToUnicode CMaps (bfchar/bfrange) for CID fonts. Layout is approximate (new line on Td/TD/T*/Tm/ET).
Treats the PDF purely as data; nothing in it is executed.
"""
import re
import sys
import zlib

data = open(sys.argv[1], 'rb').read()

objs = {}
for m in re.finditer(rb'(\d+)\s+(\d+)\s+obj\b(.*?)endobj', data, re.S):
    objs[int(m.group(1))] = m.group(3)


def stream_of(body):
    m = re.search(rb'stream\r?\n(.*?)\r?\n?endstream', body, re.S)
    if not m:
        return None
    raw = m.group(1)
    if b'FlateDecode' in body[:m.start()]:
        for wbits in (15, -15):
            try:
                return zlib.decompress(raw, wbits)
            except Exception:
                pass
        try:
            return zlib.decompressobj().decompress(raw)
        except Exception:
            return None
    return raw


# object streams (PDF 1.5+): objects packed inside /Type /ObjStm
for num, body in list(objs.items()):
    if b'/ObjStm' in body:
        s = stream_of(body)
        if not s:
            continue
        n = int(re.search(rb'/N\s+(\d+)', body).group(1))
        first = int(re.search(rb'/First\s+(\d+)', body).group(1))
        hdr = s[:first].split()
        for i in range(n):
            onum, off = int(hdr[2 * i]), int(hdr[2 * i + 1])
            end = int(hdr[2 * i + 3]) if i + 1 < n else len(s) - first
            objs.setdefault(onum, s[first + off:first + end])


def parse_cmap(s):
    cmap = {}
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', s, re.S):
        for a, b in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            try:
                cmap[int(a, 16)] = bytes.fromhex(b.decode()).decode('utf-16-be', 'ignore')
            except Exception:
                pass
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', s, re.S):
        for a, b, c in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(<[0-9A-Fa-f]+>|\[[^\]]*\])', blk):
            lo, hi = int(a, 16), int(b, 16)
            if c.startswith(b'<'):
                base = int(c[1:-1], 16)
                for k in range(lo, hi + 1):
                    try:
                        cmap[k] = chr(base + k - lo)
                    except Exception:
                        pass
            else:
                vals = re.findall(rb'<([0-9A-Fa-f]+)>', c)
                for k, v in zip(range(lo, hi + 1), vals):
                    cmap[k] = bytes.fromhex(v.decode()).decode('utf-16-be', 'ignore')
    return cmap


# font resource name -> (cmap, bytes per code)
font_cmaps = {}
for num, body in objs.items():
    if b'/Type' in body and b'/Font' in body and b'/ToUnicode' in body:
        m = re.search(rb'/ToUnicode\s+(\d+)\s+\d+\s+R', body)
        if m and int(m.group(1)) in objs:
            s = stream_of(objs[int(m.group(1))])
            if s:
                two = b'/Type0' in body or b'Identity-H' in body
                font_cmaps[num] = (parse_cmap(s), 2 if two else 1)

# page resources: map /F1 -> font obj number (collect globally; names may clash across pages, best effort)
fontname_to_obj = {}
for num, body in objs.items():
    for fm in re.finditer(rb'/Font\s*<<(.*?)>>', body, re.S):
        for nm, ref in re.findall(rb'/([A-Za-z0-9_.+-]+)\s+(\d+)\s+\d+\s+R', fm.group(1)):
            fontname_to_obj.setdefault(nm, int(ref))
    m = re.search(rb'/Font\s+(\d+)\s+\d+\s+R', body)
    if m and int(m.group(1)) in objs:
        for nm, ref in re.findall(rb'/([A-Za-z0-9_.+-]+)\s+(\d+)\s+\d+\s+R', objs[int(m.group(1))]):
            fontname_to_obj.setdefault(nm, int(ref))


def unescape_literal(s):
    out = bytearray()
    i = 0
    while i < len(s):
        c = s[i]
        if c == 0x5C and i + 1 < len(s):
            n = s[i + 1]
            mp = {ord('n'): 10, ord('r'): 13, ord('t'): 9, ord('b'): 8, ord('f'): 12}
            if n in mp:
                out.append(mp[n]); i += 2
            elif 0x30 <= n <= 0x37:
                j = i + 1
                oct_ = b''
                while j < len(s) and len(oct_) < 3 and 0x30 <= s[j] <= 0x37:
                    oct_ += bytes([s[j]]); j += 1
                out.append(int(oct_, 8) & 255); i = j
            elif n in (10, 13):
                i += 2
            else:
                out.append(n); i += 2
        else:
            out.append(c); i += 1
    return bytes(out)


def decode(bs, font):
    cm = font_cmaps.get(font)
    if cm:
        cmap, w = cm
        if w == 2 and len(bs) % 2 == 0:
            return ''.join(cmap.get(int.from_bytes(bs[i:i + 2], 'big'), '') for i in range(0, len(bs), 2))
        return ''.join(cmap.get(b, chr(b)) for b in bs)
    return bs.decode('latin-1')


tok = re.compile(rb'\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>|\[|\]|/[^\s/\[\]()<>]+|[-+]?\d*\.?\d+|[A-Za-z\'"*]+', re.S)
lines = []
for num in sorted(objs):
    body = objs[num]
    if b'stream' not in body or b'/Font' in body[:200] and b'/ToUnicode' in body[:200]:
        continue
    s = stream_of(body)
    if not s or (b'Tj' not in s and b'TJ' not in s):
        continue
    cur_font = None
    buf = []
    stack = []
    cur = ''
    for t in tok.findall(s):
        if t.startswith(b'('):
            stack.append(('s', unescape_literal(t[1:-1])))
        elif t.startswith(b'<'):
            hx = re.sub(rb'\s', b'', t[1:-1])
            if len(hx) % 2:
                hx += b'0'
            stack.append(('s', bytes.fromhex(hx.decode())))
        elif t == b'[':
            stack.append(('[', None))
        elif t == b']':
            arr = []
            while stack and stack[-1][0] != '[':
                arr.append(stack.pop())
            if stack:
                stack.pop()
            arr.reverse()
            stack.append(('a', arr))
        elif t.startswith(b'/'):
            stack.append(('n', t[1:]))
        elif re.match(rb'^[-+]?\d*\.?\d+$', t):
            stack.append(('num', float(t)))
        else:
            op = t
            if op == b'Tf':
                names = [v for k, v in stack if k == 'n']
                if names:
                    cur_font = fontname_to_obj.get(names[-1])
            elif op in (b'Tj', b"'", b'"'):
                strs = [v for k, v in stack if k == 's']
                if strs:
                    if op != b'Tj':
                        buf.append(cur); cur = ''
                    cur += decode(strs[-1], cur_font)
            elif op == b'TJ':
                arrs = [v for k, v in stack if k == 'a']
                if arrs:
                    for k, v in arrs[-1]:
                        if k == 's':
                            cur += decode(v, cur_font)
                        elif k == 'num' and v < -200:
                            cur += ' '
            elif op in (b'Td', b'TD', b'T*', b'Tm', b'ET'):
                if op in (b'Td', b'TD'):
                    nums = [v for k, v in stack if k == 'num']
                    if len(nums) >= 2 and abs(nums[-1]) < 0.01 and cur:
                        cur += ' '  # same line, horizontal move
                        stack = []
                        continue
                if cur.strip():
                    buf.append(cur)
                cur = ''
            stack = []
    if cur.strip():
        buf.append(cur)
    if buf:
        lines.append('\n'.join(x.strip() for x in buf if x.strip()))
        lines.append('\n----- [stream %d] -----\n' % num)

open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(lines))
print('objects', len(objs), 'cmaps', len(font_cmaps), 'chars', sum(len(x) for x in lines))
