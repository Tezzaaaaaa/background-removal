"""Single-model registry for the background-removal service."""
from bgr.segmenter import BiRefNetSegmenter, Segmenter

MODEL_ID = "egeorcun/lucida"
INPUT_SIZE = 1024


def get_segmenter() -> Segmenter:
    return BiRefNetSegmenter(model_id=MODEL_ID, input_size=INPUT_SIZE, name="lucida")
