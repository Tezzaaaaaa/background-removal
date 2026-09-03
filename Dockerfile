FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/root/.cache/huggingface

WORKDIR /app

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
COPY pyproject.toml ./
COPY cutout/ cutout/
RUN pip install --no-cache-dir .
COPY serving/ serving/

EXPOSE 8756
CMD ["uvicorn", "serving.app:app", "--host", "0.0.0.0", "--port", "8756"]
