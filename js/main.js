// Home page: 3D hero, lookup form, the bill, deep links.
import { $, $$, esc, D, fmt } from './util.js';
import { suggest, geocode, utilitiesAt, countyAt } from './lookup.js';
import { renderReport } from './report.js';
import { initHero, money } from './hero3d.js';

const input = $('#addr');
const list = $('#suggest');
const status = $('#lookup-status');
const report = $('#report');
let items = [];
let active = -1;
let ctrl;
let setActState = () => {};

const say = (msg, err = false) => { status.textContent = msg; status.classList.toggle('err', err); };
function closeList() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); active = -1; }
function drawList() {
  if (!items.length) return closeList();
  list.innerHTML = items.map((s, i) => `<li role="option" id="opt-${i}" aria-selected="${i === active}" data-i="${i}"><span class="s1">${esc(s.label)}</span><span class="s2">${esc(s.sub || '')}</span></li>`).join('');
  list.hidden = false;
  input.setAttribute('aria-expanded', 'true');
}

let t;
input.addEventListener('input', () => {
  clearTimeout(t);
  const q = input.value.trim();
  if (q.length < 3) { items = []; return closeList(); }
  t = setTimeout(async () => {
    ctrl?.abort();
    ctrl = new AbortController();
    try { items = await suggest(q, ctrl.signal); active = -1; drawList(); } catch { /* aborted */ }
  }, 220);
});
input.addEventListener('keydown', (e) => {
  if (list.hidden) return;
  if (e.key === 'ArrowDown') { e.preventDefault(); active = (active + 1) % items.length; drawList(); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); active = (active - 1 + items.length) % items.length; drawList(); }
  else if (e.key === 'Escape') closeList();
  else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); choose(items[active]); }
});
list.addEventListener('mousedown', (e) => { const li = e.target.closest('li'); if (li) { e.preventDefault(); choose(items[+li.dataset.i]); } });
document.addEventListener('click', (e) => { if (!e.target.closest('.lookup')) closeList(); });

$('#lookup').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return input.focus();
  closeList();
  say('Finding your address…');
  try {
    const place = await geocode(q);
    if (!place) return say("We couldn't find that address. Try adding a city and state, or a ZIP code.", true);
    await resolve(place);
  } catch (err) {
    console.error(err);
    say('Something went wrong looking that up. Please try again.', true);
  }
});

async function choose(s) {
  input.value = [s.label, s.sub].filter(Boolean).join(', ');
  closeList();
  say('Finding your utility…');
  await resolve(s);
}

async function resolve(place) {
  if (place.lat != null && !place.county) place.county = await countyAt(place.lat, place.lng).catch(() => null);
  say('Finding your utility…');
  const { candidates, method } = await utilitiesAt(place);
  if (!candidates.length) return say("We couldn't match a utility with price data to that location. Try a nearby city or your ZIP code.", true);
  say(method === 'territory' ? '' : `Matched by ${method === 'county' ? 'county' : 'ZIP code'}. Pick another utility below if this isn't yours.`);
  await show(candidates[0], place, candidates);
}

async function show(entry, place, candidates) {
  await renderReport(report, { entry, place, candidates, onSwitch: (o) => show(o, place, candidates) });
  setActState(entry.st);
}

$$('.try').forEach((b) => b.addEventListener('click', () => {
  input.value = b.dataset.q;
  $('#lookup').requestSubmit();
}));

$('#locate').addEventListener('click', () => {
  if (!navigator.geolocation) return say('Location is not available in this browser.', true);
  say('Getting your location…');
  navigator.geolocation.getCurrentPosition(
    (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude, label: 'Your location' }),
    () => say('Location blocked. Type your address instead.', true),
    { timeout: 10000, maximumAge: 600000 }
  );
});

// sticky header border
addEventListener('scroll', () => $('.topbar').classList.toggle('scrolled', scrollY > 8), { passive: true });

// deep link ?u=<eia_id>-<ST>
async function deepLink() {
  const m = new URLSearchParams(location.search).get('u')?.match(/^(\d+)-([A-Z]{2})$/);
  if (!m) return;
  const index = await D.index();
  const entry = index.find((e) => e.id === +m[1] && e.st === m[2]);
  if (entry) show(entry, null, []);
}

initHero().then((S) => {
  $('#pc-1').textContent = money(S.us[S.us.length - 1]);
  $('#pc-2').textContent = `≈$${Math.round(S.pjmDc)}`;
}).catch(console.error);
D.prices().then((p) => { $('#updated').textContent = `data through ${fmt.month(p.latestMonth)}`; }).catch(() => {});
deepLink().catch(console.error);
