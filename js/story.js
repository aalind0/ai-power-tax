// The national story: chapters below the lookup.
/* global d3, topojson */
import { $, $$, esc, safeUrl, fmt, signClass, C, DIV, D, STATE_NAMES, showTip, hideTip, rewind, circleIt } from './util.js';
import { lineChart, columns, stacked, barList, dollarFlow } from './charts.js';
import { CAT } from './util.js';
import { IMM, IMM_URL, shortName, billWaterfall, dcShareOfBill, lockedCapacity } from './report.js';

// ---------------------------------------------------------------- hero: a live sample bill cycling through real cities
const SAMPLES = [['1167-MD', 'Baltimore, MD'], ['19876-VA', 'Ashburn, VA'], ['14940-PA', 'Philadelphia, PA'], ['4110-IL', 'Chicago, IL'], ['14006-OH', 'Columbus, OH'], ['15270-DC', 'Washington, DC']];
export async function heroSample(onOpen) {
  const el = $('#sample');
  const [index, grid] = await Promise.all([D.index(), D.grid()]);
  const cards = (await Promise.all(SAMPLES.map(async ([key, city]) => {
    const [id, st] = key.split('-');
    const entry = index.find((e) => e.id === +id && e.st === st);
    if (!entry) return null;
    const u = (await D.state(st)).find((x) => x.id === +id);
    if (!u || !u.a?.length) return null;
    const latest = u.a[u.a.length - 1];
    const wf = billWaterfall(u.a, grid, u.r, u.ytd);
    const dc = dcShareOfBill(u.r, latest, wf, u.ytd);
    const lock = u.r === 'PJM' ? lockedCapacity(grid, latest[4] || 900) : null;
    return dc ? { entry, u, city, dc, lock, series: u.a.map((r) => [r[0], r[1]]) } : null;
  }))).filter(Boolean);
  if (!cards.length) { el.hidden = true; return; }
  const spark = (s) => {
    const xs = s.map((r) => r[0]), ys = s.map((r) => r[1]);
    const x = d3.scaleLinear().domain(d3.extent(xs)).range([2, 238]), y = d3.scaleLinear().domain(d3.extent(ys)).range([46, 4]);
    const line = d3.line().x((r) => x(r[0])).y((r) => y(r[1])).curve(d3.curveMonotoneX)(s);
    const last = s[s.length - 1];
    return `<svg viewBox="0 0 240 50" class="sample-spark" aria-hidden="true"><path d="${line} L238,50 L2,50 Z" fill="rgba(42,120,214,0.10)"/><path d="${line}" fill="none" stroke="${C.s[0]}" stroke-width="2.4" stroke-linecap="round"/><circle cx="${x(last[0])}" cy="${y(last[1])}" r="3.6" fill="${C.s[0]}"/></svg>`;
  };
  let i = 0, timer;
  const render = () => {
    const c = cards[i];
    el.innerHTML = `
      <button class="sample-card" type="button" aria-label="Open the ${esc(c.city)} bill">
        <div class="sample-top"><span>Sample statement</span><span class="dots">${cards.map((_, k) => `<i class="${k === i ? 'on' : ''}"></i>`).join('')}</span></div>
        <div class="sample-city">${esc(c.city)}</div>
        <div class="sample-ut">${esc(shortName(c.u.n))}</div>
        <div class="sample-rows">
          <div class="sr"><span>Bill since 2020</span><b class="up">${fmt.pct(c.u.chn, 0)}</b></div>
          <div class="sr sr-dc"><span>Data centers' share</span><b><span class="circled">≈${fmt.usd(c.dc.usd)}<small>/mo</small></span></b></div>
          ${c.lock ? `<div class="sr"><span>Locked in through 2029</span><b>${fmt.usd(c.lock[c.lock.length - 1].v)}<small>/mo</small></b></div>` : ''}
        </div>
        ${spark(c.series)}
        <div class="sample-cta">See this bill →</div>
      </button>`;
    $('.sample-card', el).addEventListener('click', () => onOpen(c.entry));
    el.querySelectorAll('.circled').forEach(circleIt);
  };
  const next = () => { i = (i + 1) % cards.length; el.classList.add('swap'); setTimeout(() => { render(); el.classList.remove('swap'); }, 260); };
  render();
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce && cards.length > 1) {
    const start = () => { clearInterval(timer); timer = setInterval(next, 5200); };
    start();
    el.addEventListener('mouseenter', () => clearInterval(timer));
    el.addEventListener('mouseleave', start);
  }
}

const ttm = (prices) => {
  const m = prices.usMonthly;
  if (m.length < 24) return null;
  const last12 = m.slice(-12), prev12 = m.slice(-24, -12);
  const el = (d3.mean(last12, (r) => r[1]) / d3.mean(prev12, (r) => r[1]) - 1) * 100;
  // same method for both: average of the latest 12 months vs the 12 before, ending in the same month
  const lastMonth = m[m.length - 1][0];
  const cpi = prices.cpi.filter((r) => r[1] && r[0] <= lastMonth);
  const c12 = d3.mean(cpi.slice(-12), (r) => r[1]), cPrev = d3.mean(cpi.slice(-24, -12), (r) => r[1]);
  return { el, cpi: (c12 / cPrev - 1) * 100, month: lastMonth };
};

// ---------------------------------------------------------------- hero
export async function heroStats() {
  const [prices, hh] = await Promise.all([D.prices(), D.households()]);
  const t = ttm(prices);
  $('#updated').textContent = `Data through ${fmt.month(prices.latestMonth)}`;
  $('#hero-stats').innerHTML = `
    <div class="hstat"><div class="v up">${fmt.pct(t.el, 1)}</div><div class="k">US home electricity prices, last 12 months. All prices rose ${fmt.pct(t.cpi, 1)}.</div><div class="src">EIA-861M, BLS CPI · through ${fmt.month(t.month)}</div></div>
    <div class="hstat"><div class="v">${fmt.big(Object.values(IMM).reduce((a, b) => a + b, 0))}</div><div class="k">of PJM capacity costs the grid's market monitor attributes to data-center demand, across 4 auctions.</div><div class="src">Monitoring Analytics, Oct 2026</div></div>
    <div class="hstat"><div class="v">${(hh.shutNational.disc / 1e6).toFixed(1)}M</div><div class="k">homes had their power shut off for unpaid bills in 2024, the first year the federal government counted.</div><div class="src">EIA-112, 2024</div></div>`;
}

