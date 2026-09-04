# Background Removal for macOS

<p align="center">
  <b>One-click background removal right from Finder</b><br>
  Local processing • No account • No cloud upload
</p>

---

## What it does

- Automatically removes backgrounds from images.
- Creates transparent PNGs next to the original image.
- Processes images locally on your Mac.
- Uses U²-Net for the lightweight Finder workflow.
- Supports batch processing from Finder.

## Setup

The normal user experience requires **no Terminal commands** and does not require Python to be installed first.

1. Download **Background Removal**.
2. Open the app.
3. Select **Set Up** on first launch.
4. Let setup install its private runtime, required packages, and AI model.
5. When setup says **You're ready**, use Finder normally.

Then:

**Finder → select an image → right-click → Quick Actions → Remove Background**

The resulting transparent PNG is saved beside the original as:

```text
photo-nobg.png
```

### What first-run setup does

The setup app automatically prepares the private runtime under:

```text
~/Library/Application Support/Background Removal/
```

It installs a private Python runtime, the required packages, downloads and verifies the AI model once, and installs the Finder workflow. The user does not need to install Python, create a virtual environment, run `pip`, configure a Shortcut, or enter shell commands manually.

An internet connection is required during first-time setup to obtain the required components and model. Image processing itself is local.

## Requirements

- macOS 10.15 or later
- Internet connection for first-time setup

## Developer build

The repository includes the macOS setup application sources under `macOS/BackgroundRemoval/`.

From the repository root on a Mac with Xcode Command Line Tools installed:

```bash
bash macOS/BackgroundRemoval/build-app.sh
```

The generated application and ZIP are placed in:

```text
macOS/BackgroundRemoval/.build-app/
```

The command is for developers building the distribution package; normal users should receive the packaged application rather than build it themselves.

## Existing command-line interface

The original `remove_bg.py` CLI remains available for development and recovery workflows. It is not part of the normal consumer setup path.

```bash
python3 remove_bg.py /path/to/photo.jpg
```

## Output

Input images are left untouched. A new transparent PNG is created alongside each source image:

```text
original.jpg
original-nobg.png
```

## Privacy

The background-removal operation runs locally. Images are not uploaded to a background-removal service.

The first-run setup does require network access to install dependencies and obtain the AI model.

## Project structure

```text
background-removal/
├── macOS/
│   └── BackgroundRemoval/
│       ├── BackgroundRemovalApp.swift
│       ├── Info.plist
│       ├── setup-runtime.command
│       ├── install-quick-action.command
│       └── build-app.sh
├── remove_bg.py
├── cutout/
├── serving/
├── pyproject.toml
└── README.md
```

## License

MIT License.
