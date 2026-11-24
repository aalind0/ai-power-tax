// Probe the public APIs/datasets in the survey: key requirements, CORS, freshness. Prints a summary; writes
// research/geo/api_probes.json. Uses only anonymous requests (and NREL's public DEMO_KEY).
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { get } from './lib/http.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const PROBES = [
  ['eia_api_v2_nokey', 'https://api.eia.gov/v2/electricity/retail-sales/data/?frequency=monthly&data[0]=price&facets[stateid][]=VA&facets[sectorid][]=RES&length=1'],
  ['eia_api_v2_demo', 'https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=DEMO_KEY&frequency=monthly&data[0]=price&facets[stateid][]=VA&facets[sectorid][]=RES&sort[0][column]=period&sort[0][direction]=desc&length=1'],
  ['nrel_utility_rates_demo', 'https://developer.nrel.gov/api/utility_rates/v3.json?api_key=DEMO_KEY&lat=39.0144&lon=-77.4578'],
  ['nlr_utility_rates_demo', 'https://developer.nlr.gov/api/utility_rates/v3.json?api_key=DEMO_KEY&lat=39.0144&lon=-77.4578'],
  ['urdb_nokey', 'https://api.openei.org/utility_rates?version=latest&format=json&ratesforutility=Virginia%20Electric%20%26%20Power%20Co&limit=1'],
  ['urdb_demo', 'https://api.openei.org/utility_rates?version=latest&format=json&api_key=DEMO_KEY&lat=39.0144&lon=-77.4578&sector=Residential&limit=3&detail=minimal'],
  ['pudl_s3_root', 'https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop?list-type=2&delimiter=/'],
  ['pudl_s3_stable', 'https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop?list-type=2&prefix=stable/&max-keys=1000'],
  ['electricitymaps_nokey', 'https://api.electricitymap.org/v3/carbon-intensity/latest?zone=US-MIDA-PJM'],
  ['gridstatus_pypi', 'https://pypi.org/pypi/gridstatus/json'],
  ['pudl_pypi', 'https://pypi.org/pypi/catalystcoop.pudl/json'],
];
const out = {};
for (const [name, url] of PROBES) {
  try {
    const r = await get(url, { headers: { Origin: 'https://example.org' }, timeoutMs: 60000 });
    const body = r.body.toString('utf8');
    out[name] = { url: url.replace(/api_key=[^&]+/, 'api_key=DEMO_KEY'), status: r.status, acao: r.headers['access-control-allow-origin'] || null, ratelimit: r.headers['x-ratelimit-limit'] || null, ratelimit_remaining: r.headers['x-ratelimit-remaining'] || null, bytes: body.length, head: body.slice(0, 1500) };
  } catch (e) { out[name] = { url, error: String(e) }; }
  const o = out[name];
  console.log(`\n## ${name}: HTTP ${o.status} ACAO=${o.acao} RL=${o.ratelimit}/${o.ratelimit_remaining}\n${(o.head || o.error || '').slice(0, 700)}`);
}
fs.writeFileSync(path.join(ROOT, 'research/geo/api_probes.json'), JSON.stringify({ run_at: new Date().toISOString(), probes: out }, null, 1));
