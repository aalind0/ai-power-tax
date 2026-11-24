// Assign each US data-center campus in compute-atlas/data/atlas.json to a county FIPS via the
// Census Bureau geocoder (coordinates -> geographies). Output:
//   data/raw/households/census_geocoder_campuses/campus_counties.json  (raw responses, trimmed)
// Usage: node scripts/households/geocode_campuses.mjs
import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..', '..');
const atlas = JSON.parse(fs.readFileSync(path.resolve(root, '..', 'compute-atlas', 'data', 'atlas.json'), 'utf8'));
const us = atlas.campuses.filter((c) => c.countryCode === 'US' && c.lat != null && c.lng != null);
const outDir = path.join(root, 'data', 'raw', 'households', 'census_geocoder_campuses');
fs.mkdirSync(outDir, { recursive: true });

function getJson(url) {
  return new Promise((resolve, reject) => {
    const r = https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (research script)' } }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); } catch (e) { reject(e); }
      });
    });
    r.setTimeout(30000, () => r.destroy(new Error('timeout')));
    r.on('error', reject);
  });
}

const out = [];
for (const c of us) {
  const url = `https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=${c.lng}&y=${c.lat}` +
    '&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json';
  let county = null, err = null;
  for (let attempt = 0; attempt < 3 && !county; attempt++) {
    try {
      const j = await getJson(url);
      const g = (j.result && j.result.geographies && j.result.geographies.Counties) || [];
      if (g.length) county = { fips: g[0].GEOID, name: g[0].NAME, state_fips: g[0].STATE };
      else err = 'no county';
    } catch (e) { err = String(e.message || e); }
  }
  out.push({
    id: c.id, name: c.name, lat: c.lat, lng: c.lng, coordPrecision: c.coordPrecision, region: c.region,
    status: c.status, powerMW: c.powerMW, powerMWNow: c.powerMWNow,
    owners: (c.owners || []).map((o) => o.name), county_fips: county && county.fips, county_name: county && county.name,
    error: county ? null : err,
  });
  process.stdout.write(county ? '.' : 'x');
}
fs.writeFileSync(path.join(outDir, 'campus_counties.json'), JSON.stringify({ fetched_at: new Date().toISOString(), source: 'https://geocoding.geo.census.gov/geocoder/ (Public_AR_Current / Current_Current, Counties layer)', campuses: out }, null, 1));
console.log(`\n${out.filter((o) => o.county_fips).length}/${out.length} geocoded`);
