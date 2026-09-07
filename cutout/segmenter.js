import { U2NetSegmenter } from './u2net.js';

export const INPUT_SIZE = 1024;

export class Segmenter {
  async predictAlpha(_image) { throw new Error('predictAlpha() must be implemented'); }
}

export class CutoutSegmenter extends Segmenter {
  constructor(runner) { super(); this.runner = runner; }

  static async create() {
    // The original Python implementation uses the Lucida/BiRefNet model.
    // The portable Node runtime uses the known-good U2Net ONNX path until a
    // directly compatible Lucida ONNX runner is supplied.
    return new CutoutSegmenter(await U2NetSegmenter.create());
  }

  async predictAlpha(image) { return this.runner.predictAlpha(image); }
}
