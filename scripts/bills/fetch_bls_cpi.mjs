// Fetch CPI series from the BLS Public Data API v2 (no key needed; max 10 years per request).
// Usage: node scripts/bills/fetch_bls_cpi.mjs <outdir>
// Series: CUUR0000SA0 (CPI-U all items, US city avg, NSA, 1982-84=100)
//         CUUR0000SEHF01 (CPI-U electricity, NSA)
//         CUSR0000SEHF01 (CPI-U electricity, SA)
import https from 'https';
import fs from 'fs';
import path from 'path';

const outdir = process.argv[2];
fs.mkdirSync(outdir, { recursive: true });
const series = ['CUUR0000SA0', 'CUUR0000SEHF01', 'CUSR0000SEHF01'];
const windows = [[2005, 2014], [2015, 2024], [2025, 2026]];

function post(body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = https.request('https://api.bls.gov/publicAPI/v2/timeseries/data/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data), 'User-Agent': 'research-script' },
      timeout: 60000,
    }, (res) => {
      let buf = '';
      res.on('data', (c) => (buf += c));
      res.on('end', () => resolve({ status: res.statusCode, body: buf }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

for (const [s, e] of windows) {
  const r = await post({ seriesid: series, startyear: String(s), endyear: String(e) });
  const f = path.join(outdir, `bls_cpi_${s}_${e}.json`);
  fs.writeFileSync(f, r.body);
  let msg = '';
  try { const j = JSON.parse(r.body); msg = j.status + ' ' + (j.message || []).join(' | '); } catch (err) { msg = 'not json'; }
  console.log(r.status, f, r.body.length, msg);
}
