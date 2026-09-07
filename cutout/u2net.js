import fs from 'node:fs/promises';
import { createHash } from 'node:crypto';
import os from 'node:os';
import path from 'node:path';
import ort from 'onnxruntime-node';
import sharp from 'sharp';

export const MODEL_URL = 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx';
export const MODEL_MD5 = '60024c5c889badc19c04ad937298a77b';
export const MODEL_DIR = path.join(os.homedir(), '.cache', 'cutout');
export const MODEL_PATH = path.join(MODEL_DIR, 'u2net.onnx');

async function md5Of(file) {
  const hash = createHash('md5');
  const data = await fs.readFile(file);
  hash.update(data);
  return hash.digest('hex');
}

export async function ensureModel() {
  await fs.mkdir(MODEL_DIR, { recursive: true });
  try {
    if ((await md5Of(MODEL_PATH)) === MODEL_MD5) return MODEL_PATH;
  } catch {}

  const response = await fetch(MODEL_URL, { redirect: 'follow' });
  if (!response.ok || !response.body) throw new Error(`Model download failed: HTTP ${response.status}`);
  const tmp = `${MODEL_PATH}.part`;
  const file = await fs.open(tmp, 'w');
  try {
    const reader = response.body.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      await file.write(value);
    }
  } finally {
    await file.close();
  }
  if ((await md5Of(tmp)) !== MODEL_MD5) {
    await fs.rm(tmp, { force: true });
    throw new Error('Downloaded U2Net model failed checksum verification.');
  }
  await fs.rename(tmp, MODEL_PATH);
  return MODEL_PATH;
}

export class U2NetSegmenter {
  constructor(session) { this.session = session; }

  static async create() {
    const model = await ensureModel();
    const session = await ort.InferenceSession.create(model, { executionProviders: ['cpu'] });
    return new U2NetSegmenter(session);
  }

  async predictAlpha(image) {
    const meta = await sharp(image).metadata();
    const width = meta.width;
    const height = meta.height;
    if (!width || !height) throw new Error('Invalid image dimensions.');

    const { data } = await sharp(image)
      .removeAlpha().resize(320, 320, { fit: 'fill', kernel: sharp.kernel.lanczos3 })
      .raw().toBuffer({ resolveWithObject: true });

    const mean = [0.485, 0.456, 0.406];
    const std = [0.229, 0.224, 0.225];
    let max = 1e-6;
    for (const value of data) if (value > max) max = value;
    const tensor = new Float32Array(3 * 320 * 320);
    for (let i = 0; i < 320 * 320; i++) {
      for (let c = 0; c < 3; c++) tensor[c * 320 * 320 + i] = (data[i * 3 + c] / max - mean[c]) / std[c];
    }

    const inputName = this.session.inputNames[0];
    const output = await this.session.run({ [inputName]: new ort.Tensor('float32', tensor, [1, 3, 320, 320]) });
    const pred = output[this.session.outputNames[0]].data;
    let min = Infinity, pmax = -Infinity;
    for (const value of pred) { if (value < min) min = value; if (value > pmax) pmax = value; }
    const range = Math.max(pmax - min, 1e-6);
    const mask = Buffer.alloc(320 * 320);
    for (let i = 0; i < mask.length; i++) mask[i] = Math.max(0, Math.min(255, Math.round(((pred[i] - min) / range) * 255)));

    return sharp(mask, { raw: { width: 320, height: 320, channels: 1 } })
      .resize(width, height, { kernel: sharp.kernel.lanczos3 })
      .raw().toBuffer();
  }
}
