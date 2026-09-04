#!/usr/bin/env python3
"""
Personal background removal tool.

Runs the u2net segmentation model directly via onnxruntime (no rembg /
pymatting / numba / llvmlite dependency chain, which fails to build on
Intel Macs). Only needs onnxruntime, pillow, and numpy.

Takes one or more image file paths, removes the background from each,
and saves a new PNG (with transparency) next to the original as
"<originalname>-nobg.png". Shows a macOS notification when done and
reveals the last output file in Finder.
"""
import sys
import os
import subprocess
import hashlib
import ssl
import urllib.request

MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx"
MODEL_MD5 = "60024c5c889badc19c04ad937298a77b"
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "u2net.onnx")


def _ssl_context():
    # Plain urllib relies on the interpreter's default CA bundle, which is
    # frequently missing or stale on macOS (a common cause of
    # CERTIFICATE_VERIFY_FAILED). Prefer certifi's bundle when available.
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def notify(title, message):
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False,
        )
    except Exception:
        pass


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if os.path.isfile(MODEL_PATH) and md5_of(MODEL_PATH) == MODEL_MD5:
        return
    print("Downloading segmentation model (one-time, ~176MB)...")
    notify("Background Removal — First Run", "Downloading AI model (~176MB), this happens once...")

    context = _ssl_context()
    tmp_path = MODEL_PATH + ".part"
    with urllib.request.urlopen(MODEL_URL, context=context) as resp, open(tmp_path, "wb") as f:
        total = resp.getheader("Content-Length")
        total = int(total) if total else None
        downloaded = 0
        last_pct = -1
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded * 100 // total
                if pct != last_pct:
                    print(f"\r  {pct}%", end="", flush=True)
                    last_pct = pct
    print()
    if md5_of(tmp_path) != MODEL_MD5:
        os.remove(tmp_path)
        raise RuntimeError("Downloaded model failed checksum verification.")
    os.replace(tmp_path, MODEL_PATH)


def remove_background(session, img):
    import numpy as np
    from PIL import Image

    orig_size = img.size
    im = img.convert("RGB").resize((320, 320), Image.Resampling.LANCZOS)

    im_ary = np.array(im).astype(np.float64)
    im_ary = im_ary / max(im_ary.max(), 1e-6)

    mean = (0.485, 0.456, 0.406)
    std = (0.229, 0.224, 0.225)
    tmp = np.zeros((320, 320, 3))
    for c in range(3):
        tmp[:, :, c] = (im_ary[:, :, c] - mean[c]) / std[c]
    tmp = tmp.transpose((2, 0, 1))
    input_tensor = np.expand_dims(tmp, 0).astype(np.float32)

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: input_tensor})

    pred = outputs[0][:, 0, :, :]
    pred = (pred - pred.min()) / (pred.max() - pred.min())
    pred = np.squeeze(pred)

    mask = Image.fromarray((pred.clip(0, 1) * 255).astype("uint8"), mode="L")
    mask = mask.resize(orig_size, Image.Resampling.LANCZOS)

    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def main():
    paths = [p for p in sys.argv[1:] if p.strip()]
    if not paths:
        notify("Background Removal", "No image files were provided.")
        print("No input files provided.")
        return

    try:
        ensure_model()
    except Exception as e:
        notify("Background Removal Failed", f"Could not download model: {e}")
        print(f"ERROR downloading model: {e}", file=sys.stderr)
        return

    import onnxruntime as ort
    from PIL import Image

    session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

    outputs = []
    errors = []

    for path in paths:
        try:
            if not os.path.isfile(path):
                errors.append(f"{os.path.basename(path)}: not a file")
                continue
            img = Image.open(path)
            result = remove_background(session, img)
            base, _ext = os.path.splitext(path)
            out_path = f"{base}-nobg.png"
            result.save(out_path)
            outputs.append(out_path)
        except Exception as e:
            errors.append(f"{os.path.basename(path)}: {e}")

    if outputs:
        if len(outputs) == 1:
            notify("Background Removed", os.path.basename(outputs[0]))
        else:
            notify("Background Removed", f"{len(outputs)} images processed")
        try:
            subprocess.run(["open", "-R", outputs[-1]], check=False)
        except Exception:
            pass

    if errors:
        notify("Background Removal — some files failed", "; ".join(errors)[:200])
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
