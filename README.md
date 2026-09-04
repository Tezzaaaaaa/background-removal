<div align="center">

<img src="banner.jpg" alt="Background Removal Tool" width="100%">

# Background Removal Tool

**Fast, high-quality image background removal from the command line.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey?style=flat-square)](https://darren-static.waft.dev/license)

</div>

---

## Overview

Background Removal Tool turns ordinary images into clean, transparent PNG cutouts with a single command.

It uses a neural-network-based background-removal model designed for accurate edges, fine details, and consistent output dimensions.

### Designed for

- Portraits
- Product images
- Objects and subjects
- Creative assets
- Video and media-production workflows
- Automated image-processing pipelines

---

## Features

| Feature | Description |
| --- | --- |
| **Automatic removal** | Detects and removes image backgrounds automatically |
| **Transparent output** | Produces PNG files with an alpha channel |
| **Detail preservation** | Designed to retain fine edges and subject detail |
| **Exact dimensions** | Output dimensions match the source image |
| **Command line** | Simple CLI designed for scripting and automation |
| **Cached model** | Model is downloaded once and reused locally |

---

## Quick Start

### 1. Install

Create the virtual environment and install the dependencies:

```bash
python3.12 -m venv ~/.venv/background-removal
~/.venv/background-removal/bin/pip install -r requirements.txt
```

### 2. Remove a background

```bash
./run remove input.jpg output.png
```

That's it.

---

## Usage

### Direct command

```bash
./run remove <input_image> <output_image>
```

### Optional convenience command

Create a symlink:

```bash
ln -s /path/to/background-removal/run ~/bin/remove-background
```

Then run:

```bash
remove-background <input_image> <output_image>
```

---

## Examples

### Photo

```bash
./run remove photo.jpg photo_no_bg.png
```

### Product

```bash
./run remove product.jpg transparent_product.png
```

### Portrait

```bash
remove-background portrait.jpg portrait_cutout.png
```

---

## Output

The tool produces a transparent PNG.

- Output format: **PNG**
- Transparency: **Alpha channel**
- Dimensions: **Same as input**
- Non-PNG output extensions are automatically replaced with `.png`
- Model cache: approximately **500 MB** on first run

---

## Development

### Lint

```bash
./run lint
```

### Test

```bash
./run test src/remove_background_test.py::test_remove_background_creates_alpha
```

### Full checks

```bash
./run check
```

---

## Project

Built and maintained by **Tere**, with **Claude** as the coding partner.

The tool is being developed as a reusable component within a broader media-production workflow, where background removal can be used as an underlying processing capability rather than a standalone destination.

---

## Repository Structure

```text
background-removal/
├── src/                # Background-removal implementation
├── requirements.txt    # Python dependencies
├── run                 # CLI entry point
├── claude.md           # Development guidance
├── banner.jpg          # README artwork
└── README.md           # Project documentation
```

---

## License

This project is licensed under **CC BY-NC 4.0**.

Free to use and modify for non-commercial purposes. Commercial use requires permission.

---

<div align="center">

**Background Removal Tool**

Built for reusable image-processing workflows.

</div>