import test from 'node:test';
import assert from 'node:assert/strict';
import sharp from 'sharp';
import { decontaminate } from '../cutout/decontaminate.js';
import { refineAlpha } from '../cutout/refiner.js';

const image = await sharp({ create: { width: 4, height: 3, channels: 3, background: { r: 255, g: 0, b: 0 } } }).png().toBuffer();

test('decontaminate returns RGBA PNG with matching dimensions', async () => {
  const alpha = Buffer.alloc(12, 255);
  const output = await decontaminate(image, alpha);
  const meta = await sharp(output).metadata();
  assert.equal(meta.width, 4);
  assert.equal(meta.height, 3);
  assert.equal(meta.channels, 4);
  assert.equal(meta.format, 'png');
});

test('refinement preserves mask dimensions and range', async () => {
  const alpha = Buffer.from([0, 20, 128, 255, 0, 50, 128, 255, 0, 20, 128, 255]);
  const segmenter = { predictAlpha: async () => Buffer.alloc(12, 200) };
  const result = await refineAlpha(segmenter, image, alpha);
  assert.equal(result.length, alpha.length);
  for (const value of result) assert.ok(value >= 0 && value <= 255);
});
