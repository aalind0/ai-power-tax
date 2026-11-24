// Anonymous GitHub repository search for the dataset/repo survey (10 search req/min unauthenticated).
// Run: node scripts/geo/github_survey.mjs  -> research/geo/github_survey.json (raw API hits, trimmed)
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { get } from './lib/http.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const QUERIES = [
  '"data center" electricity demand',
  'datacenter power demand forecast',
  'data center load growth utility',
  'utility rate case',
  'electricity bills utility rates',
  'eia-861',
  'interconnection queue',
  'gridstatus',
  'pudl catalyst',
  'large load tariff',
  'electric utility service territory',
  'electricity price data center',
];
const out = {};
for (const q of QUERIES) {
  const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(q)}&sort=stars&order=desc&per_page=15`;
  const r = await get(url, { headers: { Accept: 'application/vnd.github+json' } });
  const rem = r.headers['x-ratelimit-remaining'];
  if (r.status !== 200) { console.log(q, 'HTTP', r.status, r.body.toString().slice(0, 200)); out[q] = { error: r.status }; }
  else {
    const j = JSON.parse(r.body.toString());
    out[q] = { total: j.total_count, items: j.items.map((i) => ({ full_name: i.full_name, url: i.html_url, stars: i.stargazers_count, pushed_at: i.pushed_at, license: i.license && i.license.spdx_id, archived: i.archived, description: (i.description || '').slice(0, 200) })) };
    console.log(`\n### ${q} (total ${j.total_count}, ratelimit remaining ${rem})`);
    for (const i of out[q].items) console.log(`  ${i.stars}\t${i.full_name}\t${i.pushed_at.slice(0, 10)}\t${i.license}\t${i.description.slice(0, 110)}`);
  }
  await new Promise((res) => setTimeout(res, 6500));
}
fs.writeFileSync(path.join(ROOT, 'research/geo/github_survey.json'), JSON.stringify({ run_at: new Date().toISOString(), queries: out }, null, 1));
