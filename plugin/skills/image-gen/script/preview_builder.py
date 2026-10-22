#!/usr/bin/env python3
"""
preview_builder.py — build operator review previews for an Amazon image-suite.

Replaces the old "stack all JPGs on one axis" preview with three review artifacts:

  1) contact   套图预览图   — a labelled GRID of all generated slot images
                              (uniform tiles, captions, title bar; scales to 1..N images)
  2) compare   对比图       — YOUR image vs COMPETITOR/REF, side by side, per pair
                              (so the operator sees exactly where we're weaker)
  3) direction 意向方案方向 — YOUR product + chosen reference(s) on one board, per slot
                              (locally composited so the operator sees the INTENDED direction
                               before we spend tokens generating)

Why this is better than the original snippet:
  - Never assumes all inputs share one size — every image is letterboxed into a uniform
    tile (aspect kept, centered on white), so mixed 1024/1254/2048 + landscape/portrait
    no longer misalign or distort.
  - Grid layout (cols x rows) instead of a single tall/wide strip — readable at any count.
  - Captions per tile (slot / color / score / "YOURS" vs "REF") + a title header.
  - Robust: skips unreadable files, fixes EXIF orientation, flattens RGBA/P to RGB,
    caps tile size so previews stay small enough to send over chat.
  - Pure stdlib + Pillow. No network.

CLI:
  python preview_builder.py contact   --in DIR_OR_GLOB [--cols N] [--title T] --out preview.jpg
  python preview_builder.py compare   --pairs YOURS=REF [YOURS=REF ...] [--title T] --out compare.jpg
  python preview_builder.py direction --own PROD.jpg --refs R1 [R2 ...] [--label "S2 infographic"] --out dir.jpg

Programmatic: import build_contact_sheet / build_comparison / build_direction_board.
"""

from __future__ import annotations
import os
import sys
import glob
import argparse
from typing import Iterable, Sequence

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit("Pillow required:  pip install Pillow")

# ---- tunables -------------------------------------------------------------
TILE = 520            # max width/height of each image tile (px)
PAD = 18              # gutter between tiles and around the board
CAP_H = 34            # caption strip height under each tile
TITLE_H = 56          # title bar height (0 = no title)
BG = (255, 255, 255)
CAP_BG = (245, 245, 247)
INK = (33, 33, 38)
SUB = (120, 120, 128)
JPEG_Q = 88
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")


# ---- font helper ----------------------------------------------------------
def _font(size: int, bold: bool = False):
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/Library/Fonts/Arial Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf",
         "/Library/Fonts/Arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    )
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _text_w(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]


def _ellipsize(draw, text, font, max_w):
    if _text_w(draw, text, font) <= max_w:
        return text
    while text and _text_w(draw, text + "…", font) > max_w:
        text = text[:-1]
    return text + "…"


# ---- image loading --------------------------------------------------------
def _load(path: str) -> Image.Image | None:
    try:
        im = Image.open(path)
        im = ImageOps.exif_transpose(im)      # respect camera/phone rotation
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, BG)
            im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1])
            return bg
        return im.convert("RGB")
    except Exception as e:                      # unreadable / truncated
        print(f"  ⚠ skip {os.path.basename(path)}: {e}")
        return None


