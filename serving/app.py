"""Cutout background-removal API."""
import io
import threading

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image

from cutout.pipeline import CutoutPipeline

app = FastAPI(title="Cutout", version="1.1.0")
_pipeline = None
_lock = threading.Lock()


def load_pipeline():
    global _pipeline
    if _pipeline is None:
        with _lock:
            if _pipeline is None:
                _pipeline = CutoutPipeline()
    return _pipeline


@app.get("/health")
def health():
    return {"status": "ok", "engine": "cutout", "input_size": 1024}


@app.post("/remove")
def remove(file: UploadFile):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Use a JPG, PNG, or WebP image.")

    data = file.file.read()
    if len(data) > 22 * 1024 * 1024:
        raise HTTPException(413, "Image is too large. Maximum size is 22 MB.")

    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception as exc:
        raise HTTPException(400, "Invalid image file.") from exc

    try:
        output = load_pipeline().process(image)
        buffer = io.BytesIO()
        output.save(buffer, format="PNG", optimize=True)
        return Response(buffer.getvalue(), media_type="image/png")
    except Exception as exc:
        raise HTTPException(500, "Background removal failed.") from exc
