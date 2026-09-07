import sharp from 'sharp';
import { CutoutSegmenter } from './segmenter.js';
import { refineAlpha } from './refiner.js';
import { decontaminate } from './decontaminate.js';

export class CutoutPipeline {
  constructor(segmenter) { this.segmenter = segmenter; }

  static async create() { return new CutoutPipeline(await CutoutSegmenter.create()); }

  async process(image) {
    const alpha = await this.segmenter.predictAlpha(image);
    const refined = await refineAlpha(this.segmenter, image, alpha);
    return decontaminate(image, refined);
  }

  async processFile(inputPath, outputPath) {
    const image = await sharp(inputPath).toBuffer();
    const output = await this.process(image);
    await sharp(output).png({ compressionLevel: 9 }).toFile(outputPath);
    return outputPath;
  }
}
