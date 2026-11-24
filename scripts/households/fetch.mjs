// Download one or more URLs into data/raw/households/<folder>/ (each folder new and empty).
// Usage: node scripts/households/fetch.mjs <folder_name> <url> [<url> ...]
// Node 16, no global fetch -> https module with redirect following.
import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..', '..');
const [folder, ...urls] = process.argv.slice(2);
if (!folder || urls.length === 0) {
  console.error('usage: node fetch.mjs <folder> <url>...');
  process.exit(1);
}
const outDir = path.join(root, 'data', 'raw', 'households', folder);
if (fs.existsSync(outDir) && fs.readdirSync(outDir).length) {
  console.error(`refusing: ${outDir} exists and is not empty`);
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });

function get(url, depth = 0) {
  return new Promise((resolve, reject) => {
    if (depth > 6) return reject(new Error('too many redirects'));
    const mod = url.startsWith('https') ? https : http;
    const req = mod.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (research script)', Accept: '*/*' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        res.resume();
        return resolve(get(new URL(res.headers.location, url).toString(), depth + 1));
      }
      if (res.statusCode !== 200) {
        res.resume();
        return reject(new Error(`HTTP ${res.statusCode} for ${url}`));
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve({ buf: Buffer.concat(chunks), type: res.headers['content-type'] || '' }));
    });
    req.setTimeout(60000, () => req.destroy(new Error('timeout')));
    req.on('error', reject);
  });
}

const log = [];
for (const url of urls) {
  try {
    const { buf, type } = await get(url);
    let name = decodeURIComponent(new URL(url).pathname.split('/').filter(Boolean).pop() || 'index');
    name = name.replace(/[^A-Za-z0-9._-]/g, '_');
    if (!path.extname(name)) name += type.includes('pdf') ? '.pdf' : type.includes('json') ? '.json' : '.html';
    let k = 1;
    const base = name;
    while (fs.existsSync(path.join(outDir, name))) name = `${k++}_${base}`;
    fs.writeFileSync(path.join(outDir, name), buf);
    log.push({ url, file: name, bytes: buf.length, content_type: type, fetched_at: new Date().toISOString() });
    console.log(`ok ${buf.length} bytes -> ${folder}/${name}`);
  } catch (e) {
    log.push({ url, error: String(e.message || e), fetched_at: new Date().toISOString() });
    console.error(`FAIL ${url}: ${e.message}`);
  }
}
fs.writeFileSync(path.join(outDir, '_fetch_log.json'), JSON.stringify(log, null, 2));
