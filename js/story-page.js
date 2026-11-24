// "How it works" page: the follow-the-dollar flow and the seven chapters, each drawn when it scrolls near.
import { $ } from './util.js';
import * as story from './story.js';

function lazy(sel, fn) {
  const el = $(sel);
  if (!el) return;
  const io = new IntersectionObserver((ents) => {
    if (ents.some((e) => e.isIntersecting)) { io.disconnect(); Promise.resolve(fn()).catch((e) => console.error(sel, e)); }
  }, { rootMargin: '600px 0px' });
  io.observe(el);
}

story.heroFlow().catch(console.error);
story.about();
lazy('#ch-calm', story.chCalm);
lazy('#ch-kwh', story.chKwh);
lazy('#ch-map', () => story.chMap((e) => { location.href = `index.html?u=${e.id}-${e.st}`; }));
lazy('#ch-spike', story.chSpike);
lazy('#ch-wires', story.chWires);
lazy('#ch-load', story.chLoad);
lazy('#ch-evidence', story.chEvidence);
addEventListener('scroll', () => $('.topbar').classList.toggle('scrolled', scrollY > 8), { passive: true });
