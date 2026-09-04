#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/macOS/BackgroundRemoval"
BUILD="$SRC/.build-app"
APP="$BUILD/Background Removal.app"
CONTENTS="$APP/Contents"
RESOURCES="$CONTENTS/Resources"
MACOS="$CONTENTS/MacOS"
EXT="$CONTENTS/PlugIns/Remove Background.appex"
EXT_CONTENTS="$EXT/Contents"
EXT_MACOS="$EXT_CONTENTS/MacOS"

rm -rf "$BUILD"
mkdir -p "$RESOURCES" "$MACOS" "$EXT_MACOS"

SDK="$(xcrun --sdk macosx --show-sdk-path)"
SWIFTC="$(xcrun --find swiftc)"

build_arch() {
  local arch="$1"
  local app_binary="$BUILD/BackgroundRemoval-$arch"
  local ext_binary="$BUILD/FinderAction-$arch"

  "$SWIFTC" \
    -sdk "$SDK" \
    -target "${arch}-apple-macosx13.0" \
    -framework SwiftUI \
    -framework AppKit \
    "$SRC/BackgroundRemovalApp.swift" \
    -o "$app_binary"

  "$SWIFTC" \
    -sdk "$SDK" \
    -target "${arch}-apple-macosx13.0" \
    -framework Foundation \
    -framework UniformTypeIdentifiers \
    "$SRC/FinderAction/FinderAction.swift" \
    -o "$ext_binary"
}

build_arch x86_64
build_arch arm64

lipo -create "$BUILD/BackgroundRemoval-x86_64" "$BUILD/BackgroundRemoval-arm64" -output "$MACOS/BackgroundRemoval"
lipo -create "$BUILD/FinderAction-x86_64" "$BUILD/FinderAction-arm64" -output "$EXT_MACOS/FinderAction"

cp "$SRC/Info.plist" "$CONTENTS/Info.plist"
cp "$SRC/FinderAction/Info.plist" "$EXT_CONTENTS/Info.plist"
cp "$SRC/setup-runtime.command" "$RESOURCES/setup-runtime.command"
cp "$ROOT/remove_bg.py" "$RESOURCES/remove_bg.py"
chmod +x "$MACOS/BackgroundRemoval" "$EXT_MACOS/FinderAction" "$RESOURCES/setup-runtime.command"

codesign --force --deep --sign - "$APP" >/dev/null

mkdir -p "$BUILD/dist"
ditto -c -k --sequesterRsrc --keepParent "$APP" "$BUILD/dist/Background-Removal-macOS.zip"
printf '%s\n' "$BUILD/dist/Background-Removal-macOS.zip"
