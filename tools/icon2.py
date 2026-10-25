"""Starfield icon, take two: the Grok grammar.

What makes that mark work, after looking at it properly:

  * the ground is almost black and the light is almost white - there is no
    middle tone to muddy a 48 px launcher tile;
  * one diagonal gesture. A ring alone is a donut; a beam alone is a scratch.
    The two together are the only arrangement here that survives 16 px;
  * the beam is *occluded* by the shadow. It stops at the horizon and does not
    reappear inside it - that silhouette is what makes it read as a hole;
  * the ring is thin and sharp. My last attempt was a fat gold band with a
    broad halo, which reads as a washer.

  python -I icon2.py <repo-root>
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
RES = os.path.join(ROOT, "android", "app", "src", "main", "res")
U = 108.0

BG = np.array([28, 44, 64], float)
HOT = np.array([255, 255, 252], float)
WARM = np.array([255, 205, 140], float)
DEEP = np.array([6, 9, 14], float)


def render(size, with_bg=True, beam=True):
    S = size * 4
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    k = S / U
    cx = cy = S / 2.0
    X = (xx - cx) / k
    Y = (yy - cy) / k
    R = np.sqrt(X * X + Y * Y)
    TH = np.arctan2(-Y, X)

    bg = np.tile(BG, (S, S, 1)) if with_bg else np.zeros((S, S, 3), float)

    # ---- shadow: a little larger than before, so the hole dominates ----
    RD = 19.0
    shadow = np.clip((RD - R) / 0.55, 0, 1) * np.clip((R + 40) / 41, 0, 1)

    # ---- ring: thin, and it only exists outside the shadow ----
    RING = 20.7
    ring = np.exp(-((R - RING) / 0.85) ** 2) * (R > RD - 0.2)
    beam_ang = 0.5 + 0.5 * np.cos(TH - np.pi)          # hotter on one side
    ring = ring * (0.85 + 0.55 * beam_ang)
    ring_col = WARM[None, None, :] + (HOT - WARM)[None, None, :] * \
        np.clip(beam_ang * 1.3, 0, 1)[:, :, None]

    # ---- the beam: a tapered 45-degree streak, cut by the shadow ----
    if beam:
        a = np.deg2rad(45.0)
        d = np.abs(X * np.sin(a) - Y * np.cos(a))
        along = X * np.cos(a) + Y * np.sin(a)           # -50..50
        w = 2.45 * np.clip(1.0 - (np.abs(along) / 47.0) ** 2, 0, 1) + 0.18
        streak = np.exp(-(d / w) ** 2) * np.clip(1.0 - (np.abs(along) / 46.0) ** 2.2, 0, 1)
        streak = streak * (R > RD - 0.1)                # occluded by the hole
        # a wider, dimmer copy is the bloom; without it the beam reads as a scratch
        wob = 2.45 * 3.1 * np.clip(1.0 - (np.abs(along) / 47.0) ** 2, 0, 1) + 0.4
        bloom = np.exp(-(d / wob) ** 2) * np.clip(1.0 - (np.abs(along) / 47.0) ** 2.2, 0, 1)
        bloom = bloom * (R > RD - 0.1) * 0.30
        # the part that passes in front: a short arc hugging the upper left
        front = np.exp(-((R - RD - 0.9) / 1.1) ** 2) * np.clip((along - 8) / 14, 0, 1)
        streak = np.clip(streak + front * 0.8, 0, 1)
    else:
        streak = np.zeros((S, S), float)

    # ---- composite: additive light on the dark ground ----
    out = bg
    out = out + (ring_col - out) * np.clip(ring * 1.9, 0, 1)[:, :, None]
    out = out + HOT[None, None, :] * (streak * 1.15)[:, :, None]
    out = out + WARM[None, None, :] * ((bloom if beam else np.zeros_like(bloom)) * 0.30)[:, :, None]
    out = out + (DEEP - out) * shadow[:, :, None]
    # the ring's own faint glow, hugging the horizon
    glow = np.exp(-((R - RING) / 3.4) ** 2) * (R > RD)
    out = out + WARM[None, None, :] * (glow * 0.55)[:, :, None]

    # the glow belongs to both layers: on the adaptive foreground it is the only
    # thing that makes the ring read as light rather than as a drawn circle
    bloom = np.exp(-((R - RING) / 9.0) ** 2) * (R > RD)
    core = np.exp(-((R - RING) / 2.0) ** 2) * (R > RD - 0.5)
    out = out + WARM[None, None, :] * (bloom * 0.30)[:, :, None]
    out = out + HOT[None, None, :] * (core * 0.28)[:, :, None]
    out = np.clip(out, 0, 255)
    if with_bg:
        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    else:
        cov = np.clip(ring * 1.9 + streak * 1.15 + bloom * 1.25 + core * 0.9, 0, 1)
        rgba = np.dstack([np.clip(out, 0, 255), cov * 255.0]).astype(np.uint8)
        img = Image.fromarray(rgba, "RGBA")
    if beam and with_bg:
        pass
    return img


def squircle_mask(S, mode="squircle"):
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if mode == "circle":
        d.ellipse([0, 0, S - 1, S - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.2237), fill=255)
    return m


def icon(size, mode="squircle", bleed=False):
    S = size * 4
    img = render(size, True)
    if bleed:
        # manifest declares purpose "any maskable": the platform crops it itself,
        # so baked-in rounded corners become transparent notches
        return img.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), squircle_mask(S, mode))
    return out.resize((size, size), Image.LANCZOS)


def foreground(size):
    return render(size, False).resize((size, size), Image.LANCZOS)


def mono(size):
    S = size * 4
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    k = S / U
    X = (xx - S / 2.0) / k
    Y = (yy - S / 2.0) / k
    R = np.sqrt(X * X + Y * Y)
    ring = np.exp(-((R - 20.7) / 1.7) ** 2)
    a = np.deg2rad(45.0)
    d = np.abs(X * np.sin(a) - Y * np.cos(a))
    along = X * np.cos(a) + Y * np.sin(a)
    w = 1.7 * np.clip(1 - (np.abs(along) / 46.0) ** 2, 0, 1) + 0.2
    beam = np.exp(-(d / w) ** 2) * np.clip(1 - (np.abs(along) / 46.0) ** 2.2, 0, 1) * (R > 18.8)
    disc = np.clip((18.8 - R) / 0.9, 0, 1)
    alpha = np.clip(np.maximum(np.maximum(ring * 0.9, beam), disc), 0, 1)
    img = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    img.putalpha(Image.fromarray((alpha * 255).astype(np.uint8), "L"))
    return img.resize((size, size), Image.LANCZOS)


DENS = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FORE = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}

if __name__ == "__main__":
    for dpi, px in DENS.items():
        folder = os.path.join(RES, "mipmap-" + dpi)
        os.makedirs(folder, exist_ok=True)
        icon(px, "squircle").save(os.path.join(folder, "ic_launcher.png"))
        icon(px, "circle").save(os.path.join(folder, "ic_launcher_round.png"))
        foreground(FORE[dpi]).save(os.path.join(folder, "ic_launcher_foreground.png"))
        mono(FORE[dpi]).save(os.path.join(folder, "ic_launcher_mono.png"))
    icon(192, bleed=True).save(os.path.join(ROOT, "icon-192.png"))
    icon(512, bleed=True).save(os.path.join(ROOT, "icon-512.png"))
    print("icons written to", RES)
