// Dependency-free point-in-polygon index for GeoJSON (Polygon / MultiPolygon), browser- or node-friendly.
// Usage: const idx = buildIndex(featureCollection); idx.lookup(lng, lat) -> [feature.properties, ...]
// Territories overlap legitimately (e.g., a co-op and an IOU in one county), so lookup returns ALL matches.

function ringContains(ring, x, y) {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

function polygonContains(rings, x, y) {
  if (!ringContains(rings[0], x, y)) return false;
  for (let k = 1; k < rings.length; k++) if (ringContains(rings[k], x, y)) return false; // hole
  return true;
}

function bboxOf(coordsList) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const poly of coordsList) for (const [x, y] of poly[0]) {
    if (x < minX) minX = x; if (x > maxX) maxX = x; if (y < minY) minY = y; if (y > maxY) maxY = y;
  }
  return [minX, minY, maxX, maxY];
}

export function buildIndex(fc) {
  const items = [];
  for (const f of fc.features) {
    if (!f.geometry) continue;
    const polys = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.type === 'MultiPolygon' ? f.geometry.coordinates : [];
    if (!polys.length) continue;
    const parts = polys.map((p) => ({ rings: p, bbox: bboxOf([p]) }));
    items.push({ props: f.properties, bbox: bboxOf(polys), parts });
  }
  return {
    size: items.length,
    lookup(x, y) {
      const out = [];
      for (const it of items) {
        const b = it.bbox;
        if (x < b[0] || x > b[2] || y < b[1] || y > b[3]) continue;
        for (const part of it.parts) {
          const pb = part.bbox;
          if (x < pb[0] || x > pb[2] || y < pb[1] || y > pb[3]) continue;
          if (polygonContains(part.rings, x, y)) { out.push(it.props); break; }
        }
      }
      return out;
    },
  };
}
