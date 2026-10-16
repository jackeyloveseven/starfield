"""Crop and upscale a region of a reference image so the surface treatment is legible.

Usage: python -I crop.py <in.png|jpg> <out.png> <x> <y> <w> <h> <zoom>

Kept out of the untrusted reference directory on purpose: the image is passed in
as an argument, never imported or executed.
"""
import sys

from PIL import Image

src, dst, x, y, w, h, zoom = sys.argv[1], sys.argv[2], *[int(v) for v in sys.argv[3:8]]
im = Image.open(src).convert('RGB')
box = im.crop((x, y, x + w, y + h))
box = box.resize((w * zoom, h * zoom), Image.LANCZOS)
box.save(dst)
print(dst, box.size)
