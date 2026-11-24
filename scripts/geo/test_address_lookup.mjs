// Address -> utility recipe test. Geocodes 5 real addresses with the US Census geocoder and Photon,
// checks CORS headers (sends an Origin header like a browser would), then point-in-polygon against
// data/processed/geo_territories.geojson + geo_iso_regions.geojson, plus county and ZIP fallbacks.
// Run: node scripts/geo/test_address_lookup.mjs   -> prints a table and writes research/geo/address_tests.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { get } from './lib/http.mjs';
import { buildIndex } from './lib/pip.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const P = (f) => path.join(ROOT, f);
const ORIGIN = 'https://example.org';
const ADDRESSES = [
  { label: 'Ashburn VA (Equinix DC campus)', q: '21715 Filigree Ct, Ashburn, VA 20147' },
  { label: 'Columbus OH (Ohio Statehouse)', q: '1 Capitol Square, Columbus, OH 43215' },
  { label: 'Atlanta GA (Georgia State Capitol)', q: '206 Washington St SW, Atlanta, GA 30334' },
  { label: 'Phoenix AZ (Arizona State Capitol)', q: '1700 W Washington St, Phoenix, AZ 85007' },
  { label: 'Philadelphia PA (City Hall)', q: '1400 John F Kennedy Blvd, Philadelphia, PA 19107' },
];

function parseCSV(text) {
  const lines = text.trim().split('\n');
  const h = lines[0].split(',');
  return lines.slice(1).map((l) => {
    const out = []; let cur = ''; let q = false;
    for (const ch of l) { if (ch === '"') q = !q; else if (ch === ',' && !q) { out.push(cur); cur = ''; } else cur += ch; }
    out.push(cur);
    return Object.fromEntries(h.map((k, i) => [k, out[i]]));
  });
}

async function timed(url, headers = {}) {
  const t = Date.now();
  try {
    const r = await get(url, { headers: { Origin: ORIGIN, ...headers }, timeoutMs: 30000 });
    return { ms: Date.now() - t, status: r.status, acao: r.headers['access-control-allow-origin'] || null, body: r.body.toString('utf8'), headers: r.headers };
  } catch (e) { return { ms: Date.now() - t, status: 'ERR', error: String(e) }; }
}

const terr = buildIndex(JSON.parse(fs.readFileSync(P('data/processed/geo_territories.geojson'), 'utf8')));
const iso = buildIndex(JSON.parse(fs.readFileSync(P('data/processed/geo_iso_regions.geojson'), 'utf8')));
const zipRows = parseCSV(fs.readFileSync(P('data/processed/geo_zip_to_utility.csv'), 'utf8'));
const cntyRows = parseCSV(fs.readFileSync(P('data/processed/geo_county_to_utility.csv'), 'utf8'));
// residential customers per utility (all states summed), latest year in the bills table (bills area, read-only)
const resCust = new Map();
const billsPath = P('data/processed/bills_utility_prices.csv');
if (fs.existsSync(billsPath)) {
  const rows = parseCSV(fs.readFileSync(billsPath, 'utf8'));
  const maxYear = Math.max(...rows.map((r) => Number(r.year)));
  for (const r of rows) if (Number(r.year) === maxYear && r.res_customers) resCust.set(r.eia_utility_id, (resCust.get(r.eia_utility_id) || 0) + Number(r.res_customers));
}

