#!/bin/zsh
set -euo pipefail

APP_SUPPORT="${1:?application support path required}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUNTIME="$APP_SUPPORT/runtime"
VENV="$RUNTIME/venv"
PY="$VENV/bin/python3"

mkdir -p "$RUNTIME"

# Prefer an existing Python 3 interpreter. The app runs this silently so the
# user does not need Terminal; this is only the first-run bootstrap.
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
  echo "Python 3.10–3.13 is required for this build. Install Xcode Command Line Tools or Python 3.12, then run setup again."
  exit 1
fi

if [[ ! -x "$PY" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$PY" -m pip install --disable-pip-version-check --quiet --upgrade pip
"$PY" -m pip install --disable-pip-version-check --quiet onnxruntime pillow numpy certifi

# Keep the processing script in the private application-support directory.
install -m 755 "$ROOT/remove_bg.py" "$RUNTIME/remove_bg.py"

echo "Runtime ready."
