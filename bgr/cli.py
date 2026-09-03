"""Command line interface: bgr remove input.jpg -o output.png"""
import argparse
from PIL import Image
from bgr.pipeline import PipelineSegmenter
from bgr.registry import get_segmenter


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bgr")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rm = sub.add_parser("remove", help="remove the background")
    rm.add_argument("input")
    rm.add_argument("-o", "--output", required=True)
    args = ap.parse_args(argv)
    out = PipelineSegmenter(get_segmenter()).process(Image.open(args.input))
    out.save(args.output, format="PNG")
    print(f"saved: {args.output}")


if __name__ == "__main__":
    main()
