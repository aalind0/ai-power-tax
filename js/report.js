// The personal report, typeset as a utility bill.
/* global d3, topojson */
import { $, esc, safeUrl, fmt, signClass, C, CAT, D, STATE_NAMES, RTO_INFO, circleIt, load } from './util.js';
import { lineChart, columns, meter, territoryMap, waterfall, strip, stepTimeline, barList, dollarFlow } from './charts.js';
import { territoryFeature } from './lookup.js';
import { openShare } from './share.js';

// ---------------------------------------------------------------- "where did my extra $ go" (estimate)
// Split the change in the average monthly bill, 2020 → latest year, into regional cost components applied to the
// household's own usage, a usage effect, and a remainder that is specific to the utility.
export function billWaterfall(ann, grid, rto, ytd) {
  const a20 = ann.find((r) => r[0] === 2020), last = ann[ann.length - 1];
  if (!a20 || !a20[3] || !last[3] || last[0] < 2024) return null;
  const k20 = a20[4] || (a20[3] / a20[1]) * 100, k1 = last[4] || (last[3] / last[1]) * 100;
  const td = grid.td.filter((r) => r.g);
  const t20 = td.find((r) => r.y === 2020), t1 = td.find((r) => r.y === last[0]) || td[td.length - 1];
  if (!t20 || !t1) return null;
  const d = { dist: t1.dc - t20.dc };
  if (rto === 'PJM') {
    const c20 = grid.components.find((c) => c.per === '2020'), c1 = grid.components.find((c) => c.per === String(last[0]));
    if (!c20 || !c1) return null;
    Object.assign(d, { energy: (c1.e - c20.e) / 10, cap: (c1.c - c20.c) / 10, trans: (c1.t - c20.t) / 10 });
  } else Object.assign(d, { energy: t1.g - t20.g, trans: t1.tc - t20.tc });
  const usd = (cents) => (cents * k1) / 100;
  const parts = [
    { label: 'Energy &\nfuel', short: 'Energy & fuel', v: usd(d.energy), note: rto === 'PJM' ? 'Change in PJM wholesale energy cost per kWh (market monitor), times your usage' : 'Change in the US average generation cost per kWh (EIA), times your usage' },
    ...(d.cap != null ? [{ label: 'Capacity\n(PJM)', short: 'Capacity', v: usd(d.cap), note: `Change in PJM capacity cost per kWh, 2020 vs ${last[0]} (market monitor). The bigger jump lands in 2026.` }] : []),
    { label: 'Trans-\nmission', short: 'Transmission', v: usd(d.trans), note: rto === 'PJM' ? 'Change in PJM transmission cost per kWh (market monitor), times your usage' : 'Change in the US average transmission cost per kWh (EIA), times your usage' },
    { label: 'Local\nwires', short: 'Local wires', v: usd(d.dist), note: 'Change in the US average distribution cost per kWh (EIA), times your usage' },
    { label: 'Your\nusage', short: 'Your usage', v: ((k1 - k20) * a20[1]) / 100, note: `Average use went from ${Math.round(k20)} to ${Math.round(k1)} kWh a month, priced at 2020 rates` },
  ];
  const other = last[3] - a20[3] - parts.reduce((t, p) => t + p.v, 0);
  parts.push({ label: 'Utility rates\n& riders', short: 'Rates & riders', v: other, note: 'What is specific to your utility (base-rate increases, riders, fuel adjustments, taxes), calculated as the remainder' });
  const steps = [{ kind: 'total', label: '2020\nbill', short: '2020 bill', v: a20[3] }, ...parts.map((p) => ({ ...p, kind: 'delta' })), { kind: 'total', label: `${last[0]}\nbill`, short: `${last[0]} bill`, v: last[3], emph: ytd == null || last[0] !== 2025 }];
  let end = last[3];
  if (ytd != null && last[0] === 2025) {
    const add = (last[3] * ytd) / 100;
    end = last[3] + add;
    steps.push({ kind: 'delta', label: '2026\nso far', short: '2026 so far', v: add, note: `Your utility's 2026 price so far is ${ytd > 0 ? '+' : ''}${ytd.toFixed(1)}% vs the same months of 2025` });
    steps.push({ kind: 'total', label: '2026\n(est.)', short: '2026 est.', v: end, emph: true });
  }
  const top = parts.filter((p) => p.v > 0).sort((a, b) => b.v - a.v)[0];
  return { steps, start: a20[3], mid: last[3], end, year: last[0], top };
}

// ---------------------------------------------------------------- capacity charges already locked in (PJM)
// PJM-wide capacity cost per kWh by delivery year = auction cost ÷ PJM annual energy. The energy figure (≈793 TWh)
// is implied by LBNL's 2026 estimate of 1.957¢/kWh. Applied to the household's own usage.
const PJM_KWH = 7.93e11;
// Outside PJM: regional estimate (¢/kWh low/central/high) from assets/data/dc_regional.json, built from targeted research.
const SE = ['GA', 'AL', 'FL', 'NC', 'SC', 'TN', 'MS', 'LA', 'AR', 'KY'], WEST = ['AZ', 'NV', 'OR', 'WA', 'ID', 'UT', 'CO', 'NM', 'MT', 'WY'];
export const dcRegionKey = (rto, st) => (rto && rto !== 'none' ? rto : st === 'CA' ? 'CAISO' : SE.includes(st) ? 'Southeast' : WEST.includes(st) || st === 'TX' ? 'West' : null);
function dcEstimate(reg, latest, wf, ytd) {
  const kwh = latest[4];
  if (!reg || reg.central == null || !kwh) return null;
  const bill = wf?.end || (ytd != null ? latest[3] * (1 + ytd / 100) : latest[3]);
  const usd = (reg.central * kwh) / 100;
  return { est: true, usd, cents: reg.central, lo: (reg.low * kwh) / 100, hi: (reg.high * kwh) / 100, pct: (usd / bill) * 100, billYear: ytd != null ? 2026 : latest[0], basis: reg.basis, conf: reg.confidence, url: reg.url, label: reg.label };
}
export function dcShareOfBill(rto, latest, wf, ytd, reg) {
  if (rto !== 'PJM') return dcEstimate(reg, latest, wf, ytd);
  const now = new Date();
  const y = now.getMonth() >= 5 ? now.getFullYear() : now.getFullYear() - 1;
  const dy = `${y}/${String((y + 1) % 100).padStart(2, '0')}`;
  const imm = IMM[dy];
  const kwh = latest[4];
  if (!imm || !kwh) return null;
  const cents = (imm / PJM_KWH) * 100;
  const usd = (cents * kwh) / 100;
  const bill = wf?.end || (ytd != null ? latest[3] * (1 + ytd / 100) : latest[3]);
  return { usd, cents, pct: (usd / bill) * 100, dy, billYear: ytd != null ? 2026 : latest[0], imm };
}

