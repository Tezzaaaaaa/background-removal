import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Busboy from 'busboy';
import { CutoutPipeline } from '../cutout/index.js';

const MAX_BYTES = 22 * 1024 * 1024;
const PUBLIC_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const MIME = { '.html':'text/html; charset=utf-8', '.css':'text/css; charset=utf-8', '.js':'text/javascript; charset=utf-8', '.json':'application/json; charset=utf-8', '.svg':'image/svg+xml' };
let pipelinePromise;
function loadPipeline() { pipelinePromise ??= CutoutPipeline.create(); return pipelinePromise; }
function json(res, status, body) { res.writeHead(status, { 'content-type':'application/json; charset=utf-8' }); res.end(JSON.stringify(body)); }
async function serveStatic(req, res) {
  const pathname = new URL(req.url, 'http://localhost').pathname;
  const requested = pathname === '/' ? '/index.html' : pathname;
  const file = path.resolve(PUBLIC_DIR, `.${requested}`);
  if (!file.startsWith(PUBLIC_DIR + path.sep)) return json(res, 404, { error:'Not found' });
  try {
    const data = await fs.readFile(file);
    const ext = path.extname(file).toLowerCase();
    res.writeHead(200, { 'content-type': MIME[ext] || 'application/octet-stream', 'cache-control':'no-cache' });
    res.end(data);
  } catch { return json(res, 404, { error:'Not found' }); }
}
async function readUpload(req) {
  return new Promise((resolve, reject) => {
    const busboy = Busboy({ headers:req.headers, limits:{ fileSize:MAX_BYTES + 1, files:1 } });
    const chunks = []; let tooLarge = false, seen = false, mime = '';
    busboy.on('file', (_name, stream, info) => { seen = true; mime = info.mimeType; stream.on('data', chunk => chunks.push(chunk)); stream.on('limit', () => { tooLarge = true; }); });
    busboy.on('finish', () => resolve({ data:Buffer.concat(chunks), mime, seen, tooLarge }));
    busboy.on('error', reject); req.pipe(busboy);
  });
}
const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'GET' && req.url === '/health') return json(res, 200, { status:'ok', engine:'cutout' });
    if (req.method === 'POST' && req.url === '/remove') {
      const upload = await readUpload(req);
      if (!upload.seen) return json(res, 400, { error:'No image file provided.' });
      if (upload.tooLarge || upload.data.length > MAX_BYTES) return json(res, 413, { error:'Image is too large. Maximum size is 22 MB.' });
      if (!new Set(['image/jpeg','image/png','image/webp']).has(upload.mime)) return json(res, 415, { error:'Use a JPG, PNG, or WebP image.' });
      const output = await (await loadPipeline()).process(upload.data);
      res.writeHead(200, { 'content-type':'image/png', 'content-length':output.length, 'cache-control':'no-store' });
      return res.end(output);
    }
    if (req.method === 'GET') return serveStatic(req, res);
    return json(res, 404, { error:'Not found' });
  } catch (error) { console.error(error); return json(res, 500, { error:'Background removal failed.' }); }
});
const port = Number(process.env.PORT || 8000);
server.listen(port, '0.0.0.0', () => console.log(`Cutout listening on port ${port}`));