const results = [];
for (const a of ADDRESSES) {
  const enc = encodeURIComponent(a.q);
  const census = await timed(`https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=${enc}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json`);
  const censusLoc = await timed(`https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=${enc}&benchmark=Public_AR_Current&format=json`);
  const photon = await timed(`https://photon.komoot.io/api/?q=${enc}&limit=1&lang=en`);
  let c = null, p = null;
  try {
    const m = JSON.parse(census.body).result.addressMatches[0];
    const cnty = m && m.geographies && m.geographies.Counties && m.geographies.Counties[0];
    if (m) c = { lng: m.coordinates.x, lat: m.coordinates.y, matched: m.matchedAddress, county_fips: cnty ? cnty.GEOID : null, county: cnty ? cnty.NAME : null, zip: (m.addressComponents || {}).zip };
  } catch (e) { c = { error: String(e).slice(0, 100) }; }
  try {
    const f = JSON.parse(photon.body).features[0];
    if (f) p = { lng: f.geometry.coordinates[0], lat: f.geometry.coordinates[1], label: [f.properties.name, f.properties.housenumber, f.properties.street, f.properties.city, f.properties.postcode].filter(Boolean).join(' ') };
  } catch (e) { p = { error: String(e).slice(0, 100) }; }
  const pt = c && c.lng ? c : p;
  const utils = pt && pt.lng ? terr.lookup(pt.lng, pt.lat).map((u) => `${u.name} [${u.eia_utility_id}, ${u.type}]`) : [];
  const isos = pt && pt.lng ? iso.lookup(pt.lng, pt.lat).map((u) => u.iso) : [];
  const zip = (c && c.zip) || (a.q.match(/\b(\d{5})\b(?!.*\d{5})/) || [])[1];
  const byZip = zipRows.filter((r) => r.zip === zip).map((r) => `${r.utility_name} [${r.eia_utility_id}, ${r.service_type}, res ${r.res_rate_usd_kwh}]`);
  const byCounty = c && c.county_fips ? cntyRows.filter((r) => r.county_fips === c.county_fips).map((r) => `${r.utility_name} [${r.eia_utility_id}]`) : [];
  // Ranking: PIP candidates that also appear in the ZIP list (OpenEI 2025) first, then most residential customers
  // (EIA-861 2025 via bills table), then smallest polygon (bbox) area. Wholesale-only/irrigation blobs sink.
  const zipIds = new Set(zipRows.filter((r) => r.zip === zip).map((r) => r.eia_utility_id));
  const cands = pt && pt.lng ? terr.lookup(pt.lng, pt.lat).map((u) => ({ id: String(u.eia_utility_id), name: u.name, res: resCust.get(String(u.eia_utility_id)) || 0, inZip: zipIds.has(String(u.eia_utility_id)) })) : [];
  cands.sort((x, y) => (y.inZip - x.inZip) || (y.res - x.res));
  const best = cands[0] || null;
  const distKm = c && p && c.lng && p.lng ? (Math.hypot((c.lng - p.lng) * Math.cos((c.lat * Math.PI) / 180), c.lat - p.lat) * 111.2).toFixed(3) : null;
  results.push({
    address: a.q, label: a.label,
    census: { status: census.status, ms: census.ms, cors_acao: census.acao, locations_status: censusLoc.status, locations_ms: censusLoc.ms, ...c },
    photon: { status: photon.status, ms: photon.ms, cors_acao: photon.acao, ...p },
    census_vs_photon_km: distKm, best_guess: best, ranked_candidates: cands, territories_pip: utils, iso_pip: isos, zip, zip_fallback: byZip, county_fallback: byCounty,
  });
}
fs.writeFileSync(P('research/geo/address_tests.json'), JSON.stringify({ run_at: new Date().toISOString(), origin_header_sent: ORIGIN, results }, null, 1));
for (const r of results) {
  console.log(`\n## ${r.label}: ${r.address}`);
  console.log(`  Census: HTTP ${r.census.status} ${r.census.ms}ms ACAO=${r.census.cors_acao} -> ${r.census.matched} (${r.census.lat}, ${r.census.lng}) county ${r.census.county} ${r.census.county_fips}`);
  console.log(`  Photon: HTTP ${r.photon.status} ${r.photon.ms}ms ACAO=${r.photon.cors_acao} -> ${r.photon.label} (${r.photon.lat}, ${r.photon.lng}); ${r.census_vs_photon_km} km from Census point`);
  console.log(`  PIP territories: ${r.territories_pip.join(' | ') || 'none'}   ISO: ${r.iso_pip.join(',') || 'none'}`);
  console.log(`  BEST GUESS: ${r.best_guess ? `${r.best_guess.name} [${r.best_guess.id}] inZip=${r.best_guess.inZip} resCust=${r.best_guess.res}` : 'none'}; runner-up: ${r.ranked_candidates[1] ? r.ranked_candidates[1].name + ' resCust=' + r.ranked_candidates[1].res : '-'}`);
  console.log(`  ZIP ${r.zip}: ${r.zip_fallback.join(' | ')}`);
  console.log(`  County: ${r.county_fallback.join(' | ')}`);
}
