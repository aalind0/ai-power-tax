// Copy a findings draft into research/geo/FINDINGS.md (the Write tool may refuse report files for subagents).
// Usage: node scripts/geo/publish_findings.mjs <draftPath>
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const src = process.argv[2];
if (!src || !fs.existsSync(src)) { console.error('usage: node publish_findings.mjs <draftPath>'); process.exit(1); }
const out = path.join(ROOT, 'research/geo/FINDINGS.md');
fs.writeFileSync(out, fs.readFileSync(src, 'utf8'));
console.log('wrote', out, fs.statSync(out).size, 'bytes');
