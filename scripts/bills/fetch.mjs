// Minimal downloader (curl is blocked in this environment).
// Usage: node scripts/bills/fetch.mjs <url> <outfile>
// Follows redirects, writes the raw bytes untouched, prints status + size.
import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';

const [, , url, out] = process.argv;
if (!url || !out) {
  console.error('usage: node fetch.mjs <url> <outfile>');
  process.exit(2);
}
fs.mkdirSync(path.dirname(out), { recursive: true });

function get(u, depth = 0) {
  if (depth > 8) { console.error('too many redirects'); process.exit(1); }
  const mod = u.startsWith('https') ? https : http;
  const req = mod.get(u, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (research-downloader)',
      'Accept': '*/*',
    },
    timeout: 120000,
  }, (res) => {
    if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
      const next = new URL(res.headers.location, u).toString();
      res.resume();
      return get(next, depth + 1);
    }
    if (res.statusCode !== 200) {
      console.error(`HTTP ${res.statusCode} for ${u}`);
      res.resume();
      process.exit(1);
    }
    const ws = fs.createWriteStream(out);
    res.pipe(ws);
    ws.on('finish', () => {
      const sz = fs.statSync(out).size;
      console.log(`OK ${u} -> ${out} (${sz} bytes, ${res.headers['content-type'] || ''})`);
    });
  });
  req.on('timeout', () => { req.destroy(new Error('timeout')); });
  req.on('error', (e) => { console.error('ERR', u, e.message); process.exit(1); });
}
get(url);
