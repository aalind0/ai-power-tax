// Download daily closing prices (Nasdaq.com public quote API) for power-sector stocks and a few benchmarks.
// Usage: node scripts/finance/fetch_prices.mjs
// Writes untouched JSON to data/raw/finance/nasdaq_prices_<YYYYMMDD>/<SYMBOL>.json
// Prices are as published by nasdaq.com "historical quotes" (close, not dividend-adjusted).
import https from 'https';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const today = new Date().toISOString().slice(0, 10);
const outDir = path.join(ROOT, 'data/raw/finance', `nasdaq_prices_${today.replace(/-/g, '')}`);
fs.mkdirSync(outDir, { recursive: true });

const STOCKS = ['CEG', 'VST', 'TLN', 'NRG', 'D', 'SO', 'AEP', 'DUK', 'NEE', 'EXC', 'PEG', 'ETR', 'XEL', 'SRE',
  'CNP', 'PPL', 'FE', 'NI', 'EVRG', 'WEC', 'AEE', 'PNW', 'OKLO', 'SMR', 'GEV'];
const ETFS = ['XLU', 'SPY'];

function get(u) {
  return new Promise((resolve, reject) => {
    const req = https.get(u, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        Accept: 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        Origin: 'https://www.nasdaq.com',
        Referer: 'https://www.nasdaq.com/',
      },
      timeout: 60000,
    }, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve({ status: res.statusCode, body: Buffer.concat(chunks) }));
    });
    req.on('timeout', () => req.destroy(new Error('timeout')));
    req.on('error', reject);
  });
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (const [sym, cls] of [...STOCKS.map((s) => [s, 'stocks']), ...ETFS.map((s) => [s, 'etf'])]) {
  const url = `https://api.nasdaq.com/api/quote/${sym}/historical?assetclass=${cls}&fromdate=2022-12-01&todate=${today}&limit=9999`;
  try {
    const r = await get(url);
    fs.writeFileSync(path.join(outDir, `${sym}.json`), r.body);
    let n = null;
    try { n = JSON.parse(r.body.toString()).data.tradesTable.rows.length; } catch (e) { /* ignore */ }
    console.log(sym, r.status, r.body.length, 'rows=', n);
  } catch (e) {
    console.log(sym, 'ERROR', e.message);
  }
  await sleep(700);
}
console.log('saved to', outDir);
