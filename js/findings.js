// Findings page: the most surprising patterns across all research areas, each as an interactive card.
/* global d3 */
import { $, $$, esc, safeUrl, fmt, C, D, STATE_NAMES, showTip, hideTip, load } from './util.js';
import { columns, lineChart, barList } from './charts.js';
import { IMM, shortName } from './report.js';

const THEMES = { bill: 'Your bill', dc: 'Data centers', money: 'Money', people: 'People & policy' };
const num = (v) => { if (typeof v === 'number') return v; const m = String(v ?? '').match(/[\d.]+/g); return m ? +m[m.length - 1] : null; };
const pct = (v, d = 0) => fmt.pct(v, d);
const clean = (n) => shortName(String(n).split('(')[0]).replace(/\b(Company|Co|LLC|Inc|Corp|Corporation|Cooperative|Coop|Assn|Association)\b\.?/gi, '').replace(/[,\s]+$/, '').replace(/\s+/g, ' ').trim();

// two-row dot strip: PJM vs everywhere else
function strip2(el, rows, { fmtX = (v) => pct(v, 0) } = {}) {
  el.classList.add('chart');
  const draw = () => {
    el.innerHTML = '';
    const w = Math.max(280, el.clientWidth), h = 190, m = { l: w < 520 ? 78 : 92, r: 16, t: 12, b: 26 };
    const all = rows.flatMap((r) => r.points);
    const x = d3.scaleLinear().domain([Math.max(-25, d3.min(all, (p) => p.v)), Math.min(45, d3.max(all, (p) => p.v))]).nice().range([m.l, w - m.r]).clamp(true);
    const r = d3.scaleSqrt().domain([0, d3.max(all, (p) => p.c)]).range([2, 11]);
    const s = d3.select(el).append('svg').attr('viewBox', `0 0 ${w} ${h}`);
    s.append('g').attr('class', 'axis').attr('transform', `translate(0,${h - m.b})`).call(d3.axisBottom(x).ticks(6).tickSize(0).tickPadding(8).tickFormat((v) => fmtX(v)));
    s.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', m.t).attr('y2', h - m.b).attr('stroke', C.base);
    const band = (h - m.t - m.b) / rows.length;
    rows.forEach((row, i) => {
      const cy = m.t + band * (i + 0.5);
      s.append('text').attr('x', 0).attr('y', cy + 4).attr('font-weight', 700).attr('fill', row.color).attr('font-size', 13).text(row.label);
      let seed = 3 + i;
      const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
      s.append('g').selectAll('circle').data(row.points).join('circle').attr('cx', (p) => x(p.v)).attr('cy', () => cy + (rnd() - 0.5) * (band - 22)).attr('r', (p) => r(p.c))
        .attr('fill', row.color).attr('fill-opacity', 0.35).attr('stroke', row.color).attr('stroke-width', 1)
        .on('mousemove', (e, p) => showTip(e, `<b>${esc(p.n)}</b><div class="m">${esc(p.st)} · ${fmt.int(p.c)} homes</div><div>${pct(p.v, 1)} in 2026 so far</div>`)).on('mouseleave', hideTip);
      s.append('line').attr('x1', x(row.med)).attr('x2', x(row.med)).attr('y1', cy - band / 2 + 6).attr('y2', cy + band / 2 - 6).attr('stroke', C.ink).attr('stroke-width', 2.5);
      s.append('text').attr('x', x(row.med) + 6).attr('y', cy - band / 2 + 14).attr('font-size', 12).attr('font-weight', 700).attr('fill', C.ink).attr('stroke', C.surface).attr('stroke-width', 4).attr('paint-order', 'stroke').text(`${w < 520 ? 'median' : 'typical home'} ${pct(row.med, 1)}`);
    });
  };
  draw();
  addEventListener('resize', () => { clearTimeout(draw.t); draw.t = setTimeout(draw, 200); });
}