// who ends up with each slice of a bill
const WHO = {
  supply: 'Power plants & fuel suppliers (incl. capacity)', capacity: 'Power plant owners, paid to stand by', transmission: 'High-voltage grid owners',
  distribution: 'Your utility: poles, wires, meters', riders: 'Programs & adjustments (fuel, efficiency, storms)', fixed: 'Your utility: customer charge',
  base_energy: 'Your utility: plants and wires, bundled',
};
export function lockedCapacity(grid, kwh) {
  const rto = (grid.capacity.PJM || []).filter((r) => r.z === 'RTO' && r.cost);
  const now = new Date();
  const periods = ['2024/25', '2025/26', '2026/27', '2027/28', '2028/29'].map((dy) => {
    const r = rto.find((x) => x.dy === dy);
    if (!r) return null;
    const y = +dy.slice(0, 4);
    const cents = (r.cost / PJM_KWH) * 100;
    return { start: new Date(y, 5, 1), end: new Date(y + 1, 4, 31), v: (cents * kwh) / 100, cents, label: dy.replace('/', '–'), locked: new Date(y, 5, 1) > now,
             tip: `≈${cents.toFixed(2)}¢/kWh × your ${Math.round(kwh)} kWh a month · auction: $${r.p}/MW-day` };
  }).filter(Boolean);
  return periods.length >= 3 ? periods : null;
}

export const IMM = { '2025/26': 9.33e9, '2026/27': 7.27e9, '2027/28': 6.5e9, '2028/29': 6.27e9 }; // market monitor, data-center attribution
export const IMM_URL = 'https://www.monitoringanalytics.com/reports/Reports/2026/IMM_Analysis_of_the_20282029_RPM_Base_Residual_Auction_Part_A_20261030.pdf';
const UNCAPPED_2829 = 554.72;

const OWN = { 'Investor Owned': 'Investor-owned', Cooperative: 'Co-op', Municipal: 'City-owned', 'Political Subdivision': 'Public power district', State: 'State-owned', Federal: 'Federal', 'Retail Power Marketer': 'Retail supplier' };

function cpiAnnual(cpi) {
  const by = {};
  cpi.forEach(([d, v]) => { const y = +d.slice(0, 4); (by[y] = by[y] || []).push(v); });
  return Object.fromEntries(Object.entries(by).map(([y, a]) => [y, d3.mean(a)]));
}

export function capacityFor(grid, zone) {
  const order = (zone && grid.capLda[zone]) || ['RTO'];
  const pjm = grid.capacity.PJM || [];
  const years = [...new Set(pjm.map((r) => r.dy))].sort();
  return years.map((dy) => {
    for (const lda of order) {
      const r = pjm.find((x) => x.dy === dy && x.z === lda);
      if (r) return { dy, p: r.p, lda, cost: (pjm.find((x) => x.dy === dy && x.z === 'RTO') || {}).cost };
    }
    return null;
  }).filter(Boolean);
}

function verdictFor(rto) {
  if (rto === 'PJM') return {
    v: 0.82, h: 'Strong evidence on your grid',
    p: 'PJM\'s independent market monitor attributes $29.4B of capacity costs across the last four auctions to data-center load, and says there would have been no shortfall without it.',
    raise: ['Capacity charges went from 0.36¢ to about 1.96¢/kWh (2024 to 2026), roughly $20 a month on a 1,000 kWh bill, landing every June 1.', 'Data centers were 93–95% of PJM\'s 2025 large-load forecast additions.', '$4.36B of 2024 grid hookups for single data centers in PJM states was spread over all customers (UCS).'],
    lower: ['An E3 study funded by data-center groups attributes only about half of the capacity jump to load growth; market design and plant retirements did the rest.', 'Part of the spike is a rebound: 2022–24 capacity prices were unusually low. Per MWh, capacity costs about 1.5× its 2015–18 level.', 'Large-load tariffs (Dominion GS-5, AEP Ohio) now make new data centers sign 12–20-year contracts with minimum bills.'],
  };
  if (rto === 'ERCOT') return {
    v: 0.5, h: 'Mixed evidence on your grid',
    p: 'Texas has no capacity market, so data-center demand shows up in energy prices and transmission instead. Nobody has published a Texas attribution study yet.',
    raise: ['ERCOT has 474 GW of large-load connection requests, about 90% of them data centers, against a ~90 GW record peak.', 'New 765 kV transmission for West Texas load is recovered from all customers.'],
    lower: ['Only 205 GW of those requests qualified for study; most pipeline numbers won\'t be built.', 'Texas SB 6 (2025) makes large loads share interconnection costs and accept curtailment in emergencies.'],
  };
  if (rto === 'MISO') return {
    v: 0.55, h: 'Some evidence on your grid',
    p: 'MISO\'s summer capacity price hit $666.50/MW-day in 2025/26, then fell to $384–424 as more supply came forward. Data-center load is one of several drivers.',
    raise: ['Utilities like Entergy are building gas plants for single data-center campuses (Meta Hyperion: ~7.5 GW of new generation).', 'Capacity shortfall warnings cite load growth from data centers and manufacturing.'],
    lower: ['Many MISO utilities are vertically integrated, which partly shields customers from auction prices.', 'LBNL/Brattle: states with the fastest load growth mostly saw real price declines in 2019–24.'],
  };
  if (rto === 'none') return {
    v: 0.35, h: 'Little evidence so far',
    p: 'Your utility plans and owns most of its supply, and costs reach you through state rate cases rather than a market auction. That makes the data-center effect slower and easier for regulators to see.',
    raise: ['Utilities are filing record capex plans ($1.36T nationally for 2026–30). Customers pay for those, plus an allowed return, if regulators approve.', 'In the Southeast, Georgia Power and others are adding gigawatts of gas largely for data centers.'],
    lower: ['LBNL/Brattle: extra load often spreads fixed grid costs and lowers rates when supply is available.', 'Georgia froze base rates through 2028 and many states adopted large-load tariffs in 2025–26.'],
  };
  return {
    v: 0.45, h: 'Limited evidence on your grid',
    p: 'Your grid has seen price pressure, but studies tying it to data centers are thin. Fuel prices, wildfire and storm costs, and transmission are bigger drivers today.',
    raise: ['Capacity prices in New York City and New England rose in 2025–26.', 'Transmission spending is rising everywhere, partly for new large loads.'],
    lower: ['LBNL/Brattle find load growth usually lowered real prices in 2019–24.', 'Industry studies (CRA for EEI) find no data-center-driven increases outside PJM.'],
  };
}

