import sharp from 'sharp';

function regions(mask, width, height, minRegion = 256, maxPatches = 6) {
  // Lightweight connected-region approximation for uncertain pixels.
  const seen = new Uint8Array(mask.length);
  const result = [];
  const neighbors = [-1, 1, -width, width];
  for (let start = 0; start < mask.length && result.length < maxPatches; start++) {
    if (seen[start] || mask[start] < 13 || mask[start] > 242) continue;
    const queue = [start]; seen[start] = 1; let count = 0;
    let minX = width, maxX = 0, minY = height, maxY = 0;
    while (queue.length) {
      const p = queue.pop(); const y = Math.floor(p / width); const x = p - y * width;
      count++; minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y);
      for (const d of neighbors) {
        const q = p + d;
        if (q < 0 || q >= mask.length || seen[q]) continue;
        const qy = Math.floor(q / width);
        if (Math.abs(qy - y) > 1 || mask[q] < 13 || mask[q] > 242) continue;
        seen[q] = 1; queue.push(q);
      }
    }
    if (count >= minRegion) result.push([minY, maxY + 1, minX, maxX + 1]);
  }
  return result;
}

export async function refineAlpha(segmenter, image, alpha) {
  const meta = await sharp(image).metadata();
  const width = meta.width, height = meta.height;
  if (!width || !height) throw new Error('Invalid image dimensions.');
  const uncertain = Buffer.alloc(alpha.length);
  for (let i = 0; i < alpha.length; i++) uncertain[i] = alpha[i] > 13 && alpha[i] < 242 ? 255 : 0;
  const result = Buffer.from(alpha);
  for (const [y0, y1, x0, x1] of regions(uncertain, width, height)) {
    const padY = Math.floor((y1 - y0) * 0.35), padX = Math.floor((x1 - x0) * 0.35);
    const yy0 = Math.max(0, y0 - padY), yy1 = Math.min(height, y1 + padY);
    const xx0 = Math.max(0, x0 - padX), xx1 = Math.min(width, x1 + padX);
    const crop = await sharp(image).extract({ left: xx0, top: yy0, width: xx1 - xx0, height: yy1 - yy0 }).png().toBuffer();
    const refined = await segmenter.predictAlpha(crop);
    const rw = xx1 - xx0;
    for (let y = yy0; y < yy1; y++) for (let x = xx0; x < xx1; x++) {
      const i = y * width + x, r = (y - yy0) * rw + (x - xx0);
      if (uncertain[i]) result[i] = Math.round((result[i] + refined[r]) / 2);
    }
  }
  return result;
}
