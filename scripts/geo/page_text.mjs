// Fetch a web page and print its visible text (tags stripped) plus links matching an optional regex.
// Usage: node page_text.mjs <url> [linkRegex] [maxChars=6000]
import { get } from './lib/http.mjs';

const [url, linkRe, maxArg] = process.argv.slice(2);
const r = await get(url, { timeoutMs: 60000, headers: { Accept: 'text/html,*/*' } }).catch((e) => ({ status: 'ERR', body: Buffer.from(String(e)), headers: {} }));
const html = r.body.toString('utf8');
console.log('STATUS', r.status, r.url || url, 'bytes', html.length);
if (linkRe) {
  const re = new RegExp(linkRe, 'i');
  const links = [...html.matchAll(/<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi)].map((m) => [m[1], m[2].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()]).filter(([h, t]) => re.test(h) || re.test(t));
  for (const [h, t] of [...new Map(links.map((l) => [l[0], l])).values()].slice(0, 60)) console.log('LINK', h, '|', t.slice(0, 120));
}
const text = html.replace(/<script[\s\S]*?<\/script>/gi, ' ').replace(/<style[\s\S]*?<\/style>/gi, ' ').replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&#8217;|&rsquo;/g, "'").replace(/&#\d+;/g, ' ').replace(/\s+/g, ' ');
console.log(text.slice(0, Number(maxArg || 6000)));
