"""Cutout's end-to-end matte processing pipeline."""
import numpy as np
from PIL import Image
from .decontaminate import decontaminate
from .refiner import refine_alpha
from .segmenter import CutoutSegmenter


class CutoutPipeline:
    def __init__(self):
        try:
            self.segmenter = CutoutSegmenter()
            self.engine = "birefnet"
        except Exception as primary_error:
            from .u2net import U2NetSegmenter

            try:
                self.segmenter = U2NetSegmenter()
                self.engine = "u2net"
            except Exception:
                raise primary_error

    def process(self, image: Image.Image) -> Image.Image:
        alpha = self.segmenter.predict_alpha(image)
        if self.engine == "birefnet":
            alpha = refine_alpha(self.segmenter, image, alpha)
        return decontaminate(image, alpha)
