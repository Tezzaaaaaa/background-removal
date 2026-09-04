#!/bin/zsh
set -euo pipefail

APP_SUPPORT="${1:?application support path required}"
RESOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$APP_SUPPORT/runtime"
UV="$RUNTIME/uv"
VENV="$RUNTIME/venv"
PY="$VENV/bin/python3"
UV_VERSION="0.12.9"

mkdir -p "$RUNTIME"

# Bootstrap a private Python runtime so normal users never need to install
# Python or use Terminal. uv supplies a managed CPython interpreter.
if [[ ! -x "$UV" ]]; then
  echo "Downloading setup runtime..."
  curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | env UV_INSTALL_DIR="$RUNTIME" UV_NO_MODIFY_PATH=1 sh
  [[ -x "$UV" ]] || { echo "Could not install the setup runtime."; exit 1; }
fi

if [[ ! -x "$PY" ]]; then
  echo "Installing private Python runtime..."
  UV_PYTHON_INSTALL_DIR="$RUNTIME/python" "$UV" python install 3.12
  UV_PYTHON_INSTALL_DIR="$RUNTIME/python" "$UV" venv --python 3.12 "$VENV"
fi

"$PY" -m pip install --disable-pip-version-check --quiet --upgrade pip
"$PY" -m pip install --disable-pip-version-check --quiet onnxruntime pillow numpy certifi

install -m 755 "$RESOURCE_DIR/remove_bg.py" "$RUNTIME/remove_bg.py"

echo "Downloading AI model..."
"$PY" "$RUNTIME/remove_bg.py" --download-model

echo "Runtime ready."
