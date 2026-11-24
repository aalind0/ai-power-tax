// Download a full ArcGIS FeatureServer layer as GeoJSON, paginating with resultOffset.
// Usage: node fetch_arcgis_layer.mjs <layerUrl> <outFile.geojson> [pageSize=100] [outFields=*]
// Writes the untouched FeatureCollection (all pages concatenated) + a .meta.json with layer metadata.
import fs from 'fs';
import path from 'path';
import { get, getJSON, retry } from './lib/http.mjs';

const [layerUrl, outFile, pageSizeArg, outFieldsArg] = process.argv.slice(2);
if (!layerUrl || !outFile) { console.error('usage: node fetch_arcgis_layer.mjs <layerUrl> <out.geojson> [pageSize] [outFields]'); process.exit(1); }
const pageSize = Number(pageSizeArg || 100);
const outFields = outFieldsArg || '*';
fs.mkdirSync(path.dirname(outFile), { recursive: true });

const meta = await getJSON(layerUrl + '?f=json');
const oidField = meta.objectIdField || (meta.fields.find((f) => f.type === 'esriFieldTypeOID') || {}).name || 'OBJECTID';
const { count } = await getJSON(layerUrl + '/query?where=1%3D1&returnCountOnly=true&f=json');
console.log(`layer "${meta.name}" count=${count} oid=${oidField} pageSize=${pageSize}`);

const features = [];
for (let offset = 0; offset < count; offset += pageSize) {
  const q = new URLSearchParams({
    where: '1=1', outFields, orderByFields: oidField, resultOffset: String(offset), resultRecordCount: String(pageSize),
    geometryPrecision: '5', outSR: '4326', f: 'geojson',
  });
  const page = await retry(async () => {
    const r = await get(`${layerUrl}/query?${q}`, { timeoutMs: 180000 });
    if (r.status !== 200) throw new Error('HTTP ' + r.status);
    const j = JSON.parse(r.body.toString('utf8'));
    if (j.error) throw new Error(JSON.stringify(j.error));
    return j;
  });
  features.push(...page.features);
  process.stdout.write(`\r${features.length}/${count}`);
}
console.log();
const fc = { type: 'FeatureCollection', features };
fs.writeFileSync(outFile, JSON.stringify(fc));
fs.writeFileSync(outFile.replace(/\.geojson$/, '.meta.json'), JSON.stringify({ source: layerUrl, fetched_at: new Date().toISOString(), count, layer: meta }, null, 1));
console.log('wrote', outFile, fs.statSync(outFile).size, 'bytes', features.length, 'features');
