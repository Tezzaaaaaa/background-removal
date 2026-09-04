"""Core segmentation engines used by Cutout."""
from abc import ABC, abstractmethod

import numpy as np
import torch
from PIL import Image
from torchvision import transforms


INPUT_SIZE = 1024
MODEL_WEIGHTS = "egeorcun/lucida"


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class Segmenter(ABC):
    @abstractmethod
    def predict_alpha(self, image: Image.Image) -> np.ndarray:
        """Return an HxW float32 alpha mask in the range 0..1."""


class CutoutSegmenter(Segmenter):
    """High-resolution BiRefNet fine-tune adapted for Cutout."""

    def __init__(self):
        from transformers import AutoModelForImageSegmentation

        self.device = get_device()
        self.model = AutoModelForImageSegmentation.from_pretrained(
            MODEL_WEIGHTS,
            trust_remote_code=True,
            dtype=torch.float32,
        )
        self.model.to(self.device).eval()
        self.transform = transforms.Compose([
            transforms.Resize((INPUT_SIZE, INPUT_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225],
            ),
        ])

    @torch.inference_mode()
    def predict_alpha(self, image: Image.Image) -> np.ndarray:
        rgb = image.convert("RGB")
        inp = self.transform(rgb).unsqueeze(0).to(self.device)
        pred = self.model(inp)[-1].sigmoid().cpu()[0, 0]
        alpha = transforms.functional.resize(
            pred.unsqueeze(0), rgb.size[::-1]
        )[0]
        return alpha.clamp(0, 1).numpy().astype(np.float32)
