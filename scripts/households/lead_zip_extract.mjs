// Extract selected members from the remote DOE LEAD 2022 state zips WITHOUT downloading the whole
// archives (7.3 GB in total): uses HTTP Range requests to read the zip central directory, then
// fetches + inflates only the members whose names match a regex (default: county-level files).
//
// Usage:
//   node scripts/households/lead_zip_extract.mjs list AK            -> prints members of AK zip
//   node scripts/households/lead_zip_extract.mjs get <outFolder> <regex> [STATE ...]
//        (default states = all 52; writes data/raw/households/<outFolder>/<STATE>/<member>)
// Node 16, https module only. Downloaded bytes are data; nothing is executed.
import https from 'https';
import zlib from 'zlib';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..', '..');
const BASE = 'https://data.openei.org/files/6219/';
const STATES = ('AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH ' +
  'NJ NM NV NY OH OK OR PA PR RI SC SD TN TX UT VA VT WA WI WV WY').split(' ');

function req(url, range, depth = 0) {
  return new Promise((resolve, reject) => {
    if (depth > 6) return reject(new Error('too many redirects'));
    const headers = { 'User-Agent': 'Mozilla/5.0 (research script)' };
    if (range) headers.Range = range;
    const r = https.get(url, { headers }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return resolve(req(new URL(res.headers.location, url).toString(), range, depth + 1));
      }
      if (res.statusCode !== 206 && res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url} ${range || ''}`));
      }
      if (range && res.statusCode === 200) {
        res.destroy();
        return reject(new Error('server ignored Range header'));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve({ buf: Buffer.concat(chunks), headers: res.headers }));
    });
    r.setTimeout(120000, () => r.destroy(new Error('timeout')));
    r.on('error', reject);
  });
}

async function centralDirectory(url) {
  const tail = await req(url, 'bytes=-131072');
  const total = Number((tail.headers['content-range'] || '').split('/')[1]);
  const b = tail.buf;
  const tailStart = total - b.length;
  // ZIP64 EOCD locator (PK\x06\x07) or classic EOCD (PK\x05\x06)
  let cdOffset, cdSize, entries;
  const eocd = b.lastIndexOf(Buffer.from([0x50, 0x4b, 0x05, 0x06]));
  if (eocd < 0) throw new Error('EOCD not found');
  cdSize = b.readUInt32LE(eocd + 12);
  cdOffset = b.readUInt32LE(eocd + 16);
  entries = b.readUInt16LE(eocd + 10);
  const loc = b.lastIndexOf(Buffer.from([0x50, 0x4b, 0x06, 0x07]), eocd);
  if (cdOffset === 0xffffffff || cdSize === 0xffffffff || entries === 0xffff || loc >= 0) {
    if (loc >= 0) {
      const z64off = Number(b.readBigUInt64LE(loc + 8));
      const z = z64off >= tailStart ? b.slice(z64off - tailStart) : (await req(url, `bytes=${z64off}-${z64off + 99}`)).buf;
      entries = Number(z.readBigUInt64LE(32));
      cdSize = Number(z.readBigUInt64LE(40));
      cdOffset = Number(z.readBigUInt64LE(48));
    }
  }
  const cd = cdOffset >= tailStart ? b.slice(cdOffset - tailStart, cdOffset - tailStart + cdSize)
    : (await req(url, `bytes=${cdOffset}-${cdOffset + cdSize - 1}`)).buf;
  const out = [];
  let p = 0;
  while (p < cd.length && cd.readUInt32LE(p) === 0x02014b50) {
    const method = cd.readUInt16LE(p + 10);
    let csize = cd.readUInt32LE(p + 20);
    let usize = cd.readUInt32LE(p + 24);
    const nlen = cd.readUInt16LE(p + 28), xlen = cd.readUInt16LE(p + 30), clen = cd.readUInt16LE(p + 32);
    let lho = cd.readUInt32LE(p + 42);
    const name = cd.slice(p + 46, p + 46 + nlen).toString('utf8');
    // zip64 extra field
    let x = p + 46 + nlen;
    const xend = x + xlen;
    while (x + 4 <= xend) {
      const id = cd.readUInt16LE(x), sz = cd.readUInt16LE(x + 2);
      if (id === 0x0001) {
        let q = x + 4;
        if (usize === 0xffffffff) { usize = Number(cd.readBigUInt64LE(q)); q += 8; }
        if (csize === 0xffffffff) { csize = Number(cd.readBigUInt64LE(q)); q += 8; }
        if (lho === 0xffffffff) { lho = Number(cd.readBigUInt64LE(q)); q += 8; }
      }
      x += 4 + sz;
    }
    out.push({ name, method, csize, usize, lho });
    p = xend + clen;
  }
  return { total, entries: out };
}

async function extract(url, e) {
  const hdr = (await req(url, `bytes=${e.lho}-${e.lho + 29}`)).buf;
  const start = e.lho + 30 + hdr.readUInt16LE(26) + hdr.readUInt16LE(28);
  const data = (await req(url, `bytes=${start}-${start + e.csize - 1}`)).buf;
  if (e.method === 0) return data;
  if (e.method === 8) return zlib.inflateRawSync(data);
  throw new Error(`unsupported compression method ${e.method}`);
}

const [cmd, ...args] = process.argv.slice(2);
if (cmd === 'list') {
  const st = args[0] || 'AK';
  const { total, entries } = await centralDirectory(`${BASE}${st}-2022-LEAD-data.zip`);
  console.log(`${st}: ${total} bytes, ${entries.length} members`);
  for (const e of entries) console.log(`${e.usize}\t${e.csize}\t${e.name}`);
} else if (cmd === 'get') {
  const [folder, pattern, ...sts] = args;
  const re = new RegExp(pattern, 'i');
  const outDir = path.join(root, 'data', 'raw', 'households', folder);
  fs.mkdirSync(outDir, { recursive: true });
  const log = [];
  for (const st of (sts.length ? sts : STATES)) {
    const url = `${BASE}${st}-2022-LEAD-data.zip`;
    try {
      const { total, entries } = await centralDirectory(url);
      const pick = entries.filter((e) => re.test(e.name) && !e.name.endsWith('/'));
      fs.mkdirSync(path.join(outDir, st), { recursive: true });
      for (const e of pick) {
        const buf = await extract(url, e);
        const fname = path.basename(e.name).replace(/[^A-Za-z0-9._-]/g, '_');
        fs.writeFileSync(path.join(outDir, st, fname), buf);
        log.push({ state: st, url, zip_bytes: total, member: e.name, bytes: buf.length, fetched_at: new Date().toISOString() });
        console.log(`ok ${st} ${e.name} ${buf.length}`);
      }
      if (!pick.length) console.error(`no match in ${st}`);
    } catch (err) {
      log.push({ state: st, url, error: String(err.message || err) });
      console.error(`FAIL ${st}: ${err.message}`);
    }
  }
  fs.writeFileSync(path.join(outDir, `_fetch_log_${Date.now()}.json`), JSON.stringify(log, null, 2));
} else {
  console.error('usage: list <ST> | get <folder> <regex> [ST...]');
  process.exit(1);
}
