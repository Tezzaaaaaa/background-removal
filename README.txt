![](banner.jpg)

# Background Removal Tool

Remove image backgrounds with a single command using neural-network-based edge detection.

## What it does

This tool removes backgrounds from images and outputs transparent PNGs. It is designed for clean, accurate cutouts while preserving fine detail and keeping the original image dimensions.

## Project

Built and maintained by **Tere** with **Claude** as the coding partner.

The project is being developed as a reusable background-removal component for a larger media-production workflow.

## Requirements

* Python 3.12
* The dependencies listed in `requirements.txt`
* A first run downloads and caches the model (~500 MB)

## Installation

Create the virtual environment and install the dependencies:

```bash
python3.12 -m venv ~/.venv/background-removal
~/.venv/background-removal/bin/pip install -r requirements.txt
```

Optional: create a convenient command in `~/bin`:

```bash
ln -s /path/to/background-removal/run ~/bin/remove-background
```

## Usage

### Direct

```bash
./run remove <input_image> <output_image>
```

### Convenience command

```bash
remove-background <input_image> <output_image>
```

## Examples

Remove the background from a photo:

```bash
./run remove photo.jpg photo_no_bg.png
```

Process a product image:

```bash
./run remove product.jpg transparent_product.png
```

Process a portrait:

```bash
remove-background portrait.jpg portrait_cutout.png
```

## Output

* Output is always a transparent PNG.
* If a non-PNG extension is supplied, it is replaced with `.png`.
* Output dimensions match the input image exactly.

## Development

Run linting:

```bash
./run lint
```

Run the background-removal test:

```bash
./run test src/remove_background_test.py::test_remove_background_creates_alpha
```

Run the full quality checks:

```bash
./run check
```

## License

This project is licensed under [CC BY-NC 4.0](https://darren-static.waft.dev/license) - free to use and modify, but no commercial use without permission.
