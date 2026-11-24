// d3 chart toolkit: thin marks, recessive grid, direct labels, hover layer on every chart.
/* global d3 */
import { C, esc, showTip, hideTip } from './util.js';

const renders = new Set();
let resizeTimer;
addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => renders.forEach((fn) => fn()), 180);
});
function responsive(el, draw) {
  const run = () => {
    if (!el.isConnected) return renders.delete(run);
    el.innerHTML = '';
    draw(Math.max(280, el.clientWidth));
  };
  renders.add(run);
  run();
}
const svgIn = (el, w, h, label) => d3.select(el).append('svg').attr('viewBox', `0 0 ${w} ${h}`).attr('role', 'img').attr('aria-label', label || '');

// ---------------------------------------------------------------- multi-line with crosshair
// series: [{ key, label, color, width, dash, values: [[x, y]] }]; x: number (year) or 'YYYY-MM'
export function lineChart(el, { series, height = 300, yFmt = (v) => v, xFmt, label, markers = [], yMin, endLabels = true, area }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const narrow = w < 520;
    const m = { t: 14, r: endLabels ? (narrow ? 64 : 120) : 16, b: 28, l: 44 };
    const h = narrow ? Math.round(height * 0.85) : height;
    const isMonth = typeof series[0].values[0][0] === 'string';
    const parse = (x) => (isMonth ? new Date(+x.slice(0, 4), +x.slice(5, 7) - 1, 1) : new Date(x, 0, 1));
    const all = series.flatMap((s) => s.values.filter((v) => v[1] != null));
    const x = d3.scaleTime().domain(d3.extent(all, (d) => parse(d[0]))).range([m.l, w - m.r]);
    const lo = yMin ?? d3.min(all, (d) => d[1]) * 0.9;
    const y = d3.scaleLinear().domain([lo, d3.max(all, (d) => d[1]) * 1.06]).nice().range([h - m.b, m.t]);
    const s = svgIn(el, w, h, label);
    s.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(w - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    s.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(0).tickPadding(8).tickFormat(yFmt));
    s.append('g').attr('class', 'axis').attr('transform', `translate(0,${h - m.b})`).call(d3.axisBottom(x).ticks(narrow ? 4 : 7).tickSize(0).tickPadding(10).tickFormat(xFmt || (isMonth ? d3.timeFormat('%b %y') : d3.timeFormat('%Y'))));
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', h - m.b).attr('y2', h - m.b);
    markers.forEach((mk) => {
      const xx = x(parse(mk.x));
      s.append('line').attr('x1', xx).attr('x2', xx).attr('y1', m.t).attr('y2', h - m.b).attr('stroke', mk.color || C.base).attr('stroke-dasharray', '3 4');
      s.append('text').attr('class', 'ann').attr('x', xx + 5).attr('y', m.t + 10).text(mk.label);
    });
    const line = d3.line().defined((d) => d[1] != null).x((d) => x(parse(d[0]))).y((d) => y(d[1])).curve(d3.curveMonotoneX);
    if (area) {
      const s0 = series[0];
      s.append('path').attr('d', d3.area().defined((d) => d[1] != null).x((d) => x(parse(d[0]))).y0(h - m.b).y1((d) => y(d[1])).curve(d3.curveMonotoneX)(s0.values)).attr('fill', s0.color).attr('opacity', 0.08);
    }
    [...series].reverse().forEach((sr) => {
      s.append('path').attr('d', line(sr.values)).attr('fill', 'none').attr('stroke', sr.color).attr('stroke-width', sr.width || 2).attr('stroke-dasharray', sr.dash || null).attr('stroke-linecap', 'round');
    });
    // end labels with collision avoidance
    if (endLabels) {
      const ends = series.filter((sr) => !sr.quiet).map((sr) => {
        const last = [...sr.values].reverse().find((v) => v[1] != null);
        return { sr, last, y: y(last[1]) };
      }).sort((a, b) => a.y - b.y);
      for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 15) ends[i].y = ends[i - 1].y + 15;
      ends.forEach(({ sr, last, y: yy }) => {
        const xx = x(parse(last[0]));
        s.append('circle').attr('cx', xx).attr('cy', y(last[1])).attr('r', 4).attr('fill', sr.color).attr('stroke', C.page).attr('stroke-width', 2);
        const t = s.append('text').attr('x', xx + 9).attr('y', yy + 4).attr('class', sr.emph ? 'lbl' : 'lbl2');
        t.append('tspan').text(narrow ? yFmt(last[1]) : `${sr.label} `);
        if (!narrow) t.append('tspan').attr('font-weight', 600).attr('fill', C.ink).text(yFmt(last[1]));
      });
    }
    // crosshair
    const xs = [...new Set(all.map((d) => String(d[0])))].map((k) => (isMonth ? k : +k)).sort((a, b) => parse(a) - parse(b));
    const hover = s.append('g').style('display', 'none');
    hover.append('line').attr('y1', m.t).attr('y2', h - m.b).attr('stroke', C.ink).attr('stroke-width', 1).attr('opacity', 0.35);
    const dots = series.map((sr) => hover.append('circle').attr('r', 4.5).attr('fill', sr.color).attr('stroke', C.page).attr('stroke-width', 2));
    s.append('rect').attr('x', m.l).attr('y', m.t).attr('width', w - m.l - m.r).attr('height', h - m.t - m.b).attr('fill', 'transparent')
      .on('mousemove', (e) => {
        const [px] = d3.pointer(e);
        const xv = x.invert(px);
        const k = xs.reduce((a, b) => (Math.abs(parse(b) - xv) < Math.abs(parse(a) - xv) ? b : a));
        hover.style('display', null).select('line').attr('x1', x(parse(k))).attr('x2', x(parse(k)));
        const rowsHtml = series.map((sr, i) => {
          const v = sr.values.find((d) => String(d[0]) === String(k));
          dots[i].attr('cx', x(parse(k))).attr('cy', v && v[1] != null && !sr.quiet ? y(v[1]) : -99);
          return v && v[1] != null && !sr.quiet ?`<div class="r"><span><i style="--c:${sr.color}"></i>${esc(sr.label)}</span><b>${yFmt(v[1])}</b></div>` : '';
        }).join('');
        showTip(e, `<div class="m">${isMonth ? d3.timeFormat('%B %Y')(parse(k)) : k}</div>${rowsHtml}`);
      })
      .on('mouseleave', () => { hover.style('display', 'none'); hideTip(); });
  });
}

