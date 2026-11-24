// Build data/processed/geo_territories.geojson from the raw HIFLD Electric Retail Service Territories download.
// Run from anywhere:  node scripts/geo/build_territories.mjs [simplifyPct=3] [precision=0.0001]
//   input : data/raw/geo/hifld_retail_territories/electric_retail_service_territories.geojson (fetch_arcgis_layer.mjs)
//           data/processed/geo_eia861_utilities.csv (build_eia861_lookup.py) - fills missing ownership type
//   output: data/processed/geo_territories.geojson  properties: eia_utility_id, name, state, type, customers
// Simplification: mapshaper Visvalingam (weighted) keeping `simplifyPct` % of removable vertices, keep-shapes,
// coordinates rounded to `precision` degrees. Canadian features (non-numeric NA* ids) are dropped.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mapshaper = require('mapshaper');
const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(here, '..', '..');
const RAW = path.join(ROOT, 'data/raw/geo/hifld_retail_territories/electric_retail_service_territories.geojson');
const UTIL = path.join(ROOT, 'data/processed/geo_eia861_utilities.csv');
const OUT = path.join(ROOT, 'data/processed/geo_territories.geojson');
const pct = process.argv[2] || '3';
const precision = process.argv[3] || '0.0001';

function parseCSV(text) {
  const rows = []; let row = []; let cur = ''; let q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) { if (ch === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += ch; }
    else if (ch === '"') q = true; else if (ch === ',') { row.push(cur); cur = ''; }
    else if (ch === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; } else if (ch !== '\r') cur += ch;
  }
  if (cur || row.length) { row.push(cur); rows.push(row); }
  const [h, ...rest] = rows;
  return rest.filter((r) => r.length === h.length).map((r) => Object.fromEntries(h.map((k, i) => [k, r[i]])));
}

const ownById = new Map();
if (fs.existsSync(UTIL)) for (const r of parseCSV(fs.readFileSync(UTIL, 'utf8'))) if (!ownById.has(r.eia_utility_id)) ownById.set(r.eia_utility_id, r.ownership);

// HIFLD STATE is the utility's mailing-address state (e.g. Penelec -> OH, Ameren Illinois -> MO), so `state` is
// rebuilt as the ';'-joined states the utility serves per EIA-861 2025 Service_Territory (fallback: HIFLD STATE).
const CNTY = path.join(ROOT, 'data/processed/geo_county_to_utility.csv');
const statesById = new Map();
if (fs.existsSync(CNTY)) for (const r of parseCSV(fs.readFileSync(CNTY, 'utf8'))) {
  if (!statesById.has(r.eia_utility_id)) statesById.set(r.eia_utility_id, new Set());
  statesById.get(r.eia_utility_id).add(r.state);
}
const titleCase = (s) => s.toLowerCase().replace(/\b\w/g, (m) => m.toUpperCase());
const raw = JSON.parse(fs.readFileSync(RAW, 'utf8'));
let filled = 0, dropped = 0, mismatch = 0, stateFixed = 0, stateFallback = 0;
const features = [];
for (const f of raw.features) {
  const p = f.properties;
  if (!/^\d+$/.test(p.ID)) { dropped++; continue; }
  const id = Number(p.ID);
  let type = p.TYPE && p.TYPE !== 'NOT AVAILABLE' ? titleCase(p.TYPE) : null;
  const eiaOwn = ownById.get(String(id)) || null;
  if (!type && eiaOwn) { type = eiaOwn; filled++; }
  else if (type && eiaOwn && type.toLowerCase() !== eiaOwn.toLowerCase()) mismatch++;
  const customers = Number.isFinite(p.CUSTOMERS) && p.CUSTOMERS >= 0 ? p.CUSTOMERS : null;
  const served = statesById.get(String(id));
  const state = served && served.size ? [...served].sort().join(';') : p.STATE;
  if (!served) stateFallback++; else if (!served.has(p.STATE)) stateFixed++;
  features.push({ type: 'Feature', geometry: f.geometry, properties: { eia_utility_id: id, name: p.NAME, state, type, customers } });
}
console.log(`features kept ${features.length}, dropped (non-US / non-numeric id) ${dropped}, type filled from EIA-861 2025: ${filled}, HIFLD vs EIA type differ: ${mismatch}`);
console.log(`state: HIFLD mailing state not among EIA-861 served states for ${stateFixed}; no EIA-861 service-territory rows (kept HIFLD state) for ${stateFallback}; multi-state ${features.filter((f) => f.properties.state.includes(';')).length}`);

const input = { 'in.json': { type: 'FeatureCollection', features } };
const cmd = `-i in.json -simplify ${pct}% weighted keep-shapes -o out.json format=geojson precision=${precision}`;
const out = await mapshaper.applyCommands(cmd, input);
const fc = JSON.parse(Buffer.from(out['out.json']).toString());
// Guard: any feature whose geometry collapsed (tiny municipal polygons) gets its raw geometry back, rounded to 1e-4 deg.
const rawById = new Map(features.map((f) => [f.properties.eia_utility_id, f.geometry]));
const round = (c) => (typeof c[0] === 'number' ? [Math.round(c[0] * 1e4) / 1e4, Math.round(c[1] * 1e4) / 1e4] : c.map(round));
let restored = 0;
for (const f of fc.features) if (!f.geometry) { const g = rawById.get(f.properties.eia_utility_id); f.geometry = { type: g.type, coordinates: round(g.coordinates) }; restored++; }
const buf = Buffer.from('{"type":"FeatureCollection","features":[\n' + fc.features.map((f) => JSON.stringify(f)).join(',\n') + '\n]}\n');
fs.writeFileSync(OUT, buf);
console.log(`wrote ${OUT} ${(buf.length / 1e6).toFixed(2)} MB, ${fc.features.length} features (simplify ${pct}%, precision ${precision}); restored collapsed geometries: ${restored}`);