export async function renderReport(host, { entry, place, candidates = [], onSwitch }) {
  host.hidden = false;
  host.innerHTML = '<div class="skeleton" aria-label="Loading your bill"></div>';
  host.scrollIntoView({ behavior: 'smooth', block: 'start' });
  const [shard, prices, grid, anat, pol, hh, feats, statesTopo, index] = await Promise.all([
    D.state(entry.st), D.prices(), D.grid(), D.anatomy(), D.policy(), D.households(), territoryFeature(entry.id), D.usStates().catch(() => null), D.index(),
  ]);
  const u = shard.find((x) => x.id === entry.id) || entry;
  const st = u.st;
  const stName = STATE_NAMES[st] || st;
  const rto = u.r || 'none';
  const rinfo = RTO_INFO[rto] || RTO_INFO.none;
  const cpiY = cpiAnnual(prices.cpi);
  const usA = prices.us;
  const stA = prices.states[st]?.a || [];
  const ann = u.a || [];
  const first = ann[0];
  const latest = ann[ann.length - 1];
  const y20 = ann.find((r) => r[0] === 2020);
  const us20 = usA.find((r) => r[0] === 2020), usL = usA.find((r) => r[0] === latest[0]) || usA[usA.length - 1];
  const usCh = us20 && usL ? (usL[1] / us20[1] - 1) * 100 : null;
  const cpiCh = cpiY[2020] && cpiY[latest[0]] ? (cpiY[latest[0]] / cpiY[2020] - 1) * 100 : null;
  const vsUS = usL ? (latest[1] / usL[1] - 1) * 100 : null;
  const billCh = y20 && y20[3] && latest[3] ? latest[3] - y20[3] : null;
  const anatomy = anat.utilities[String(u.id)];
  const zone = u.z;
  const cap = rto === 'PJM' ? capacityFor(grid, zone) : [];
  const nits = zone && grid.nits[zone];
  const nitsRatio = nits ? (() => { const s = nits.s; const a = s.find((r) => r[0] === 2015); const b = s[s.length - 1]; return a && b ? { x: b[1] / a[1], y: b[0] } : null; })() : null;
  const share = grid.loadShare[st];
  const usShare = (grid.usLoad || []).find((r) => r.y === 2023 && !r.proj);
  const disc = grid.disclosures.filter((d) => d.id === u.id && /share/.test(d.m)).sort((a, b) => String(b.per).localeCompare(String(a.per)))[0];
  const feature = feats.length ? { type: 'FeatureCollection', features: feats } : null;
  const stateFeature = statesTopo ? topojson.feature(statesTopo, statesTopo.objects.states).features.find((f) => (f.properties.name || '') === stName) : null;
  const camps = grid.campuses.filter((c) => !c.cl && (c.st === st || (feature && d3.geoContains(feature, [c.lng, c.lat])))).map((c) => ({ ...c, inside: feature ? d3.geoContains(feature, [c.lng, c.lat]) : false }));
  const inside = camps.filter((c) => c.inside);
  const policy = pol.states[st];
  const nameTokens = u.n.toLowerCase().replace(/[^a-z ]/g, ' ').split(/\s+/).filter((t) => t.length > 3 && !['company', 'power', 'electric', 'energy', 'light', 'corp'].includes(t));
  const cases = pol.cases.filter((c) => c.state === st).map((c) => ({ ...c, mine: nameTokens.some((t) => (c.utility || '').toLowerCase().includes(t)) })).sort((a, b) => b.mine - a.mine || (b.requested_increase_usd || 0) - (a.requested_increase_usd || 0)).slice(0, 4);
  const county = place?.county ? hh.county[place.county] : null;
  const shut = hh.shutoffs[`${u.id}-${st}`];
  const verdict = verdictFor(rto);
  const nomCh = u.chn;
  const own = OWN[u.o] || u.o;

  // you vs America: customer-weighted percentile of the real change since 2020
  const pool = index.filter((e) => e.ch != null && e.c >= 1000);
  const totalC = d3.sum(pool, (e) => e.c);
  const pctile = u.ch != null ? (d3.sum(pool.filter((e) => e.ch < u.ch), (e) => e.c) / totalC) * 100 : null;
  let accW = 0;
  const medianCh = (pool.slice().sort((a, b) => a.ch - b.ch).find((e) => (accW += e.c) >= totalC / 2) || {}).ch;
  const above = pctile != null && u.ch > medianCh;
  const wf = billWaterfall(ann, grid, rto, u.ytd);
  const locked = rto === 'PJM' ? lockedCapacity(grid, latest[4] || 900) : null;
  // scale: an average home's continuous draw, and the state's homes
  const usKwh = (usA.find((r) => r[0] === latest[0]) || usA[usA.length - 1])[4] || 870;
  const homeKw = (usKwh * 12) / 8760;
  const stHomes = ([...stA].reverse().find((r) => r[4]) || [])[4];
  const st2023 = stA.find((r) => r[0] === 2023);
  const biggest = grid.campuses.filter((c) => c.st === st && !c.cl && c.mw && !/cancel|block/i.test(c.s)).sort((a, b) => b.mw - a.mw)[0];
  const bigHomes = biggest ? (biggest.mw * 1000) / homeKw : null;
  const ratio = bigHomes && stHomes ? bigHomes / stHomes : null;
  // THE answer: data centers' share of this bill. Only PJM has a published attribution (the market monitor's
  // data-center share of each capacity auction); we convert the current delivery year to $/month at this
  // utility's average usage. It's a floor: transmission and energy-price effects are not included.
  const dcReg = await load('assets/data/dc_regional.json').then((r) => r.regions[dcRegionKey(rto, u.st)]).catch(() => null);
  const dcx = dcShareOfBill(rto, latest, wf, u.ytd, dcReg);
  const dcAmt = (x) => (x.usd < 1 ? 'under $1' : fmt.usd(x.usd));
  const noDcText = rto === 'ERCOT' ? 'Texas has no capacity market, and no study yet attributes Texas bill increases to data centers. The evidence is below.'
    : rto === 'MISO' ? 'MISO\'s capacity prices spiked in 2025, but no study yet separates out data centers\' share. The evidence is below.'
    : 'No study yet measures how much data centers add to bills in your area. Your costs reach you through state rate cases. The evidence is below.';
  const name = esc(shortName(u.n));
  const summaryLine = `${name}'s price is ${nomCh >= 0 ? 'up' : 'down'} <b>${Math.abs(Math.round(nomCh ?? 0))}%</b> since 2020${pctile != null && above ? `, a bigger increase than ${Math.round(pctile)}% of American homes saw` : ''}. `
    + (dcx?.est ? `Roughly <span class="hl-ink">${dcAmt(dcx)} a month</span> of a typical bill may trace to data-center demand in your region (estimate). ` : '')
    + (dcx && !dcx.est ? `About <span class="hl-ink">${fmt.usd(dcx.usd)} a month</span> of a typical bill now traces to data-center demand in PJM's capacity market${locked ? ', and PJM\'s auctions have already set those costs through 2029' : ''}.` : 'Data centers\' effect on bills here hasn\'t been measured yet.')
    + (wf?.top ? ` The biggest driver since 2020: <b>${esc(wf.top.short.toLowerCase())}</b>.` : '');

  // ---------------- itemized charges
  let items, itemsNote, itemsTotal, itemsVerified = true;
  if (anatomy) {
    const cats = Object.entries(anatomy.by_category_usd || {}).filter(([, v]) => v > 0);
    itemsTotal = anatomy.total_usd_at_1000kwh;
    items = (anatomy.lines || []).filter((l) => l.usd_at_1000kwh).map((l) => ({ cat: l.category, label: l.label, usd: l.usd_at_1000kwh, pct: l.pct_of_bill, ok: l.verified }));
    itemsVerified = items.every((i) => i.ok !== false);
    itemsNote = `Real tariff, ${esc(anatomy.rate || '')}. Effective ${esc(anatomy.effective || '')}. ${anatomy.capacity_note ? esc(anatomy.capacity_note) : ''}`;
    items._cats = cats;
  } else {
    const t = [...grid.td].reverse().find((r) => r.g && r.tc && r.dc);
    const tot = latest[1] * 10;
    const shares = { supply: t.g / t.all, transmission: t.tc / t.all, distribution: t.dc / t.all };
    const norm = shares.supply + shares.transmission + shares.distribution;
    items = Object.entries(shares).map(([k, v]) => ({ cat: k, label: CAT[k].label, usd: (tot * v) / norm }));
    if (rto === 'PJM') {
      const capUsd = 19.57;
      items[0].usd -= capUsd;
      items.splice(1, 0, { cat: 'capacity', label: 'Capacity (PJM, 2026 est.)', usd: capUsd });
    }
    itemsTotal = tot;
    items.forEach((i) => (i.pct = (i.usd / tot) * 100));
    items._cats = items.map((i) => [i.cat, i.usd]);
    itemsVerified = false;
    itemsNote = `Estimated: your utility's ${latest[0]} average price of ${fmt.cents(latest[1])}/kWh, split using EIA's national shares for generation, transmission and distribution${rto === 'PJM' ? ', with PJM\'s 2026 capacity cost (≈1.96¢/kWh, LBNL) carved out of supply' : ''}. Real tariffs are researched for 13 large utilities so far.`;
  }
  const catOrder = Object.keys(CAT);
  const stackCats = items._cats.slice().sort((a, b) => catOrder.indexOf(a[0]) - catOrder.indexOf(b[0]));
  const stackTotal = stackCats.reduce((t, [, v]) => t + v, 0);

  const others = candidates.filter((c) => !(c.id === u.id && c.st === u.st));
  const ytdTxt = u.ytd != null ? `${fmt.pct(u.ytd, 1)}` : '—';
  const stYtd = prices.states[st]?.ytd;
  const share_url = `${location.origin}${location.pathname}?u=${u.id}-${u.st}`;

  host.innerHTML = `
  <article class="bill" aria-label="Your electricity bill story">
    <header class="bill-head">
      <div>
        <div class="bill-meta"><span>Statement · ${esc(prices.latestMonth ? fmt.month(prices.latestMonth) : '')}</span><span>EIA ID ${u.id}</span><span>${esc(stName)}</span>${rto !== 'none' ? `<span>Grid: ${esc(rto)}${zone ? ` · zone ${esc(zone)}` : ''}</span>` : '<span>Vertically integrated</span>'}</div>
        <h2>${esc(shortName(u.n))}</h2>
        <div class="bill-sub">${place?.label ? `Service address: <b>${esc(place.label)}</b> · ` : ''}${own} · ${fmt.int(u.c)} homes served</div>
        ${others.length ? `<div class="switch">Not your utility? ${others.slice(0, 5).map((o, i) => `<button data-i="${i}">${esc(shortName(o.n))}</button>`).join('')}</div>` : ''}
      </div>
      ${nomCh != null ? '<div class="head-cta"><button class="btn share-btn" id="share-card" type="button">Share my bill card</button></div>' : ''}
    </header>

    <div class="answer" aria-label="The short answer">
      <div class="ans">
        <div class="k">Your bill since 2020</div>
        <div class="v ${signClass(nomCh)}">${fmt.pct(nomCh, 0)}</div>
        <div class="s">${u.ch != null ? `${fmt.pct(u.ch, 0)} after inflation · ` : ''}US average ${fmt.pct(usCh, 0)} · prices overall ${fmt.pct(cpiCh, 0)}</div>
      </div>
      <div class="ans ans-dc">
        <div class="k">Data centers' share of your bill</div>
        ${dcx?.est ? `<div class="v"><span class="circled">${dcx.usd < 1 ? '&lt;$1' : `≈${fmt.usd(dcx.usd)}`}<small>/mo</small></span></div>
        <div class="s">about <b>${dcx.pct < 1 ? '<1' : dcx.pct.toFixed(0)}%</b> of a typical ${dcx.billYear} bill${dcx.hi >= 1 ? `, range ${fmt.usd(dcx.lo)}–${fmt.usd(dcx.hi)}` : ''}. <span class="badge warn">estimate</span>${dcx.usd < 1.5 ? '<div class="why"><b>Why so low?</b> In the PJM grid (Philadelphia to Chicago), data-center demand raised a capacity charge every home pays, about $7/mo. Here, those costs mostly aren\'t in rates yet, or data centers pay them directly.</div>' : ''}<div class="why-basis">${esc(dcx.basis || '')}${dcx.url ? ` <a href="${safeUrl(dcx.url)}" target="_blank" rel="noopener">source</a>` : ''}</div></div>`
        : dcx ? `<div class="v"><span class="circled">≈${fmt.usd(dcx.usd)}<small>/mo</small></span></div>
        <div class="s">about <b>${dcx.pct.toFixed(0)}%</b> of a typical ${dcx.billYear} bill. Floor estimate: the data-center share of PJM capacity costs, per the grid's market monitor (${esc(dcx.dy)}).</div>`
        : `<div class="v v-sm">Not measurable yet</div><div class="s">${esc(noDcText)}</div>`}
      </div>
      <div class="ans">
        ${locked ? `<div class="k">Already locked in</div><div class="v up">${fmt.usd(locked[locked.length - 1].v)}<small>/mo</small></div><div class="s">capacity charge through May ${locked[locked.length - 1].end.getFullYear()}, up from ${fmt.usd(locked[0].v)} in ${esc(locked[0].label)}</div>`
        : `<div class="k">2026 so far</div><div class="v ${signClass(u.ytd)}">${ytdTxt}</div><div class="s">${u.ytd != null ? `vs the same months of 2025${stYtd != null ? ` · ${esc(stName)}: ${fmt.pct(stYtd, 1)}` : ''}` : 'monthly data not reported'}</div>`}
      </div>
    </div>
    <p class="answer-line">${summaryLine}</p>

    <div class="tiles">
      <div class="tile"><div class="k">${latest[0]} price</div><div class="v num">${fmt.cents(latest[1], 2)}<small style="font-size:14px;font-weight:500">/kWh</small></div><div class="s ${signClass(vsUS)}">${fmt.pct(vsUS, 0)} vs US average</div></div>
      <div class="tile"><div class="k">Avg monthly bill</div><div class="v num">${fmt.usd(latest[3])}</div><div class="s">${billCh != null ? `${billCh >= 0 ? '+' : '−'}${fmt.usd(Math.abs(billCh))} vs 2020` : `at ${fmt.int(latest[4])} kWh/month`}</div></div>
      ${locked ? `<div class="tile"><div class="k">2026 so far</div><div class="v num ${signClass(u.ytd)}">${ytdTxt}</div><div class="s">${u.ytd != null ? 'vs the same months of 2025' : 'monthly data not reported'}${stYtd != null ? ` · ${esc(st)}: ${fmt.pct(stYtd, 1)}` : ''}</div></div>` : `<div class="tile"><div class="k">Homes served</div><div class="v num">${fmt.int(u.c)}</div><div class="s">${esc(own)} utility</div></div>`}
      <div class="tile"><div class="k">vs. America</div><div class="v num">${pctile != null ? `${Math.round(above ? pctile : 100 - pctile)}%` : '—'}</div><div class="s">${pctile != null ? (above ? 'of US homes saw a smaller increase' : 'of US homes saw a bigger increase') : ''}</div></div>
    </div>

    ${wf ? `<section class="bsec" aria-labelledby="h-wf">
      <div class="bsec-h"><h3 id="h-wf">Why it went up</h3><span class="aside"><span class="badge warn">estimate</span> hover a bar for how it's calculated</span></div>
      <p class="lead">The average monthly bill went from <b>${fmt.usd(wf.start)}</b> in 2020 to <b>${fmt.usd(wf.mid)}</b> in ${wf.year}${wf.end !== wf.mid ? `, and is running at about <b>${fmt.usd(wf.end)}</b> in 2026` : ''}. Here's roughly where the extra ${fmt.usd(Math.abs(wf.end - wf.start))} ${wf.end >= wf.start ? 'went' : 'came from'}.</p>
      <div id="r-wf"></div>
      <p class="note">How we estimate it: regional cost changes per kWh (${rto === 'PJM' ? 'PJM\'s market monitor for energy, capacity and transmission; ' : ''}EIA national averages ${rto === 'PJM' ? 'for local wires' : 'for generation, transmission and local wires'}) times this utility's average usage. "Utility rates & riders" is the remainder: everything specific to this utility. Your own bill depends on your usage and plan.</p>
    </section>` : ''}

    <section class="bsec" aria-labelledby="h-hist">
      <div class="bsec-h"><h3 id="h-hist">Your price over time</h3><span class="aside">Residential average, ¢ per kWh · hover for values</span></div>
      <p class="lead">${historyLead(u, latest, first, cpiY, usCh)}</p>
      <div class="legend"><span><i style="--c:${C.s[0]}"></i>${esc(shortName(u.n))}</span><span><i style="--c:${C.muted}"></i>${esc(stName)} average</span><span><i class="dash" style="--c:${C.ink}"></i>US average</span><span><i class="dash" style="--c:${C.base}"></i>If it tracked inflation</span></div>
      <div id="r-hist"></div>
      ${u.mo && u.mo.length > 6 ? `<div class="bsec-h" style="margin-top:18px"><h3>Month by month</h3><span class="aside">${rto === 'PJM' ? 'Dashed lines: new PJM capacity prices take effect each June 1' : 'Monthly revenue ÷ sales, EIA-861M'}</span></div><div id="r-month"></div>` : ''}
      ${ann.some((r) => r[5]) ? '<p class="note">Your area has retail choice. The price combines delivery charges with an estimated average energy charge.</p>' : ''}
      ${pctile != null ? `<div class="bsec-h" style="margin-top:22px"><h3>Compared with every US utility</h3><span class="aside">Change since 2020 after inflation · dot size = homes served</span></div>
      <p class="lead">${above ? `The increase after inflation (<b class="up">${fmt.pct(u.ch, 0)}</b>) is bigger than what <b>${Math.round(pctile)}%</b> of American homes saw.` : `The change after inflation (<b class="${signClass(u.ch)}">${fmt.pct(u.ch, 0)}</b>) is better than what <b>${Math.round(100 - pctile)}%</b> of American homes saw.`}</p>
      <div id="r-strip"></div>` : ''}
    </section>

    ${locked ? `<section class="bsec" aria-labelledby="h-lock">
      <div class="bsec-h"><h3 id="h-lock">Already decided: your next bills</h3><span class="aside">PJM capacity charge per month · each bar runs June to May</span></div>
      <p class="lead">PJM sets capacity prices at auctions held up to three years ahead, so this part of your bill is <b>locked in through May ${locked[locked.length - 1].end.getFullYear()}</b>: about <b class="up">${fmt.usd(locked[locked.length - 1].v)} a month</b>, up from about ${fmt.usd(locked[0].v)} in ${locked[0].label}.</p>
      <div id="r-lock"></div>
      <p class="note">Estimate: PJM's total capacity cost per year ÷ PJM's total energy use (≈1.96¢/kWh in 2026, LBNL), times this utility's average usage of ${fmt.int(latest[4])} kWh a month. Homes that use more power at peak usually pay more, and some zones (BGE, Dominion) paid more in 2025–26. PJM's market monitor attributes ${fmt.big(IMM['2025/26'])}, ${fmt.big(IMM['2026/27'])}, ${fmt.big(IMM['2027/28'])} and ${fmt.big(IMM['2028/29'])} of these four auctions to data-center load (<a href="${IMM_URL}" target="_blank" rel="noopener">source</a>).</p>
    </section>` : ''}

    <section class="bsec" aria-labelledby="h-items">
      <div class="bsec-h"><h3 id="h-items">Where your dollar goes</h3><span class="aside">${anatomy ? '<span class="badge ok">real tariff</span>' : '<span class="badge warn">estimate</span>'} hover a stream to see who gets paid</span></div>
      <div id="r-flow"></div>
      <p class="fig-title" style="margin:18px 0 4px">The receipt: a typical 1,000 kWh month</p>
      <div class="lines">
        ${items.map((i) => `<div class="line"><span class="sw" style="background:${(CAT[i.cat] || {}).c || C.base}"></span><span class="lb"><span class="t">${esc(i.label)}</span></span><span class="amt">${fmt.usd(i.usd, 2)}</span><span class="pct">${i.pct != null ? `${i.pct.toFixed(0)}%` : ''}</span></div>`).join('')}
        <div class="line total"><span></span><span class="lb">Total at 1,000 kWh</span><span class="amt">${fmt.usd(itemsTotal, 2)}</span><span class="pct"></span></div>
      </div>
      <p class="note">${itemsNote}${anatomy && !itemsVerified ? ' <span class="badge warn">some lines unverified</span>' : ''}</p>
    </section>

    <section class="bsec" aria-labelledby="h-grid">
      <div class="bsec-h"><h3 id="h-grid">Data centers near you</h3><span class="aside">${esc(rinfo.long)}</span></div>
      <div class="grid2">
        <div>
          <p class="lead">${gridLead(rto, share, stName, inside.length, camps.length)}</p>
          <div class="msgs" style="margin-top:14px">
            <div class="msg"><div class="k">Data centers in ${esc(stName)}</div><div class="v">${share ? `${share.pct.toFixed(1)}%` : '—'}</div><div class="s">${share ? `of the state's electricity in 2023 (EPRI). US: ${usShare ? usShare.pct.toFixed(1) : '4.4'}%.` : 'No significant data-center load in EPRI\'s 2023 estimate.'}</div></div>
            ${disc ? `<div class="msg"><div class="k">Your utility says</div><div class="v">${disc.v}${disc.unit === 'pct' ? '%' : ''}</div><div class="s">${esc(disc.q)} <a href="${safeUrl(disc.url)}" target="_blank" rel="noopener">${esc(disc.per)} filing</a></div></div>` : ''}
            ${nitsRatio ? `<div class="msg"><div class="k">Transmission rate, zone ${esc(zone)}</div><div class="v">${nitsRatio.x.toFixed(1)}×</div><div class="s">its 2015 level (PJM network transmission rate, ${nitsRatio.y}).</div></div>` : ''}
            ${biggest ? `<div class="msg"><div class="k">Biggest campus planned in ${esc(stName)}</div><div class="v">${bigHomes >= 1e6 ? `${(bigHomes / 1e6).toFixed(1)}M` : `${Math.round(bigHomes / 1000)}K`} homes</div><div class="s">At full power, ${esc(biggest.n)} (${fmt.mw(biggest.mw)}) would draw as much electricity as about ${fmt.int(Math.round(bigHomes / 1000) * 1000)} average homes${ratio ? `, ${ratio >= 1.1 ? `<b>${ratio.toFixed(1)}×</b> every home in ${esc(stName)}` : `<b>${Math.round(ratio * 100)}%</b> of all homes in ${esc(stName)}`}` : ''}.</div></div>` : ''}
          </div>
          ${share && st2023 && st2023[5] ? `<div style="margin-top:16px"><p class="fig-title" style="margin:0 0 6px">Data centers vs. every home in ${esc(stName)}, 2023</p>${barList([{ label: 'Data centers', value: share.twh, color: C.s[1] }, { label: `All ${fmt.int(st2023[4])} homes`, value: st2023[5] / 1e6, color: C.s[0] }], { fmt: (v) => `${v.toFixed(1)} TWh` })}<p class="note">Data centers used <b>${Math.round((share.twh / (st2023[5] / 1e6)) * 100)}%</b> as much electricity as all homes in the state combined. EPRI (data centers), EIA-861 (homes). An average home draws about ${homeKw.toFixed(1)} kW around the clock.</p></div>` : ''}
        </div>
        <div>
          ${feature ? `<div id="r-map" aria-label="Map of your utility's territory and data centers"></div><p class="note">Blue: ${esc(shortName(u.n))}'s territory. Orange dots: data-center campuses we track (${inside.length} inside, ${camps.length - inside.length} elsewhere in ${esc(stName)}). Size: planned power.</p>` : ''}
          ${camps.length ? `<div class="cases" style="margin-top:8px">${camps.sort((a, b) => b.inside - a.inside || (b.mw || 0) - (a.mw || 0)).slice(0, 4).map((c) => `<div class="case"><div><div class="c1">${esc(c.n)}</div><div class="c2">${esc(c.u || '')} · ${esc(c.s)}${c.inside ? ' · in your territory' : ''}</div></div><div class="amt">${c.mw ? fmt.mw(c.mw) : ''}</div></div>`).join('')}</div>` : ''}
        </div>
      </div>
    </section>

    <section class="bsec" aria-labelledby="h-verdict">
      <div class="bsec-h"><h3 id="h-verdict">How sure is this?</h3><span class="aside">Evidence on both sides, for your grid</span></div>
      <div class="verdict">${meter(verdict.v, verdict.h)}<div><h4>${esc(verdict.h)}</h4><p>${esc(verdict.p)}</p></div></div>
      <div class="sides">
        <div class="side raise"><h5>The case it's raising bills</h5><ul>${verdict.raise.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>
        <div class="side lower"><h5>The case it isn't (yet)</h5><ul>${verdict.lower.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>
      </div>
    </section>

    <section class="bsec" aria-labelledby="h-pays">
      <div class="bsec-h"><h3 id="h-pays">Who pays in ${esc(stName)}</h3>${policy && policy.v === false ? '<span class="badge warn">partly verified</span>' : ''}</div>
      <div class="grid2">
        <dl class="kv">
          <dt>Large-load tariff</dt><dd>${policy ? tariffText(policy.llt) : '—'}</dd>
          <dt>Data-center tax break</dt><dd>${policy ? incentiveText(policy.inc) : '—'}</dd>
          ${policy && policy.laws.length ? `<dt>2025–26 laws</dt><dd>${policy.laws.slice(0, 2).map((l) => `<div>${l.url ? `<a href="${safeUrl(l.url)}" target="_blank" rel="noopener">${esc(l.bill)}</a>` : esc(l.bill)}: ${esc(l.sum)} <span class="note">(${esc(l.status || '')})</span></div>`).join('')}</dd>` : ''}
        </dl>
        <div>
          ${cases.length ? `<div class="cases">${cases.map((c) => `<div class="case"><div><div class="c1">${esc(c.utility)}${c.mine ? ' <span class="badge pjm">your utility</span>' : ''}</div><div class="c2">${esc(c.status || '')}${c.docket ? ` · docket ${esc(c.docket)}` : ''}${c.filed_date ? ` · filed ${esc(c.filed_date)}` : ''}</div></div><div class="amt">${c.requested_increase_usd ? `${fmt.big(c.requested_increase_usd)} asked` : ''}${c.approved_increase_usd ? `<div class="c2">${fmt.big(c.approved_increase_usd)} approved</div>` : ''}</div></div>`).join('')}</div><p class="note">Recent and open rate cases in ${esc(stName)}.</p>` : `<p class="note">No large rate case tracked for ${esc(stName)} in 2025–26.</p>`}
        </div>
      </div>
    </section>

    ${county || shut ? `<section class="bsec" aria-labelledby="h-hurt">
      <div class="bsec-h"><h3 id="h-hurt">Who feels it most</h3><span class="aside">DOE LEAD energy burden · EIA-112 shutoffs (2024)</span></div>
      <div class="msgs">
        ${county ? `<div class="msg"><div class="k">${esc(county[0])}: average home</div><div class="v">${county[2]?.toFixed(1)}%</div><div class="s">of income goes to energy bills</div></div><div class="msg"><div class="k">Low-income homes</div><div class="v up">${county[3]?.toFixed(1)}%</div><div class="s">${county[6] ? `${county[6].toFixed(0)}% of households here are low-income (≤80% of area median income)` : ''}</div></div>` : ''}
        ${shut ? `<div class="msg"><div class="k">Shutoffs at ${esc(shortName(u.n))}</div><div class="v">${shut[0].toFixed(1)}</div><div class="s">per 100 homes in 2024 (${fmt.int(shut[1])} disconnections). National: ${hh.shutNational.per100.toFixed(1)}.</div></div>` : ''}
      </div>
    </section>` : ''}

    <section class="bsec" aria-labelledby="h-act">
      <div class="bsec-h"><h3 id="h-act">What you can do</h3></div>
      <p class="lead">Rates are set in public proceedings, and your comments go on the record.</p>
      <div class="cta">
        ${policy?.adv?.url ? `<a class="btn" href="${safeUrl(policy.adv.url)}" target="_blank" rel="noopener">Contact your consumer advocate</a>` : '<span class="note">' + esc(stName) + ' has no official residential utility advocate.</span>'}
        ${policy?.puc?.url ? `<a class="btn ghost" href="${safeUrl(policy.puc.url)}" target="_blank" rel="noopener">${esc(policy.puc.name || 'Public utility commission')}</a>` : ''}
        ${nomCh != null ? '<button class="btn ghost" id="share-card2" type="button">Make my bill card</button>' : ''}
        <button class="btn ghost" id="copy-link">Copy link to this bill</button>
        <a class="btn ghost" target="_blank" rel="noopener" href="https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(share_url)}">Share on LinkedIn</a>
      </div>
    </section>
    <footer class="bill-foot"><span>Data: EIA-861 / 861M, PJM & Monitoring Analytics, EPRI, DOE LEAD, EIA-112, state PUCs. Prices are revenue ÷ sales averages, so your own bill varies.</span><span>Your address stays in your browser; only the geocoder sees it.</span></footer>
  </article>`;

  // charts
  const infl = first && cpiY[first[0]] ? ann.map((r) => [r[0], cpiY[r[0]] ? +(first[1] * (cpiY[r[0]] / cpiY[first[0]])).toFixed(2) : null]) : [];
  const yrs = new Set(ann.map((r) => r[0]));
  lineChart($('#r-hist', host), {
    label: 'Price history', yFmt: (v) => `${(+v).toFixed(0)}¢`,
    series: [
      { key: 'u', label: shortName(u.n), color: C.s[0], width: 3, emph: true, values: ann.map((r) => [r[0], r[1]]) },
      { key: 's', label: `${st} avg`, color: C.muted, values: stA.filter((r) => yrs.has(r[0])).map((r) => [r[0], r[1]]) },
      { key: 'us', label: 'US avg', color: C.ink, dash: '5 4', width: 1.5, values: usA.filter((r) => yrs.has(r[0])).map((r) => [r[0], r[1]]) },
      { key: 'i', label: 'Inflation path', color: C.base, dash: '2 4', width: 2, values: infl },
    ],
  });
  if (u.mo && u.mo.length > 6) {
    lineChart($('#r-month', host), {
      label: 'Monthly price', height: 220, yFmt: (v) => `${(+v).toFixed(0)}¢`, area: true,
      series: [{ key: 'm', label: shortName(u.n), color: C.s[0], width: 2.5, emph: true, values: u.mo.map((r) => [r[0], r[1]]) }],
      markers: rto === 'PJM' ? [{ x: '2025-06', label: 'Jun 2025' }, { x: '2026-06', label: 'Jun 2026' }].filter((mk) => u.mo.some((r) => r[0] === mk.x)) : [],
    });
  }
  if (rto === 'PJM' && cap.length && $('#r-cap', host)) {
    columns($('#r-cap', host), {
      label: 'Capacity price', height: 240, yFmt: (v) => `$${v}`,
      data: cap.filter((c) => c.dy >= '2018/19').map((c) => ({
        x: c.dy.replace('20', '').replace('/', '–'), y: c.p, color: c.dy >= '2025/26' ? C.up : C.base,
        ghost: c.dy === '2028/29' && c.lda === 'RTO' ? UNCAPPED_2829 : null,
        tip: `<b>${c.dy}</b><div>${fmt.usd(c.p, 2)} per MW-day (${esc(c.lda)})</div>${IMM[c.dy] ? `<div class="m">Data-center share per market monitor: ${fmt.big(IMM[c.dy])}</div>` : ''}${c.dy === '2028/29' ? `<div class="m">Uncapped it would have been $${UNCAPPED_2829}</div>` : ''}`,
      })),
    });
  }
  if (feature) territoryMap($('#r-map', host), { feature, states: stateFeature, campuses: camps, label: 'Territory map' });
  if (pctile != null) strip($('#r-strip', host), { label: 'You vs America', median: medianCh, mine: { v: u.ch, label: shortName(u.n) }, points: pool.map((e) => ({ v: e.ch, c: e.c, n: shortName(e.n), st: e.st, k: `${e.id}-${e.st}` })) });
  if (wf) waterfall($('#r-wf', host), { steps: wf.steps, label: 'Where the bill change came from' });
  dollarFlow($('#r-flow', host), {
    label: 'Follow your dollar', coinSub: 'your bill dollar', height: 300,
    parts: stackCats.filter(([, v]) => v > 0).map(([k, v]) => ({ key: k, label: (CAT[k] || {}).label || k, who: WHO[k], share: v, color: (CAT[k] || {}).c || C.base, note: `${fmt.usd(v, 2)} of a 1,000 kWh bill` })),
  });
  if (locked) stepTimeline($('#r-lock', host), { periods: locked, today: new Date(), label: 'Capacity charge by delivery year' });
  const shareData = {
    nominal: nomCh, utility: shortName(u.n), stateName: stName, homes: fmt.int(u.c),
    series: ann.map((r) => [r[0], r[1]]), us: usA.map((r) => [r[0], r[1]]),
    stats: [
      dcx ? { v: dcx.usd < 1 ? '<$1/mo' : `≈$${Math.round(dcx.usd)}/mo`, k: dcx.est ? 'of a typical bill may trace to data-center demand (estimate)' : 'of a typical bill traces to data-center demand (PJM)', color: C.upText } : null,
      u.ytd != null ? { v: fmt.pct(u.ytd, 1), k: '2026 so far, vs the same months of 2025', color: u.ytd > 0 ? C.upText : C.downText } : { v: fmt.pct(u.ch, 0), k: 'after inflation, since 2020' },
      pctile != null ? (above ? { v: `${Math.round(pctile)}%`, k: 'of US homes saw a smaller increase' } : { v: `${Math.round(100 - pctile)}%`, k: 'of US homes saw a bigger increase' }) : null,
      locked ? { v: `$${Math.round(locked[locked.length - 1].v)}/mo`, k: `capacity charge locked in through May ${locked[locked.length - 1].end.getFullYear()}` } : { v: fmt.pct(u.ch, 0), k: 'after inflation, since 2020' },
    ].filter(Boolean),
    url: (location.host + location.pathname).replace(/\/$/, ''), link: share_url, slug: `${u.id}-${u.st}`.toLowerCase(),
    caption: `My power bill is up ${Math.round(nomCh)}% since 2020. I looked into why, including how much of it traces back to data centers.`,
  };
  ['#share-card', '#share-card2'].forEach((sel) => $(sel, host)?.addEventListener('click', () => openShare(shareData)));
  host.querySelectorAll('.circled').forEach(circleIt);

  host.querySelectorAll('.switch button').forEach((b) => b.addEventListener('click', () => onSwitch?.(others[+b.dataset.i])));
  $('#copy-link', host)?.addEventListener('click', async (e) => {
    try { await navigator.clipboard.writeText(share_url); e.target.textContent = 'Link copied ✓'; } catch { prompt('Copy this link', share_url); }
  });
  detailTabs(host);
  history.replaceState(null, '', `?u=${u.id}-${u.st}${location.hash}`);
}

// Keep the answer on top; tuck the detail sections into tabs (charts redraw at full width when a tab opens).
const TABS = [['why', 'Why it went up', ['h-wf']], ['time', 'Past & next', ['h-lock', 'h-hist']], ['dollar', 'Your dollar', ['h-items']], ['near', 'Data centers near you', ['h-grid', 'h-verdict']], ['pays', 'Who pays', ['h-pays', 'h-hurt']], ['act', 'What you can do', ['h-act']]];
function detailTabs(host) {
  const first = host.querySelector('section.bsec');
  const tabs = TABS.map(([k, label, ids]) => [k, label, ids.map((id) => host.querySelector(`section[aria-labelledby="${id}"]`)).filter(Boolean)]).filter(([, , els]) => els.length);
  if (!first || !tabs.length) return;
  const bar = document.createElement('div');
  bar.className = 'rtabs'; bar.setAttribute('role', 'tablist'); bar.setAttribute('aria-label', 'Bill details');
  bar.innerHTML = `<span class="rtabs-k">The details</span>${tabs.map(([k, label], i) => `<button role="tab" type="button" aria-selected="${i === 0}" data-k="${k}">${label}</button>`).join('')}`;
  first.before(bar);
  let anchor = bar;
  tabs.forEach(([k, , els]) => els.forEach((el) => { el.dataset.tab = k; el.setAttribute('role', 'tabpanel'); anchor.after(el); anchor = el; }));
  const show = (k) => {
    bar.querySelectorAll('button').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.k === k)));
    tabs.forEach(([kk, , els]) => els.forEach((el) => { el.hidden = kk !== k; }));
    dispatchEvent(new Event('resize'));
  };
  bar.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) show(b.dataset.k); });
  show(tabs[0][0]);
}

export const shortName = (n) => String(n).replace(/\s*-\s*\([A-Z]{2}\)\s*$/, '').replace(/\b(Co|Company|Inc|Corp|Corporation|LLC)\.?$/i, '').replace(/\s+/g, ' ').trim();

function historyLead(u, latest, first, cpiY, usCh) {
  const ch = u.chn;
  const real = u.ch;
  const name = esc(shortName(u.n));
  if (ch == null) return `${name}'s residential price averaged <b>${fmt.cents(latest[1], 1)}/kWh</b> in ${latest[0]}.`;
  const faster = usCh != null && ch > usCh + 3 ? 'faster than' : usCh != null && ch < usCh - 3 ? 'slower than' : 'about in line with';
  return `Since 2020, ${name}'s price is <b class="${signClass(ch)}">${fmt.pct(ch, 0)}</b>, ${faster} the US average (${fmt.pct(usCh, 0)}). After inflation, that's <b class="${signClass(real)}">${fmt.pct(real, 0)}</b>.`;
}
function gridLead(rto, share, stName, inside, total) {
  const pre = rto === 'none' ? 'Your utility isn\'t part of a regional market, so new demand reaches your bill through state rate cases.' : `Your utility is part of ${esc((RTO_INFO[rto] || {}).long || rto)}.`;
  const dc = total ? ` We track <b>${total}</b> data-center campuses in ${esc(stName)}${inside ? `, ${inside} inside your utility's territory` : ''}.` : '';
  return pre + dc;
}
function tariffText(l) {
  if (!l || !l.status) return '—';
  const s = { adopted: '<span class="badge ok">Adopted</span>', proposed: '<span class="badge warn">Proposed</span>', none: '<span class="badge">None</span>' }[l.status] || esc(l.status);
  const t = l.terms || {};
  const bits = [t.eligibility_threshold, t.minimum_demand_or_take_or_pay, t.contract_years && `contracts: ${t.contract_years}`].filter(Boolean).map((x) => esc(String(x))).slice(0, 2);
  return `${s} ${l.utilities && l.utilities.length ? esc(l.utilities.slice(0, 2).join(', ')) : ''}${bits.length ? `<div class="note">${bits.join(' · ')}</div>` : ''}${l.url ? ` <a class="note" href="${safeUrl(l.url)}" target="_blank" rel="noopener">source</a>` : ''}`;
}
function incentiveText(i) {
  if (!i || !i.type) return '—';
  return `${esc(i.type)}${i.cost ? ` · <b>≈${fmt.big(i.cost)}/yr</b>${i.costYear ? ` (${esc(i.costYear)})` : ''}` : ''}${i.status ? `<div class="note">${esc(i.status)}</div>` : ''}`;
}
