"""Remove background colour contamination from soft foreground edges."""
import numpy as np
from PIL import Image
from pymatting import estimate_foreground_ml


def decontaminate(image: Image.Image, alpha: np.ndarray) -> Image.Image:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float64) / 255.0
    if alpha.shape != rgb.shape[:2]:
        raise ValueError(f"alpha shape {alpha.shape} != image {rgb.shape[:2]}")
    foreground = estimate_foreground_ml(rgb, alpha.astype(np.float64))
    rgba = np.dstack([np.clip(foreground, 0, 1), alpha.clip(0, 1)])
    return Image.fromarray(np.round(rgba * 255).astype(np.uint8), mode="RGBA")
