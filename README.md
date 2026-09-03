# Cutout

**Cutout** is a standalone, self-hosted background-removal engine for clean transparent PNG extraction.

It is deliberately a single-purpose tool: upload an image, Cutout finds the foreground, refines uncertain edges, removes background colour contamination, and returns RGBA PNG.

## What is adapted

Cutout uses the released BiRefNet fine-tune weights from egeorcun/lucida as its segmentation foundation, but the application layer, package structure, API, pipeline defaults, and user-facing naming are adapted for this project. Lucida is not exposed as a selectable model or product name.

The adapted pipeline adds:

- 1024px high-resolution inference
- automatic refinement of uncertain edges
- foreground colour decontamination
- Apple Silicon MPS acceleration when available
- CPU fallback
- one fixed engine with no model selector

## Run locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn serving.app:app --host 0.0.0.0 --port 8756
```

The model weights are downloaded from Hugging Face on first use and cached locally.

## API

`POST /remove` — multipart field `file`; accepts JPG, PNG, or WebP and returns a transparent PNG.

`GET /health` — service health and engine information.

Example:

```bash
curl -F "file=@input.jpg" http://localhost:8756/remove -o output.png
```

## CLI

```bash
cutout input.jpg -o output.png
```

## Attribution and licensing

Cutout's segmentation foundation uses the MIT-licensed `egeorcun/lucida` model weights and builds on the MIT-licensed BiRefNet architecture. See `LICENSE` and the upstream project for attribution and licensing details.

The upstream model was trained using datasets with mixed licensing terms. Anyone deploying this commercially should review those terms independently.
