// Probe ArcGIS FeatureServer layers: name, count, fields, year/sourcedate distribution.
// Usage: node probe_layers.mjs <featureServerUrl> [<featureServerUrl> ...]
import { getJSON } from './lib/http.mjs';

for (const base of process.argv.slice(2)) {
  console.log('\n===', base);
  try {
    const svc = await getJSON(base + '?f=json');
    const layers = svc.layers || [{ id: 0, name: '(layer)' }];
    for (const l of layers) {
      const lu = /\/\d+$/.test(base) ? base : `${base}/${l.id}`;
      const meta = await getJSON(lu + '?f=json');
      const fields = (meta.fields || []).map((f) => f.name);
      const cnt = await getJSON(lu + '/query?where=1%3D1&returnCountOnly=true&f=json').catch((e) => ({ count: 'ERR ' + e.message.slice(0, 80) }));
      console.log(`layer ${l.id} "${meta.name}" geom=${meta.geometryType} count=${cnt.count} maxRec=${meta.maxRecordCount} lastEdit=${meta.editingInfo ? new Date(meta.editingInfo.lastEditDate).toISOString().slice(0, 10) : '?'}`);
      console.log('  fields:', fields.join(','));
      const yf = fields.find((f) => /^year$/i.test(f));
      const sf = fields.find((f) => /^sourcedate$/i.test(f));
      if (yf) {
        const stats = encodeURIComponent(JSON.stringify([{ statisticType: 'count', onStatisticField: fields.find((f) => /objectid|fid/i.test(f)) || fields[0], outStatisticFieldName: 'n' }]));
        const g = [yf, sf].filter(Boolean).join(',');
        const r = await getJSON(`${lu}/query?where=1%3D1&outStatistics=${stats}&groupByFieldsForStatistics=${g}&f=json`).catch((e) => ({ error: e.message.slice(0, 100) }));
        if (r.features) console.log('  year/sourcedate:', r.features.map((f) => `${f.attributes[yf]}/${f.attributes[sf] ? new Date(f.attributes[sf]).toISOString().slice(0, 10) : ''}:${f.attributes.n}`).join(' '));
        else console.log('  stats err', JSON.stringify(r).slice(0, 200));
      }
      if (meta.description) console.log('  desc:', meta.description.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 500));
    }
  } catch (e) {
    console.log('ERR', e.message.slice(0, 300));
  }
}