// ---------------------------------------------------------------- hero: follow the dollar
export async function heroFlow() {
  const grid = await D.grid();
  const aeo = [...grid.td].reverse().find((r) => r.g && r.tc && r.dc);
  const a13 = grid.td.find((r) => r.y === 2013 && r.tc);
  const comp = (per) => grid.components.find((c) => c.per === per);
  const c24 = comp('2024'), c26 = comp('2026 Jan-Sep') || comp('2025');
  const wholesale = (c) => [
    { key: 'e', label: 'Energy: fuel & running plants', who: 'Power plant owners & fuel suppliers', share: c.e, color: CAT.supply.c },
    { key: 'c', label: 'Capacity: paying plants to stand by', who: 'Power plant owners (Constellation, Vistra, Talen…)', share: c.c, color: CAT.capacity.c, note: 'Set by PJM\'s auction three years ahead' },
    { key: 't', label: 'Transmission: high-voltage lines', who: 'Utilities\' transmission businesses', share: c.t, color: CAT.transmission.c },
    { key: 'o', label: 'Other grid services', who: 'Reserves, congestion & grid operation', share: Math.max(0.5, c.tot - c.e - c.c - c.t), color: C.base },
  ];
  const cents = (c, k) => Math.round((c[k] / c.tot) * 100);
  const views = {
    us: {
      title: 'Where every $1 of the average US power bill goes', coinSub: `average US bill, ${aeo.y}`,
      parts: [
        { key: 'g', label: 'Making the power', who: 'Power plants & fuel suppliers', share: aeo.g, color: CAT.supply.c, note: 'Generation, including payments to keep plants available (EIA)' },
        { key: 't', label: 'Long-distance lines', who: 'High-voltage transmission owners', share: aeo.tc, color: CAT.transmission.c },
        { key: 'd', label: 'Local delivery', who: 'Your utility: poles, wires, meters, storms', share: aeo.dc, color: CAT.distribution.c },
      ],
      insight: `Transmission's slice has roughly doubled since ${a13 ? 2013 : 'a decade ago'}, from ${a13 ? a13.tc.toFixed(2) : '0.9'}¢ to <b>${aeo.tc.toFixed(2)}¢</b> per kWh. Source: EIA, average across all customers.`,
    },
    pjm24: {
      title: 'Where every $1 of PJM wholesale power went in 2024', coinSub: 'PJM wholesale, 2024', parts: wholesale(c24),
      insight: `In 2024, paying power plants to stand by took just <b>${cents(c24, 'c')}¢</b> of every wholesale dollar, and power cost <b>$${c24.tot.toFixed(0)}</b> per MWh in total. Now switch to 2026.`,
    },
    pjm26: {
      title: 'Where every $1 of PJM wholesale power goes in 2026', coinSub: 'PJM wholesale, 2026', parts: wholesale(c26),
      insight: `The standby slice grew to <b>${cents(c26, 'c')}¢</b> of each dollar, and the dollar itself got bigger: <b>$${c26.tot.toFixed(0)}</b> per MWh, up from $${c24.tot.toFixed(0)} in 2024. Most of that standby jump traces to data-center demand (see chapter 04). Source: Monitoring Analytics, Jan–Sep 2026.`,
    },
  };
  let n = 0;
  const show = (v) => {
    const view = views[v];
    $('#hf-title').textContent = view.title;
    $('#hf-insight').innerHTML = view.insight;
    $('#hero-flow').innerHTML = `<div id="hflow-${++n}"></div>`;
    dollarFlow($(`#hflow-${n}`), { parts: view.parts, coinSub: view.coinSub, label: view.title, height: innerWidth < 600 ? 260 : 300 });
  };
  $$('#hf-toggle button').forEach((b) => b.addEventListener('click', () => {
    $$('#hf-toggle button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    show(b.dataset.v);
  }));
  show('us');
}

// ---------------------------------------------------------------- 02 life of a kilowatt-hour (scroll-driven)
export async function chKwh() {
  const [grid, prices, anat] = await Promise.all([D.grid(), D.prices(), D.anatomy()]);
  const aeo = [...grid.td].reverse().find((r) => r.g && r.tc && r.dc);
  const res = prices.us.find((r) => r[0] === aeo.y) || prices.us[prices.us.length - 1];
  const capC = anat.pjm?.pjm_capacity_cost_cents_per_kwh_all_load || {};
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  $('#kwh-intro').innerHTML = `<p>Every kilowatt-hour you use is made, held in reserve, carried hundreds of miles and delivered down your street, and each step adds to the price. Scroll to follow one from the power plant to your home, and see where data centers plug in.</p>`;
  const steps = [
    { at: 'plant', tag: `${aeo.g.toFixed(1)}¢`, total: aeo.g, h: 'Make it', p: `A power plant burns gas, splits atoms or catches sun and wind. Making the power is the biggest part of the price: about <b>${aeo.g.toFixed(1)}¢</b> of an average <b>${aeo.all.toFixed(1)}¢</b> kWh across all US customers. Fuel prices swing it most: PJM's wholesale energy cost jumped sharply in 2026 with natural gas.` },
    { at: 'plant', tag: '≈2¢ standby', total: aeo.g, badge: true, h: 'Keep it on standby', p: `Grids also pay plants just to be <i>available</i> on the hottest day: that's <b>capacity</b>. In PJM it rose from <b>${capC['2024'] ?? 0.36}¢</b> per kWh in 2024 to about <b>${capC['2026_est'] ?? 1.96}¢</b> in 2026, already part of the cost of making power. The auction for it is held three years ahead.` },
    { at: 'lines', tag: `+${aeo.tc.toFixed(1)}¢`, total: aeo.g + aeo.tc, h: 'Move it long-distance', p: `High-voltage lines carry it across the region. That adds about <b>${aeo.tc.toFixed(1)}¢</b>, roughly double the 2013 figure, as utilities spend record sums on new lines.` },
    { at: 'dc', tag: 'data centers', total: aeo.g + aeo.tc, dc: true, h: 'Where data centers plug in', p: `A hyperscale campus taps the high-voltage grid directly and can draw as much as a city. Its demand ripples back up the line: PJM's market monitor attributes <b>$29.4B</b> of capacity costs over four auctions to data-center load, and PJM says about <b>$23B</b> of new regional lines are driven mainly by data centers. Everyone on the grid shares those costs.` },
    { at: 'street', tag: `+${aeo.dc.toFixed(1)}¢`, total: aeo.all, h: 'Deliver it to your street', p: `Substations step the voltage down and poles and wires bring it to your block: about <b>${aeo.dc.toFixed(1)}¢</b>. This part is set in your utility's own rate case, and it's where storm repairs and new meters show up.` },
    { at: 'home', tag: `${res[1].toFixed(1)}¢ at home`, total: res[1], home: true, h: 'Arrive at your home', p: `Across all customers the average kWh costs about <b>${aeo.all.toFixed(1)}¢</b>. Homes paid more, about <b>${res[1].toFixed(1)}¢</b> in ${res[0]}, because more of the wires cost falls on households than on factories.` },
  ];
  $('#kwh-steps').innerHTML = steps.map((s, i) => `<div class="kwh-step" data-i="${i}"><p class="kwh-n">Step ${i + 1} of ${steps.length}</p><h3>${s.h}</h3><p>${s.p}</p></div>`).join('');

  // ---- the scene (viewBox units)
  const W = 1000, H = 440, G = 360;
  const X = { plant: 110, lines: 400, dc: 430, street: 760, home: 905 };
  const svg = d3.select('#kwh-fig').append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img').attr('aria-label', 'Journey of a kilowatt-hour');
  const defs = svg.append('defs');
  const gl = defs.append('filter').attr('id', 'kglow').attr('x', '-100%').attr('y', '-100%').attr('width', '300%').attr('height', '300%');
  gl.append('feGaussianBlur').attr('stdDeviation', 4).attr('result', 'b');
  const fm = gl.append('feMerge'); fm.append('feMergeNode').attr('in', 'b'); fm.append('feMergeNode').attr('in', 'SourceGraphic');
  svg.append('rect').attr('width', W).attr('height', H).attr('rx', 18).attr('fill', C.surface);
  svg.append('line').attr('x1', 20).attr('x2', W - 20).attr('y1', G).attr('y2', G).attr('stroke', C.base).attr('stroke-width', 2);
  const ink = C.ink, stroke = (sel, w = 2.2) => sel.attr('stroke', ink).attr('stroke-width', w).attr('fill', 'none').attr('stroke-linejoin', 'round').attr('stroke-linecap', 'round');
  // plant
  const pl = svg.append('g').attr('class', 'k-plant');
  stroke(pl.append('path').attr('d', `M60 ${G} V280 H150 V${G}`));
  stroke(pl.append('path').attr('d', `M80 280 V215 H102 V280 M118 280 V235 H138 V280`));
  [0, 1, 2].forEach((k) => pl.append('circle').attr('class', reduce ? '' : 'smoke').style('animation-delay', `${k * 0.9}s`).attr('cx', 91 + k * 6).attr('cy', 200 - k * 16).attr('r', 7 + k * 3).attr('fill', '#3a3c42'));
  const badge = pl.append('g').attr('opacity', 0).attr('transform', 'translate(150,300)');
  badge.append('rect').attr('x', -4).attr('y', -16).attr('width', 92).attr('height', 24).attr('rx', 12).attr('fill', CAT.capacity.c);
  badge.append('text').attr('x', 42).attr('y', 0).attr('text-anchor', 'middle').attr('fill', C.onInk).attr('font-size', 12).attr('font-weight', 700).text('ON STANDBY');
  // towers
  const tower = (x) => { const g = svg.append('g'); stroke(g.append('path').attr('d', `M${x - 22} ${G} L${x} 150 L${x + 22} ${G} M${x - 14} 260 H${x + 14} M${x - 9} 210 H${x + 9} M${x - 30} 170 H${x + 30} M${x - 18} ${G} L${x + 9} 210 M${x + 18} ${G} L${x - 9} 210`), 1.8); };
  tower(300); tower(520);
  // substation + pole + house
  const sub = svg.append('g');
  stroke(sub.append('rect').attr('x', 640).attr('y', 300).attr('width', 70).attr('height', 60).attr('rx', 4));
  stroke(sub.append('path').attr('d', 'M652 300 V280 M675 300 V272 M698 300 V280'), 1.6);
  const pole = svg.append('g');
  stroke(pole.append('path').attr('d', `M800 ${G} V220 M780 232 H820`), 2.2);
  stroke(pole.append('rect').attr('x', 804).attr('y', 245).attr('width', 12).attr('height', 18).attr('rx', 3), 1.6);
  const home = svg.append('g');
  stroke(home.append('path').attr('d', `M870 ${G} V300 L905 270 L940 300 V${G} Z`));
  const win = home.append('rect').attr('x', 893).attr('y', 312).attr('width', 24).attr('height', 22).attr('rx', 3).attr('fill', '#2a2c31').attr('stroke', ink).attr('stroke-width', 1.6);
  // data center
  const dc = svg.append('g').attr('class', 'k-dc').attr('opacity', 0.35);
  dc.append('rect').attr('x', 360).attr('y', 300).attr('width', 140).attr('height', 60).attr('rx', 6).attr('fill', '#1c1c1a').attr('stroke', '#3a3c42');
  const leds = dc.append('g');
  for (let r = 0; r < 3; r++) for (let c = 0; c < 9; c++) leds.append('rect').attr('x', 372 + c * 14).attr('y', 312 + r * 13).attr('width', 8).attr('height', 4).attr('rx', 1).attr('fill', C.s[2]).attr('class', reduce ? '' : 'led').style('animation-delay', `${((r * 9 + c) % 7) * 0.21}s`);
  dc.append('text').attr('x', 430).attr('y', 384).attr('text-anchor', 'middle').attr('font-size', 13).attr('font-weight', 700).attr('fill', ink).text('AI data center campus');
  // the wire
  const wireD = `M150 250 Q225 205 300 170 Q410 215 520 170 Q600 230 675 272 Q740 236 800 232 Q860 252 905 282`;
  const wire = svg.append('path').attr('d', wireD).attr('fill', 'none').attr('stroke', C.ink2).attr('stroke-width', 2).attr('stroke-dasharray', '1 0');
  const tap = svg.append('path').attr('d', 'M410 192 L430 300').attr('stroke', C.s[1]).attr('stroke-width', 2.4).attr('stroke-dasharray', '5 4').attr('opacity', 0.25);
  const lit = svg.append('path').attr('d', wireD).attr('fill', 'none').attr('stroke', C.volt).attr('stroke-width', 4).attr('stroke-linecap', 'round').attr('filter', 'url(#kglow)');
  const L = wire.node().getTotalLength();
  lit.attr('stroke-dasharray', `0 ${L}`);
  const samples = d3.range(0, L + 1, 4).map((l) => ({ l, p: wire.node().getPointAtLength(l) }));
  const lenAtX = (x) => samples.reduce((a, b) => (Math.abs(b.p.x - x) < Math.abs(a.p.x - x) ? b : a)).l;
  const STOP = { plant: lenAtX(150), lines: lenAtX(520), dc: lenAtX(410), street: lenAtX(800), home: L };
  // spark + meter + tags
  const spark = svg.append('g').attr('filter', 'url(#kglow)');
  spark.append('circle').attr('r', 13).attr('fill', 'rgba(255,214,10,0.45)').attr('class', reduce ? '' : 'spark-halo');
  spark.append('circle').attr('r', 6.5).attr('fill', C.volt).attr('stroke', ink).attr('stroke-width', 1.2);
  const meter = svg.append('g').attr('transform', 'translate(34,40)');
  meter.append('rect').attr('width', 230).attr('height', 64).attr('rx', 12).attr('fill', '#08090b').attr('stroke', '#3a3c42');
  meter.append('text').attr('x', 16).attr('y', 24).attr('fill', '#b9b6ad').attr('font-size', 11.5).attr('font-family', 'JetBrains Mono, monospace').text('THIS KWH SO FAR');
  const meterV = meter.append('text').attr('x', 16).attr('y', 52).attr('fill', C.volt).attr('font-size', 26).attr('font-family', 'Instrument Serif, Georgia, serif').text('0.0¢');
  const tagG = svg.append('g');
  const tagPos = { plant: [105, 175], lines: [520, 120], dc: [430, 270], street: [760, 205], home: [905, 245] };
  const drawTag = (s, active) => {
    const [tx, ty] = tagPos[s.at];
    const g = tagG.append('g').attr('transform', `translate(${tx + (s.badge ? 70 : 0)},${ty - (s.badge ? 30 : 0)})`).attr('opacity', 0);
    const wTag = Math.max(54, s.tag.length * 8.4 + 18);
    g.append('rect').attr('x', -wTag / 2).attr('y', -16).attr('width', wTag).attr('height', 28).attr('rx', 14).attr('fill', active ? C.volt : C.surface).attr('stroke', active ? C.volt : C.ink2).attr('stroke-width', 1.4);
    g.append('text').attr('text-anchor', 'middle').attr('y', 3).attr('font-size', 13.5).attr('font-weight', 700).attr('fill', active ? C.onInk : C.ink).text(s.tag);
    g.transition().duration(reduce ? 0 : 450).attr('opacity', 1);
  };
  // feedback pulses from the data center back up the line
  let pulseTimer = null;
  const pulses = svg.append('g');
  const startPulses = () => {
    if (reduce || pulseTimer) return;
    const fire = () => {
      const c = pulses.append('circle').attr('r', 5).attr('fill', C.up).attr('filter', 'url(#kglow)');
      c.transition().duration(2200).ease(d3.easeLinear).attrTween('transform', () => (t) => { const p = wire.node().getPointAtLength(STOP.dc * (1 - t)); return `translate(${p.x},${p.y})`; }).on('end', () => c.remove());
    };
    fire();
    pulseTimer = setInterval(fire, 650);
  };
  const stopPulses = () => { clearInterval(pulseTimer); pulseTimer = null; pulses.selectAll('*').interrupt().remove(); };

  let cur = 0, curLen = 0, curTotal = 0;
  const go = (i) => {
    const s = steps[i];
    const target = STOP[s.at === 'dc' ? 'dc' : s.at];
    const from = curLen;
    const dur = reduce ? 0 : Math.min(1600, 300 + Math.abs(target - from) * 1.6);
    spark.interrupt().transition().duration(dur).ease(d3.easeCubicInOut).attrTween('transform', () => (t) => { const p = wire.node().getPointAtLength(from + (target - from) * t); return `translate(${p.x},${p.y})`; });
    lit.interrupt().transition().duration(dur).ease(d3.easeCubicInOut).attrTween('stroke-dasharray', () => (t) => `${from + (target - from) * t} ${L}`);
    const t0 = curTotal;
    meterV.interrupt().transition().duration(reduce ? 0 : 900).tween('text', () => (t) => meterV.text(`${(t0 + (s.total - t0) * t).toFixed(1)}¢`));
    curLen = target; curTotal = s.total;
    tagG.selectAll('*').remove();
    steps.slice(0, i + 1).forEach((st, k) => drawTag(st, k === i));
    badge.transition().duration(300).attr('opacity', i >= 1 ? 1 : 0);
    dc.transition().duration(400).attr('opacity', i >= 3 ? 1 : 0.35);
    tap.transition().duration(400).attr('opacity', i >= 3 ? 1 : 0.25);
    win.transition().duration(400).attr('fill', i === steps.length - 1 ? C.volt : '#2a2c31');
    if (i === 3) startPulses(); else stopPulses();
    $$('#kwh-steps .kwh-step').forEach((el) => el.classList.toggle('on', +el.dataset.i === i));
    cur = i;
  };
  spark.attr('transform', () => { const p = wire.node().getPointAtLength(0); return `translate(${p.x},${p.y})`; });
  go(0);
  const io = new IntersectionObserver((ents) => {
    ents.filter((e) => e.isIntersecting).forEach((e) => { const i = +e.target.dataset.i; if (i !== cur) go(i); });
  }, { rootMargin: '-45% 0px -45% 0px' });
  $$('#kwh-steps .kwh-step').forEach((el) => io.observe(el));
}

// ---------------------------------------------------------------- 01 calm
export async function chCalm() {
  const prices = await D.prices();
  const t = ttm(prices);
  const us = prices.us;
  const y15 = us.find((r) => r[0] === 2015), y25 = us.find((r) => r[0] === 2025);
  $('#calm-text').innerHTML = `
    <p>In 2025 the average American home paid <strong>${fmt.cents(y25[1], 2)}/kWh</strong>. After inflation that is <strong>${fmt.pct((y25[2] / y15[2] - 1) * 100, 1)}</strong> compared with 2015. A decade of roughly flat power.</p>
    <p>Then the last twelve months happened.</p>
    <span class="big up">${fmt.pct(t.el, 1)}</span>
    <p>That's the rise in residential prices over the 12 months to ${fmt.month(t.month)}, roughly double the ${fmt.pct(t.cpi, 1)} rise in everything else.</p>`;
  $('#calm-chart').innerHTML = `<p class="fig-title">US residential electricity price, ¢/kWh</p><p class="fig-sub">Nominal vs adjusted for inflation (2025 dollars)</p><div id="calm-c"></div><p class="fig-src">Source: EIA-861, BLS CPI-U</p>`;
  lineChart($('#calm-c'), {
    label: 'US residential price', yFmt: (v) => `${(+v).toFixed(0)}¢`, yMin: 10,
    series: [
      { key: 'n', label: 'Nominal', color: C.s[0], width: 3, emph: true, values: us.map((r) => [r[0], r[1]]) },
      { key: 'r', label: 'After inflation', color: C.ink, dash: '5 4', width: 1.8, values: us.map((r) => [r[0], r[2]]) },
    ],
  });
}

// ---------------------------------------------------------------- 02 map
let mapMode = 'real';
export async function chMap(onPick) {
  const [index, topo, statesTopo, prices] = await Promise.all([D.index(), D.territories(), D.usStates(), D.prices()]);
  const byId = new Map();
  index.forEach((e) => { const k = e.id; if (!byId.has(k) || byId.get(k).c < e.c) byId.set(k, e); });
  const xw = await D.crosswalk();
  const feats = topojson.feature(topo, topo.objects.territories).features;
  feats.forEach((f) => { rewind(f); f._e = byId.get(xw[String(f.properties.id)] || f.properties.id); f._a = d3.geoArea(f); });
  feats.sort((a, b) => b._a - a._a);
  const iso = topojson.feature(topo, topo.objects.iso).features.map(rewind);
  const states = topojson.feature(statesTopo, statesTopo.objects.states);
  const big = index.filter((e) => e.c >= 150000);
  const pjmBig = big.filter((e) => e.r === 'PJM' && e.ytd != null);
  const nonPjm = big.filter((e) => e.r !== 'PJM' && e.ytd != null);
  const wmean = (arr, k) => d3.sum(arr, (e) => e[k] * e.c) / d3.sum(arr, (e) => e.c);
  $('#map-text').innerHTML = `<p>Each shape is one utility's service territory, colored by how its residential price changed. Utilities inside <strong>PJM</strong> (dashed outline), the grid with the most data-center demand, are up <strong class="up">${fmt.pct(wmean(pjmBig, 'ytd'), 1)}</strong> so far in 2026, against <strong>${fmt.pct(wmean(nonPjm, 'ytd'), 1)}</strong> elsewhere (customer-weighted, large utilities). Hover any territory, or click to open its bill.</p>`;
  $('#map-controls').innerHTML = `<div class="seg" role="group" aria-label="Map measure"><button aria-pressed="true" data-m="real">Since 2020, after inflation</button><button aria-pressed="false" data-m="ytd">2026 so far vs 2025</button></div>`;
  const fig = $('#map-fig');
  const draw = () => {
    const w = Math.max(320, fig.clientWidth - 20);
    const h = Math.round(w * 0.62);
    const proj = d3.geoAlbersUsa().fitExtent([[0, 8], [w, h - 8]], states);
    const path = d3.geoPath(proj);
    const key = mapMode === 'real' ? 'ch' : 'ytd';
    const dom = mapMode === 'real' ? [-20, -10, -5, -1, 1, 5, 10, 20] : [-15, -8, -4, -1, 1, 4, 8, 15];
    const color = d3.scaleThreshold().domain(dom).range(DIV);
    fig.innerHTML = '';
    const s = d3.select(fig).append('svg').attr('viewBox', `0 0 ${w} ${h}`).attr('role', 'img').attr('aria-label', 'Map of utility price changes');
    s.append('path').attr('d', path(states)).attr('fill', '#1c1e22');
    s.append('g').selectAll('path').data(feats).join('path').attr('class', 'terr').attr('d', path)
      .attr('fill', (f) => (f._e && f._e[key] != null ? color(f._e[key]) : '#2a2c31'))
      .on('mousemove', (e, f) => {
        const u = f._e;
        showTip(e, u ? `<b>${esc(shortName(u.n))}</b><div class="m">${esc(u.st)} · ${fmt.int(u.c)} homes · ${esc(u.r === 'none' ? 'no RTO' : u.r)}</div><div class="r"><span>Since 2020, real</span><b>${fmt.pct(u.ch, 1)}</b></div><div class="r"><span>2026 so far</span><b>${fmt.pct(u.ytd, 1)}</b></div><div class="r"><span>${u.y} price</span><b>${fmt.cents(u.p, 1)}</b></div><div class="m">Click to open its bill</div>` : `<b>${esc(f.properties.n)}</b><div class="m">No recent price data</div>`);
      })
      .on('mouseleave', hideTip)
      .on('click', (e, f) => f._e && onPick(f._e));
    s.append('path').attr('class', 'states').attr('d', path(topojson.mesh(statesTopo, statesTopo.objects.states, (a, b) => a !== b)));
    const pjm = iso.find((f) => f.properties.iso === 'PJM');
    if (pjm) {
      s.append('path').attr('class', 'iso').attr('d', path(pjm));
      const c = path.centroid(pjm);
      s.append('text').attr('class', 'iso-label').attr('x', c[0] + 30).attr('y', c[1] - 30).text('PJM');
    }
    const lab = mapMode === 'real' ? 'Real change since 2020' : 'Change, 2026 vs 2025 (same months)';
    d3.select(fig).append('div').attr('class', 'ramp').html(`<span>${lab}</span><span>${fmt.pct(dom[0], 0)}</span><span class="bar">${DIV.map((c) => `<span style="background:${c}"></span>`).join('')}</span><span>${fmt.pct(dom[dom.length - 1], 0)}+</span><span style="margin-left:8px"><i style="display:inline-block;width:12px;height:10px;background:#e4e2da;border-radius:2px;vertical-align:middle"></i> no data</span>`);
  };
  draw();
  addEventListener('resize', () => { clearTimeout(draw._t); draw._t = setTimeout(draw, 200); });
  $$('#map-controls button').forEach((b) => b.addEventListener('click', () => {
    mapMode = b.dataset.m;
    $$('#map-controls button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    draw();
  }));
  // side panels
  const stYtd = Object.entries(prices.states).filter(([s, v]) => s !== 'US' && v.ytd != null).map(([s, v]) => ({ s, v: v.ytd })).sort((a, b) => b.v - a.v);
  const topU = big.filter((e) => e.ch != null).sort((a, b) => b.ch - a.ch).slice(0, 10);
  $('#map-side').innerHTML = `
    <figure class="ch-fig"><p class="fig-title">Biggest increases in 2026 so far, by state</p><p class="fig-sub">Residential price, same months vs 2025</p>${barList(stYtd.slice(0, 10).map((r) => ({ label: STATE_NAMES[r.s] || r.s, value: r.v, color: C.up })), { fmt: (v) => fmt.pct(v, 1) })}<p class="fig-src">EIA-861M</p></figure>
    <figure class="ch-fig"><p class="fig-title">Biggest real increases since 2020</p><p class="fig-sub">Utilities with 150,000+ homes, after inflation</p>${barList(topU.map((e) => ({ label: shortName(e.n), sub: e.st, value: e.ch, color: C.up })), { fmt: (v) => fmt.pct(v, 0) })}<p class="fig-src">EIA-861, BLS CPI-U</p></figure>`;
}

// ---------------------------------------------------------------- 03 spike
export async function chSpike() {
  const [grid, anat] = await Promise.all([D.grid(), D.anatomy()]);
  const rto = (grid.capacity.PJM || []).filter((r) => r.z === 'RTO').sort((a, b) => a.dy.localeCompare(b.dy));
  const total = Object.values(IMM).reduce((a, b) => a + b, 0);
  const cents = anat.pjm?.pjm_capacity_cost_cents_per_kwh_all_load || {};
  $('#spike-text').innerHTML = `
    <p>PJM buys "capacity", promises from power plants to be available at peak, three years ahead. In 2024 the price was <strong>$28.92</strong> per megawatt-day. Then data-center forecasts arrived.</p>
    <span class="big up">${(333.44 / 28.92).toFixed(0)}×</span>
    <p>The price jumped to <strong>$269.92</strong>, then hit the cap of about <strong>$330</strong> three years running. Without the cap, 2028/29 would have cleared at <strong>$554.72</strong>.</p>
    <p>PJM's independent market monitor puts <strong>${fmt.big(total)}</strong> of the cost on data-center load, and says there would have been no shortfall without it. On bills, capacity went from <strong>${cents['2024'] ?? 0.36}¢</strong> to about <strong>${cents['2026_est'] ?? 1.96}¢</strong> per kWh, landing every June 1. <a href="${IMM_URL}" target="_blank" rel="noopener">Read the report</a>.</p>
    <p class="note">The other side: an E3 study funded by data-center groups puts about half of the jump on load growth, and 2022–24 prices were unusually low to begin with.</p>`;
  $('#spike-chart').innerHTML = `<p class="fig-title">PJM capacity price by delivery year</p><p class="fig-sub">$ per MW-day, RTO clearing price. Dashed outline: 2028/29 without the price cap. Labels: data-center share per the market monitor.</p><div id="spike-c"></div><p class="fig-src">PJM BRA reports; Monitoring Analytics</p>`;
  columns($('#spike-c'), {
    label: 'PJM capacity price', height: 330, yFmt: (v) => `$${v}`,
    data: rto.map((r) => ({
      x: r.dy.replace(/^20/, '').replace('/', '–'), y: r.p, color: r.dy >= '2025/26' ? C.up : C.base,
      ghost: r.dy === '2028/29' ? 554.72 : null, top: IMM[r.dy] ? fmt.big(IMM[r.dy]) : null,
      tip: `<b>${r.dy}</b><div>${fmt.usd(r.p, 2)}/MW-day</div>${r.cost ? `<div class="m">Total cost ${fmt.big(r.cost)}</div>` : ''}${IMM[r.dy] ? `<div class="m">Data centers: ${fmt.big(IMM[r.dy])} (market monitor)</div>` : ''}`,
    })),
  });
}

// ---------------------------------------------------------------- 04 wires
export async function chWires() {
  const grid = await D.grid();
  const td = grid.td.filter((r) => r.t != null);
  const a = td[0], b = td[td.length - 1];
  const share = grid.td.filter((r) => r.tc);
  const s0 = share[0], s1 = share[share.length - 1];
  $('#wires-text').innerHTML = `
    <p>Every new data center needs substations and high-voltage lines, and so do new homes, factories and storm repairs. Utilities earn a regulated return on all of it, which is why spending on wires has exploded.</p>
    <span class="big">${(((b.t || 0) + (b.d || 0)) / ((a.t || 0) + (a.d || 0))).toFixed(1)}×</span>
    <p>Utility transmission and distribution spending, ${a.y} to ${b.y}, after inflation. Transmission's slice of the average US price went from <strong>${fmt.cents(s0.tc, 2)}</strong> (${s0.y}) to <strong>${fmt.cents(s1.tc, 2)}</strong>/kWh (${s1.y}).</p>
    <p>In PJM, the grid operator says about <strong>$23B</strong> of new regional lines are driven mainly by data centers. Maryland homes are assigned about <strong>$345</strong> each over 10 years for lines largely serving Virginia. PJM counters that every zone benefits.</p>`;
  $('#wires-chart').innerHTML = `<p class="fig-title">Utility spending on wires, $ billions (2025 dollars)</p><div class="legend"><span><i class="dot" style="--c:${C.s[1]}"></i>Transmission</span><span><i class="dot" style="--c:${C.s[2]}"></i>Distribution</span></div><div id="wires-c"></div><p class="fig-src">FERC Form 1 via Catalyst PUDL · investor-owned utilities</p>`;
  stacked($('#wires-c'), { label: 'T&D capex', yFmt: (v) => `$${Math.round(v)}B`, keys: [{ key: 't', label: 'Transmission', color: C.s[1] }, { key: 'd', label: 'Distribution', color: C.s[2] }], data: td.map((r) => ({ x: String(r.y), t: r.t, d: r.d })) });
  // NITS index
  const zones = Object.entries(grid.nits).map(([z, v]) => {
    const base = v.s.find((r) => r[0] === 2015);
    return base ? { z, name: v.name, s: v.s.filter((r) => r[0] >= 2015).map((r) => [r[0], +(r[1] / base[1]).toFixed(2)]) } : null;
  }).filter(Boolean);
  const hi = ['AEP', 'DOM', 'BGE'];
  const years = [...new Set(zones.flatMap((z) => z.s.map((r) => r[0])))].sort();
  const median = years.map((y) => [y, d3.median(zones.map((z) => (z.s.find((r) => r[0] === y) || [])[1]).filter((v) => v != null))]);
  $('#nits-chart').innerHTML = `<p class="fig-title">PJM transmission rates by zone, 2015 = 1</p><p class="fig-sub">Network transmission service rate; gray lines are the other zones</p><div id="nits-c"></div><p class="fig-src">PJM transmission owner formula rates</p>`;
  lineChart($('#nits-c'), {
    label: 'Transmission rate index', height: 280, yFmt: (v) => `${(+v).toFixed(1)}×`, yMin: 0.5,
    series: [
      ...zones.filter((z) => hi.includes(z.z)).map((z, i) => ({ key: z.z, label: z.z === 'DOM' ? 'Dominion' : z.z, color: [C.s[1], C.s[6], C.s[0]][i], width: 2.5, emph: true, values: z.s })),
      { key: 'med', label: 'PJM median', color: C.ink, dash: '5 4', width: 1.8, values: median },
      ...zones.filter((z) => !hi.includes(z.z)).map((z) => ({ key: z.z, label: z.z, color: '#3a3c42', width: 1, quiet: true, values: z.s })),
    ],
  });
}

// ---------------------------------------------------------------- 05 load
export async function chLoad() {
  const grid = await D.grid();
  const rows = Object.entries(grid.loadShare).map(([s, v]) => ({ s, ...v })).sort((a, b) => b.pct - a.pct);
  const us = (grid.usLoad || []).filter((r) => !r.proj && r.pct != null).sort((a, b) => a.y - b.y);
  const usBy = [...new Map(us.map((r) => [r.y, r])).values()];
  const proj = (grid.usLoad || []).filter((r) => r.proj && r.y === 2030);
  const p30 = proj.find((r) => /lbnl|central|mid/i.test(`${r.sc} ${r.src}`)) || proj[0];
  $('#load-text').innerHTML = `
    <p>US data centers used about <strong>${usBy.length ? usBy[usBy.length - 1].pct.toFixed(1) : '4.7'}%</strong> of the country's electricity in ${usBy.length ? usBy[usBy.length - 1].y : 2024}${p30 ? `, and LBNL projects around <strong>${p30.pct.toFixed(0)}%</strong> by 2030` : ''}. But the load is wildly concentrated.</p>
    <span class="big">${rows[0] ? rows[0].pct.toFixed(0) : 25}%</span>
    <p>of ${esc(STATE_NAMES[rows[0]?.s] || 'Virginia')}'s electricity went to data centers in 2023 (EPRI). Dominion's own filings put data centers at <strong>26–28%</strong> of its sales. Only Ireland is in the same league among countries (about 23%).</p>`;
  $('#load-chart').innerHTML = `<p class="fig-title">Data centers' share of state electricity use, 2023</p><p class="fig-sub">Top 12 states, EPRI estimates</p>${barList(rows.slice(0, 12).map((r) => ({ label: STATE_NAMES[r.s] || r.s, value: r.pct, color: C.s[1] })), { fmt: (v) => `${v.toFixed(1)}%` })}<p class="fig-src">EPRI, Powering Intelligence (2024)</p>`;
}

// ---------------------------------------------------------------- 06 evidence
const STANCE = { 'raises-bills': { label: 'Raises bills', c: C.up }, mixed: { label: 'Mixed', c: C.base }, 'lowers-or-neutral': { label: 'Lowers or neutral', c: C.down } };
export async function chEvidence() {
  const grid = await D.grid();
  const studies = grid.studies.slice().sort((a, b) => String(b.date).localeCompare(String(a.date)));
  const n = (s) => studies.filter((x) => x.stance === s).length;
  $('#evidence-text').innerHTML = `<p>We collected <strong>${studies.length}</strong> studies, reports and analyses: market monitors, national labs, academics, consumer advocates and industry. <strong>${n('raises-bills')}</strong> find data centers raise bills, <strong>${n('mixed')}</strong> are mixed and <strong>${n('lowers-or-neutral')}</strong> find no effect or lower rates. Who funded the work is noted on each card. The honest synthesis: <em>both can be true</em>. Where supply is tight and costs are shared (PJM), households pay. Where there's spare capacity and a tariff that covers costs, data centers can spread fixed costs and lower rates.</p>`;
  const host = $('#evidence');
  let filter = 'all';
  const draw = () => {
    host.innerHTML = `<div class="ev-filters seg" role="group" aria-label="Filter studies">${[['all', `All (${studies.length})`], ['raises-bills', `Raises bills (${n('raises-bills')})`], ['mixed', `Mixed (${n('mixed')})`], ['lowers-or-neutral', `Lowers or neutral (${n('lowers-or-neutral')})`]].map(([k, l]) => `<button data-f="${k}" aria-pressed="${filter === k}">${l}</button>`).join('')}</div>
      <div class="ev-grid">${studies.filter((s) => filter === 'all' || s.stance === filter).map((s) => `
        <article class="ev" style="--c:${(STANCE[s.stance] || {}).c || C.base}">
          <div class="meta"><span class="badge">${esc((STANCE[s.stance] || {}).label || s.stance)}</span><span>${esc(s.type || '')}</span><span>${esc(String(s.date || '').slice(0, 7))}</span>${s.verified === false ? '<span class="badge warn">unverified</span>' : ''}</div>
          <h4>${esc(s.title)}</h4>
          <p><b>${esc(s.author_org || '')}</b>${s.region ? ` · ${esc(s.region)}` : ''}</p>
          <p>${esc(s.claim || '')}</p>
          ${s.notes ? `<p class="note">${esc(String(s.notes).slice(0, 180))}</p>` : ''}
          ${s.url ? `<a href="${safeUrl(s.url)}" target="_blank" rel="noopener">Read the source →</a>` : ''}
        </article>`).join('')}</div>`;
    $$('#evidence .ev-filters button').forEach((b) => b.addEventListener('click', () => { filter = b.dataset.f; draw(); }));
  };
  draw();
}

// ---------------------------------------------------------------- 07 act
export async function chAct() {
  const pol = await D.policy();
  const nat = pol.national;
  $('#act-text').innerHTML = `<p>Utilities asked regulators for record rate increases: about <strong>$31B</strong> across gas and electric in 2025, double 2024, and <strong>$23.1B</strong> through Q3 2026 (PowerLines). Regulators typically grant <strong>about 60%</strong> of what's requested. The gap is where public comments, consumer advocates and intervenors matter.</p><p>${Object.values(pol.states).filter((s) => s.llt.status === 'adopted').length} states have adopted large-load tariffs that make data centers sign long contracts and pay minimum bills. State rules can't reach PJM's regional capacity and transmission costs, though; those are fought at FERC.</p>`;
  const opts = Object.entries(pol.states).sort((a, b) => a[1].name.localeCompare(b[1].name)).map(([k, v]) => `<option value="${k}">${esc(v.name)}</option>`).join('');
  $('#act').innerHTML = `
    <ol class="steps">
      <li><div><b>Find your utility's rate case</b><span>Search your public utility commission's docket for your utility's name. Look for "base rate case" or "general rate case" and the public comment deadline.</span></div></li>
      <li><div><b>Call your consumer advocate</b><span>Most states have an office that represents residential customers in rate cases. They can tell you which hearings matter.</span></div></li>
      <li><div><b>File a comment or show up</b><span>Commissions take written comments and hold public hearings. Short, personal comments about your bill count.</span></div></li>
      <li><div><b>Ask the data-center question</b><span>Does your state have a large-load tariff? Who pays for new transmission and generation built for data centers?</span></div></li>
    </ol>
    <figure class="ch-fig"><p class="fig-title">Your state's contacts</p><label class="sr-only" for="st-pick">Choose a state</label><select class="select" id="st-pick">${opts}</select><div id="st-info" style="margin-top:12px"></div></figure>`;
  const show = (st) => {
    const s = pol.states[st];
    $('#st-info').innerHTML = `<dl class="kv">
      <dt>Consumer advocate</dt><dd>${s.adv?.url ? `<a href="${safeUrl(s.adv.url)}" target="_blank" rel="noopener">${esc(s.adv.office || 'Website')}</a>` : 'None (no official residential advocate)'}</dd>
      <dt>Utility commission</dt><dd>${s.puc?.url ? `<a href="${safeUrl(s.puc.url)}" target="_blank" rel="noopener">${esc(s.puc.name)}</a>` : '—'}</dd>
      <dt>Large-load tariff</dt><dd>${esc(s.llt.status || '—')}</dd>
      <dt>Data-center tax break</dt><dd>${esc(s.inc.type || '—')}${s.inc.cost ? ` · ≈${fmt.big(s.inc.cost)}/yr` : ''}</dd></dl>`;
  };
  $('#st-pick').value = 'VA';
  show('VA');
  $('#st-pick').addEventListener('change', (e) => show(e.target.value));
  return (st) => { if (pol.states[st]) { $('#st-pick').value = st; show(st); } };
}

// ---------------------------------------------------------------- about
export function about() {
  $('#about-inner').innerHTML = `
    <h2>How we built this</h2>
    <p>Eight research tracks gathered public data before a line of the site was written: retail bills, wholesale and capacity markets, transmission, data-center load, state policy, utility finance, household burden and geography. Everything is open, including the data, the scripts and the evidence for and against.</p>
    <h3>Method</h3>
    <ul>
      <li><b>Prices</b> are average revenue ÷ sales per utility from EIA-861 (annual, 2013–2025) and EIA-861M (monthly, through ${'2026'}). In retail-choice states we add an estimated energy charge to delivery-only rates. Real values use BLS CPI-U.</li>
      <li><b>Your utility</b> is found by matching your location against 2,919 utility service territories (HIFLD, 2022 vintage), with county and ZIP fallbacks. Where territories overlap, you can pick.</li>
      <li><b>Itemized bills</b> use real tariffs for 13 large utilities. Elsewhere they're estimated from EIA's national generation, transmission and distribution shares, and labelled as estimates.</li>
      <li><b>Data-center attribution</b> comes from the studies themselves. We never invent a share. The verdict on each bill is region-specific and shows both sides.</li>
      <li><b>Unverified</b> items, ones our researchers could not confirm against a live source, carry a badge.</li>
    </ul>
    <h3>Main sources</h3>
    <table><tr><th>Data</th><th>Source</th></tr>
      <tr><td>Utility prices, sales, customers</td><td>EIA-861, EIA-861M</td></tr>
      <tr><td>Capacity auctions, attribution</td><td>PJM BRA reports; Monitoring Analytics (IMM); MISO, ISO-NE, NYISO</td></tr>
      <tr><td>Transmission and distribution spending</td><td>FERC Form 1 via Catalyst Cooperative PUDL; PJM formula rates</td></tr>
      <tr><td>Data-center load</td><td>EPRI (2024), LBNL US Data Center Energy Usage Report (2024, 2025 update), utility 10-Ks</td></tr>
      <tr><td>State policy, rate cases</td><td>State PUC orders and statutes, PowerLines, utility filings</td></tr>
      <tr><td>Energy burden, shutoffs</td><td>DOE LEAD tool, EIA-112 (2024), NEADA, Census Household Pulse</td></tr>
      <tr><td>Geography</td><td>HIFLD retail service territories, OpenEI ZIP lookups, US Census geocoder, us-atlas</td></tr>
    </table>
    <h3>Privacy</h3>
    <p>Your address is sent only to the geocoder (US Census, or Photon/OpenStreetMap as a fallback) and never stored. Shared links contain your utility, not your address.</p>
    <h3>Limits</h3>
    <p>Averages hide variation: your own bill depends on your usage, rate plan and supplier. Territory maps date from 2022. No published study attributes energy-price (as opposed to capacity) changes to data centers, and evidence for ERCOT and the Southeast is thin. Corrections are welcome.</p>`;
}
