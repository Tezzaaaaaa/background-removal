# Background Removal

Self-hosted background removal service powered by **Lucida** (`egeorcun/lucida`), a BiRefNet fine-tune for high-quality image matting.

## Run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn serving.app:app --host 0.0.0.0 --port 8756
```

The Lucida weights are downloaded from Hugging Face on first use and cached locally.

### API

`POST /remove` — multipart field `file`; returns a transparent PNG.

`GET /health` — service health.

`GET /models` — reports the installed model (`lucida`).

## Attribution

The core segmentation implementation is from the Lucida project by egeorcun:
https://github.com/egeorcun/lucida

Lucida's code and weights are released under MIT. See `LICENSE`. Model/data licensing should be reviewed independently before commercial deployment.
