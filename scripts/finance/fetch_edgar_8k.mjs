// Find and download 8-K exhibits (earnings releases, EEI Financial Conference / investor presentations) for the
// largest US utility holding companies and IPPs, using SEC EDGAR full-text search.
// Usage: node scripts/finance/fetch_edgar_8k.mjs <startdt YYYY-MM-DD> <enddt YYYY-MM-DD> <outSubdir> [query]
// e.g.   node scripts/finance/fetch_edgar_8k.mjs 2026-10-01 2026-11-22 edgar_8k_2026q3 '"capital"'
// Saves an index.json of hits plus each EX-99 exhibit (htm) untouched under data/raw/finance/<outSubdir>/<TICKER>/.
import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const [, , startdt, enddt, sub, q = '"capital"'] = process.argv;
const OUT = path.join(ROOT, 'data/raw/finance', sub);
const CIK = {
  D: '0000715957', SO: '0000092122', AEP: '0000004904', DUK: '0001326160', NEE: '0000753308', EXC: '0001109357',
  PEG: '0000788784', ETR: '0000065984', XEL: '0000072903', SRE: '0001032208', CNP: '0001130310', PPL: '0000922224',
  FE: '0001031296', NI: '0001111711', EVRG: '0001711269', WEC: '0000783325', AEE: '0001002910', PNW: '0000764622',
  NRG: '0001013871', VST: '0001692819', CEG: '0001868275', TLN: '0001622536',
};
const only = process.env.ONLY ? process.env.ONLY.split(',') : Object.keys(CIK);
const UA = 'ai-power-tax-research research-bot@example.org';
function get(u) {
  return new Promise((resolve, reject) => {
    https.get(u, { headers: { 'User-Agent': UA, Accept: '*/*' }, timeout: 60000 }, (res) => {
      const c = []; res.on('data', (x) => c.push(x)); res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(c) }));
    }).on('error', reject);
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const index = {};
for (const t of only) {
  const cik = CIK[t];
  const url = `https://efts.sec.gov/LATEST/search-index?q=${encodeURIComponent(q)}&forms=8-K&dateRange=custom&startdt=${startdt}&enddt=${enddt}&ciks=${cik}`;
  const r = await get(url);
  await sleep(250);
  let hits = [];
  try { hits = JSON.parse(r.body.toString()).hits.hits; } catch (e) { console.log(t, 'bad json', r.status); continue; }
  index[t] = [];
  for (const h of hits) {
    const [adsh, file] = h._id.split(':');
    const s = h._source;
    if (!/^EX-99/.test(s.file_type || '')) continue;
    const docUrl = `https://www.sec.gov/Archives/edgar/data/${parseInt(cik, 10)}/${adsh.replace(/-/g, '')}/${file}`;
    const dest = path.join(OUT, t, `${s.file_date}_${file}`);
    index[t].push({ file_date: s.file_date, adsh, file, type: s.file_type, desc: s.file_description, url: docUrl });
    if (!fs.existsSync(dest)) {
      const d = await get(docUrl);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, d.body);
      await sleep(250);
    }
  }
  console.log(t, index[t].map((x) => `${x.file_date} ${x.file} ${x.desc || ''}`).join(' | '));
}
fs.mkdirSync(OUT, { recursive: true });
fs.writeFileSync(path.join(OUT, `index_${Date.now()}.json`), JSON.stringify(index, null, 1));
