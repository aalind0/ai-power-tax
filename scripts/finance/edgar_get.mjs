// Fetch a URL from SEC EDGAR (www.sec.gov / efts.sec.gov / data.sec.gov) with a declared generic User-Agent.
// Usage: node scripts/finance/edgar_get.mjs <url> <outFile>
import https from 'https';
import fs from 'fs';
import path from 'path';
const [, , url, outFile] = process.argv;
function get(u, hops = 0) {
  return new Promise((resolve, reject) => {
    https.get(u, { headers: { 'User-Agent': 'ai-power-tax-research research-bot@example.org', Accept: '*/*' }, timeout: 60000 }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && hops < 5) {
        res.resume(); return resolve(get(new URL(res.headers.location, u).toString(), hops + 1));
      }
      const c = []; res.on('data', (x) => c.push(x)); res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(c), type: res.headers['content-type'] }));
    }).on('error', reject);
  });
}
const r = await get(url);
fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, r.body);
console.log(JSON.stringify({ status: r.status, bytes: r.body.length, type: r.type }));