// ---------------------------------------------------------------- columns with annotations
// data: [{ x, y, color, ghost, tip, top }]
export function columns(el, { data, height = 300, yFmt = (v) => v, label, hline, rotate = false }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const narrow = w < 520;
    const m = { t: 22, r: 10, b: rotate || narrow ? 44 : 28, l: 46 };
    const h = narrow ? Math.round(height * 0.9) : height;
    const x = d3.scaleBand().domain(data.map((d) => d.x)).range([m.l, w - m.r]).padding(0.22);
    const y = d3.scaleLinear().domain([0, d3.max(data, (d) => Math.max(d.y || 0, d.ghost || 0)) * 1.12]).nice().range([h - m.b, m.t]);
    const s = svgIn(el, w, h, label);
    s.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(w - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    s.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(0).tickPadding(8).tickFormat(yFmt));
    const every = Math.ceil(data.length / Math.max(4, Math.floor(w / 62)));
    const ax = s.append('g').attr('class', 'axis').attr('transform', `translate(0,${h - m.b})`).call(d3.axisBottom(x).tickSize(0).tickPadding(8).tickValues(data.map((d) => d.x).filter((_, i) => i % every === 0)));
    if (rotate || narrow) ax.selectAll('text').attr('transform', 'rotate(-35)').attr('text-anchor', 'end').attr('dx', '-0.4em').attr('dy', '0.4em');
    const bw = x.bandwidth();
    const rr = Math.min(4, bw / 3);
    const bar = (xx, top, bottom, fill, extra = {}) => {
      const hh = Math.max(0, bottom - top);
      const r = Math.min(rr, hh);
      return s.append('path').attr('d', `M${xx},${bottom}V${top + r}Q${xx},${top} ${xx + r},${top}H${xx + bw - r}Q${xx + bw},${top} ${xx + bw},${top + r}V${bottom}Z`).attr('fill', fill).attr('stroke', extra.stroke || null).attr('stroke-dasharray', extra.dash || null).attr('stroke-width', extra.stroke ? 1.5 : null);
    };
    data.forEach((d) => {
      const xx = x(d.x);
      if (d.ghost) bar(xx, y(d.ghost), h - m.b, 'transparent', { stroke: d.color || C.up, dash: '3 3' });
      if (d.y != null) bar(xx, y(d.y), h - m.b, d.color || C.s[0]);
      if (d.top) s.append('text').attr('class', 'ann').attr('x', xx + bw / 2).attr('y', y(Math.max(d.y || 0, d.ghost || 0)) - 6).attr('text-anchor', 'middle').attr('font-weight', 600).attr('fill', C.ink).text(d.top);
      s.append('rect').attr('x', xx - 2).attr('y', m.t).attr('width', bw + 4).attr('height', h - m.t - m.b).attr('fill', 'transparent')
        .on('mousemove', (e) => showTip(e, d.tip || `<b>${esc(d.x)}</b><div>${yFmt(d.y)}</div>`)).on('mouseleave', hideTip);
    });
    if (hline) {
      s.append('line').attr('x1', m.l).attr('x2', w - m.r).attr('y1', y(hline.y)).attr('y2', y(hline.y)).attr('stroke', C.ink).attr('stroke-dasharray', '4 4').attr('opacity', 0.6);
      s.append('text').attr('class', 'ann').attr('x', m.l + 6).attr('y', y(hline.y) - 6).text(hline.label);
    }
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', h - m.b).attr('y2', h - m.b);
  });
}

