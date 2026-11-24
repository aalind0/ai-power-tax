// Minimal downloader for the grid area (curl is blocked; Node 16 has no global fetch).
// Usage: node scripts/grid/fetch.mjs <url> <outFile> [maxBytes]
// Follows up to 5 redirects, writes raw bytes untouched, never executes anything downloaded.
// Optional maxBytes sends a Range header (for probing large files).
import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';

const [, , url, outFile, maxBytes] = process.argv;
if (!url || !outFile) { console.error('usage: node fetch.mjs <url> <outFile> [maxBytes]'); process.exit(2); }

function get(u, hops = 0) {
  return new Promise((resolve, reject) => {
    const lib = u.startsWith('https') ? https : http;
    const headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      Accept: 'text/html,application/pdf,application/xhtml+xml,application/json,text/csv,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
    };
    if (maxBytes) headers.Range = `bytes=0-${Number(maxBytes) - 1}`;
    const req = lib.get(u, { headers, timeout: 120000 }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && hops < 5) {
        const next = new URL(res.headers.location, u).toString();
        res.resume();
        return resolve(get(next, hops + 1));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks), finalUrl: u }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', reject);
  });
}

const r = await get(url);
fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, r.body);
console.log(JSON.stringify({ status: r.status, bytes: r.body.length, type: r.headers['content-type'], len: r.headers['content-length'], range: r.headers['content-range'], finalUrl: r.finalUrl }));
