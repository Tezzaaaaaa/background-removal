#!/usr/bin/env node
import path from 'node:path';
import { CutoutPipeline } from './pipeline.js';

const args = process.argv.slice(2);
if (!args.length || args.includes('--help') || args.includes('-h')) {
  console.log('Usage: cutout <input> -o <output.png>');
  process.exit(args.length ? 0 : 1);
}
const outputIndex = args.findIndex((arg) => arg === '-o' || arg === '--output');
if (outputIndex < 0 || !args[outputIndex + 1]) {
  console.error('Missing required -o/--output path.');
  process.exit(2);
}
const input = args[0];
const output = path.resolve(args[outputIndex + 1]);
try {
  const pipeline = await CutoutPipeline.create();
  await pipeline.processFile(input, output);
  console.log(`saved: ${output}`);
} catch (error) {
  console.error(`ERROR: ${error.message}`);
  process.exit(1);
}
