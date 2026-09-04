# Background Remover for macOS

<p align="center">
  <img src="https://img.shields.io/badge/macOS-10.15+-blue.svg" alt="macOS"/>
  <img src="https://img.shields.io/badge/python-3.10--3.13-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/status-stable-brightgreen.svg" alt="Status"/>
</p>

<p align="center">
  <b>One-click background removal right from Finder</b><br>
  100% local after setup • No account • Completely free
</p>

---

## ✨ Features

- **Finder Integration** – Right-click any image → Quick Actions → Remove Background
- **Batch Processing** – Select multiple images at once
- **100% Local** – Everything runs on your machine, nothing leaves your Mac
- **One-Time Setup** – Downloads a single AI model (~176MB) and you're done
- **Lightweight** – Minimal dependencies, no compiler required

## 📸 Demo

```
Right-click an image → Quick Actions → Remove Background
                    ↓
         "photo-nobg.png" appears next to the original
                    ↓
            Background removed. Done.
```

## 🚀 Installation

### Prerequisites

- macOS 10.15 or later
- Python 3.10–3.13 (Homebrew recommended)

### One‑Line Setup

```bash
git clone https://github.com/yourusername/bg-removal-tool.git ~/bg-removal-tool
cd ~/bg-removal-tool
bash install.sh
```

The install script will:
1. Create a private Python virtual environment at `~/.background-removal-tool/venv`
2. Download the AI model (~176MB)
3. Install minimal dependencies: `onnxruntime`, `pillow`, `numpy`, and `certifi`

### Verify Installation

```bash
~/.background-removal-tool/venv/bin/python3 ~/.background-removal-tool/remove_bg.py /path/to/photo.jpg
```

You should see `photo-nobg.png` appear next to the original.

## 🖱️ Setting Up the Quick Action

### Step 1: Open Shortcuts.app

Create a **New Shortcut** and name it `Remove Background`.

### Step 2: Configure as Quick Action

Tap the **Info** icon (ℹ️) and enable:

- **Use as Quick Action** ✅
- **Show in:** Finder only
- **Workflow receives:** Image files

### Step 3: Add Shell Script Action

Add a **Run Shell Script** action with these settings:

| Setting | Value |
|---------|-------|
| Shell | `/bin/zsh` |
| Pass Input | `as arguments` |
| Run as Administrator | ❌ **UNCHECKED** |

### Step 4: Script Contents

```bash
for f in "$@"; do "$HOME/.background-removal-tool/venv/bin/python3" "$HOME/.background-removal-tool/remove_bg.py" "$f"; done
```

> **Note:** The semicolon before `done` is required!

### Step 5: Save

Press `⌘ + S` and you're all set.

## 🎯 Usage

1. Select one or more image files in Finder
2. Right-click → **Quick Actions** → **Remove Background**
3. Wait a few seconds
4. New files appear: `<original>-nobg.png` with transparent backgrounds
5. macOS notification confirms completion

## 🛠️ Troubleshooting

### Python Version Issues

If `install.sh` fails with a Python version error, the script auto-detects and prefers in this order:
- `python3.12` → `python3.13` → `python3.11` → `python3.10`

### SSL Certificate Errors

If you see `CERTIFICATE_VERIFY_FAILED` during model download, `remove_bg.py` already uses `certifi`'s CA bundle explicitly to avoid this.

### Fresh Install

If you need to start over:

```bash
rm -rf ~/.background-removal-tool
cd ~/bg-removal-tool
bash install.sh
```

The script uses `venv --clear` and verifies the Python interpreter version automatically.

## 📁 Project Structure

```
bg-removal-tool/
├── install.sh              # One‑click setup
├── remove_bg.py            # Core background removal script
└── README.md               # This file
```

## 📄 License

The project code is licensed under the **MIT License**.

The U²-Net model is a separate third-party component and is **not bundled with this repository**. It is downloaded at first run from a pinned model revision identified as **Apache License 2.0**, with SHA-256 verification before use. See [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for model provenance, attribution, and dependency licence information.

The MIT licence for this project does not relicense third-party dependencies or model weights. Each third-party component remains subject to its own licence.

---

<p align="center">
  Made for macOS users who just want to remove backgrounds without the cloud
</p>