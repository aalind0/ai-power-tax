// Check that PUC / consumer-advocate / source URLs in data/processed/policy_states.json resolve.
// Usage: node scripts/policy/check_urls.mjs  -> writes data/raw/policy/url_check/url_check.json
import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const states = JSON.parse(fs.readFileSync(path.join(root, 'data/processed/policy_states.json'), 'utf8')).states;
const urls = new Map();
for (const s of states) {
  if (s.puc?.url) urls.set(s.puc.url, `${s.state} puc`);
  if (s.consumer_advocate?.url) urls.set(s.consumer_advocate.url, `${s.state} advocate`);
}

function head(url, depth = 0) {
  return new Promise((resolve) => {
    if (depth > 5) return resolve({ status: 'too many redirects' });
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Macintosh) research-link-check', Accept: 'text/html' } }, (res) => {
      res.resume();
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(head(new URL(res.headers.location, url).toString(), depth + 1).then((r) => ({ ...r, redirected_to: r.redirected_to || new URL(res.headers.location, url).toString() })));
      }
      resolve({ status: res.statusCode });
    });
    req.setTimeout(20000, () => req.destroy(new Error('timeout')));
    req.on('error', (e) => resolve({ status: 'error', error: e.code || e.message }));
  });
}

const out = [];
const list = [...urls.entries()];
const N = 8;
for (let i = 0; i < list.length; i += N) {
  const batch = await Promise.all(list.slice(i, i + N).map(async ([u, label]) => ({ label, url: u, ...(await head(u)) })));
  out.push(...batch);
}
const dir = path.join(root, 'data/raw/policy/url_check');
fs.mkdirSync(dir, { recursive: true });
fs.writeFileSync(path.join(dir, 'url_check.json'), JSON.stringify({ checked_at: new Date().toISOString(), results: out }, null, 1));
const bad = out.filter((r) => !(typeof r.status === 'number' && r.status < 400));
console.log(`${out.length} urls, ${bad.length} not OK`);
for (const b of bad) console.log(b.label, b.url, b.status, b.error || '', b.redirected_to || '');
