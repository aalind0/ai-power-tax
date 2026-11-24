// Formatting, colour roles, tiny DOM helpers, data loading with caching.

export const $ = (s, r = document) => r.querySelector(s);
export const $$ = (s, r = document) => [...r.querySelectorAll(s)];
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export const safeUrl = (u) => (/^https?:\/\//i.test(String(u || '')) ? esc(u) : '#');

export const C = {
  ink: '#f3f1ea', ink2: '#b9b6ad', muted: '#8a877f', hair: '#25272c', base: '#4b4e56', page: '#08090b', surface: '#111316', onInk: '#0b0b0b',
  volt: '#ffd60a', up: '#e34948', upText: '#ff7b76', down: '#3987e5', downText: '#79b3ff',
  s: ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#0ca30c', '#9085e9'], // dark-surface steps of the validated order
};
// bill categories → fixed categorical slot (validated order)
export const CAT = {
  supply: { label: 'Supply / generation', c: C.s[0] },
  transmission: { label: 'Transmission', c: C.s[1] },
  distribution: { label: 'Distribution (local wires)', c: C.s[2] },
  riders: { label: 'Riders & surcharges', c: C.s[3] },
  fixed: { label: 'Fixed monthly charges', c: C.s[4] },
  base_energy: { label: 'Bundled base rate', c: C.s[5] },
  capacity: { label: 'Capacity (PJM)', c: C.s[6] },
};
// diverging blue ↔ gray ↔ red for price change
export const DIV = ['#a9cdf7', '#6ea8ee', '#3987e5', '#25548f', '#383835', '#8c3532', '#d0433f', '#f06e68', '#ffa39c']; // dark: extremes brightest, gray midpoint

export const fmt = {
  cents: (v, d = 1) => (v == null ? '—' : `${(+v).toFixed(d)}¢`),
  usd: (v, d = 0) => (v == null ? '—' : `$${(+v).toLocaleString(undefined, { minimumFractionDigits: d, maximumFractionDigits: d })}`),
  big: (v) => {
    if (v == null) return '—';
    const a = Math.abs(v);
    if (a >= 1e12) return `$${(v / 1e12).toFixed(2).replace(/\.?0+$/, '')}T`;
    if (a >= 1e9) return `$${(v / 1e9).toFixed(a >= 1e11 ? 0 : 1).replace(/\.0$/, '')}B`;
    if (a >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
    return `$${Math.round(v).toLocaleString()}`;
  },
  pct: (v, d = 0, sign = true) => (v == null ? '—' : `${sign && v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v).toFixed(d)}%`),
  int: (v) => (v == null ? '—' : Math.round(v).toLocaleString()),
  mw: (v) => (v == null ? '—' : v >= 1000 ? `${(v / 1000).toFixed(v >= 10000 ? 0 : 1).replace(/\.0$/, '')} GW` : `${Math.round(v)} MW`),
  month: (ym) => {
    const [y, m] = String(ym).split('-');
    return `${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][+m - 1]} ${y}`;
  },
};
export const signClass = (v) => (v == null ? '' : v > 0.05 ? 'up' : v < -0.05 ? 'down' : '');

export const STATE_NAMES = { AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas', CA: 'California', CO: 'Colorado', CT: 'Connecticut', DE: 'Delaware', DC: 'District of Columbia', FL: 'Florida', GA: 'Georgia', HI: 'Hawaii', ID: 'Idaho', IL: 'Illinois', IN: 'Indiana', IA: 'Iowa', KS: 'Kansas', KY: 'Kentucky', LA: 'Louisiana', ME: 'Maine', MD: 'Maryland', MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota', MS: 'Mississippi', MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada', NH: 'New Hampshire', NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York', NC: 'North Carolina', ND: 'North Dakota', OH: 'Ohio', OK: 'Oklahoma', OR: 'Oregon', PA: 'Pennsylvania', RI: 'Rhode Island', SC: 'South Carolina', SD: 'South Dakota', TN: 'Tennessee', TX: 'Texas', UT: 'Utah', VT: 'Vermont', VA: 'Virginia', WA: 'Washington', WV: 'West Virginia', WI: 'Wisconsin', WY: 'Wyoming', US: 'United States' };
export const RTO_INFO = {
  PJM: { name: 'PJM', long: 'PJM Interconnection, the grid for 65M people across 13 states and DC', capacity: true },
  MISO: { name: 'MISO', long: 'MISO, the Midcontinent grid', capacity: true },
  ERCOT: { name: 'ERCOT', long: 'ERCOT, the Texas grid (no capacity market)', capacity: false },
  SPP: { name: 'SPP', long: 'Southwest Power Pool', capacity: false },
  NYISO: { name: 'NYISO', long: 'the New York grid', capacity: true },
  'ISO-NE': { name: 'ISO-NE', long: 'the New England grid', capacity: true },
  CAISO: { name: 'CAISO', long: 'the California grid', capacity: false },
  none: { name: 'No RTO', long: 'no regional market (your utility plans and owns most of its supply)', capacity: false },
};

// d3-geo expects clockwise exterior rings; GeoJSON from most tools is counter-clockwise, which d3 reads as
// "the whole globe except this shape". Reverse any feature whose spherical area exceeds a hemisphere.
// Checked per polygon part: some multi-part territories mix both windings.
export function rewind(f) {
  /* global d3 */
  const fix = (rings) => (d3.geoArea({ type: 'Polygon', coordinates: rings }) > 2 * Math.PI ? rings.map((r) => r.slice().reverse()) : rings);
  const g = f.geometry;
  if (!g) return f;
  if (g.type === 'Polygon') g.coordinates = fix(g.coordinates);
  else if (g.type === 'MultiPolygon') g.coordinates = g.coordinates.map(fix);
  return f;
}

// Hand-drawn circle around the key number. It draws itself when it scrolls into view.
const CIRCLE_D = 'M24,60 C18,30 72,7 120,9 C172,11 197,35 191,60 C185,86 132,96 86,94 C38,91 6,72 13,48 C18,33 42,20 74,15';
export function circleIt(el) {
  if (el.querySelector('svg.circle-mark')) return;
  el.insertAdjacentHTML('beforeend', `<svg class="circle-mark" viewBox="0 0 200 100" preserveAspectRatio="none" aria-hidden="true"><path d="${CIRCLE_D}" pathLength="1"/></svg>`);
  const io = new IntersectionObserver((ents) => {
    if (ents.some((e) => e.isIntersecting)) { io.disconnect(); setTimeout(() => el.classList.add('in'), 250); }
  }, { threshold: 0.6 });
  io.observe(el);
}

// tooltip
const tipEl = () => document.getElementById('tip');
export function showTip(evt, html) {
  const t = tipEl();
  t.innerHTML = html;
  t.hidden = false;
  const r = t.getBoundingClientRect();
  let x = evt.clientX + 14;
  let y = evt.clientY + 14;
  if (x + r.width > innerWidth - 8) x = evt.clientX - r.width - 14;
  if (y + r.height > innerHeight - 8) y = evt.clientY - r.height - 14;
  t.style.left = `${Math.max(8, x)}px`;
  t.style.top = `${Math.max(8, y)}px`;
}
export const hideTip = () => (tipEl().hidden = true);

// data
const cache = new Map();
export function load(path) {
  if (!cache.has(path)) cache.set(path, fetch(path).then((r) => { if (!r.ok) throw new Error(`${path}: ${r.status}`); return r.json(); }));
  return cache.get(path);
}
export const D = {
  index: () => load('assets/data/utilities_index.json'),
  state: (st) => load(`assets/data/utilities/${st}.json`),
  prices: () => load('assets/data/prices.json'),
  grid: () => load('assets/data/grid.json'),
  anatomy: () => load('assets/data/anatomy.json'),
  policy: () => load('assets/data/policy.json'),
  households: () => load('assets/data/households.json'),
  zip: () => load('assets/data/zip.json'),
  zcta: () => load('assets/data/zcta.json'),
  countyUtils: () => load('assets/data/county_utils.json'),
  crosswalk: () => load('assets/data/crosswalk.json'),
  territories: () => load('assets/data/territories.topo.json'),
  usStates: () => load('https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-10m.json'),
  usCounties: () => load('https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/counties-10m.json'),
};