// ---------------------------------------------------------------- stacked columns (2px surface gap between segments)
export function stacked(el, { data, keys, height = 280, yFmt = (v) => v, label }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const narrow = w < 520;
    const m = { t: 12, r: 10, b: 28, l: 46 };
    const h = narrow ? Math.round(height * 0.9) : height;
    const x = d3.scaleBand().domain(data.map((d) => d.x)).range([m.l, w - m.r]).padding(0.18);
    const y = d3.scaleLinear().domain([0, d3.max(data, (d) => keys.reduce((t, k) => t + (d[k.key] || 0), 0)) * 1.08]).nice().range([h - m.b, m.t]);
    const s = svgIn(el, w, h, label);
    s.append('g').attr('class', 'grid').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(w - m.l - m.r)).tickFormat('')).call((g) => g.select('.domain').remove());
    s.append('g').attr('class', 'axis').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(0).tickPadding(8).tickFormat(yFmt));
    const every = Math.ceil(data.length / Math.max(4, Math.floor(w / 58)));
    s.append('g').attr('class', 'axis').attr('transform', `translate(0,${h - m.b})`).call(d3.axisBottom(x).tickSize(0).tickPadding(8).tickValues(data.map((d) => d.x).filter((_, i) => i % every === 0)));
    data.forEach((d) => {
      let acc = 0;
      keys.forEach((k, i) => {
        const v = d[k.key] || 0;
        if (!v) return;
        const y0 = y(acc), y1 = y(acc + v);
        const top = i === keys.length - 1 || keys.slice(i + 1).every((kk) => !d[kk.key]);
        s.append('rect').attr('x', x(d.x)).attr('width', x.bandwidth()).attr('y', y1 + (acc ? 1 : 0)).attr('height', Math.max(0.5, y0 - y1 - (acc ? 1 : 0))).attr('rx', top ? 3 : 0).attr('fill', k.color);
        acc += v;
      });
      s.append('rect').attr('x', x(d.x)).attr('y', m.t).attr('width', x.bandwidth()).attr('height', h - m.t - m.b).attr('fill', 'transparent')
        .on('mousemove', (e) => showTip(e, `<div class="m">${esc(d.x)}</div>${keys.map((k) => `<div class="r"><span><i style="--c:${k.color}"></i>${esc(k.label)}</span><b>${yFmt(d[k.key] || 0)}</b></div>`).join('')}<div class="r"><span>Total</span><b>${yFmt(keys.reduce((t, k) => t + (d[k.key] || 0), 0))}</b></div>`))
        .on('mouseleave', hideTip);
    });
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', h - m.b).attr('y2', h - m.b);
  });
}

