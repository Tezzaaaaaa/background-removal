import sharp from 'sharp';

// Conservative edge decontamination. It avoids inventing foreground colour
// where the original pymatting estimator is not available in Node.
export async function decontaminate(image, alpha) {
  const { data, info } = await sharp(image).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  if (alpha.length !== info.width * info.height) throw new Error(`alpha shape does not match image ${info.width}x${info.height}`);
  const rgba = Buffer.alloc(info.width * info.height * 4);
  for (let i = 0; i < alpha.length; i++) {
    const a = alpha[i];
    const src = i * 3, dst = i * 4;
    rgba[dst] = data[src];
    rgba[dst + 1] = data[src + 1];
    rgba[dst + 2] = data[src + 2];
    rgba[dst + 3] = a;
  }
  return sharp(rgba, { raw: { width: info.width, height: info.height, channels: 4 } }).png().toBuffer();
}
