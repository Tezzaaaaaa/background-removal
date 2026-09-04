#!/bin/zsh
set -euo pipefail

APP_SUPPORT="${1:?application support path required}"
SERVICES="$HOME/Library/Services"
SERVICE="$SERVICES/Remove Background.workflow"
RUNTIME="$APP_SUPPORT/runtime"
PY="$RUNTIME/venv/bin/python3"
SCRIPT="$RUNTIME/remove_bg.py"

mkdir -p "$SERVICES"
rm -rf "$SERVICE"
mkdir -p "$SERVICE/Contents"

# Automator services are bundles containing a workflow document. Generate the
# minimal service here so setup remains automatic and Finder can expose it as
# a Quick Action/Service without asking the user to build a Shortcut manually.
cat > "$SERVICE/Contents/document.wflow" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>AMApplicationBuild</key><string>macOS</string>
<key>AMApplication</key><string>Finder</string>
<key>AMInputType</key><string>files</string>
<key>AMOutputType</key><string>none</string>
<key>AMIconName</key><string>NSActionTemplate</string>
<key>AMName</key><string>Remove Background</string>
<key>actions</key><array>
<dict>
<key>actionBundleID</key><string>com.apple.RunShellScript</string>
<key>actionName</key><string>Run Shell Script</string>
<key>actionParameters</key><dict>
<key>COMMAND_STRING</key><string>for f in "$@"; do "$PY" "$SCRIPT" "$f"; done</string>
<key>INPUT_METHOD</key><integer>1</integer>
<key>INPUT_TYPE</key><string>files</string>
<key>Shell</key><string>/bin/zsh</string>
</dict>
</dict>
</array>
</dict></plist>
EOF

# Refresh LaunchServices so Finder can discover the newly installed service.
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister \
  -f "$SERVICE" >/dev/null 2>&1 || true

killall Finder >/dev/null 2>&1 || true

echo "Finder Quick Action installed."
