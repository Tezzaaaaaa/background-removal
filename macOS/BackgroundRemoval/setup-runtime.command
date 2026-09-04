#!/bin/zsh
set -euo pipefail

APP_SUPPORT="${1:?application support path required}"
RESOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNTIME="$APP_SUPPORT/runtime"
VENV="$RUNTIME/venv"
PY="$VENV/bin/python3"

mkdir -p "$RUNTIME"

PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) and sys.version_info < (3,14) else 1)' 2>/dev/null; then
      PYTHON="$(command -v "$candidate")"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "Python 3.10–3.13 is required for this build."
  exit 1
fi

if [[ ! -x "$PY" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$PY" -m pip install --disable-pip-version-check --quiet --upgrade pip
"$PY" -m pip install --disable-pip-version-check --quiet onnxruntime pillow numpy certifi

install -m 755 "$RESOURCE_DIR/remove_bg.py" "$RUNTIME/remove_bg.py"
echo "Runtime ready."
