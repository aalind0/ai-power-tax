// Extract text from a PDF using macOS PDFKit via JXA (no third-party packages needed).
// Usage: osascript -l JavaScript scripts/markets/pdf2txt.js <in.pdf> <out.txt>
ObjC.import('PDFKit');
ObjC.import('Foundation');
function run(argv) {
  const inPath = argv[0];
  const outPath = argv[1];
  const url = $.NSURL.fileURLWithPath(inPath);
  const doc = $.PDFDocument.alloc.initWithURL(url);
  if (!doc || doc.isNil()) return 'ERROR: could not open ' + inPath;
  const n = doc.pageCount;
  let parts = [];
  for (let i = 0; i < n; i++) {
    const p = doc.pageAtIndex(i);
    const s = p.string;
    parts.push('\n=== PAGE ' + (i + 1) + ' ===\n' + (s && !s.isNil() ? s.js : ''));
  }
  const str = $.NSString.alloc.initWithUTF8String(parts.join(''));
  str.writeToFileAtomicallyEncodingError(outPath, true, $.NSUTF8StringEncoding, null);
  return 'pages=' + n;
}