// ---------------------------------------------------------------- waterfall: start → +/- steps → end (→ optional extra step → final)
// steps: [{ label, v, kind: 'total' | 'delta', note }]
export function waterfall(el, { steps, height = 300, label, fmt = (v) => `$${Math.round(v)}` }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const narrow = w < 560;
    const m = { t: 26, r: 8, b: narrow ? 74 : 54, l: 8 };
    const h = narrow ? height + 30 : height;
    let run = 0;
    const bars = steps.map((s) => {
      if (s.kind === 'total') { run = s.v; return { ...s, y0: 0, y1: s.v }; }
      const y0 = run; run += s.v; return { ...s, y0, y1: run };
    });
    const x = d3.scaleBand().domain(bars.map((_, i) => i)).range([m.l, w - m.r]).padding(0.22);
    const lo = Math.min(0, d3.min(bars, (b) => Math.min(b.y0, b.y1)));
    const y = d3.scaleLinear().domain([lo, d3.max(bars, (b) => Math.max(b.y0, b.y1)) * 1.12]).nice().range([h - m.b, m.t]);
    const s = svgIn(el, w, h, label);
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', y(0)).attr('y2', y(0));
    bars.forEach((b, i) => {
      const xx = x(i), bw = x.bandwidth();
      const top = y(Math.max(b.y0, b.y1)), bot = y(Math.min(b.y0, b.y1));
      const color = b.kind === 'total' ? (b.emph ? C.s[0] : C.base) : b.v >= 0 ? C.up : C.down;
      s.append('rect').attr('x', xx).attr('y', top).attr('width', bw).attr('height', Math.max(2, bot - top)).attr('rx', 4).attr('fill', color).attr('opacity', b.kind === 'total' && !b.emph ? 0.9 : 1);
      if (i < bars.length - 1) {
        const nx = x(i + 1);
        s.append('line').attr('x1', xx + bw).attr('x2', nx).attr('y1', y(b.y1)).attr('y2', y(b.y1)).attr('stroke', C.muted).attr('stroke-dasharray', '2 3');
      }
      const val = b.kind === 'total' ? fmt(b.v) : `${b.v >= 0 ? '+' : '−'}${fmt(Math.abs(b.v))}`;
      s.append('text').attr('x', xx + bw / 2).attr('y', top - 7).attr('text-anchor', 'middle').attr('font-weight', 700).attr('fill', C.ink).attr('font-size', narrow ? 11 : 13).text(val);
      const lab = s.append('text').attr('x', xx + bw / 2).attr('y', h - m.b + 16).attr('text-anchor', narrow ? 'end' : 'middle').attr('class', b.kind === 'total' ? 'lbl' : 'lbl2').attr('font-size', narrow ? 10.5 : 12);
      if (narrow) lab.attr('transform', `rotate(-35 ${xx + bw / 2} ${h - m.b + 16})`).text(b.short || b.label);
      else String(b.label).split('\n').forEach((t, k) => lab.append('tspan').attr('x', xx + bw / 2).attr('dy', k ? 14 : 0).text(t));
      s.append('rect').attr('x', xx).attr('y', m.t).attr('width', bw).attr('height', h - m.t - m.b).attr('fill', 'transparent')
        .on('mousemove', (e) => showTip(e, `<b>${esc(String(b.label).replace('\n', ' '))}</b><div>${val}${b.kind === 'total' ? ' a month' : ' a month'}</div>${b.note ? `<div class="m">${esc(b.note)}</div>` : ''}`))
        .on('mouseleave', hideTip);
    });
  });
}

// ---------------------------------------------------------------- percentile strip: every utility as a dot, yours highlighted
export function strip(el, { points, mine, height = 150, label, xFmt = (v) => `${v > 0 ? '+' : ''}${v}%`, median }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const m = { t: 30, r: 16, b: 28, l: 16 };
    const h = height;
    const ext = [Math.max(-40, d3.min(points, (p) => p.v)), Math.min(90, d3.max(points, (p) => p.v))];
    const x = d3.scaleLinear().domain(ext).nice().range([m.l, w - m.r]).clamp(true);
    const r = d3.scaleSqrt().domain([0, d3.max(points, (p) => p.c)]).range([1.4, 7]);
    const s = svgIn(el, w, h, label);
    s.append('g').attr('class', 'axis').attr('transform', `translate(0,${h - m.b})`).call(d3.axisBottom(x).ticks(w < 520 ? 5 : 9).tickSize(0).tickPadding(10).tickFormat(xFmt));
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', h - m.b).attr('y2', h - m.b);
    s.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', m.t - 8).attr('y2', h - m.b).attr('stroke', C.base);
    const mid = (m.t + h - m.b) / 2, span = (h - m.b - m.t) / 2 - 6;
    const hash = (str) => { let a = 0; for (const ch of String(str)) a = (a * 31 + ch.charCodeAt(0)) >>> 0; return (a % 1000) / 1000; };
    s.append('g').selectAll('circle').data(points).join('circle')
      .attr('cx', (p) => x(p.v)).attr('cy', (p) => mid + (hash(p.k) - 0.5) * 2 * span).attr('r', (p) => r(p.c))
      .attr('fill', (p) => (p.v > 0 ? 'rgba(227,73,72,0.28)' : 'rgba(42,120,214,0.3)')).attr('stroke', 'none')
      .on('mousemove', (e, p) => showTip(e, `<b>${esc(p.n)}</b><div class="m">${esc(p.st)} · ${Math.round(p.c).toLocaleString()} homes</div><div>${xFmt(p.v.toFixed(0))} since 2020, after inflation</div>`))
      .on('mouseleave', hideTip);
    if (median != null) {
      s.append('line').attr('x1', x(median)).attr('x2', x(median)).attr('y1', m.t - 4).attr('y2', h - m.b).attr('stroke', C.ink).attr('stroke-dasharray', '3 3').attr('opacity', 0.55);
      s.append('text').attr('class', 'ann').attr('x', x(median)).attr('y', m.t - 10).attr('text-anchor', 'middle').text(`typical home ${xFmt(median.toFixed(0))}`);
    }
    if (mine) {
      const cx = x(mine.v);
      s.append('circle').attr('cx', cx).attr('cy', mid).attr('r', 9).attr('fill', C.s[0]).attr('stroke', C.page).attr('stroke-width', 3);
      s.append('line').attr('x1', cx).attr('x2', cx).attr('y1', mid - 12).attr('y2', m.t - 2).attr('stroke', C.s[0]).attr('stroke-width', 2);
      const t = s.append('text').attr('x', Math.min(Math.max(cx, 60), w - 60)).attr('y', 14).attr('text-anchor', 'middle').attr('font-weight', 700).attr('fill', C.s[0]).attr('font-size', 13);
      t.text(`${mine.label} ${xFmt(mine.v.toFixed(0))}`);
    }
  });
}

