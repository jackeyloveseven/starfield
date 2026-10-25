import os
import math
from PIL import Image, ImageDraw, ImageFilter

def create_starfield_icon(size=512, is_round=False):
    # Render at 4x supersampling for ultra-crisp antialiasing
    scale = 4
    W = size * scale
    H = size * scale

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = W / 2, H / 2
    r_outer = W * 0.46

    # 1. Base Shape (Squircle or Round)
    if is_round:
        # Perfect circle
        mask = Image.new("L", (W, H), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), fill=255)
    else:
        # Modern continuous squircle (rounded rectangle with radius = 0.22 * W)
        mask = Image.new("L", (W, H), 0)
        mask_draw = ImageDraw.Draw(mask)
        rad = W * 0.22
        margin = W * 0.04
        mask_draw.rounded_rectangle((margin, margin, W - margin, H - margin), radius=rad, fill=255)

    # Background gradient on separate image
    bg = Image.new("RGBA", (W, H), (11, 17, 24, 255))
    bg_draw = ImageDraw.Draw(bg)

    # Radial cosmic gradient: #1a273a at center to #070b10 at edges
    steps = 100
    for i in range(steps, 0, -1):
        ratio = i / steps
        r_step = W * 0.75 * ratio
        # Color interpolation
        cr = int(7 + (26 - 7) * (1 - ratio))
        cg = int(11 + (39 - 11) * (1 - ratio))
        cb = int(16 + (58 - 16) * (1 - ratio))
        bg_draw.ellipse((cx - r_step, cy - r_step, cx + r_step, cy + r_step), fill=(cr, cg, cb, 255))

    # 2. Golden Orbital Rings
    ring_color = (255, 215, 0, 60)
    for ring_r in [W * 0.28, W * 0.38]:
        bg_draw.ellipse((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r), outline=ring_color, width=int(2.5 * scale))

    # Tilted elliptic orbit ring
    # Draw tilted orbit using polygon points
    orbit_pts = []
    orbit_a, orbit_b = W * 0.39, W * 0.16
    tilt_rad = math.radians(-32)
    cos_t, sin_t = math.cos(tilt_rad), math.sin(tilt_rad)
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        x0 = orbit_a * math.cos(rad)
        y0 = orbit_b * math.sin(rad)
        x = cx + x0 * cos_t - y0 * sin_t
        y = cy + x0 * sin_t + y0 * cos_t
        orbit_pts.append((x, y))
    bg_draw.line(orbit_pts + [orbit_pts[0]], fill=(56, 189, 248, 110), width=int(3 * scale))

    # 3. Constellation & Star Dust
    stars = [
        (-0.25, -0.28, 3.5, (255, 255, 255, 220)),
        (0.28, -0.22, 2.5, (254, 240, 138, 200)),
        (-0.32, 0.18, 2.0, (56, 189, 248, 180)),
        (0.30, 0.24, 3.0, (255, 255, 255, 230)),
        (0.08, -0.34, 4.0, (255, 215, 0, 240)),
        (-0.15, 0.32, 2.5, (255, 255, 255, 190)),
        (0.18, 0.36, 1.8, (56, 189, 248, 160)),
    ]
    for sx, sy, srad, scol in stars:
        px = cx + sx * W
        py = cy + sy * H
        bg_draw.ellipse((px - srad * scale, py - srad * scale, px + srad * scale, py + srad * scale), fill=scol)

    # 4. Origami Flagship (Silhouette with 3D paper facets)
    # Lead tip: (cx, cy - W * 0.18)
    # Wing Left: (cx - W * 0.22, cy + W * 0.16)
    # Wing Right: (cx + W * 0.22, cy + W * 0.16)
    # Center Tail: (cx, cy + W * 0.08)
    tip = (cx, cy - W * 0.17)
    wing_l = (cx - W * 0.20, cy + W * 0.16)
    wing_r = (cx + W * 0.20, cy + W * 0.16)
    tail_c = (cx, cy + W * 0.08)
    tail_l = (cx - W * 0.06, cy + W * 0.12)
    tail_r = (cx + W * 0.06, cy + W * 0.12)

    # Facet 1: Left Main Wing (Off-white paper light)
    bg_draw.polygon([tip, wing_l, tail_c], fill=(240, 245, 250, 255))
    # Facet 2: Right Main Wing (Golden light reflection)
    bg_draw.polygon([tip, wing_r, tail_c], fill=(254, 240, 138, 255))
    # Facet 3: Left Inner Fold (Shadowed cool paper)
    bg_draw.polygon([tip, tail_l, tail_c], fill=(200, 215, 230, 255))
    # Facet 4: Right Inner Fold (Warm shaded gold)
    bg_draw.polygon([tip, tail_r, tail_c], fill=(250, 204, 21, 255))

    # Crisp origami fold lines (wireframe edges)
    bg_draw.line([tip, wing_l], fill=(255, 255, 255, 255), width=int(2.5 * scale))
    bg_draw.line([tip, wing_r], fill=(255, 255, 255, 255), width=int(2.5 * scale))
    bg_draw.line([wing_l, tail_c], fill=(160, 180, 200, 220), width=int(2.0 * scale))
    bg_draw.line([wing_r, tail_c], fill=(234, 179, 8, 220), width=int(2.0 * scale))
    bg_draw.line([tip, tail_c], fill=(255, 255, 255, 255), width=int(2.5 * scale))

    # Glow beneath ship (Golden engine thruster burst)
    thrust_pts = [(cx, cy + W * 0.08), (cx - W * 0.04, cy + W * 0.22), (cx + W * 0.04, cy + W * 0.22)]
    bg_draw.polygon(thrust_pts, fill=(255, 215, 0, 180))
    thrust_core = [(cx, cy + W * 0.08), (cx - W * 0.018, cy + W * 0.17), (cx + W * 0.018, cy + W * 0.17)]
    bg_draw.polygon(thrust_core, fill=(255, 255, 255, 240))

    # Apply mask
    final = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    final.paste(bg, (0, 0), mask)

    # Downsample with high-quality Lanczos resampling
    final = final.resize((size, size), Image.Resampling.LANCZOS)
    return final