// paired horizontal bars (two measures per row, same unit)
function paired(rows, { a, b, fmtV = (v) => pct(v, 0) }) {
  const mx = Math.max(...rows.flatMap((r) => [Math.abs(r.a || 0), Math.abs(r.b || 0)]), 1);
  return `<div class="legend"><span><i class="dot" style="--c:${a.color}"></i>${esc(a.label)}</span><span><i class="dot" style="--c:${b.color}"></i>${esc(b.label)}</span></div>
  <div class="paired">${rows.map((r) => `<div class="pr" title="${esc(r.tip || '')}"><div class="pr-l">${esc(r.label)}${r.sub ? ` <small>${esc(r.sub)}</small>` : ''}</div>
    <div class="pr-bars"><div class="pr-row"><span class="pr-t"><span class="pr-f" style="width:${Math.max(0.8, (Math.max(0, r.a || 0) / mx) * 100)}%;background:${a.color}"></span></span><span class="pr-v">${r.a == null ? '—' : fmtV(r.a)}</span></div>
    <div class="pr-row"><span class="pr-t"><span class="pr-f" style="width:${Math.max(0.8, (Math.max(0, r.b || 0) / mx) * 100)}%;background:${b.color}"></span></span><span class="pr-v">${r.b == null ? '—' : fmtV(r.b)}</span></div></div></div>`).join('')}</div>`;
}

const linkLabel = (t = '') => (/^stated/.test(t) ? 'Data centers cited' : /^reported/.test(t) ? 'Data centers partly cited' : /^none/.test(t) ? 'Not data-center driven' : 'Link unclear');
const whoPays = (a = '') => (/Schedule 12 hybrid/i.test(a) ? 'Half shared by all PJM customers, half billed to the areas that use it.'
  : /postage-stamp/i.test(a) ? 'Shared by every customer on the Texas grid.'
  : /100% to the host zone/i.test(a) ? 'Billed entirely to the local utility’s customers.'
  : /DFAX/i.test(a) ? 'Billed to the areas the power flows to.'
  : String(a).slice(0, 110));

