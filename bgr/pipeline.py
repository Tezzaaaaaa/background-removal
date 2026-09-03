"""Foreground extraction pipeline."""
import numpy as np
from PIL import Image
from bgr.segmenter import Segmenter


class PipelineSegmenter(Segmenter):
    def __init__(self, base: Segmenter):
        self.base = base
        self.name = base.name

    def predict_alpha(self, image: Image.Image) -> np.ndarray:
        return self.base.predict_alpha(image)

    def process(self, image: Image.Image) -> Image.Image:
        alpha = self.predict_alpha(image)
        rgba = image.convert("RGB").copy()
        rgba.putalpha(Image.fromarray(np.round(alpha * 255).astype(np.uint8)))
        return rgba
