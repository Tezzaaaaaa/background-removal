"""Cutout's end-to-end matte processing pipeline."""
import numpy as np
from PIL import Image
from .decontaminate import decontaminate
from .refiner import refine_alpha
from .segmenter import CutoutSegmenter


class CutoutPipeline:
    def __init__(self):
        self.segmenter = CutoutSegmenter()

    def process(self, image: Image.Image) -> Image.Image:
        alpha = self.segmenter.predict_alpha(image)
        alpha = refine_alpha(self.segmenter, image, alpha)
        return decontaminate(image, alpha)
