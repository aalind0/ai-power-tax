// "My bill" share card: drawn on a canvas, previewed in a dialog, downloadable / shareable as PNG.
import { esc } from './util.js';

const W = 1200, H = 1200;
const INK = '#0b0b0b', INK2 = '#52514e', MUTED = '#898781', PAPER = '#f6f4ee', UP = '#c4302b', DOWN = '#1c5cab', BLUE = '#2a78d6', VOLT = '#ffd60a', HAIR = '#e1e0d9';

async function fontsReady() {
  try {
    await Promise.all([
      document.fonts.load('400 120px "Instrument Serif"'), document.fonts.load('italic 400 120px "Instrument Serif"'),
      document.fonts.load('600 30px Inter'), document.fonts.load('400 30px Inter'), document.fonts.load('500 22px "JetBrains Mono"'),
    ]);
  } catch { /* fall back to system fonts */ }
}

function roundRect(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r);
  g.closePath();
}
function fitText(g, text, maxW, font, start) {
  let size = start;
  do { g.font = font.replace('{s}', size); size -= 2; } while (g.measureText(text).width > maxW && size > 18);
}

export async function drawCard(d) {
  await fontsReady();
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  // paper + glow
  g.fillStyle = PAPER; g.fillRect(0, 0, W, H);
  const grad = g.createRadialGradient(W * 0.85, -60, 10, W * 0.85, -60, 700);
  grad.addColorStop(0, 'rgba(255,214,10,0.35)'); grad.addColorStop(1, 'rgba(255,214,10,0)');
  g.fillStyle = grad; g.fillRect(0, 0, W, H);
  const P = 80;
  // brand
  g.fillStyle = INK; roundRect(g, P, P, 52, 52, 13); g.fill();
  g.fillStyle = VOLT; g.beginPath(); const bx = P + 8, by = P + 6, s = 0.6;
  [[36, 6], [16, 36], [30, 36], [26, 58], [48, 26], [34, 26]].forEach(([x, y], i) => (i ? g.lineTo(bx + x * s, by + y * s) : g.moveTo(bx + x * s, by + y * s)));
  g.closePath(); g.fill();
  g.fillStyle = INK; g.font = '600 26px Inter'; g.textBaseline = 'middle'; g.fillText('The AI Power Tax', P + 68, P + 27);
  g.fillStyle = INK2; g.font = '500 20px "JetBrains Mono"'; g.textAlign = 'right'; g.fillText(d.stateName.toUpperCase(), W - P, P + 27); g.textAlign = 'left';
  // headline
  g.textBaseline = 'alphabetic';
  g.fillStyle = INK; g.font = '400 76px "Instrument Serif"'; g.fillText('My power bill is up', P, 268);
  g.fillStyle = d.nominal >= 0 ? UP : DOWN; g.font = 'italic 400 232px "Instrument Serif"';
  const big = `${d.nominal >= 0 ? '+' : '−'}${Math.abs(Math.round(d.nominal))}%`;
  g.fillText(big, P - 6, 470);
  const bw = g.measureText(big).width;
  g.fillStyle = INK; g.font = '400 76px "Instrument Serif"'; g.fillText('since 2020', P + bw + 24, 470);
  g.fillStyle = INK2; fitText(g, `${d.utility} · ${d.homes} homes`, W - 2 * P, '400 {s}px Inter', 30); g.fillText(`${d.utility} · ${d.homes} homes`, P, 530);
  // mini chart
  const cx = P, cy = 580, cw = W - 2 * P, ch = 250;
  g.fillStyle = '#fcfcfb'; roundRect(g, cx, cy, cw, ch, 22); g.fill(); g.strokeStyle = HAIR; g.lineWidth = 2; g.stroke();
  const series = d.series.filter((r) => r[1] != null);
  const us = (d.us || []).filter((r) => r[1] != null);
  if (series.length > 2) {
    const xs = series.map((r) => r[0]);
    const all = [...series, ...us.filter((r) => r[0] >= xs[0])].map((r) => r[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...all) * 0.92, y1 = Math.max(...all) * 1.05;
    const X = (v) => cx + 40 + ((v - x0) / (x1 - x0)) * (cw - 190), Y = (v) => cy + ch - 34 - ((v - y0) / (y1 - y0)) * (ch - 70);
    g.strokeStyle = HAIR; g.lineWidth = 1.5;
    [0.25, 0.5, 0.75].forEach((f) => { g.beginPath(); g.moveTo(cx + 30, cy + 30 + f * (ch - 64)); g.lineTo(cx + cw - 30, cy + 30 + f * (ch - 64)); g.stroke(); });
    const line = (pts, color, width, dash) => {
      g.setLineDash(dash || []); g.strokeStyle = color; g.lineWidth = width; g.lineJoin = 'round'; g.lineCap = 'round';
      g.beginPath(); pts.forEach((r, i) => (i ? g.lineTo(X(r[0]), Y(r[1])) : g.moveTo(X(r[0]), Y(r[1])))); g.stroke(); g.setLineDash([]);
    };
    line(us.filter((r) => r[0] >= x0 && r[0] <= x1), INK, 3, [10, 9]);
    line(series, BLUE, 7);
    const last = series[series.length - 1], lastUs = us.filter((r) => r[0] <= x1).pop();
    g.fillStyle = BLUE; g.beginPath(); g.arc(X(last[0]), Y(last[1]), 10, 0, 7); g.fill();
    g.font = '600 24px Inter'; g.fillText(`${last[1].toFixed(1)}¢`, X(last[0]) + 18, Y(last[1]) + 8);
    if (lastUs) { g.fillStyle = INK2; g.font = '400 20px Inter'; g.fillText(`US ${lastUs[1].toFixed(1)}¢`, X(lastUs[0]) + 18, Y(lastUs[1]) + 8); }
    g.fillStyle = MUTED; g.font = '500 18px "JetBrains Mono"';
    g.fillText(String(x0), cx + 34, cy + ch - 10); g.textAlign = 'right'; g.fillText(`${x1} · ¢ per kWh`, cx + cw - 160, cy + ch - 10); g.textAlign = 'left';
  }
  // stat boxes
  const sy = 870, gap = 20, sw = (W - 2 * P - 2 * gap) / 3, sh = 170;
  d.stats.slice(0, 3).forEach((st, i) => {
    const sx = P + i * (sw + gap);
    g.fillStyle = '#fff'; roundRect(g, sx, sy, sw, sh, 18); g.fill(); g.strokeStyle = HAIR; g.lineWidth = 2; g.stroke();
    g.fillStyle = st.color || INK; fitText(g, st.v, sw - 40, '400 {s}px "Instrument Serif"', 64); g.fillText(st.v, sx + 22, sy + 74);
    g.fillStyle = INK2; g.font = '400 20px Inter';
    const words = st.k.split(' '); let lineTxt = '', ly = sy + 112;
    words.forEach((w) => { const t = lineTxt ? `${lineTxt} ${w}` : w; if (g.measureText(t).width > sw - 40) { g.fillText(lineTxt, sx + 22, ly); lineTxt = w; ly += 26; } else lineTxt = t; });
    g.fillText(lineTxt, sx + 22, ly);
  });
  // footer
  g.fillStyle = INK; g.fillRect(0, H - 96, W, 96);
  g.fillStyle = VOLT; g.font = '600 26px Inter'; g.fillText(`See yours → ${d.url}`, P, H - 40);
  g.fillStyle = '#b9b6ad'; g.font = '400 18px Inter'; g.textAlign = 'right'; g.fillText('Data: EIA-861/861M · PJM market monitor · BLS', W - P, H - 42); g.textAlign = 'left';
  return c;
}

export async function openShare(d) {
  const canvas = await drawCard(d);
  const url = canvas.toDataURL('image/png');
  const dlg = document.createElement('dialog');
  dlg.className = 'share-dlg';
  dlg.innerHTML = `
    <div class="share-in">
      <div class="share-h"><b>Your bill card</b><button class="x" aria-label="Close">✕</button></div>
      <img src="${url}" alt="${esc(`My power bill is up ${Math.round(d.nominal)}% since 2020, ${d.utility}`)}" />
      <div class="cta">
        <a class="btn" download="my-power-bill-${d.slug}.png" href="${url}">Download image</a>
        <button class="btn ghost" data-share hidden>Share…</button>
        <button class="btn ghost" data-copy>Copy caption</button>
      </div>
      <p class="note">Suggested caption: “${esc(d.caption)}”</p>
    </div>`;
  document.body.appendChild(dlg);
  const close = () => { dlg.close(); dlg.remove(); };
  dlg.querySelector('.x').addEventListener('click', close);
  dlg.addEventListener('click', (e) => { if (e.target === dlg) close(); });
  dlg.querySelector('[data-copy]').addEventListener('click', async (e) => { try { await navigator.clipboard.writeText(`${d.caption} ${d.link}`); e.target.textContent = 'Caption copied ✓'; } catch { prompt('Copy caption', `${d.caption} ${d.link}`); } });
  const shareBtn = dlg.querySelector('[data-share]');
  canvas.toBlob((blob) => {
    const file = blob && new File([blob], `my-power-bill-${d.slug}.png`, { type: 'image/png' });
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
      shareBtn.hidden = false;
      shareBtn.addEventListener('click', () => navigator.share({ files: [file], text: `${d.caption} ${d.link}` }).catch(() => {}));
    }
  }, 'image/png');
  dlg.showModal();
}
