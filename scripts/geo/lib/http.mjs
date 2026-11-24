// Minimal HTTP helper for Node 16 (no global fetch). No dependencies.
// get(url, {headers, timeoutMs}) -> {status, headers, body: Buffer}; follows redirects.
import https from 'https';
import http from 'http';
import fs from 'fs';
import zlib from 'zlib';

const UA = 'ai-power-tax-research/0.1 (node)';

export function get(url, opts = {}, redirects = 0) {
  const { headers = {}, timeoutMs = 120000 } = opts;
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https:') ? https : http;
    const req = mod.get(url, { headers: { 'User-Agent': UA, 'Accept-Encoding': 'gzip, deflate', ...headers } }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode) && res.headers.location && redirects < 8) {
        res.resume();
        const next = new URL(res.headers.location, url).toString();
        return resolve(get(next, opts, redirects + 1));
      }
      const chunks = [];
      let stream = res;
      const enc = res.headers['content-encoding'];
      if (enc === 'gzip') stream = res.pipe(zlib.createGunzip());
      else if (enc === 'deflate') stream = res.pipe(zlib.createInflate());
      stream.on('data', (c) => chunks.push(c));
      stream.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks), url }));
      stream.on('error', reject);
    });
    req.setTimeout(timeoutMs, () => req.destroy(new Error('timeout ' + url)));
    req.on('error', reject);
  });
}

export async function getJSON(url, opts = {}) {
  const r = await get(url, { ...opts, headers: { Accept: 'application/json', ...(opts.headers || {}) } });
  if (r.status !== 200) throw new Error(`HTTP ${r.status} for ${url}: ${r.body.toString().slice(0, 300)}`);
  return JSON.parse(r.body.toString('utf8'));
}

export async function download(url, dest, opts = {}) {
  const r = await get(url, opts);
  if (r.status !== 200) throw new Error(`HTTP ${r.status} for ${url}`);
  fs.writeFileSync(dest, r.body);
  return { bytes: r.body.length, headers: r.headers };
}

export async function retry(fn, tries = 4) {
  let err;
  for (let i = 0; i < tries; i++) {
    try { return await fn(); } catch (e) { err = e; await new Promise((r) => setTimeout(r, 1500 * (i + 1))); }
  }
  throw err;
}