async function main() {
  const [F, index, prices, grid, policy] = await Promise.all([load('assets/data/findings.json'), D.index(), D.prices(), D.grid(), D.policy()]);
  $('#f-updated').textContent = `Data through ${fmt.month(prices.latestMonth)}`;
  const big = index.filter((e) => e.c >= 100000 && e.ytd != null);
  const wmed = (arr) => { const s = arr.slice().sort((p, q) => p.ytd - q.ytd); const tot = d3.sum(s, (e) => e.c); let acc = 0; return (s.find((e) => (acc += e.c) >= tot / 2) || {}).ytd; };
  const pjm = big.filter((e) => e.r === 'PJM'), rest = big.filter((e) => e.r !== 'PJM');
  const withYtd = index.filter((e) => e.ytd != null);
  const dd26 = (100 * withYtd.filter((e) => e.ytd >= 10).length) / withYtd.length;
  const dd24 = F.doubleDigit.find((d) => d.y === '2024')?.share;
  const dd22 = F.doubleDigit.find((d) => d.y === '2022')?.share;
  const cpi = prices.cpi.filter((r) => r[2]);
  const cpiBase = cpi.find((r) => r[0] === '2022-12'), cpiLast = cpi[cpi.length - 1];
  const elecChg = cpiBase && cpiLast ? (cpiLast[2] / cpiBase[2] - 1) * 100 : null;
  const pipesBoth = F.pipelines.filter((p) => num(p.contracted_gw) && num(p.total_pipeline_gw));
  const signedShare = pipesBoth.length ? (d3.sum(pipesBoth, (p) => num(p.contracted_gw)) / d3.sum(pipesBoth, (p) => num(p.total_pipeline_gw))) * 100 : null;
  const capexProj = d3.sum(F.capexIndustry.filter((c) => c.kind === 'projected'), (c) => c.usd);
  const capexPast = d3.sum(F.capexIndustry.filter((c) => c.kind === 'actual'), (c) => c.usd);
  const roeLast = F.roe[F.roe.length - 1];
  const roeFirstUst = F.roe.find((r) => r.ust != null);
  const projLevel = F.projects.filter((p) => p.level === 'project').sort((a, b) => b.cost_usd - a.cost_usd);
  const pkgs = F.projects.filter((p) => p.level === 'package');
  const burdenBins = F.burden.filter((b) => b.type === 'ami_bin');
  const lowest = burdenBins[0], highest = burdenBins[burdenBins.length - 1];
  const shutNat = F.shutState.reduce((t, s) => t + s.d, 0) / F.shutState.reduce((t, s) => t + (s.cust || 0), 0) * 100;
  const heat = F.polls.filter((p) => /heatmap/i.test(p.pollster || ''));
  const firstNum = (v) => { const m = String(v ?? '').match(/\d+(\.\d+)?/); return m ? +m[0] : null; };
  const oppSeries = [];
  heat.forEach((p) => Object.entries(p.results || {}).forEach(([k, v]) => {
    if (!/^oppose/i.test(k)) return;
    if (v && typeof v === 'object') Object.entries(v).forEach(([ym, x]) => { if (/^\d{4}-\d{2}$/.test(ym) && firstNum(x) != null) oppSeries.push([ym, firstNum(x)]); });
    else if (firstNum(v) != null && p.field_dates) oppSeries.push([String(p.field_dates).slice(0, 7), firstNum(v)]);
  }));
  const opp = [...new Map(oppSeries.sort((a, b) => a[0].localeCompare(b[0])).map((r) => [r[0], r])).values()];
  const tax = Object.entries(policy.states).filter(([, s]) => s.inc?.cost).map(([k, s]) => ({ st: k, name: s.name, cost: s.inc.cost, yr: s.inc.costYear, type: s.inc.type })).sort((a, b) => b.cost - a.cost);
  const tln = F.stocks.find((s) => s.t === 'TLN');

  const findings = [
    {
      theme: 'bill', big: `${dd26.toFixed(0)}%`, cls: 'up', title: 'Double-digit increases are back',
      lede: `So far in 2026, <b>${dd26.toFixed(0)}%</b> of utilities are charging homes at least 10% more than a year ago. In 2024 it was <b>${dd24}%</b>. The last time it was this common was the 2022 gas-price spike (${dd22}%).`,
      why: 'Big jumps used to be rare outside fuel shocks. This year’s are spread across many utilities at once.',
      src: 'EIA-861 (annual), EIA-861M (2026 so far)',
      render: (el) => columns(el, { height: 250, yFmt: (v) => `${v}%`, label: 'Share of utilities with 10%+ increases', data: [...F.doubleDigit.map((d) => ({ x: d.y, y: d.share, color: d.y === '2022' ? '#f29890' : C.base, tip: `<b>${d.y}</b><div>${d.share}% of ${d.n} utilities rose 10%+</div>` })), { x: '2026*', y: +dd26.toFixed(1), color: C.up, top: `${dd26.toFixed(0)}%`, tip: `<b>2026 so far</b><div>${dd26.toFixed(1)}% of ${withYtd.length} utilities reporting monthly</div>` }] }),
      foot: '*2026 compares the same months of 2026 and 2025.',
    },
    {
      theme: 'bill', big: `${pct(wmed(pjm), 0)} vs ${pct(wmed(rest), 0)}`, cls: 'up', title: 'The 2026 jump is concentrated in PJM',
      lede: `For a typical home served by a large utility in PJM, the grid with the most data-center demand, prices are up <b>${pct(wmed(pjm), 1)}</b> in 2026. Everywhere else the typical home sees <b>${pct(wmed(rest), 1)}</b>.`,
      why: 'PJM is where capacity costs tied to data-center demand reach default-service bills every June.',
      src: 'EIA-861M; utilities with 100,000+ homes; dot size = homes served',
      render: (el) => strip2(el, [{ label: 'PJM', color: C.up, med: wmed(pjm), points: pjm.map((e) => ({ v: e.ytd, c: e.c, n: shortName(e.n), st: e.st })) }, { label: 'Elsewhere', color: C.down, med: wmed(rest), points: rest.map((e) => ({ v: e.ytd, c: e.c, n: shortName(e.n), st: e.st })) }]),
    },
    {
      theme: 'dc', big: `+${Math.round(F.salesGrowth[0].ci)}%`, cls: 'up', title: 'The new demand isn’t coming from homes',
      lede: `At data-center hotspots, commercial and industrial sales are soaring while homes barely move. ${esc(clean(F.salesGrowth[0].u))}: <b>+${Math.round(F.salesGrowth[0].ci)}%</b> commercial & industrial since ${F.salesGrowth[0].base}, against <b>${pct(F.salesGrowth[0].res, 1)}</b> for homes.`,
      why: 'Grid upgrades for that new load are often shared with households.',
      src: 'EIA-861, commercial + industrial vs residential sales',
      html: () => paired(F.salesGrowth.slice(0, 8).map((s) => ({ label: clean(s.u), sub: s.st, a: s.ci, b: s.res, tip: s.hot })), { a: { label: 'Commercial & industrial sales', color: C.s[1] }, b: { label: 'Home sales', color: C.s[0] } }),
    },
    {
      theme: 'dc', big: `${F.ciRank[0].twh} TWh`, title: 'Where the new power demand landed',
      lede: `${esc(clean(F.ciRank[0].u))} added <b>${F.ciRank[0].twh} TWh</b> of commercial and industrial demand since ${F.ciRank[0].base}, more than many states use in a year. Texas and Virginia utilities dominate the list.`,
      why: 'This is the load that drives new plants, new lines and capacity prices.',
      src: 'EIA-861; added commercial + industrial sales',
      html: () => barList(F.ciRank.slice(0, 10).map((r) => ({ label: clean(r.u), sub: r.st, value: r.twh, color: /PJM/.test(r.ba) ? C.up : /ERCO/.test(r.ba) ? C.s[1] : C.base, tip: `C&I ${pct(r.ci, 0)}, homes ${pct(r.res, 0)}` })), { fmt: (v) => `${v} TWh` }) + '<p class="note">Red: PJM · Orange: ERCOT (Texas) · Gray: other grids</p>',
    },
    {
      theme: 'dc', big: `${F.international[0].dc_share_pct}%`, title: 'Virginia and Ireland are the canaries',
      lede: `Data centers use <b>${F.international[0].dc_share_pct}%</b> of Ireland’s electricity and about <b>${(grid.loadShare.VA?.pct || 25.6).toFixed(0)}%</b> of Virginia’s. Ireland went from ${F.international[0].series?.['2015'] ?? 5}% in 2015 to ${F.international[0].dc_share_pct}% in ${F.international[0].year}, and paused new grid connections around Dublin.`,
      why: 'They show what happens to a grid when data centers become a quarter of demand.',
      src: 'Ireland CSO; EPRI (US states, 2023)',
      tabs: { Countries: () => barList(F.international.filter((p) => p.dc_share_pct).sort((a, b) => b.dc_share_pct - a.dc_share_pct).map((p) => ({ label: p.country, sub: p.year ? String(p.year) : '', value: p.dc_share_pct, color: p.iso2 === 'IE' ? C.up : C.s[1] })), { fmt: (v) => `${+(+v).toFixed(1)}%` }),
        'US states': () => barList(Object.entries(grid.loadShare).sort((a, b) => b[1].pct - a[1].pct).slice(0, 10).map(([k, v]) => ({ label: STATE_NAMES[k] || k, value: v.pct, color: k === 'VA' ? C.up : C.s[1] })), { fmt: (v) => `${v.toFixed(1)}%` }) },
    },
    {
      theme: 'dc', big: signedShare ? `${Math.round(signedShare)}%` : '?', title: 'Data-center pipelines are mostly promises',
      lede: `Utilities advertise huge data-center pipelines, but only about <b>${Math.round(signedShare)}%</b> of the gigawatts is under signed contract at the utilities that report both. In Texas, ERCOT has <b>474 GW</b> of large-load requests, and only 205 GW is eligible for its first study batch.`,
      why: 'Planning and capacity markets that use inflated forecasts can push costs onto everyone, which is why PJM tightened its forecast rules.',
      src: 'Utility earnings and filings via press (several unverified); ERCOT',
      html: () => paired(F.pipelines.filter((p) => num(p.total_pipeline_gw) || num(p.contracted_gw)).sort((a, b) => (num(b.total_pipeline_gw) || 0) - (num(a.total_pipeline_gw) || 0)).slice(0, 8).map((p) => ({ label: clean(p.utility), sub: p.state, a: num(p.total_pipeline_gw), b: num(p.contracted_gw), tip: `${p.contracted_definition || ''} · as of ${p.as_of || ''}` })), { a: { label: 'Total pipeline (GW)', color: C.base }, b: { label: 'Signed / contracted (GW)', color: C.up }, fmtV: (v) => `${v} GW` }),
    },
    {
      theme: 'money', big: tln ? `+${Math.round(tln.chg)}%` : '', cls: 'up', title: 'Power producers’ stocks vs. your bill',
      lede: `Since the end of 2022, shares of power producers that sell into PJM’s capacity market soared: Talen <b>+${Math.round(tln?.chg)}%</b>, Vistra <b>+${Math.round(F.stocks.find((s) => s.t === 'VST')?.chg)}%</b>. Your electricity price index rose <b>${fmt.pct(elecChg, 0, false)}</b>.`,
      why: 'Scarcity is profitable for whoever owns the plants. Stock moves also reflect AI hopes and nuclear deals, so read this as context, not cause.',
      src: 'Nasdaq closing prices (not dividend-adjusted); BLS CPI electricity',
      tabs: Object.fromEntries([['Today', 'chg'], ['At peak', 'peak']].map(([lab, key]) => [lab, () => barList([...['TLN', 'VST', 'NRG', 'CEG', 'GEV', 'SPY', 'XLU', 'AEP', 'D', 'EXC'].map((t) => F.stocks.find((s) => s.t === t)).filter(Boolean).map((s) => ({ label: s.n, sub: s.g.startsWith('IPP') ? 'power producer' : s.g.split(':')[0].replace('regulated utility holding co.', 'utility'), value: s[key], color: s.g.startsWith('IPP') ? C.up : /benchmark/.test(s.g) ? C.ink2 : C.base })), { label: 'Your electricity price (CPI)', sub: '', value: elecChg, color: C.s[0] }].sort((a, b) => b.value - a.value), { fmt: (v) => pct(v, 0) })])),
    },
    {
      theme: 'money', big: fmt.big(capexProj), title: 'The utility spending wave',
      lede: `US investor-owned utilities plan to spend <b>${fmt.big(capexProj)}</b> in 2026–30. That’s five years of spending nearly matching the previous ten (${fmt.big(capexPast)} in ${F.capexIndustry[0].y}–2025). Utilities earn an allowed return on every dollar that goes into their rate base.`,
      why: 'That spending becomes your bill for the next 30–40 years. Data centers are one of the main stated reasons.',
      src: 'EEI industry capex (actual and projected); company plans',
      render: (el) => columns(el, { height: 250, yFmt: (v) => `$${Math.round(v / 1e9)}B`, label: 'Utility capex by year', data: F.capexIndustry.map((c) => ({ x: c.y, y: c.kind === 'actual' ? c.usd : null, ghost: c.kind === 'projected' ? c.usd : null, color: c.kind === 'actual' ? C.base : C.up, tip: `<b>${c.y}</b><div>${fmt.big(c.usd)} ${c.kind}</div>` })) }),
      foot: 'Gray bars: actual. Dashed red outlines: projected.',
    },
    {
      theme: 'money', big: `${roeLast.roe}%`, title: 'Allowed profits barely move when interest rates do',
      lede: `Regulators let utilities earn about <b>${roeLast.roe}%</b> on equity in ${roeLast.y}, almost unchanged in a decade, while 10-year Treasury yields swung from under 1% to over 4%. ${roeLast.share ? `Utilities also got about <b>${Math.round(roeLast.share)}%</b> of the rate increases they asked for.` : ''}`,
      why: 'A peer-reviewed 2026 study estimates returns set above the cost of capital cost customers about $7B a year.',
      src: 'EEI Rate Review (authorized ROE); US Treasury 10-year',
      legend: [['Allowed return on equity', C.up], ['10-year Treasury yield', C.s[0]]],
      render: (el) => lineChart(el, { height: 250, yMin: 0, yFmt: (v) => `${(+v).toFixed(0)}%`, label: 'ROE vs Treasury', series: [{ key: 'roe', label: 'Allowed return', color: C.up, width: 3, emph: true, values: F.roe.map((r) => [r.y, r.roe]) }, { key: 'ust', label: '10-yr Treasury', color: C.s[0], values: F.roe.filter((r) => r.ust != null).map((r) => [r.y, r.ust]) }] }),
    },
    {
      theme: 'people', big: fmt.big(d3.sum(pkgs, (p) => p.cost_usd)), title: 'Who pays for the new power lines',
      lede: `The biggest new power lines in our data cost billions each. PJM’s last three planning packages alone total <b>${fmt.big(d3.sum(pkgs, (p) => p.cost_usd))}</b>, much of it driven by data-center load. The largest lines are split across the region, so Maryland and New Jersey households help pay for lines serving Virginia.`,
      why: 'Lines last decades, and residents pay through transmission charges no matter where the data center is.',
      src: 'PJM RTEP reports; Maryland OPC; grid research (some project details unverified)',
      html: () => `<div class="projects">${projLevel.slice(0, 5).map((p) => `<div class="proj"><div class="proj-h"><b>${esc(p.project.replace(/\s*\(.*$/, '').replace(/^Dominion HVDC /, 'Dominion HVDC line '))}</b><span class="amt">${fmt.big(p.cost_usd)}</span></div><div class="proj-m">${esc(p.region || '')}${p.voltage_kv ? ` · ${esc(String(p.voltage_kv))} kV` : ''}</div><div class="proj-a"><span class="badge ${/^stated/.test(p.dc_link_type || '') ? 'pjm' : ''}">${linkLabel(p.dc_link_type)}</span> ${esc(whoPays(p.cost_allocation))}</div></div>`).join('')}</div>`,
    },
    {
      theme: 'people', big: `${Math.round(lowest.pct)}%`, cls: 'up', title: 'The poorest pay the most, by far',
      lede: `Households below 30% of area median income spend <b>${Math.round(lowest.pct)}%</b> of their income on energy. The best-off spend <b>${highest.pct.toFixed(1)}%</b>, about ${Math.round(lowest.pct / highest.pct)}× less. Every cent added to the price per kWh hits the bottom hardest.`,
      why: 'Rate increases that look small on average can be large for the families least able to pay.',
      src: 'DOE LEAD tool (2022 update); AMI = area median income',
      html: () => barList(burdenBins.map((b) => ({ label: b.g.replace('AMI', 'of area income'), value: b.pct, color: b === lowest ? C.up : C.s[0], tip: `Avg income ${fmt.usd(b.inc)}, energy ${fmt.usd(b.cost)}/yr` })), { fmt: (v) => `${v.toFixed(1)}%` }),
    },
    {
      theme: 'people', big: `${F.shutState[0].per100.toFixed(0)}<small> per 100 homes</small>`, title: 'Where the power gets shut off',
      lede: `In 2024, the first year the federal government counted, ${STATE_NAMES[F.shutState[0].st]} utilities logged <b>${F.shutState[0].per100.toFixed(1)}</b> disconnections per 100 homes. The national rate was about <b>${shutNat.toFixed(1)}</b>. Shutoffs are about affordability in general; we don’t attribute them to data centers.`,
      why: 'Shows where higher bills meet households that are already falling behind.',
      src: 'EIA-112 (2024); events per 100 residential customers',
      html: () => barList(F.shutState.slice(0, 10).map((s) => ({ label: STATE_NAMES[s.st] || s.st, value: s.per100, color: C.up, tip: `${fmt.int(s.d)} disconnections` })), { fmt: (v) => v.toFixed(1) }),
    },
    {
      theme: 'people', big: opp.length >= 2 ? `${opp[0][1]}% → ${opp[opp.length - 1][1]}%` : '7 in 10', title: 'Public opinion flipped in a year',
      lede: `In Heatmap/Embold polling, opposition to a data center being built nearby went from about <b>${opp[0]?.[1] ?? 40}%</b> to <b>${opp[opp.length - 1]?.[1] ?? 70}%</b> of registered voters. Electricity prices were a central issue in the 2025 New Jersey and Virginia elections.`,
      why: 'Bills are now political, which is why states are rushing to pass large-load tariffs.',
      src: 'Embold Research for Heatmap (some readings via press summaries); other polls listed in the research',
      render: opp.length >= 2 ? (el) => columns(el, { height: 220, yFmt: (v) => `${Math.round(v)}%`, label: 'Share opposing a data center nearby', data: opp.map(([ym, v], i) => ({ x: fmt.month(ym), y: v, top: `${v}%`, color: i === opp.length - 1 ? C.up : '#f29890', tip: `<b>${fmt.month(ym)}</b><div>${v}% oppose a data center nearby</div>` })) }) : null,
    },
    {
      theme: 'people', big: tax[0] ? fmt.big(tax[0].cost) : '', title: 'The tax-break bill',
      lede: `States compete for data centers with sales-tax exemptions. ${tax[0] ? `${esc(tax[0].name)}’s costs about <b>${fmt.big(tax[0].cost)}</b> a year` : ''}${tax[1] ? `, ${esc(tax[1].name)}’s about <b>${fmt.big(tax[1].cost)}</b>` : ''}. In 2026, at least 8 states curbed theirs, and Maine repealed its own.`,
      why: 'Tax breaks are money states don’t collect, so other taxpayers make up the difference.',
      src: 'State fiscal notes and Good Jobs First via policy research (some unverified)',
      html: () => barList(tax.slice(0, 10).map((t) => ({ label: t.name, value: t.cost, color: C.s[3], tip: `${t.type || ''} (${t.yr || ''})` })), { fmt: (v) => fmt.big(v) }),
    },
  ];

  // stats + filters
  $('#f-stats').innerHTML = [[findings.length, 'findings'], ['47', 'datasets'], [fmt.int(index.length), 'utilities'], [grid.studies.length, 'studies weighed']].map(([v, k]) => `<div><b>${v}</b><span>${k}</span></div>`).join('');
  const counts = Object.fromEntries(Object.keys(THEMES).map((t) => [t, findings.filter((f) => f.theme === t).length]));
  $('#f-filters').innerHTML = `<button aria-pressed="true" data-t="all">All ${findings.length}</button>${Object.entries(THEMES).map(([k, v]) => `<button aria-pressed="false" data-t="${k}">${v} <small>${counts[k]}</small></button>`).join('')}`;

  const grid0 = $('#f-grid');
  grid0.innerHTML = findings.map((f, i) => `
    <article class="fcard" data-theme="${f.theme}" style="--d:${(i % 2) * 80}ms">
      <div class="f-top"><span class="f-theme t-${f.theme}">${THEMES[f.theme]}</span><span class="f-no">${String(i + 1).padStart(2, '0')}</span></div>
      <div class="f-big ${f.cls || ''}">${f.big}</div>
      <h2 class="f-title">${f.title}</h2>
      <p class="f-lede">${f.lede}</p>
      ${f.tabs ? `<div class="seg f-tabs" role="group">${Object.keys(f.tabs).map((k, j) => `<button aria-pressed="${j === 0}" data-k="${esc(k)}">${esc(k)}</button>`).join('')}</div>` : ''}
      ${f.legend ? `<div class="legend">${f.legend.map(([l, c]) => `<span><i style="--c:${c}"></i>${esc(l)}</span>`).join('')}</div>` : ''}
      <div class="f-viz" id="fv-${i}"></div>
      ${f.foot ? `<p class="note">${f.foot}</p>` : ''}
      <p class="f-why"><b>Why it matters:</b> ${f.why}</p>
      <p class="f-src">Source: ${esc(f.src)}</p>
    </article>`).join('');
  const drawn = new Set();
  const drawCard = (i) => {
    if (drawn.has(i)) return;
    drawn.add(i);
    const f = findings[i], el = $(`#fv-${i}`);
    if (f.render) f.render(el);
    else if (f.html) el.innerHTML = f.html();
    else if (f.tabs) {
      const show = (k) => { el.innerHTML = f.tabs[k](); };
      show(Object.keys(f.tabs)[0]);
      $$('.f-tabs button', el.parentElement).forEach((b) => b.addEventListener('click', () => { $$('.f-tabs button', el.parentElement).forEach((x) => x.setAttribute('aria-pressed', String(x === b))); show(b.dataset.k); }));
    }
  };
  const io = new IntersectionObserver((ents) => ents.forEach((e) => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in');
    drawCard(+e.target.querySelector('.f-viz').id.slice(3));
    io.unobserve(e.target);
  }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
  $$('.fcard').forEach((c) => io.observe(c));
  $$('#f-filters button').forEach((b) => b.addEventListener('click', () => {
    $$('#f-filters button').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    $$('.fcard').forEach((c) => { const show = b.dataset.t === 'all' || c.dataset.theme === b.dataset.t; c.hidden = !show; if (show) { c.classList.add('in'); drawCard(+c.querySelector('.f-viz').id.slice(3)); } });
  }));
  addEventListener('scroll', () => $('.topbar').classList.toggle('scrolled', scrollY > 8), { passive: true });
}
main().catch((e) => { console.error(e); $('#f-grid').innerHTML = '<p class="note">Couldn’t load the findings data.</p>'; });
