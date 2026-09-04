"""Lightweight U2Net fallback used when the primary segmenter is unavailable."""
import hashlib
import os
import ssl
import urllib.request

import numpy as np
from PIL import Image

MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
MODEL_MD5 = "60024c5c889badc19c04ad937298a77b"
MODEL_DIR = os.path.join(os.path.expanduser("~"), ".cache", "cutout")
MODEL_PATH = os.path.join(MODEL_DIR, "u2net.onnx")


def _ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _md5_of(path):
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.isfile(MODEL_PATH) and _md5_of(MODEL_PATH) == MODEL_MD5:
        return

    tmp_path = MODEL_PATH + ".part"
    try:
        with urllib.request.urlopen(MODEL_URL, context=_ssl_context()) as response, open(tmp_path, "wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        if _md5_of(tmp_path) != MODEL_MD5:
            raise RuntimeError("Downloaded U2Net model failed checksum verification.")
        os.replace(tmp_path, MODEL_PATH)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


class U2NetSegmenter:
    """CPU-only U2Net segmenter adapted from the known-good local tool."""

    def __init__(self):
        import onnxruntime as ort

        ensure_model()
        self.session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

    def predict_alpha(self, image: Image.Image) -> np.ndarray:
        orig_size = image.size
        resized = image.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS)
        array = np.asarray(resized).astype(np.float64) / max(np.asarray(resized).max(), 1e-6)

        mean = (0.485, 0.456, 0.406)
        std = (0.229, 0.224, 0.225)
        normalized = np.empty((320, 320, 3), dtype=np.float64)
        for channel in range(3):
            normalized[:, :, channel] = (array[:, :, channel] - mean[channel]) / std[channel]
        input_tensor = normalized.transpose((2, 0, 1))[None].astype(np.float32)

        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_tensor})
        pred = outputs[0][:, 0, :, :]
        pred = (pred - pred.min()) / max(pred.max() - pred.min(), 1e-6)
        mask = Image.fromarray((np.squeeze(pred).clip(0, 1) * 255).astype("uint8"), mode="L")
        mask = mask.resize(orig_size, Image.Resampling.LANCZOS)
        return np.asarray(mask, dtype=np.float32) / 255.0
