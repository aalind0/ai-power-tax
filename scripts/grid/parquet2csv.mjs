// Convert a parquet file to CSV using the pure-JS hyparquet reader (no pyarrow on this machine).
// Usage: node scripts/grid/parquet2csv.mjs <in.parquet> <out.csv> [--schema]
import fs from 'fs';
import { parquetRead, parquetMetadata, parquetSchema } from 'hyparquet';
import { compressors } from 'hyparquet-compressors';

const [, , inFile, outFile, flag] = process.argv;
const buf = fs.readFileSync(inFile);
const ab = buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength);
const meta = parquetMetadata(ab);
const cols = meta.schema.slice(1).filter((s) => !s.num_children).map((s) => s.name);
if (flag === '--schema') { console.log(meta.num_rows, cols.join(', ')); process.exit(0); }
const esc = (v) => {
  if (v === null || v === undefined) return '';
  if (v instanceof Date) return v.toISOString().slice(0, 10);
  if (typeof v === 'bigint') return v.toString();
  const s = String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};
const out = fs.createWriteStream(outFile);
out.write(cols.join(',') + '\n');
await parquetRead({
  file: ab, compressors, rowFormat: 'array',
  onComplete: (rows) => { for (const r of rows) out.write(r.map(esc).join(',') + '\n'); },
});
out.end();
console.log('rows', meta.num_rows);
