// Measure precision loss of a simplified territories file vs the raw HIFLD download.
// Usage: node eval_simplify.mjs <simplified.geojson> [nPoints=4000] [seed=42]
// Samples random points: half uniformly over CONUS bbox (land-or-not), half at random raw-polygon vertices
// jittered by ~0-2 km (stress test near boundaries). Reports exact-set agreement and any-overlap agreement.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { buildIndex } from './lib/pip.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const rawFc = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/raw/geo/hifld_retail_territories/electric_retail_service_territories.geojson'), 'utf8'));
rawFc.features = rawFc.features.filter((f) => /^\d+$/.test(f.properties.ID)).map((f) => ({ ...f, properties: { eia_utility_id: Number(f.properties.ID) } }));
const simp = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const N = Number(process.argv[3] || 4000);
let s = Number(process.argv[4] || 42);
const rand = () => ((s = (s * 1103515245 + 12345) % 2147483648) / 2147483648);

const A = buildIndex(rawFc), B = buildIndex(simp);
const verts = [];
for (const f of rawFc.features) {
  const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  for (const p of polys) for (let i = 0; i < p[0].length; i += 50) verts.push(p[0][i]);
}
const pts = [];
for (let i = 0; i < N / 2; i++) pts.push(['uniform', -124.7 + rand() * 57.8, 24.5 + rand() * 25]);
for (let i = 0; i < N / 2; i++) { const v = verts[Math.floor(rand() * verts.length)]; pts.push(['near-boundary', v[0] + (rand() - 0.5) * 0.04, v[1] + (rand() - 0.5) * 0.04]); }

const stats = {};
for (const [kind, x, y] of pts) {
  const a = A.lookup(x, y).map((p) => p.eia_utility_id).sort().join(',');
  if (!a && kind === 'uniform') continue; // ignore ocean / Canada / Mexico points
  const b = B.lookup(x, y).map((p) => p.eia_utility_id).sort().join(',');
  const st = (stats[kind] ||= { n: 0, exact: 0, anyOverlap: 0, simpEmpty: 0 });
  st.n++;
  if (a === b) st.exact++;
  if (a) {
    st.nRaw = (st.nRaw || 0) + 1;
    const as = new Set(a.split(','));
    if (b.split(',').some((id) => id && as.has(id))) st.anyOverlap++;
    if (!b) st.simpEmpty++;
  }
}
for (const [k, v] of Object.entries(stats)) console.log(`${path.basename(process.argv[2])} ${k}: n=${v.n} exact-set match ${(100 * v.exact / v.n).toFixed(2)}% | of ${v.nRaw} pts inside a raw territory: simplified returns >=1 same utility ${(100 * v.anyOverlap / v.nRaw).toFixed(2)}%, returns none ${(100 * v.simpEmpty / v.nRaw).toFixed(2)}%`);
