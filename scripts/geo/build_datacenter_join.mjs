// Spatial join: US data-center campuses (compute-atlas, read-only) -> utility territories + ISO/RTO.
// Run: node scripts/geo/build_datacenter_join.mjs
// Input : ../compute-atlas/data/atlas.json (campuses[] with lat/lng, status, powerMW)
//         data/processed/geo_territories.geojson, data/processed/geo_iso_regions.geojson
// Output: data/processed/geo_datacenter_campuses.csv  one row per US campus:
//   campus_id, name, status, power_mw, power_mw_now, lat, lng, coord_precision, state, iso,
//   utility_ids (all territories containing the point, ';'), utility_names, likely_utility_id/name (largest residential
//   customer base among overlapping territories - a heuristic; campuses usually take service from the incumbent IOU/co-op,
//   verify against the atlas `energy` notes), atlas_energy_note (first 200 chars), utility_match_basis
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { buildIndex } from './lib/pip.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const ATLAS = new URL('../../../compute-atlas/data/atlas.json', import.meta.url).pathname; // sibling compute-atlas checkout
const terrFc = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/processed/geo_territories.geojson'), 'utf8'));
const terr = buildIndex(terrFc);
const iso = buildIndex(JSON.parse(fs.readFileSync(path.join(ROOT, 'data/processed/geo_iso_regions.geojson'), 'utf8')));
const atlas = JSON.parse(fs.readFileSync(ATLAS, 'utf8'));

const esc = (v) => (v == null ? '' : /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v));
const rows = [];
const header = ['campus_id', 'name', 'status', 'power_mw', 'power_mw_now', 'lat', 'lng', 'coord_precision', 'state', 'iso', 'utility_ids', 'utility_names', 'likely_utility_id', 'likely_utility_name', 'utility_match_basis', 'atlas_energy_note'];
let matched = 0;
for (const c of atlas.campuses.filter((x) => x.countryCode === 'US' && Number.isFinite(x.lat) && Number.isFinite(x.lng))) {
  const hits = terr.lookup(c.lng, c.lat);
  const isos = iso.lookup(c.lng, c.lat).map((p) => p.iso);
  const energyText = JSON.stringify(c.energy || '').toUpperCase();
  // prefer a territory whose name the atlas energy note mentions (first word >= 5 chars), else biggest customer base
  const named = hits.find((h) => h.name.split(/[^A-Z]+/).filter((w) => w.length >= 5).slice(0, 2).every((w) => energyText.includes(w)));
  const biggest = [...hits].sort((a, b) => (b.customers || 0) - (a.customers || 0))[0];
  const pick = named || biggest;
  if (hits.length) matched++;
  rows.push([c.id, c.name, c.status, c.powerMW, c.powerMWNow, c.lat, c.lng, c.coordPrecision, c.region, isos.join(';') || 'non-RTO',
    hits.map((h) => h.eia_utility_id).join(';'), hits.map((h) => h.name).join(';'), pick ? pick.eia_utility_id : '', pick ? pick.name : '',
    !hits.length ? 'no territory hit' : named ? 'territory named in atlas energy note' : hits.length === 1 ? 'single territory' : 'largest of overlapping territories (heuristic)',
    typeof c.energy === 'string' ? c.energy.slice(0, 200) : JSON.stringify(c.energy || '').slice(0, 200)]);
}
fs.writeFileSync(path.join(ROOT, 'data/processed/geo_datacenter_campuses.csv'), [header, ...rows].map((r) => r.map(esc).join(',')).join('\n') + '\n');
console.log(`US campuses ${rows.length}, with territory hit ${matched}`);
const byIso = {};
for (const r of rows) { const k = r[9]; byIso[k] ||= { n: 0, mw: 0 }; byIso[k].n++; byIso[k].mw += Number(r[3]) || 0; }
console.log('by ISO (n, sum powerMW where disclosed):', JSON.stringify(byIso));
console.log('basis:', JSON.stringify(rows.reduce((a, r) => ((a[r[14]] = (a[r[14]] || 0) + 1), a), {})));
