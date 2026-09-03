"""Command line interface for Cutout."""
import argparse
from PIL import Image
from .pipeline import CutoutPipeline


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cutout")
    parser.add_argument("input", help="input JPG, PNG, or WebP")
    parser.add_argument("-o", "--output", required=True, help="output PNG")
    args = parser.parse_args(argv)

    output = CutoutPipeline().process(Image.open(args.input))
    output.save(args.output, format="PNG", optimize=True)
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
