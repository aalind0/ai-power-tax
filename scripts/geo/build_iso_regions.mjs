// Build data/processed/geo_iso_regions.geojson from the HIFLD "Independent System Operators" layer.
// Run: node scripts/geo/build_iso_regions.mjs [simplifyPct=2] [precision=0.001]
// input : data/raw/geo/hifld_iso_pnnl/independent_system_operators.geojson (fetch_arcgis_layer.mjs, PNNL-hosted copy)
// output: properties iso (short code used across the project), name, eia_id, peak_load_mw, avg_load_mw, data_year, source_date
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const mapshaper = require('mapshaper');
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const RAW = path.join(ROOT, 'data/raw/geo/hifld_iso_pnnl/independent_system_operators.geojson');
const OUT = path.join(ROOT, 'data/processed/geo_iso_regions.geojson');
const pct = process.argv[2] || '2';
const precision = process.argv[3] || '0.001';

const SHORT = [[/MIDCONTINENT/, 'MISO'], [/SOUTHWEST POWER POOL/, 'SPP'], [/PJM/, 'PJM'], [/ELECTRIC RELIABILITY COUNCIL OF TEXAS/, 'ERCOT'],
  [/CALIFORNIA INDEPENDENT/, 'CAISO'], [/ISO NEW ENGLAND/, 'ISO-NE'], [/NEW YORK INDEPENDENT/, 'NYISO']];
const raw = JSON.parse(fs.readFileSync(RAW, 'utf8'));
const features = raw.features.map((f) => {
  const p = f.properties;
  const iso = (SHORT.find(([re]) => re.test(p.NAME)) || [null, null])[1];
  return {
    type: 'Feature', geometry: f.geometry,
    properties: {
      iso, name: p.NAME.replace(/\.\.$/, '.'), eia_id: Number(p.ID) || null,
      peak_load_mw: p.PEAK_LOAD > 0 ? p.PEAK_LOAD : null, avg_load_mw: p.AVG_LOAD > 0 ? p.AVG_LOAD : null,
      data_year: Number(p.YEAR) || null, source_date: p.SOURCEDATE ? new Date(p.SOURCEDATE).toISOString().slice(0, 10) : null,
    },
  };
});
const out = await mapshaper.applyCommands(`-i in.json -simplify ${pct}% weighted keep-shapes -o out.json format=geojson precision=${precision}`,
  { 'in.json': { type: 'FeatureCollection', features } });
fs.writeFileSync(OUT, out['out.json']);
const fc = JSON.parse(out['out.json'].toString());
console.log(`wrote ${OUT} ${(fs.statSync(OUT).size / 1e6).toFixed(2)} MB, ${fc.features.length} features:`, fc.features.map((f) => f.properties.iso).join(','));
