// Fetch metadata for specific GitHub repos (anonymous core API, 60 req/h).
// Run: node scripts/geo/github_repos.mjs owner/repo ... -> appends to research/geo/github_repos.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { get } from './lib/http.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = path.join(ROOT, 'research/geo/github_repos.json');
const prev = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : {};
for (const full of process.argv.slice(2)) {
  const r = await get(`https://api.github.com/repos/${full}`, { headers: { Accept: 'application/vnd.github+json' } });
  if (r.status !== 200) { console.log(full, 'HTTP', r.status); prev[full] = { error: r.status, checked_at: new Date().toISOString() }; continue; }
  const i = JSON.parse(r.body.toString());
  prev[full] = { url: i.html_url, stars: i.stargazers_count, forks: i.forks_count, pushed_at: i.pushed_at, created_at: i.created_at, license: i.license && i.license.spdx_id, archived: i.archived, homepage: i.homepage, description: i.description, topics: i.topics, checked_at: new Date().toISOString() };
  console.log(`${i.stargazers_count}\t${full}\tcreated ${i.created_at.slice(0, 10)}\tpushed ${i.pushed_at.slice(0, 10)}\t${i.license && i.license.spdx_id}\t${i.homepage || ''}\t${(i.description || '').slice(0, 160)}  [remaining ${r.headers['x-ratelimit-remaining']}]`);
}
fs.writeFileSync(OUT, JSON.stringify(prev, null, 1));
