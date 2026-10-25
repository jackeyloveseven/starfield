"""Generate the Starfield Focus icon set.

The icon is the artwork's heaviest object: a Schwarzschild shadow with a hot
accretion ring. Two things had to be right for it to survive a launcher:

  * the ring is a *radial brightness profile*, not a stroked circle. An arc with
    a stroke width reads as a metal washer; plasma has a soft inner and outer
    edge, so the ring is computed per pixel as a gaussian in radius.
  * the brightness is asymmetric. The approaching side is white-hot, the
    receding side is dying ember. A uniform ring is a donut; the asymmetry is
    what makes it a hole.

Outputs: legacy PNGs (squircle + round), adaptive foreground + monochrome,
and the two web icons.

  python -I icon.py <repo-root>
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
RES = os.path.join(ROOT, "android", "app", "src", "main", "res")

U = 108.0
BG_IN = np.array([26, 40, 56], float)
BG_OUT = np.array([4, 7, 12], float)
EMBER = np.array([120, 55, 24], float)
WARM = np.array([255, 158, 74], float)
HOT = np.array([255, 246, 220], float)
DISC = np.array([2, 4, 8], float)
STAR = np.array([223, 233, 245], float)


def render(size, with_bg=True, scale=1.0):
    """Float RGB + alpha, size*size, computed in one pass."""
    S = size * 4
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    u = U / scale
    k = S / u
    cx = cy = S / 2.0
    # a touch of vertical squash: face-on is a diagram, slightly tilted is a disc
    X = (xx - cx) / k
    Y = (yy - cy) / (k * 0.965)
    R = np.sqrt(X * X + Y * Y)
    TH = np.arctan2(-Y, X)

    # ---------- background ----------
    if with_bg:
        rad = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (S * 0.72)
        t = np.clip(rad, 0, 1) ** 0.75
        bg = BG_IN[None, None, :] + (BG_OUT - BG_IN)[None, None, :] * t[:, :, None]
        # the ring spills warm light onto the paper behind it
        spill = np.exp(-((R - 24.0) / 11.0) ** 2) * 0.16
        bg = bg + (WARM - bg) * spill[:, :, None]
    else:
        bg = np.zeros((S, S, 3), float)

    # ---------- the ring ----------
    RING = 24.2
    sigma_out = 2.5
    sigma_in = 3.6                      # softer towards the shadow
    side = np.where(R > RING, sigma_out, sigma_in)
    prof = np.exp(-((R - RING) / side) ** 2)

    # beaming: hot on the approaching (left) side
    beam = 0.5 + 0.5 * np.cos(TH - np.pi)
    beam = beam ** 1.45
    prof = prof * (0.40 + 0.78 * beam)

    col_ring = EMBER[None, None, :] + (WARM - EMBER)[None, None, :] * np.clip(beam * 1.9 + 0.12, 0, 1)[:, :, None]
    mx = np.clip((beam - 0.55) / 0.45, 0, 1)[:, :, None]
    col_ring = col_ring + (HOT - col_ring) * mx

    # ---------- photon ring ----------
    RPH = 18.5
    photon = np.exp(-((R - RPH) / 0.62) ** 2) * (0.55 + 0.45 * beam)

    # ---------- shadow ----------
    shadow = np.clip((17.6 - R) / 0.7, 0, 1)

    # ---------- composite, screen order ----------
    lit = np.clip(prof + photon * 1.35, 0, 1.6)
    col_hot = col_ring * prof[:, :, None] + HOT[None, None, :] * (photon * 1.35)[:, :, None]
    denom = np.maximum(lit, 1e-4)
    col_hot = col_hot / denom[:, :, None]

    out = bg + (col_hot - bg) * np.clip(lit, 0, 1)[:, :, None]
    out = out + HOT[None, None, :] * np.clip(lit - 1.0, 0, 0.6)[:, :, None]  # over-bright core
    out = out + (DISC - out) * shadow[:, :, None]

    # ---------- stars ----------
    for (sx, sy, sr, sa) in ((33.0, 29.0, 0.95, 0.75), (75.0, 26.0, 0.8, 0.6),
                             (84.5, 63.0, 0.9, 0.65), (24.0, 71.0, 0.75, 0.55),
                             (66.5, 88.5, 0.7, 0.45)):
        d2 = ((X - sx) ** 2 + (Y - sy) ** 2) / (sr * sr)
        g = np.exp(-d2) * sa
        out = out + (STAR[None, None, :] - out) * g[:, :, None]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return img


def squircle_mask(S, mode="squircle"):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if mode == "circle":
        d.ellipse([0, 0, S - 1, S - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.2237), fill=255)
    return m


def icon(size, mode="squircle"):
    S = size * 4
    img = render(size, with_bg=True)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), squircle_mask(S, mode))
    return out.resize((size, size), Image.LANCZOS)


def foreground(size):
    S = size * 4
    return render(size, with_bg=False).resize((size, size), Image.LANCZOS)


def mono(size):
    S = size * 4
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    k = S / U
    X = (xx - S / 2.0) / k
    Y = (yy - S / 2.0) / (k * 0.965)
    R = np.sqrt(X * X + Y * Y)
    a = (np.clip((24.6 - R) / 1.6, 0, 1) * np.clip((R - 20.4) / 1.4, 0, 1) * 255
         + np.clip((17.0 - R) / 1.0, 0, 1) * 255)
    a = np.clip(a, 0, 255).astype(np.uint8)
    img = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    img.putalpha(Image.fromarray(a, "L"))
    return img.resize((size, size), Image.LANCZOS)


DENS = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FORE = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}

for dpi, px in DENS.items():
    folder = os.path.join(RES, "mipmap-" + dpi)
    os.makedirs(folder, exist_ok=True)
    icon(px, "squircle").save(os.path.join(folder, "ic_launcher.png"))
    icon(px, "circle").save(os.path.join(folder, "ic_launcher_round.png"))
    foreground(FORE[dpi]).save(os.path.join(folder, "ic_launcher_foreground.png"))
    mono(FORE[dpi]).save(os.path.join(folder, "ic_launcher_mono.png"))

icon(192).save(os.path.join(ROOT, "icon-192.png"))
icon(512).save(os.path.join(ROOT, "icon-512.png"))
print("icons written to", RES)