// ---------------------------------------------------------------- step timeline: values per period, past vs locked-in future
// periods: [{ start: Date, end: Date, v, label, locked }]
export function stepTimeline(el, { periods, today, height = 230, label, vFmt = (v) => `$${v.toFixed(0)}` }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const narrow = w < 520;
    const m = { t: 30, r: 12, b: 34, l: 12 };
    const h = height;
    const x = d3.scaleTime().domain([periods[0].start, periods[periods.length - 1].end]).range([m.l, w - m.r]);
    const y = d3.scaleLinear().domain([0, d3.max(periods, (p) => p.v) * 1.25]).range([h - m.b, m.t]);
    const s = svgIn(el, w, h, label);
    const lockStart = periods.find((p) => p.locked)?.start;
    if (lockStart) {
      s.append('rect').attr('x', x(lockStart)).attr('y', m.t - 18).attr('width', w - m.r - x(lockStart)).attr('height', h - m.b - m.t + 18).attr('fill', 'rgba(255,214,10,0.18)').attr('rx', 8);
      s.append('text').attr('class', 'ann').attr('x', x(lockStart) + 8).attr('y', m.t - 5).attr('font-weight', 600).attr('fill', C.ink).text('🔒 Already decided at auction');
    }
    periods.forEach((p) => {
      const x0 = x(p.start) + 2, x1 = x(p.end) - 2;
      s.append('rect').attr('x', x0).attr('y', y(p.v)).attr('width', Math.max(2, x1 - x0)).attr('height', h - m.b - y(p.v)).attr('rx', 4).attr('fill', p.v > periods[0].v * 2 ? C.up : C.base);
      s.append('text').attr('x', (x0 + x1) / 2).attr('y', y(p.v) - 7).attr('text-anchor', 'middle').attr('font-weight', 700).attr('fill', C.ink).attr('font-size', narrow ? 11.5 : 14).text(vFmt(p.v));
      s.append('text').attr('x', (x0 + x1) / 2).attr('y', h - m.b + 16).attr('text-anchor', 'middle').attr('class', 'lbl2').attr('font-size', narrow ? 10.5 : 12).text(narrow ? p.label.replace(/20(\d\d)/g, '$1') : p.label);
      s.append('rect').attr('x', x0).attr('y', m.t).attr('width', Math.max(2, x1 - x0)).attr('height', h - m.t - m.b).attr('fill', 'transparent')
        .on('mousemove', (e) => showTip(e, `<b>June ${p.start.getFullYear()} – May ${p.end.getFullYear()}</b><div>≈${vFmt(p.v)} a month for capacity</div>${p.tip ? `<div class="m">${p.tip}</div>` : ''}`))
        .on('mouseleave', hideTip);
    });
    s.append('line').attr('class', 'baseline').attr('x1', m.l).attr('x2', w - m.r).attr('y1', h - m.b).attr('y2', h - m.b);
    if (today) {
      const tx = x(today);
      s.append('line').attr('x1', tx).attr('x2', tx).attr('y1', m.t - 18).attr('y2', h - m.b).attr('stroke', C.ink).attr('stroke-width', 1.5);
      s.append('text').attr('class', 'ann').attr('x', tx - 6).attr('y', m.t - 5).attr('text-anchor', 'end').attr('font-weight', 600).attr('fill', C.ink).text('Today');
    }
  });
}