def _tile(im: Image.Image, box: int = TILE) -> Image.Image:
    """Letterbox `im` into a box x box white tile, aspect preserved, centered."""
    canvas = Image.new("RGB", (box, box), BG)
    fitted = im.copy()
    fitted.thumbnail((box, box), Image.LANCZOS)
    canvas.paste(fitted, ((box - fitted.width) // 2, (box - fitted.height) // 2))
    return canvas


def _caption(tile: Image.Image, line1: str, line2: str = "") -> Image.Image:
    """Return tile with a caption strip appended below it."""
    w = tile.width
    out = Image.new("RGB", (w, tile.height + CAP_H), CAP_BG)
    out.paste(tile, (0, 0))
    d = ImageDraw.Draw(out)
    f1, f2 = _font(18, bold=True), _font(15)
    d.text((8, tile.height + 4), _ellipsize(d, line1, f1, w - 16), font=f1, fill=INK)
    if line2:
        d.text((8, tile.height + 4 + 19), _ellipsize(d, line2, f2, w - 16), font=f2, fill=SUB)
    return out


def _board(tiles: Sequence[Image.Image], cols: int, title: str = "") -> Image.Image:
    """Lay captioned tiles into a grid with optional title bar."""
    if not tiles:
        raise ValueError("no tiles to render")
    cols = max(1, min(cols, len(tiles)))
    rows = (len(tiles) + cols - 1) // cols
    tw, th = tiles[0].size
    top = TITLE_H if title else 0
    W = PAD + cols * (tw + PAD)
    H = top + PAD + rows * (th + PAD)
    board = Image.new("RGB", (W, H), BG)
    if title:
        d = ImageDraw.Draw(board)
        d.rectangle([0, 0, W, top], fill=(28, 30, 36))
        d.text((PAD, top // 2 - 13), title, font=_font(26, bold=True), fill=(255, 255, 255))
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        board.paste(t, (PAD + c * (tw + PAD), top + PAD + r * (th + PAD)))
    return board


# ---- public builders ------------------------------------------------------
def build_contact_sheet(paths: Sequence[str], out: str,
                        labels: Sequence[str] | None = None,
                        cols: int = 0, title: str = "Image set preview") -> str:
    """套图预览图 — grid of all slot images with captions."""
    loaded = [(p, _load(p)) for p in paths]
    loaded = [(p, im) for p, im in loaded if im is not None]
    if not loaded:
        raise ValueError("no readable images")
    if not cols:                       # auto: ~square grid, max 4 wide
        cols = min(4, max(1, round(len(loaded) ** 0.5)))
    tiles = []
    for i, (p, im) in enumerate(loaded):
        cap = labels[i] if labels and i < len(labels) else os.path.splitext(os.path.basename(p))[0]
        tiles.append(_caption(_tile(im), cap))
    _board(tiles, cols, title).save(out, "JPEG", quality=JPEG_Q)
    print(f"✅ contact sheet → {out}  ({len(tiles)} imgs, {cols} cols)")
    return out


def build_comparison(pairs: Iterable[tuple[str, str]], out: str,
                     title: str = "Yours vs Competitor") -> str:
    """对比图 — each pair rendered as YOURS | REF, stacked down the board."""
    tiles = []
    for own, ref in pairs:
        oi, ri = _load(own), _load(ref)
        if oi is None or ri is None:
            continue
        tiles.append(_caption(_tile(oi), "YOURS", os.path.basename(own)))
        tiles.append(_caption(_tile(ri), "COMPETITOR / REF", os.path.basename(ref)))
    if not tiles:
        raise ValueError("no readable pairs")
    _board(tiles, cols=2, title=title).save(out, "JPEG", quality=JPEG_Q)
    print(f"✅ comparison → {out}  ({len(tiles)//2} pairs)")
    return out


def build_direction_board(own: str, refs: Sequence[str], out: str,
                          label: str = "") -> str:
    """意向方案方向 — YOUR product + chosen reference(s) on one board."""
    oi = _load(own)
    if oi is None:
        raise ValueError(f"cannot read own product image: {own}")
    tiles = [_caption(_tile(oi), "YOUR PRODUCT", os.path.basename(own))]
    for i, r in enumerate(refs, 1):
        ri = _load(r)
        if ri is not None:
            tiles.append(_caption(_tile(ri), f"REF {i} (style to borrow)", os.path.basename(r)))
    cols = min(len(tiles), 3)
    title = f"Direction proposal — {label}" if label else "Direction proposal"
    _board(tiles, cols, title).save(out, "JPEG", quality=JPEG_Q)
    print(f"✅ direction board → {out}  (own + {len(tiles)-1} refs)")
    return out


# ---- input expansion + CLI -----------------------------------------------
def _expand(spec: str) -> list[str]:
    if os.path.isdir(spec):
        files = [os.path.join(spec, f) for f in os.listdir(spec)
                 if f.lower().endswith(IMG_EXTS) and not f.startswith("preview")]
    else:
        files = [f for f in glob.glob(spec) if f.lower().endswith(IMG_EXTS)]
    return sorted(files)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build Amazon image-suite review previews.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("contact", help="grid preview of all slot images")
    c.add_argument("--in", dest="inp", required=True, help="directory or glob")
    c.add_argument("--cols", type=int, default=0)
    c.add_argument("--title", default="Image set preview")
    c.add_argument("--out", required=True)

    m = sub.add_parser("compare", help="yours vs competitor/ref, side by side")
    m.add_argument("--pairs", nargs="+", required=True, help="YOURS=REF YOURS=REF ...")
    m.add_argument("--title", default="Yours vs Competitor")
    m.add_argument("--out", required=True)

    d = sub.add_parser("direction", help="your product + reference(s) -> direction board")
    d.add_argument("--own", required=True)
    d.add_argument("--refs", nargs="+", required=True)
    d.add_argument("--label", default="")
    d.add_argument("--out", required=True)

    a = ap.parse_args(argv)
    if a.cmd == "contact":
        files = _expand(a.inp)
        if len(files) < 2:
            print(f"ℹ only {len(files)} image(s); contact sheet still written.")
        build_contact_sheet(files, a.out, cols=a.cols, title=a.title)
    elif a.cmd == "compare":
        pairs = []
        for token in a.pairs:
            if "=" not in token:
                sys.exit(f"bad --pairs token (need YOURS=REF): {token}")
            own, ref = token.split("=", 1)
            pairs.append((own, ref))
        build_comparison(pairs, a.out, title=a.title)
    elif a.cmd == "direction":
        build_direction_board(a.own, a.refs, a.out, label=a.label)


if __name__ == "__main__":
    main()
