# Background Removal

Local background removal engine and macOS Finder integration.

## JavaScript runtime

The processing engine is being ported to **Node.js 20+ / JavaScript ES modules**. The JS implementation keeps the existing pipeline shape:

`image → segmentation → alpha refinement → RGBA output`

The portable runtime uses `onnxruntime-node` and `sharp`, with U²-Net as the directly compatible ONNX segmentation path. The segmenter is deliberately isolated so a compatible high-resolution model runner can be substituted without rewriting the pipeline.

### CLI

```bash
npm install
npx cutout input.jpg -o output.png
```

or:

```bash
node cutout/cli.js input.jpg -o output.png
```

### HTTP API

```bash
npm install
npm start
```

Health check:

```text
GET /health
```

Background removal:

```text
POST /remove
Content-Type: multipart/form-data
field: file
```

Accepted formats: JPEG, PNG, WebP. Maximum upload size: 22 MB.

### Tests

```bash
npm test
```

GitHub Actions runs the Node.js test suite on the JavaScript port branch and pull requests into `main`.

## macOS integration

The native macOS application and Finder Quick Action remain Swift because Swift is the appropriate native language for the macOS shell and Finder extension. The processing engine is being separated from that native shell so it can also be used by KEFE and the HTTP/MCP layers.

The existing Python runtime remains on this branch only where the current macOS packaging path still depends on it. It is not the target processing implementation for the JavaScript port.

## Privacy

Image processing is local. Images are not uploaded to a background-removal service.

The first model download requires an internet connection.

## Project structure

```text
background-removal/
├── cutout/
│   ├── cli.js
│   ├── decontaminate.js
│   ├── index.js
│   ├── pipeline.js
│   ├── refiner.js
│   ├── segmenter.js
│   └── u2net.js
├── serving/
│   └── app.js
├── test/
│   └── pipeline.test.js
├── macOS/
│   └── BackgroundRemoval/
├── package.json
└── README.md
```

## License

MIT License.
