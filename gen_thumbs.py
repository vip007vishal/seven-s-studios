"""
Generate optimized JPEG thumbnails for all portfolio images.
Thumbnails: max 800x800px, JPEG quality 80 — fast to load in grid.
Full-res images are kept untouched for lightbox use.
"""

import os
import sys
from pathlib import Path
from PIL import Image

THUMB_DIR_NAME = "_thumbs"
MAX_SIZE = (800, 800)
QUALITY = 80

PORTFOLIO_DIRS = [
    "portfolio/graphic-design/logos",
    "portfolio/graphic-design/mockups",
    "portfolio/graphic-design/posters",
    "portfolio/3d-animation",
]

IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def make_thumbs(src_dir: str):
    src_path = Path(src_dir)
    if not src_path.is_dir():
        print(f"SKIP (not found): {src_dir}")
        return

    thumb_path = src_path / THUMB_DIR_NAME
    thumb_path.mkdir(exist_ok=True)

    images = [f for f in src_path.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS]

    if not images:
        print(f"  No images in {src_dir}")
        return

    total = len(images)
    done = 0
    skipped = 0

    for img_file in sorted(images):
        out_name = img_file.stem + ".jpg"
        out_path = thumb_path / out_name

        # Skip if already up to date (compare mtime)
        if out_path.exists() and out_path.stat().st_mtime >= img_file.stat().st_mtime:
            skipped += 1
            continue

        try:
            Image.MAX_IMAGE_PIXELS = None  # design files are safe, not attacks
            with Image.open(img_file) as im:
                im = im.convert("RGB")
                im.thumbnail(MAX_SIZE, Image.LANCZOS)
                im.save(out_path, "JPEG", quality=QUALITY, optimize=True, progressive=True)
                orig_kb = img_file.stat().st_size / 1024
                new_kb  = out_path.stat().st_size / 1024
                done += 1
                ratio = (1 - new_kb / orig_kb) * 100
                print(f"  [{done}/{total}] {img_file.name}: {orig_kb:.0f}KB -> {new_kb:.0f}KB  (-{ratio:.0f}%)")
        except Exception as e:
            print(f"  ERROR {img_file.name}: {e}")

    print(f"  Done: {done} converted, {skipped} already up-to-date in {src_dir}")


if __name__ == "__main__":
    print("=== Generating portfolio thumbnails ===\n")
    for d in PORTFOLIO_DIRS:
        print(f"\n--- {d} ---")
        make_thumbs(d)
    print("\n=== All done! ===")
