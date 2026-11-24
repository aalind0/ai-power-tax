// Converts the utility-territory and ISO GeoJSON into one quantized, simplified TopoJSON for the web.
// Usage (from repo root):  (cd scripts/site && npm i) && node scripts/site/topo.mjs
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(path.join(here, 'package.json'));
const { topology } = require('topojson-server');
const { presimplify, simplify, quantile, filter, filterWeight } = require('topojson-simplify');
const root = path.resolve(here, '..', '..');

const terr = JSON.parse(fs.readFileSync(path.join(root, 'data/processed/geo_territories.geojson'), 'utf8'));
const iso = JSON.parse(fs.readFileSync(path.join(root, 'data/processed/geo_iso_regions.geojson'), 'utf8'));
terr.features = terr.features
  .filter((f) => f.geometry)
  .map((f) => ({ type: 'Feature', geometry: f.geometry, properties: { id: f.properties.eia_utility_id, n: f.properties.name, st: f.properties.state, c: f.properties.customers || 0 } }));
iso.features = iso.features.map((f) => ({ type: 'Feature', geometry: f.geometry, properties: { iso: f.properties.iso } }));

const { quantize } = require('topojson-client');
let topo = topology({ territories: terr, iso }); // unquantized, absolute coordinates
topo = presimplify(topo);
const target = Number(process.argv[2] || 0.12); // keep the top X share of points by importance
topo = simplify(topo, quantile(topo, 1 - target));
topo = filter(topo, filterWeight(topo, 1e-7));
// presimplify adds a weight as a 3rd coordinate to every point: drop it, then quantize + delta-encode
topo.arcs = topo.arcs.map((arc) => arc.map((p) => [p[0], p[1]]));
topo = quantize(topo, Number(process.argv[3] || 2e4));
const out = path.join(root, 'assets/data/territories.topo.json');
fs.writeFileSync(out, JSON.stringify(topo));
console.log('features', terr.features.length, '→', out, (fs.statSync(out).size / 1e6).toFixed(2), 'MB');