// ---------------------------------------------------------------- animated dollar flow
// A $1 coin on the left; ribbons fan out to each destination, sized by share; glowing particles (≈1¢ each) stream along
// them; counters tick up to each share. parts: [{ key, label, who, share, color, note }]
export function dollarFlow(el, { parts, height = 330, label, coin = '$1', coinSub = 'your dollar', unit = '¢', total = 100 }) {
  el.classList.add('chart', 'flow');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let raf = 0, io = null;
  const stop = () => { cancelAnimationFrame(raf); raf = 0; io?.disconnect(); };
  responsive(el, (w) => {
    stop();
    const narrow = w < 600;
    const sum = d3.sum(parts, (p) => p.share);
    const n = parts.length;
    const labelH = narrow ? 50 : 56;
    const h = Math.max(height, n * (labelH + 6) + 30);
    const m = { t: 14, b: 14 };
    const srcR = narrow ? 30 : 46;
    const srcX = narrow ? srcR + 6 : srcR + 30;
    const tgtX = Math.round(narrow ? w * 0.4 : w * 0.5);
    const labelX = tgtX + (narrow ? 12 : 18);
    const maxChars = Math.max(10, Math.floor((w - labelX - 6) / (narrow ? 6.4 : 7)));
    const clip = (t) => (t && t.length > maxChars ? `${t.slice(0, maxChars - 1)}…` : t);
    const gap = narrow ? 8 : 12;
    const avail = h - m.t - m.b - gap * (n - 1);
    let hs = parts.map((p) => Math.max(5, (avail * p.share) / sum));
    const k = avail / d3.sum(hs);
    hs = hs.map((v) => v * k);
    const srcH = srcR * 1.7;
    const cy = h / 2;
    let ys = cy - srcH / 2, yt = m.t;
    const bands = parts.map((p, i) => {
      const thS = (srcH * p.share) / sum, thT = hs[i];
      const b = { ...p, s0: ys, s1: ys + thS, t0: yt, t1: yt + thT, thS, thT };
      ys += thS; yt += thT + gap;
      return b;
    });
    const x0 = srcX + srcR * 0.55, x1 = tgtX, xm = (x0 + x1) / 2;
    const s = svgIn(el, w, h, label);
    const defs = s.append('defs');
    bands.forEach((b, i) => {
      const g = defs.append('linearGradient').attr('id', `fg-${i}-${el.id}`).attr('x1', '0%').attr('x2', '100%');
      g.append('stop').attr('offset', '0%').attr('stop-color', b.color).attr('stop-opacity', 0.08);
      g.append('stop').attr('offset', '100%').attr('stop-color', b.color).attr('stop-opacity', 0.3);
    });
    const glow = defs.append('filter').attr('id', `glow-${el.id}`).attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%');
    glow.append('feGaussianBlur').attr('stdDeviation', 1.6).attr('result', 'b');
    const fm = glow.append('feMerge'); fm.append('feMergeNode').attr('in', 'b'); fm.append('feMergeNode').attr('in', 'SourceGraphic');
    const ribbon = (b) => `M${x0},${b.s0} C${xm},${b.s0} ${xm},${b.t0} ${x1},${b.t0} L${x1},${b.t1} C${xm},${b.t1} ${xm},${b.s1} ${x0},${b.s1} Z`;
    const ribs = s.append('g').selectAll('path').data(bands).join('path').attr('d', ribbon).attr('fill', (b, i) => `url(#fg-${i}-${el.id})`).attr('stroke', 'none').style('cursor', 'default')
      .on('mousemove', function (e, b) { d3.select(this).attr('fill', b.color).attr('fill-opacity', 0.35); showTip(e, `<b>${esc(b.label)}</b><div>${(b.share / sum * total).toFixed(0)}${unit} of every ${coin}</div>${b.who ? `<div class="m">Paid to: ${esc(b.who)}</div>` : ''}${b.note ? `<div class="m">${esc(b.note)}</div>` : ''}`); })
      .on('mouseleave', function (e, b) { const i = bands.indexOf(b); d3.select(this).attr('fill', `url(#fg-${i}-${el.id})`).attr('fill-opacity', null); hideTip(); });
    // destination bars
    s.append('g').selectAll('rect').data(bands).join('rect').attr('x', x1).attr('y', (b) => b.t0).attr('width', 6).attr('height', (b) => b.thT).attr('rx', 2).attr('fill', (b) => b.color);
    // labels with collision avoidance
    const lab = bands.map((b) => ({ b, y: (b.t0 + b.t1) / 2 }));
    for (let i = 1; i < lab.length; i++) if (lab[i].y - lab[i - 1].y < labelH) lab[i].y = lab[i - 1].y + labelH;
    const over = lab.length ? lab[lab.length - 1].y + labelH / 2 - (h - 4) : 0;
    if (over > 0) lab.forEach((l) => (l.y -= over));
    const counters = [];
    lab.forEach(({ b, y }) => {
      const g = s.append('g').attr('transform', `translate(${labelX},${y})`);
      if (Math.abs(y - (b.t0 + b.t1) / 2) > 3) s.append('path').attr('d', `M${x1 + 8},${(b.t0 + b.t1) / 2} L${labelX - 4},${y}`).attr('stroke', b.color).attr('stroke-width', 1).attr('fill', 'none').attr('opacity', 0.6);
      // narrow: share on top, label underneath (no "who" line; it's in the tooltip). wide: share left, two text lines right
      const big = g.append('text').attr('x', 0).attr('y', narrow ? -4 : 4).attr('font-family', 'Instrument Serif, Georgia, serif').attr('font-size', narrow ? 24 : 34).attr('fill', C.ink).text(`0${unit}`);
      counters.push({ el: big, v: (b.share / sum) * total });
      g.append('text').attr('x', narrow ? 0 : 62).attr('y', narrow ? 14 : -3).attr('font-weight', 600).attr('font-size', narrow ? 12 : 14).attr('fill', C.ink).text(clip(b.label));
      if (b.who && !narrow) g.append('text').attr('x', 62).attr('y', 15).attr('font-size', 12.5).attr('fill', C.ink2).text(clip(b.who));
    });
    // coin
    const coinG = s.append('g').attr('transform', `translate(${srcX},${cy})`);
    coinG.append('circle').attr('r', srcR + 8).attr('fill', 'rgba(255,214,10,0.25)').attr('class', reduce ? '' : 'coin-pulse');
    coinG.append('circle').attr('r', srcR).attr('fill', '#15171b').attr('stroke', C.volt).attr('stroke-opacity', 0.5);
    coinG.append('circle').attr('r', srcR - 5).attr('fill', 'none').attr('stroke', C.volt).attr('stroke-width', 1.5).attr('stroke-dasharray', '2 3');
    coinG.append('text').attr('text-anchor', 'middle').attr('dy', '0.35em').attr('font-family', 'Instrument Serif, Georgia, serif').attr('font-size', narrow ? 26 : 38).attr('fill', C.volt).text(coin);
    s.append('text').attr('x', narrow ? 2 : srcX).attr('y', cy + srcR + 22).attr('text-anchor', narrow ? 'start' : 'middle').attr('font-size', narrow ? 10.5 : 12).attr('fill', C.ink2).text(narrow && coinSub.length > 16 ? coinSub.split(',')[0] : coinSub);
    // particles
    const N = reduce ? 0 : narrow ? 70 : 120;
    const parts2 = [];
    bands.forEach((b) => {
      const cnt = Math.max(3, Math.round((b.share / sum) * N));
      for (let i = 0; i < cnt; i++) parts2.push({ b, t: Math.random(), sp: 0.12 + Math.random() * 0.1, f: Math.random() - 0.5, r: 1.6 + Math.random() * 1.6 });
    });
    const dots = s.append('g').attr('filter', `url(#glow-${el.id})`).selectAll('circle').data(parts2).join('circle').attr('r', (p) => p.r).attr('fill', (p) => p.b.color);
    const bez = (t, a, b2) => { const u = 1 - t; return u * u * u * a + 3 * u * u * t * a + 3 * u * t * t * b2 + t * t * t * b2; }; // control points share y with ends
    const bx = (t) => { const u = 1 - t; return u * u * u * x0 + 3 * u * u * t * xm + 3 * u * t * t * xm + t * t * t * x1; };
    const place = () => dots.attr('cx', (p) => bx(p.t)).attr('cy', (p) => { const c = bez(p.t, (p.b.s0 + p.b.s1) / 2, (p.b.t0 + p.b.t1) / 2); const th = p.b.thS + (p.b.thT - p.b.thS) * p.t; return c + p.f * th * 0.85; }).attr('opacity', (p) => Math.min(1, Math.sin(Math.PI * p.t) * 1.6));
    place();
    let last = 0, started = false;
    const tick = (ts) => {
      if (!el.isConnected) { stop(); return; } // chart was replaced (e.g. a toggle): stop animating
      const dt = last ? Math.min(0.05, (ts - last) / 1000) : 0;
      last = ts;
      parts2.forEach((p) => { p.t += p.sp * dt; if (p.t > 1) { p.t -= 1; p.f = Math.random() - 0.5; } });
      place();
      raf = requestAnimationFrame(tick);
    };
    const countUp = () => counters.forEach((c) => c.el.transition().duration(reduce ? 0 : 1400).ease(d3.easeCubicOut).tween('text', () => { const i = d3.interpolateNumber(0, c.v); return (t) => c.el.text(`${Math.round(i(t))}${unit}`); }));
    io = new IntersectionObserver((ents) => {
      const vis = ents.some((e) => e.isIntersecting);
      if (vis && !started) { started = true; countUp(); }
      if (vis && !raf && N) { last = 0; raf = requestAnimationFrame(tick); } else if (!vis && raf) { cancelAnimationFrame(raf); raf = 0; }
    }, { threshold: 0.15 });
    io.observe(el);
  });
}

