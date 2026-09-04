# Third-Party Notices

## U²-Net

This project downloads the `u2net.onnx` model at first run. The model is **not bundled in this repository**.

- Model: U²-Net (`u2net.onnx`)
- Original project: Xuebin Qin et al., University of Alberta
- Base model: `xuebinqin/U-2-Net`
- Model distribution source: `Heliosoph/u2net-onnx`
- Model licence: **Apache License 2.0**
- Pinned model revision: `7fc34de`
- SHA-256: `8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491`

The Apache License 2.0 permits commercial use, modification, and distribution subject to its terms, including preservation of applicable copyright and licence notices.

The model repository identifies these ONNX checkpoints as official U²-Net checkpoints republished from the `danielgatis/rembg` release and identifies the underlying U²-Net project as Apache-2.0.

## Runtime dependencies

The background-removal script uses the following Python packages. They are installed separately by the setup process and are not included in this repository:

- **ONNX Runtime** — MIT License
- **Pillow** — HPND License
- **NumPy** — BSD 3-Clause License
- **certifi** — Mozilla Public License 2.0

Each dependency remains subject to its own licence. Users redistributing the software should retain the applicable notices required by those licences.

## U²-Net citation

Qin, Xuebin; Zhang, Zichen; Huang, Chenyang; Dehghan, Masood; Zaiane, Osmar R.; Jagersand, Martin. “U²-Net: Going Deeper with Nested U-Structure for Salient Object Detection.” Pattern Recognition, volume 106, 107404, 2020.
