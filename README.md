# Cutout

**Cutout** is a standalone, self-hosted background-removal engine for clean transparent PNG extraction.

It is deliberately a single-purpose tool: upload an image, Cutout finds the foreground, refines uncertain edges, removes background colour contamination, and returns a transparent PNG.

## ChatGPT tool

Cutout now includes a ChatGPT-compatible MCP server. Once the server is deployed at a public HTTPS address, add its `/mcp` endpoint as a private ChatGPT app in Developer Mode.

Then the workflow is simply:

1. Attach an image in ChatGPT.
2. Ask: **"Remove the background."**
3. ChatGPT calls `remove_background` automatically.
4. Cutout returns a transparent PNG as a downloadable MCP resource.

The tool has one fixed processing engine. There is no model selector or processing-mode question.

Set `PUBLIC_BASE_URL` to the public HTTPS origin used by the server, for example `https://cutout.example.com`.

### ChatGPT connection

The MCP endpoint is:

```text
https://YOUR-DOMAIN/mcp
```

For local development, run the server on port 8756 and expose it through an HTTPS tunnel before connecting it to ChatGPT. OpenAI's current plugin documentation describes MCP servers as the backend for ChatGPT tools and uses Streamable HTTP for deployed servers.

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
uvicorn serving.mcp:app --host 0.0.0.0 --port 8756
```

The model weights are downloaded from Hugging Face on first use and cached locally.

## API

`POST /remove` — multipart field `file`; accepts JPG, PNG, or WebP and returns a transparent PNG.

`GET /health` — service health and engine information.

`GET /files/<token>.png` — serves generated PNG resources using an unguessable token.

`POST /mcp` — Streamable HTTP MCP endpoint for ChatGPT and other MCP clients.

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
