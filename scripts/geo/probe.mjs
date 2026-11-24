// Probe a URL and print status + first bytes. Usage: node probe.mjs <url> [maxChars]
import { get } from './lib/http.mjs';
const url = process.argv[2];
const max = Number(process.argv[3] || 1500);
const r = await get(url, { timeoutMs: 60000 }).catch((e) => ({ status: 'ERR', headers: {}, body: Buffer.from(String(e)) }));
console.log('STATUS', r.status, 'URL', r.url || url);
console.log('content-type', r.headers['content-type'], 'len', r.body.length, 'acao', r.headers['access-control-allow-origin']);
console.log(r.body.toString('utf8').slice(0, max));