// ---------------------------------------------------------------- HTML bar list
export function barList(rows, { fmt = (v) => v, max, color = C.s[0] } = {}) {
  const mx = max ?? Math.max(...rows.map((r) => Math.abs(r.value || 0)), 1e-9);
  return `<div class="barlist">${rows.map((r) => `
    <div class="bl-row" ${r.tip ? `title="${esc(r.tip)}"` : ''}>
      <span class="bl-l">${esc(r.label)}${r.sub ? ` <small>${esc(r.sub)}</small>` : ''}</span>
      <span class="bl-t"><span class="bl-f" style="width:${Math.max(1, (Math.abs(r.value || 0) / mx) * 100)}%;background:${r.color || color}"></span></span>
      <span class="bl-v">${fmt(r.value)}</span>
    </div>`).join('')}</div>`;
}

// ---------------------------------------------------------------- semicircle meter (0 = lowers, 1 = raises)
export function meter(value, label) {
  const a = Math.PI * (1 - value);
  const cx = 60, cy = 58, r = 46;
  const nx = cx + r * 0.82 * Math.cos(a), ny = cy - r * 0.82 * Math.sin(a);
  const seg = (a0, a1, c) => {
    const p = (ang) => [cx + r * Math.cos(Math.PI * (1 - ang)), cy - r * Math.sin(Math.PI * (1 - ang))];
    const [x0, y0] = p(a0), [x1, y1] = p(a1);
    return `<path d="M${x0},${y0} A${r},${r} 0 0 1 ${x1},${y1}" stroke="${c}" stroke-width="10" fill="none" stroke-linecap="butt"/>`;
  };
  return `<svg class="meter" viewBox="0 0 120 70" role="img" aria-label="${esc(label)}">
    ${seg(0, 0.32, C.down)}${seg(0.34, 0.66, '#c3c2b7')}${seg(0.68, 1, C.up)}
    <line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="${C.ink}" stroke-width="3" stroke-linecap="round"/>
    <circle cx="${cx}" cy="${cy}" r="5" fill="${C.ink}"/>
  </svg>`;
}