def generate_all_icons():
    root = os.path.abspath(r"d:\items\code\starfield-pub")
    res_dir = os.path.join(root, "android", "app", "src", "main", "res")
    assets_dir = os.path.join(root, "android", "app", "src", "main", "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Android mipmap densities
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192
    }

    print("Generating native Android app icons...")
    for folder, px in densities.items():
        out_folder = os.path.join(res_dir, folder)
        os.makedirs(out_folder, exist_ok=True)
        # Standard squircle
        icon = create_starfield_icon(size=px, is_round=False)
        icon.save(os.path.join(out_folder, "ic_launcher.png"), "PNG")
        # Round variant
        icon_round = create_starfield_icon(size=px, is_round=True)
        icon_round.save(os.path.join(out_folder, "ic_launcher_round.png"), "PNG")
        print(f"  -> Created {folder}/ic_launcher.png ({px}x{px}) & ic_launcher_round.png")

    # High-res icons for store / assets / PWA
    icon_512 = create_starfield_icon(size=512, is_round=False)
    icon_512.save(os.path.join(root, "icon-512.png"), "PNG")
    icon_512.save(os.path.join(assets_dir, "icon-512.png"), "PNG")

    icon_192 = create_starfield_icon(size=192, is_round=False)
    icon_192.save(os.path.join(root, "icon-192.png"), "PNG")
    icon_192.save(os.path.join(assets_dir, "icon-192.png"), "PNG")

    print("  -> Created icon-512.png and icon-192.png in root and assets!")
    print("ALL ICONS SUCCESSFULLY GENERATED!")

if __name__ == "__main__":
    generate_all_icons()
