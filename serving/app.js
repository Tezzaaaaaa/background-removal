import http from 'node:http';
import Busboy from 'busboy';
import { CutoutPipeline } from '../cutout/index.js';

const MAX_BYTES = 22 * 1024 * 1024;
let pipelinePromise;
function loadPipeline() { pipelinePromise ??= CutoutPipeline.create(); return pipelinePromise; }

function json(res, status, body) {
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body));
}

async function readUpload(req) {
  return new Promise((resolve, reject) => {
    const busboy = Busboy({ headers: req.headers, limits: { fileSize: MAX_BYTES + 1, files: 1 } });
    let chunks = [], tooLarge = false, seen = false, mime = '';
    busboy.on('file', (_name, stream, info) => {
      seen = true; mime = info.mimeType;
      stream.on('data', (chunk) => chunks.push(chunk));
      stream.on('limit', () => { tooLarge = true; });
    });
    busboy.on('finish', () => resolve({ data: Buffer.concat(chunks), mime, seen, tooLarge }));
    busboy.on('error', reject);
    req.pipe(busboy);
  });
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/health') return json(res, 200, { status: 'ok', engine: 'cutout', input_size: 1024 });
    if (req.method !== 'POST' || req.url !== '/remove') return json(res, 404, { error: 'Not found' });

    const upload = await readUpload(req);
    if (!upload.seen) return json(res, 400, { error: 'No image file provided.' });
    if (upload.tooLarge || upload.data.length > MAX_BYTES) return json(res, 413, { error: 'Image is too large. Maximum size is 22 MB.' });
    if (!new Set(['image/jpeg', 'image/png', 'image/webp']).has(upload.mime)) return json(res, 415, { error: 'Use a JPG, PNG, or WebP image.' });

    const output = await (await loadPipeline()).process(upload.data);
    res.writeHead(200, { 'content-type': 'image/png', 'content-length': output.length });
    res.end(output);
  } catch (error) {
    console.error(error);
    json(res, 500, { error: 'Background removal failed.' });
  }
});

const port = Number(process.env.PORT || 8000);
server.listen(port, () => console.log(`Cutout listening on http://localhost:${port}`));
