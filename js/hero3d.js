// Hero: 3D spike map of how much more the same electricity costs than in 2020, then the data-center slice in PJM.
// Canvas 2D with a small perspective camera; draws ~14k spikes per frame in grouped fills.
/* global d3, topojson */
const $ = (s) => document.querySelector(s);
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SPEED = Math.min(4, Math.max(0.25, +new URLSearchParams(location.search).get('speed') || 1)); // story speed (for recordings)

const W0 = 975, H0 = 610;
const HS = 0.95; // world units per $ a month
const RAMP = ['#fff3b0', '#ffe36e', '#ffd60a', '#ffb21f', '#ff8a2a', '#ff6235', '#f23f43', '#d92a44', '#b81d45'];
const STEPS = [6, 14, 22, 30, 38, 47, 58, 72];
const bucket = (v) => { let i = 0; while (i < STEPS.length && v > STEPS[i]) i++; return i; };
const lerp = (a, b, t) => a + (b - a) * t;
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const seg = (t, a, b) => ease(Math.min(1, Math.max(0, (t - a) / (b - a))));
export const money = (v) => `${v < 0 ? '−' : '+'}$${Math.abs(v).toFixed(0)}`;
const L48 = (lon, lat) => lon > -125.5 && lon < -66 && lat > 24 && lat < 49.6;

