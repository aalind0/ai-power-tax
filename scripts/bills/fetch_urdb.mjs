// Fetch recent residential tariffs from the OpenEI Utility Rate Database (URDB) API for the bill-anatomy utilities.
// Usage: node scripts/bills/fetch_urdb.mjs <outdir> [eiaId ...]
// Uses the public NREL/OpenEI DEMO_KEY (rate-limited); one request per utility, newest 25 residential rates, full detail.
import https from 'https';
import fs from 'fs';
import path from 'path';

const outdir = process.argv[2];
fs.mkdirSync(outdir, { recursive: true });
const DEFAULT = {
  14940: 'PECO', 1167: 'BGE', 15270: 'Pepco', 19876: 'Dominion VA', 15477: 'PSE&G', 9726: 'JCP&L',
  4110: 'ComEd', 14006: 'AEP Ohio (Ohio Power)', 7140: 'Georgia Power', 44372: 'Oncor', 8901: 'CenterPoint',
  5416: 'Duke Energy Carolinas', 14328: 'PG&E', 17609: 'SCE', 11241: 'Entergy Louisiana', 814: 'Entergy Arkansas',
};
const ids = process.argv.length > 3 ? process.argv.slice(3).map(Number) : Object.keys(DEFAULT).map(Number);

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'research-script' }, timeout: 90000 }, (res) => {
      let b = '';
      res.on('data', (c) => (b += c));
      res.on('end', () => resolve({ status: res.statusCode, body: b }));
    }).on('error', reject);
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const id of ids) {
  const url = `https://api.openei.org/utility_rates?version=latest&format=json&eia=${id}&sector=Residential&detail=full&approved=true&orderby=startdate&direction=desc&limit=25&api_key=DEMO_KEY`;
  const r = await get(url);
  const f = path.join(outdir, `urdb_${id}.json`);
  fs.writeFileSync(f, r.body);
  let n = '?';
  try { n = JSON.parse(r.body).items.length; } catch (e) { n = 'parse-error'; }
  console.log(r.status, id, DEFAULT[id] || '', f, r.body.length, 'items', n);
  await sleep(2500);
}
