#!/bin/bash
# Installer for the personal background removal tool.
# Sets up an isolated Python environment in ~/.background-removal-tool
# and installs remove_bg.py there, so it never conflicts with anything
# else on your Mac.

set -e

INSTALL_DIR="$HOME/.background-removal-tool"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing background removal tool to $INSTALL_DIR ..."

# onnxruntime (a hard dependency of the background-removal model) does not
# yet ship stable wheels for every newest Python release. Look for a Python
# version known to work, preferring the newest supported one, instead of
# blindly using whatever "python3" happens to point to.
PYBIN=""
for cand in python3.12 python3.13 python3.11 python3.10; do
    if command -v "$cand" >/dev/null 2>&1; then
        PYBIN="$cand"
        break
    fi
done

if [ -z "$PYBIN" ]; then
    if command -v python3 >/dev/null 2>&1; then
        PYVER="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
        echo "Only found python3 (version $PYVER), and no python3.10-3.13 install."
        echo "onnxruntime doesn't yet support brand-new Python releases (e.g. 3.14)."
        echo "Install a compatible version with Homebrew, then re-run this installer:"
        echo "  brew install python@3.12"
        exit 1
    else
        echo "python3 was not found."
        echo "Install it first: either run 'xcode-select --install' (installs Apple's python3),"
        echo "or install Python from https://www.python.org/downloads/, then re-run this installer."
        exit 1
    fi
fi

echo "Using $PYBIN ($($PYBIN -c 'import sys; print(sys.version.split()[0])'))"

mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/remove_bg.py" "$INSTALL_DIR/remove_bg.py"

echo "Creating virtual environment..."
"$PYBIN" -m venv --clear "$INSTALL_DIR/venv"

# Sanity check: confirm the venv's interpreter is actually the one we asked
# for. A stale venv directory from an earlier failed attempt can otherwise
# leave behind a python3 that resolves to a different (wrong) interpreter.
EXPECTED_VER="$($PYBIN -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
ACTUAL_VER="$("$INSTALL_DIR/venv/bin/python3" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
if [ "$EXPECTED_VER" != "$ACTUAL_VER" ]; then
    echo "Something went wrong: expected the virtual environment to use"
    echo "Python $EXPECTED_VER but it's actually using Python $ACTUAL_VER."
    echo "Try removing the install directory and re-running:"
    echo "  rm -rf $INSTALL_DIR"
    echo "  bash $SCRIPT_DIR/install.sh"
    exit 1
fi

echo "Installing dependencies (this is quick — no heavy build tools needed)..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip >/dev/null
"$INSTALL_DIR/venv/bin/pip" install onnxruntime pillow numpy certifi

echo ""
echo "Downloading the AI model (one-time, ~176MB)..."
"$INSTALL_DIR/venv/bin/python3" -c "
import sys
sys.path.insert(0, '$INSTALL_DIR')
from remove_bg import ensure_model
ensure_model()
"

echo ""
echo "Done! The tool is installed at: $INSTALL_DIR"
echo "Test it with:"
echo "  $INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/remove_bg.py /path/to/some/photo.jpg"
echo ""
echo "Next: follow the 'Set up the right-click Quick Action' instructions"
echo "to hook this up to Finder's right-click menu."