export async function initHero() {
  const proj = d3.geoAlbersUsa().scale(1300).translate([W0 / 2, H0 / 2]);
  const TO_PJM = RAMP.map((c) => d3.interpolateRgb(c, '#8c6c3e')), TO_DIM = RAMP.map((c) => d3.interpolateRgb(c, '#4e545e'));
  const [S, us] = await Promise.all([
    fetch('assets/data/spikes.json').then((r) => r.json()),
    fetch('https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-10m.json').then((r) => r.json()),
  ]);

  // cells
  const N0 = S.z.length;
  const X = new Float32Array(N0), Y = new Float32Array(N0), UI = new Uint16Array(N0), PJM = new Uint8Array(N0);
  let N = 0;
  for (const [lon, lat, ui] of S.z) {
    if (!L48(lon, lat)) continue;
    const p = proj([lon, lat]);
    if (!p) continue;
    X[N] = p[0] - W0 / 2; Y[N] = p[1] - H0 / 2; UI[N] = ui; PJM[N] = S.u[ui][2] === 'PJM' ? 1 : 0; N++;
  }
  const NU = S.u.length;
  const UV = new Float32Array(NU), UDC = Float32Array.from(S.u, (u) => u[4]);
  const SX = new Float32Array(N), SY = new Float32Array(N), TX = new Float32Array(N), TY = new Float32Array(N);
  const SW = new Float32Array(N), GI = new Int32Array(19 * N), GC = new Int32Array(19);
  const LX = new Float32Array(N), LY = new Float32Array(N), LW = new Float32Array(N), LI = new Int32Array(N);
  let TIPN = 0;

  // outlines (decimated, world coords)
  const toLines = (mls, minD = 1.6) => mls.coordinates.map((line) => {
    const o = []; let lx = 1e9, ly = 1e9;
    for (const c of line) {
      const p = proj(c);
      if (!p) continue;
      const x = p[0] - W0 / 2, y = p[1] - H0 / 2;
      if (Math.hypot(x - lx, y - ly) < minD) continue;
      o.push(x, y); lx = x; ly = y;
    }
    return Float32Array.from(o);
  }).filter((a) => a.length >= 4);
  const st48 = { type: 'GeometryCollection', geometries: us.objects.states.geometries.filter((g) => !['02', '15', '72', '78', '60', '66', '69'].includes(g.id)) };
  const inner = toLines(topojson.mesh(us, st48, (a, b) => a !== b));
  const outer = toLines(topojson.mesh(us, st48, (a, b) => a === b), 1.2);

  // campuses + labels
  const DCS = S.dcs.map(([lon, lat, mw]) => { const p = L48(lon, lat) && proj([lon, lat]); return p && { x: p[0] - W0 / 2, y: p[1] - H0 / 2, h: 26 + 15 * Math.log10(Math.max(100, mw || 300)) }; }).filter(Boolean);
  const wpt = (lon, lat) => { const p = proj([lon, lat]); return { x: p[0] - W0 / 2, y: p[1] - H0 / 2 }; };
  const PJMC = wpt(-79.0, 39.7);
  const LABELS = [
    { ...wpt(-82.6, 40.4), t: 'PJM GRID · 13 STATES + DC', big: true },
    { ...wpt(-77.49, 39.03), t: 'Northern Virginia · world’s largest data-center hub', lead: 92 },
  ];

  // canvas + camera
  const stage = $('#h3-stage'), cv = $('#h3-cv'), ctx = cv.getContext('2d');
  let W = 0, H = 0, DPR = 1, K = 1, CX = 0, CY = 0, PORTRAIT = false, WIDE = false, vignette, scrimB, scrimT, scrimR;
  function resize() {
    DPR = Math.min(2, devicePixelRatio || 1);
    W = stage.clientWidth; H = stage.clientHeight;
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    PORTRAIT = H / W > 0.9; WIDE = !PORTRAIT && W >= 980;
    K = PORTRAIT ? (W * 1.45) / W0 : WIDE ? Math.min((W * 0.62) / W0, (H * 0.95) / H0) : Math.min((W * 0.86) / W0, (H * 1.02) / H0);
    CX = WIDE ? W * 0.63 : W / 2; CY = H * (PORTRAIT ? 0.5 : 0.57);
    scrimB = ctx.createLinearGradient(0, H * 0.74, 0, H); scrimB.addColorStop(0, 'rgba(8,9,11,0)'); scrimB.addColorStop(1, 'rgba(8,9,11,0.92)');
    scrimT = ctx.createRadialGradient(0, H * 0.35, 0, 0, H * 0.35, Math.max(560, W * 0.46)); scrimT.addColorStop(0, 'rgba(8,9,11,0.88)'); scrimT.addColorStop(0.6, 'rgba(8,9,11,0.55)'); scrimT.addColorStop(1, 'rgba(8,9,11,0)');
    scrimR = ctx.createRadialGradient(W, 0, 0, W, 0, 420); scrimR.addColorStop(0, 'rgba(8,9,11,0.8)'); scrimR.addColorStop(1, 'rgba(8,9,11,0)');
    vignette = ctx.createRadialGradient(CX, H * 0.55, Math.min(W, H) * 0.2, CX, H * 0.55, Math.max(W, H) * 0.8);
    vignette.addColorStop(0, 'rgba(22,24,30,0)'); vignette.addColorStop(1, 'rgba(0,0,0,0.6)');
  }
  new ResizeObserver(resize).observe(stage); resize();

  const cam = { yaw: 0, pitch: 0, zoom: 0.72, tx: 0, ty: 0 };
  let cy_ = 1, sy_ = 0, cp_ = 1, sp_ = 0, KZ = 1;
  const F = 1600, out = [0, 0, 0];
  function P(x, y, z) {
    const x0 = x - cam.tx, y0 = y - cam.ty;
    const x1 = x0 * cy_ - y0 * sy_, y1 = x0 * sy_ + y0 * cy_;
    const vy = y1 * cp_ - z * sp_, vz = y1 * sp_ + z * cp_;
    const s = (F / (F - vz)) * KZ;
    out[0] = CX + x1 * s; out[1] = CY + vy * s; out[2] = s;
    return out;
  }

  // story: prices grow 2020 -> 2026, then the camera flies to PJM and shows the data-center slice
  const LOOP = 19800;
  const story = (t) => {
    const tilt = seg(t, 900, 4000), grow = seg(t, 1200, 7200), toDc = seg(t, 9000, 11000), back = seg(t, 16000, 18200);
    const zd = PORTRAIT ? 1.9 : 1.85, focus = toDc * (1 - back);
    return {
      alpha: seg(t, 0, 900) * (1 - seg(t, 19000, LOOP)), yf: 6 * grow,
      pitch: lerp(0, 0.98, tilt) - 0.08 * focus, zoom: lerp(lerp(0.72, 1, tilt), zd, focus),
      tx: PJMC.x * focus, ty: PJMC.y * focus, yaw: 0.07 * Math.sin(t / 3800) - 0.16 * focus,
      dc: toDc, beams: seg(t, 9500, 11800), labels: seg(t, 10800, 12000) * (1 - back),
      scene: t < 9000 ? 'grow' : t < 16000 ? 'dc' : 'end',
    };
  };
  let t = REDUCED ? 13000 : 0, playing = !REDUCED, manual = null;
  const cur = story(t), user = { yaw: 0, pitch: 0 };

  function draw(p, now) {
    cam.yaw = p.yaw + user.yaw; cam.pitch = Math.max(0, Math.min(1.25, p.pitch + user.pitch)); cam.zoom = p.zoom; cam.tx = p.tx; cam.ty = p.ty;
    cy_ = Math.cos(cam.yaw); sy_ = Math.sin(cam.yaw); cp_ = Math.cos(cam.pitch); sp_ = Math.sin(cam.pitch); KZ = K * cam.zoom;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    ctx.fillStyle = '#08090b'; ctx.fillRect(0, 0, W, H);
    const A = p.alpha;
    ctx.lineJoin = 'round';
    const stroke = (lines, style, lw) => {
      ctx.beginPath();
      for (const a of lines) { P(a[0], a[1], 0); ctx.moveTo(out[0], out[1]); for (let i = 2; i < a.length; i += 2) { P(a[i], a[i + 1], 0); ctx.lineTo(out[0], out[1]); } }
      ctx.strokeStyle = style; ctx.lineWidth = lw; ctx.stroke();
    };
    ctx.globalAlpha = A;
    stroke(inner, 'rgba(160,170,190,0.16)', 0.7);
    stroke(outer, 'rgba(190,200,220,0.38)', 1);
    const i0 = Math.floor(p.yf), f = p.yf - i0, i1 = Math.min(6, i0 + 1);
    for (let u = 0; u < NU; u++) { const d = S.u[u][3]; UV[u] = d[i0] + (d[i1] - d[i0]) * f; }
    ctx.fillStyle = 'rgba(150,162,182,0.42)'; ctx.beginPath();
    for (let i = 0; i < N; i++) { P(X[i], Y[i], 0); const r = Math.max(0.5, 0.55 * out[2]); ctx.rect(out[0] - r / 2, out[1] - r / 2, r, r); }
    ctx.fill();
    const dcOn = p.dc > 0.01;
    GC.fill(0); TIPN = 0;
    for (let i = 0; i < N; i++) {
      const u = UI[i], v = UV[u], z = v * HS;
      P(X[i], Y[i], 0); const bx = out[0], by = out[1], s = out[2];
      P(X[i], Y[i], z);
      SX[i] = bx; SY[i] = by; TX[i] = out[0]; TY[i] = out[1]; SW[i] = Math.max(0.45, 0.62 * s);
      const g = v < 0 ? 18 : PJM[i] * 9 + bucket(v);
      GI[g * N + GC[g]++] = i;
      if (dcOn && PJM[i] && v > 0) {
        const dz = Math.min(UDC[u], v) * HS;
        P(X[i], Y[i], z - dz); LX[TIPN] = out[0]; LY[TIPN] = out[1]; LW[TIPN] = SW[i] * Math.max(0.6, dz / z); LI[TIPN++] = i;
      }
    }
    const fillGroup = (g, color, alpha) => {
      const n = GC[g]; if (!n || alpha <= 0.003) return;
      ctx.globalAlpha = alpha; ctx.fillStyle = color; ctx.beginPath();
      for (let k = 0, o = g * N; k < n; k++) { const i = GI[o + k], w = SW[i]; ctx.moveTo(SX[i] - w, SY[i]); ctx.lineTo(TX[i], TY[i]); ctx.lineTo(SX[i] + w, SY[i]); }
      ctx.fill();
    };
    ctx.globalCompositeOperation = 'lighter';
    for (let b = 0; b < 9; b++) { fillGroup(b, TO_DIM[b](p.dc), A * 0.5 * (1 - 0.55 * p.dc)); fillGroup(9 + b, TO_PJM[b](p.dc), A * 0.5); }
    fillGroup(18, '#3987e5', A * 0.7);
    if (TIPN) {
      ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = A * 0.95 * p.dc; ctx.fillStyle = '#ff2d43'; ctx.beginPath();
      for (let k = 0; k < TIPN; k++) { const i = LI[k]; ctx.moveTo(LX[k] - LW[k], LY[k]); ctx.lineTo(TX[i], TY[i]); ctx.lineTo(LX[k] + LW[k], LY[k]); }
      ctx.fill();
    }
    if (p.beams > 0.01) {
      ctx.globalCompositeOperation = 'lighter';
      DCS.forEach((d, k) => {
        P(d.x, d.y, 0); const bx = out[0], by = out[1], s = out[2];
        P(d.x, d.y, d.h * p.beams); const tx = out[0], ty = out[1];
        const g = ctx.createLinearGradient(bx, by, tx, ty);
        g.addColorStop(0, 'rgba(150,215,255,0.95)'); g.addColorStop(1, 'rgba(150,215,255,0)');
        ctx.globalAlpha = A * p.beams;
        ctx.strokeStyle = 'rgba(120,190,255,0.10)'; ctx.lineWidth = 3.5 * Math.min(1.3, s); ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke();
        ctx.strokeStyle = g; ctx.lineWidth = 1.1 * Math.min(1.3, s); ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke();
        const ph = ((now / 1600) + k * 0.137) % 1, r = (2 + 7 * ph) * Math.min(1.8, s);
        ctx.globalAlpha = A * p.beams * (1 - ph) * 0.8; ctx.strokeStyle = '#9fdcff'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.ellipse(bx, by, r, r * Math.max(0.2, cp_), 0, 0, Math.PI * 2); ctx.stroke();
      });
    }
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    ctx.fillStyle = vignette; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = scrimB; ctx.fillRect(0, H * 0.74, W, H * 0.26);
    if (WIDE) { ctx.fillStyle = scrimT; ctx.fillRect(0, 0, W, H); ctx.fillStyle = scrimR; ctx.fillRect(W - 420, 0, 420, 420); }
    if (p.labels > 0.01) {
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      LABELS.forEach((l) => {
        P(l.x, l.y, 0); const bx = out[0], by = out[1], ty = by - (l.lead || 0);
        ctx.globalAlpha = A * p.labels;
        ctx.font = l.big ? '600 12.5px "JetBrains Mono", monospace' : '600 13px Inter, sans-serif';
        const tw = ctx.measureText(l.t).width + 18;
        if (l.lead) {
          ctx.strokeStyle = 'rgba(217,239,255,0.85)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx, ty + 12); ctx.stroke();
          ctx.fillStyle = '#d9efff'; ctx.beginPath(); ctx.arc(bx, by, 3, 0, Math.PI * 2); ctx.fill();
        }
        ctx.fillStyle = 'rgba(8,9,12,0.82)'; ctx.beginPath(); ctx.roundRect(bx - tw / 2, ty - 12, tw, 24, 12); ctx.fill();
        ctx.strokeStyle = l.big ? 'rgba(255,90,95,0.55)' : 'rgba(150,215,255,0.5)'; ctx.lineWidth = 1; ctx.stroke();
        ctx.fillStyle = l.big ? '#ffb3b6' : '#d9efff'; ctx.fillText(l.t, bx, ty + 0.5);
      });
    }
  }

  // overlay text (only touches the DOM when a value changes)
  const set = (el, v) => { if (el && el.textContent !== v) el.textContent = v; };
  const interp = (arr, yf) => { const i = Math.floor(yf), j = Math.min(arr.length - 1, i + 1); return arr[i] + (arr[j] - arr[i]) * (yf - i); };
  const elN = $('#h3-n'), elL = $('#h3-l'), elS = $('#h3-s'), box = $('.hero3d .lookup-box');
  function overlay(p) {
    set($('#h3-yr'), String(2020 + Math.min(6, Math.floor(p.yf + 0.02))));
    set($('#h3-yr-s'), p.yf > 5.5 ? '2026 so far · vs 2020' : 'vs 2020 prices');
    if (p.dc > 0.5) {
      set(elN, `≈$${Math.round(S.pjmDc)}`); elN.classList.add('r');
      set(elL, 'a month of a typical PJM home’s bill traces to data-center demand');
      set(elS, `out of ${money(S.pjm[6])} a month since 2020 · PJM market monitor`);
    } else {
      set(elN, money(interp(S.us, p.yf))); elN.classList.remove('r');
      set(elL, 'a month more for a typical US home than in 2020, for the same electricity');
      set(elS, p.yf > 5.5 ? 'Customer-weighted across 2,000+ utilities' : '');
    }
    $('#h3-lg-dc').style.opacity = 0.3 + 0.7 * p.dc;
    $('#h3-lg-b').style.opacity = 0.3 + 0.7 * p.beams;
    box?.classList.toggle('nudge', p.scene === 'end' && !manual && document.activeElement?.id !== 'addr');
  }

  // loop (paused while the hero is off screen)
  let last = performance.now(), visible = true, raf = 0;
  function frame(now) {
    raf = 0;
    const dt = Math.min(64, now - last); last = now;
    if (manual) {
      const on = manual.dc ? 1 : 0, zd = PORTRAIT ? 1.9 : 1.85;
      cur.yf = lerp(cur.yf, manual.yf, 0.12); cur.dc = lerp(cur.dc, on, 0.1); cur.beams = lerp(cur.beams, on, 0.08); cur.labels = lerp(cur.labels, on, 0.1);
      cur.zoom = lerp(cur.zoom, manual.dc ? zd : 1, 0.06); cur.tx = lerp(cur.tx, manual.dc ? PJMC.x : 0, 0.06); cur.ty = lerp(cur.ty, manual.dc ? PJMC.y : 0, 0.06);
      cur.pitch = lerp(cur.pitch, 0.95, 0.06); cur.yaw = lerp(cur.yaw, manual.dc ? -0.16 : 0, 0.05); cur.alpha = lerp(cur.alpha, 1, 0.1);
      cur.scene = manual.dc ? 'dc' : 'grow';
    } else {
      if (playing) { t += dt * SPEED; if (t > LOOP) t = 0; }
      Object.assign(cur, story(t));
    }
    draw(cur, now);
    overlay(cur);
    if (visible) raf = requestAnimationFrame(frame);
  }
  new IntersectionObserver(([e]) => {
    visible = e.isIntersecting;
    if (visible && !raf) { last = performance.now(); raf = requestAnimationFrame(frame); }
  }).observe(stage);
  raf = requestAnimationFrame(frame);

  // controls
  const bPlay = $('#h3-play'), bDc = $('#h3-dc'), rYear = $('#h3-year');
  const syncPlay = () => { const on = playing && !manual; bPlay.textContent = on ? '❚❚' : '▶'; bPlay.setAttribute('aria-label', on ? 'Pause animation' : 'Play animation'); };
  bPlay.onclick = () => { if (manual) { manual = null; playing = true; bDc.setAttribute('aria-pressed', 'false'); } else playing = !playing; syncPlay(); };
  $('#h3-replay').onclick = () => { manual = null; t = 0; playing = true; user.yaw = user.pitch = 0; bDc.setAttribute('aria-pressed', 'false'); syncPlay(); };
  rYear.oninput = () => { manual = { yf: +rYear.value - 2020, dc: manual ? manual.dc : cur.dc > 0.5 }; syncPlay(); };
  bDc.onclick = () => { const on = bDc.getAttribute('aria-pressed') !== 'true'; bDc.setAttribute('aria-pressed', String(on)); manual = { yf: manual ? manual.yf : +rYear.value - 2020, dc: on }; syncPlay(); };
  syncPlay();

  // drag to turn, hover to inspect
  let drag = null;
  const tip = $('#tip');
  stage.addEventListener('pointerdown', (e) => { if (e.target.closest('.h3-ctrl')) return; drag = { x: e.clientX, y: e.clientY, yaw: user.yaw, pitch: user.pitch }; stage.classList.add('drag'); });
  addEventListener('pointerup', () => { drag = null; stage.classList.remove('drag'); });
  stage.addEventListener('pointermove', (e) => {
    if (drag) { user.yaw = drag.yaw + (e.clientX - drag.x) * 0.004; user.pitch = Math.max(-0.9, Math.min(0.3, drag.pitch + (e.clientY - drag.y) * 0.003)); tip.hidden = true; return; }
    if (e.pointerType === 'touch' || e.target.closest('.h3-ctrl')) { tip.hidden = true; return; }
    const r = stage.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
    let best = -1, bd = 36;
    for (let i = 0; i < N; i++) {
      const ax = SX[i], ay = SY[i], bx = TX[i], by = TY[i];
      if (mx < Math.min(ax, bx) - 6 || mx > Math.max(ax, bx) + 6 || my < Math.min(ay, by) - 6 || my > Math.max(ay, by) + 6) continue;
      const vx = bx - ax, vy = by - ay, l2 = vx * vx + vy * vy || 1;
      const k = Math.max(0, Math.min(1, ((mx - ax) * vx + (my - ay) * vy) / l2));
      const dx = ax + k * vx - mx, dy = ay + k * vy - my, d = dx * dx + dy * dy;
      if (d < bd) { bd = d; best = i; }
    }
    if (best < 0) { tip.hidden = true; return; }
    const u = S.u[UI[best]], v = UV[UI[best]], yr = 2020 + Math.min(6, Math.round(cur.yf));
    tip.innerHTML = `<b>${u[0]}</b> <span class="m">${u[1]}</span><div>${money(v)} a month vs 2020</div><div class="m">same ${u[5]} kWh/month · ${yr}${yr === 2026 ? ' so far' : ''}</div>${u[2] === 'PJM' && cur.dc > 0.5 ? `<div class="dcx">≈ $${u[4].toFixed(0)} of it: data-center demand</div>` : ''}`;
    tip.hidden = false;
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    tip.style.left = `${Math.min(innerWidth - tw - 8, e.clientX + 14)}px`; tip.style.top = `${Math.max(8, e.clientY - th - 12)}px`;
  });
  stage.addEventListener('pointerleave', () => { tip.hidden = true; });
  return S;
}