// ---------------------------------------------------------------- small territory map with data-center dots
export function territoryMap(el, { feature, states, campuses = [], label }) {
  el.classList.add('chart');
  responsive(el, (w) => {
    const h = Math.round(Math.min(360, w * 0.72));
    const proj = d3.geoMercator().fitExtent([[12, 12], [w - 12, h - 12]], feature);
    const path = d3.geoPath(proj);
    const s = svgIn(el, w, h, label).style('overflow', 'hidden').style('border-radius', '10px').style('background', '#14161a');
    if (states) s.append('path').attr('d', path(states)).attr('fill', '#1c1e22').attr('stroke', C.page).attr('stroke-width', 1.2);
    s.append('path').attr('d', path(feature)).attr('fill', 'rgba(42,120,214,0.16)').attr('stroke', C.s[0]).attr('stroke-width', 1.6);
    const rScale = d3.scaleSqrt().domain([0, 5000]).range([4, 16]).clamp(true);
    campuses
      .filter((c) => { const p = proj([c.lng, c.lat]); return p && p[0] > -20 && p[0] < w + 20 && p[1] > -20 && p[1] < h + 20; })
      .sort((a, b) => (b.mw || 0) - (a.mw || 0))
      .forEach((c) => {
        const [px, py] = proj([c.lng, c.lat]);
        s.append('circle').attr('cx', px).attr('cy', py).attr('r', rScale(c.mw || 150)).attr('fill', c.inside ? C.s[1] : 'rgba(235,104,52,0.25)').attr('stroke', C.page).attr('stroke-width', 2)
          .on('mousemove', (e) => showTip(e, `<b>${esc(c.n)}</b><div class="m">${esc(c.u || '')}${c.u ? ' · ' : ''}${esc(c.s || '')}</div><div>${c.mw ? (c.mw >= 1000 ? `${(c.mw / 1000).toFixed(1)} GW` : `${c.mw} MW`) : 'size not disclosed'}</div>`))
          .on('mouseleave', hideTip);
      });
  });
}
