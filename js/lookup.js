// Address → coordinates → county → utility candidates.
/* global d3, topojson */
import { D, rewind } from './util.js';

const US_BBOX = '-171.8,18.9,-66.9,71.4';
const STATE_FIPS = { '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI', '56': 'WY' };
export const stateFromFips = (fips) => STATE_FIPS[String(fips).slice(0, 2)] || null;

// ---------- ZIP codes: resolved from the Census ZIP (ZCTA) centroid table, never by free-text geocoding
const ZIP_ONLY = /^\s*(\d{5})(?:-\d{4})?\s*$/;
export async function zipPlace(zip) {
  const z = (await D.zcta())[zip];
  if (!z) return null;
  const label = `ZIP ${zip}${z[2] ? `, ${z[2]}` : ''}`;
  if (z[0] == null) return { zipOnly: zip, st: z[2], label, sub: 'ZIP code' }; // no mapped area: use the ZIP table
  return { lat: z[0], lng: z[1], st: z[2], zip, label, sub: 'ZIP code area' };
}

// ---------- geocoders
export async function suggest(q, signal) {
  const zm = q.match(ZIP_ONLY);
  if (zm) { const p = await zipPlace(zm[1]); return p ? [p] : []; }
  if (/^\s*\d{1,4}\s*$/.test(q)) return []; // partial ZIP: wait for all five digits
  const r = await fetch(`https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=6&lang=en&bbox=${US_BBOX}`, { signal });
  const j = await r.json();
  return j.features
    .filter((f) => (f.properties.countrycode || '').toUpperCase() === 'US')
    .map((f) => {
      const p = f.properties;
      const line1 = [p.housenumber && p.street ? `${p.housenumber} ${p.street}` : p.name || p.street, p.city && p.city !== p.name ? p.city : null].filter(Boolean).join(', ');
      const line2 = [p.county, p.state, p.postcode].filter(Boolean).join(' · ');
      return { lat: f.geometry.coordinates[1], lng: f.geometry.coordinates[0], label: line1 || p.name, sub: line2, zip: /^\d{5}$/.test(p.postcode || '') ? p.postcode : null };
    })
    .filter((x, i, a) => a.findIndex((y) => y.label === x.label && y.sub === x.sub) === i);
}

function jsonp(url, timeout = 7000) {
  return new Promise((resolve, reject) => {
    const cb = `__census_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
    const s = document.createElement('script');
    const t = setTimeout(() => { cleanup(); reject(new Error('timeout')); }, timeout);
    const cleanup = () => { clearTimeout(t); delete window[cb]; s.remove(); };
    window[cb] = (data) => { cleanup(); resolve(data); };
    s.src = `${url}&callback=${cb}`;
    s.onerror = () => { cleanup(); reject(new Error('network')); };
    document.head.appendChild(s);
  });
}

export async function geocode(q) {
  // 0) a bare ZIP code
  const zm = q.match(ZIP_ONLY);
  if (zm) return (await zipPlace(zm[1])) || { zipOnly: zm[1], label: `ZIP ${zm[1]}` };
  // 1) US Census (best for full street addresses; also returns the county)
  try {
    const j = await jsonp(`https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=${encodeURIComponent(q)}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=jsonp`);
    const m = j?.result?.addressMatches?.[0];
    if (m) return { lat: m.coordinates.y, lng: m.coordinates.x, label: m.matchedAddress, county: m.geographies?.Counties?.[0]?.GEOID || null, zip: (m.matchedAddress.match(/\b\d{5}\b(?!.*\b\d{5}\b)/) || [])[0] };
  } catch { /* fall through */ }
  // 2) Photon (cities, places, partial addresses)
  const s = await suggest(q);
  if (s.length) return s[0];
  return null;
}

// ---------- spatial lookups
let terrCache, countyCache;
async function territories() {
  if (!terrCache) {
    const topo = await D.territories();
    const fc = topojson.feature(topo, topo.objects.territories);
    fc.features.forEach((f) => { rewind(f); f.bbox = d3.geoBounds(f); });
    terrCache = fc.features;
  }
  return terrCache;
}
export async function territoryFeature(id) {
  const all = await territories();
  const xw = await D.crosswalk();
  return all.filter((f) => f.properties.id === id || xw[String(f.properties.id)] === id);
}
const inBox = (b, lng, lat) => lat >= b[0][1] - 0.01 && lat <= b[1][1] + 0.01 && (b[0][0] <= b[1][0] ? lng >= b[0][0] - 0.01 && lng <= b[1][0] + 0.01 : lng >= b[0][0] || lng <= b[1][0]);

export async function countyAt(lat, lng) {
  if (!countyCache) {
    const topo = await D.usCounties();
    countyCache = topojson.feature(topo, topo.objects.counties).features;
    countyCache.forEach((f) => (f.bbox = d3.geoBounds(f)));
  }
  const hit = countyCache.find((f) => inBox(f.bbox, lng, lat) && d3.geoContains(f, [lng, lat]));
  return hit ? String(hit.id).padStart(5, '0') : null;
}

// Returns { candidates: [indexEntry...], method, state }
// Three independent sources are combined: the territory polygons (point-in-polygon), the county→utility table and the
// ZIP→utility table. A candidate must be in the same state as the location (state guard); utilities the ZIP table also
// lists for this ZIP are ranked first.
export async function utilitiesAt(place) {
  const [index, xw] = await Promise.all([D.index(), D.crosswalk()]);
  const byId = new Map();
  index.forEach((e) => { if (!byId.has(e.id)) byId.set(e.id, []); byId.get(e.id).push(e); });
  const st = (place.county && stateFromFips(place.county)) || place.st || null;
  const pick = (id, prefSt) => {
    const cur = xw[String(id)] || id;
    const list = byId.get(cur);
    if (!list) return null;
    return list.find((e) => e.st === prefSt) || (prefSt ? null : list.slice().sort((a, b) => b.c - a.c)[0]);
  };
  const uniq = (arr) => arr.filter(Boolean).filter((e, i, a) => a.findIndex((x) => x.id === e.id && x.st === e.st) === i);
  const zip = place.zipOnly || place.zip;
  const zipIds = new Set(zip ? ((await D.zip())[zip] || []).map((id) => xw[String(id)] || id) : []);
  const rank = (list) => list.sort((a, b) => (zipIds.has(b.id) - zipIds.has(a.id)) || b.c - a.c);
  const inState = (list) => (st ? list.filter((e) => e.st === st) : list);

  if (place.lat != null) {
    const feats = (await territories()).filter((f) => inBox(f.bbox, place.lng, place.lat) && d3.geoContains(f, [place.lng, place.lat]));
    const c = rank(inState(uniq(feats.map((f) => pick(f.properties.id, st || f.properties.st)))));
    // If the ZIP table knows this ZIP and none of the polygon hits agree with it, trust the ZIP table instead.
    if (c.length && (!zipIds.size || c.some((e) => zipIds.has(e.id)))) return { candidates: c, method: 'territory', state: st };
  }
  if (zipIds.size) {
    const c = rank(inState(uniq([...zipIds].map((id) => pick(id, st)))));
    if (c.length) return { candidates: c, method: 'zip', state: st };
  }
  if (place.county) {
    const ids = (await D.countyUtils())[place.county] || [];
    const c = rank(inState(uniq(ids.map((id) => pick(id, st)))));
    if (c.length) return { candidates: c, method: 'county', state: st };
  }
  return { candidates: [], method: 'none', state: st };
}
