#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/macOS/BackgroundRemoval"
BUILD="$SRC/.build-app"
APP="$BUILD/Background Removal.app"
CONTENTS="$APP/Contents"
RESOURCES="$CONTENTS/Resources"

rm -rf "$BUILD"
mkdir -p "$RESOURCES/MacOS"

SDK="$(xcrun --sdk macosx --show-sdk-path)"
SWIFTC="$(xcrun --find swiftc)"

"$SWIFTC" \
  -sdk "$SDK" \
  -target x86_64-apple-macosx10.15 \
  -framework SwiftUI \
  "$SRC/BackgroundRemovalApp.swift" \
  -o "$CONTENTS/BackgroundRemoval"

cp "$SRC/Info.plist" "$CONTENTS/Info.plist"
cp "$SRC/setup-runtime.command" "$RESOURCES/setup-runtime.command"
cp "$SRC/install-quick-action.command" "$RESOURCES/install-quick-action.command"
cp "$ROOT/remove_bg.py" "$RESOURCES/remove_bg.py"
chmod +x "$CONTENTS/BackgroundRemoval" "$RESOURCES"/*.command

codesign --force --deep --sign - "$APP" >/dev/null

mkdir -p "$BUILD/dist"
ditto -c -k --sequesterRsrc --keepParent "$APP" "$BUILD/dist/Background-Removal-macOS.zip"
printf '%s\n' "$BUILD/dist/Background-Removal-macOS.zip"
