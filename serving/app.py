"""Self-hosted Lucida background-removal API."""
import io
import threading
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image
from bgr.pipeline import PipelineSegmenter
from bgr.registry import get_segmenter, MODEL_ID, INPUT_SIZE

app = FastAPI(title="Background Removal")
_segmenter = None
_lock = threading.Lock()


def load_model():
    global _segmenter
    if _segmenter is None:
        with _lock:
            if _segmenter is None:
                _segmenter = PipelineSegmenter(get_segmenter())
    return _segmenter


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID, "input_size": INPUT_SIZE}


@app.get("/models")
def models():
    return {"models": [MODEL_ID], "default": MODEL_ID}


@app.post("/remove")
def remove(file: UploadFile):
    if not file.content_type or file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Use a JPG, PNG, or WebP image.")
    try:
        data = file.file.read()
        if len(data) > 22 * 1024 * 1024:
            raise HTTPException(413, "Image is too large. Maximum size is 22 MB.")
        image = Image.open(io.BytesIO(data))
        image.load()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(400, "Invalid image file.") from exc

    try:
        output = load_model().process(image)
        buffer = io.BytesIO()
        output.save(buffer, format="PNG", optimize=True)
        return Response(buffer.getvalue(), media_type="image/png")
    except Exception as exc:
        raise HTTPException(500, "Background removal failed.") from exc
