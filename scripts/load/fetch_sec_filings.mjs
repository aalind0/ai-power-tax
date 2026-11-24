// Download the latest 10-K and 10-Q (primary documents) for hotspot utility holding companies from SEC EDGAR.
// Usage (from project root): FETCH_UA="<generic research UA>" node scripts/load/fetch_sec_filings.mjs
// SEC asks automated clients for a descriptive User-Agent; use a generic one (no personal details).
// Output: data/raw/load/sec_<ticker>_<form>_<period>/<primaryDocument>  (one new folder per download)
import https from 'https';
import fs from 'fs';
import path from 'path';

const UA = process.env.FETCH_UA || 'ai-power-tax-research/0.1 research-contact@example.org';
const COS = {
  D: '0000715957', // Dominion Energy
  AEP: '0000004904', // American Electric Power
  SO: '0000092122', // Southern Company (Georgia Power)
  ETR: '0000065984', // Entergy
  DUK: '0001326160', // Duke Energy
  EXC: '0001109357', // Exelon (ComEd)
  PCG: '0001004980', // PG&E Corp
  PNW: '0000764622', // Pinnacle West (APS)
  ONCOR: '0001193311', // Oncor Electric Delivery
  BHE: '0001081316', // Berkshire Hathaway Energy (NV Energy, MidAmerican)
};
const only = process.argv.slice(2);

function get(u) {
  return new Promise((resolve, reject) => {
    https
      .get(u, { headers: { 'User-Agent': UA, Accept: '*/*' }, timeout: 120000 }, (res) => {
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(chunks) }));
      })
      .on('error', reject);
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const [tic, cik] of Object.entries(COS)) {
  if (only.length && !only.includes(tic)) continue;
  const sub = await get(`https://data.sec.gov/submissions/CIK${cik}.json`);
  if (sub.status !== 200) {
    console.log(tic, 'submissions status', sub.status);
    continue;
  }
  const r = JSON.parse(sub.body.toString()).filings.recent;
  for (const form of ['10-K', '10-Q']) {
    const i = r.form.findIndex((f) => f === form);
    if (i < 0) continue;
    const acc = r.accessionNumber[i].replace(/-/g, '');
    const doc = r.primaryDocument[i];
    const period = r.reportDate[i];
    const dir = path.join('data/raw/load', `sec_${tic.toLowerCase()}_${form.replace('-', '').toLowerCase()}_${period}`);
    const out = path.join(dir, doc);
    if (fs.existsSync(out)) {
      console.log(tic, form, period, 'exists');
      continue;
    }
    await sleep(300);
    const url = `https://www.sec.gov/Archives/edgar/data/${parseInt(cik, 10)}/${acc}/${doc}`;
    const res = await get(url);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(out, res.body);
    console.log(JSON.stringify({ tic, form, period, filed: r.filingDate[i], status: res.status, bytes: res.body.length, url }));
  }
}
