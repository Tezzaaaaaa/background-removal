"""Targeted edge refinement for uncertain matte regions."""
import numpy as np
from PIL import Image
from scipy import ndimage
from .segmenter import Segmenter


def _regions(mask: np.ndarray, min_region: int = 256, max_patches: int = 6):
    labels, count = ndimage.label(ndimage.binary_dilation(mask, iterations=4))
    if count == 0:
        return []
    sizes = ndimage.sum(mask, labels, range(1, count + 1))
    boxes = ndimage.find_objects(labels)
    out = []
    for i in np.argsort(sizes)[::-1][:max_patches]:
        if sizes[i] < min_region:
            break
        sl = boxes[i]
        out.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop))
    return out


def refine_alpha(segmenter: Segmenter, image: Image.Image, alpha: np.ndarray) -> np.ndarray:
    h, w = alpha.shape
    uncertain = (alpha > 0.05) & (alpha < 0.95)
    result = alpha.copy()
    rgb = image.convert("RGB")

    for y0, y1, x0, x1 in _regions(uncertain):
        cy = int((y1 - y0) * 0.35)
        cx = int((x1 - x0) * 0.35)
        yy0, yy1 = max(0, y0 - cy), min(h, y1 + cy)
        xx0, xx1 = max(0, x0 - cx), min(w, x1 + cx)
        crop = rgb.crop((xx0, yy0, xx1, yy1))
        refined = segmenter.predict_alpha(crop)

        band = uncertain[yy0:yy1, xx0:xx1].astype(np.float32)
        weight = ndimage.gaussian_filter(band, 2).clip(0, 1)
        weight[band == 0] = 0
        result[yy0:yy1, xx0:xx1] = (
            weight * refined + (1 - weight) * result[yy0:yy1, xx0:xx1]
        )

    return result.clip(0, 1).astype(np.float32)
