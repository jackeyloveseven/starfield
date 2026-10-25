import math
from PIL import Image, ImageDraw, ImageFilter

def create_grok_blackhole_icon(size=1024, is_round=False):
    # Render at 2x resolution (2048x2048) and Lanczos downsample for pristine anti-aliasing
    scale = 2
    canvas_size = size * scale
    center = canvas_size / 2

    # Canvas with alpha
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Background Squircle or Circle
    bg_radius = canvas_size * 0.46
    if is_round:
        # Perfect circle for ic_launcher_round
        draw.ellipse(
            [center - bg_radius, center - bg_radius, center + bg_radius, center + bg_radius],
            fill=(11, 17, 24, 255)
        )
    else:
        # Modern Squircle with rounded corners (Android adaptive / iOS style)
        corner_r = int(canvas_size * 0.22)
        pad = int(canvas_size * 0.04)
        draw.rounded_rectangle(
            [pad, pad, canvas_size - pad, canvas_size - pad],
            radius=corner_r,
            fill=(11, 17, 24, 255)
        )

    # Subtle deep space ambient vignette
    ambient = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    amb_draw = ImageDraw.Draw(ambient)
    for r in range(int(canvas_size * 0.45), int(canvas_size * 0.2), -15):
        alpha = int((1.0 - (r / (canvas_size * 0.45))) * 45)
        amb_draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(26, 42, 60, alpha)
        )
    img = Image.alpha_composite(img, ambient)
    draw = ImageDraw.Draw(img)

    # 2. Black Hole Luminous Accretion Disk & Gravitational Lensing
    # In Grok 3 / Gargantua style:
    # There is a dramatic outer photon glow, a tilted glowing accretion torus, and a diagonal slash
    glow_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # Outer gravitational lensing halo
    halo_r = canvas_size * 0.32
    for dr in range(60, 0, -4):
        rad = halo_r + dr * 1.5
        alpha = int(25 * (1.0 - dr / 60))
        glow_draw.ellipse(
            [center - rad, center - rad, center + rad, center + rad],
            outline=(245, 215, 140, alpha),
            width=3
        )

    # Gravitational Lensing Upper Arc (bent around top of singularity)
    arc_w = canvas_size * 0.30
    arc_h = canvas_size * 0.26
    glow_draw.arc(
        [center - arc_w, center - arc_h - canvas_size * 0.05, center + arc_w, center + arc_h - canvas_size * 0.05],
        start=170, end=370,
        fill=(255, 235, 180, 220),
        width=int(14 * scale)
    )

    # Gravitational Lensing Lower Arc (bent under bottom of singularity)
    glow_draw.arc(
        [center - arc_w * 0.88, center - arc_h * 0.65 + canvas_size * 0.08, center + arc_w * 0.88, center + arc_h * 0.65 + canvas_size * 0.08],
        start=0, end=180,
        fill=(230, 200, 150, 160),
        width=int(10 * scale)
    )

    # Main Tilted Accretion Disk (35-degree angle blade/ring)
    # Sliced by a diagonal slash (Grok slash aesthetic)
    disk_w = canvas_size * 0.38
    disk_h = canvas_size * 0.12
    # Draw intense glowing core of the accretion disk
    for step in range(5):
        w_offset = step * 2 * scale
        h_offset = step * 1 * scale
        alpha_val = int(240 - step * 35)
        glow_draw.ellipse(
            [center - disk_w - w_offset, center - disk_h - h_offset, center + disk_w + w_offset, center + disk_h + h_offset],
            outline=(255, 245, 220, alpha_val),
            width=int(4 * scale)
        )

    # 3. Grok Relativistic Diagonal Jet / Slash (The cutting forward slash)
    # Slicing from bottom-left to top-right at ~48 degrees
    slash_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(slash_layer)
    
    slash_len = canvas_size * 0.42
    slash_angle = math.radians(-42)
    dx = math.cos(slash_angle) * slash_len
    dy = math.sin(slash_angle) * slash_len
    
    # Beam glow
    for w, a in [(24 * scale, 30), (12 * scale, 80), (6 * scale, 180), (2.5 * scale, 255)]:
        s_draw.line(
            [center - dx, center - dy, center + dx, center + dy],
            fill=(255, 255, 255, a),
            width=int(w)
        )

    # 4. Central Singularity / Event Horizon (Absolute Pitch Black Void)
    # The pure black circle that absorbs all light in the center
    hole_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    h_draw = ImageDraw.Draw(hole_layer)
    hole_r = canvas_size * 0.19
    h_draw.ellipse(
        [center - hole_r, center - hole_r, center + hole_r, center + hole_r],
        fill=(4, 6, 10, 255) # Deep cosmic void black
    )
    # Razor-sharp photon ring boundary
    h_draw.ellipse(
        [center - hole_r, center - hole_r, center + hole_r, center + hole_r],
        outline=(255, 240, 200, 240),
        width=int(3 * scale)
    )

    # Subtle inner origami craft silhouette traversing the singularity event horizon
    craft_layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(craft_layer)
    cr_size = canvas_size * 0.05
    # Small paper crane silhouette riding the light beam
    c_pts = [
        (center + dx * 0.4, center + dy * 0.4 - cr_size),
        (center + dx * 0.4 + cr_size * 0.8, center + dy * 0.4 + cr_size * 0.8),
        (center + dx * 0.4, center + dy * 0.4 + cr_size * 0.3),
        (center + dx * 0.4 - cr_size * 0.8, center + dy * 0.4 + cr_size * 0.8),
    ]
    c_draw.polygon(c_pts, fill=(255, 215, 0, 230))

    # Composite layers
    img = Image.alpha_composite(img, glow_layer)
    img = Image.alpha_composite(img, slash_layer)
    img = Image.alpha_composite(img, hole_layer)
    img = Image.alpha_composite(img, craft_layer)

    # If is_round, mask strictly to circle
    if is_round:
        mask = Image.new("L", (canvas_size, canvas_size), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse(
            [center - bg_radius, center - bg_radius, center + bg_radius, center + bg_radius],
            fill=255
        )
        img.putalpha(mask)

    # Lanczos high-quality downsampling to target size
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

if __name__ == "__main__":
    import os
    out_dir = r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367"
    
    # 1. Preview 512x512
    icon_square = create_grok_blackhole_icon(512, is_round=False)
    icon_square.save(os.path.join(out_dir, "test_grok_blackhole_icon.png"), "PNG")
    print("Saved test_grok_blackhole_icon.png")

    icon_round = create_grok_blackhole_icon(512, is_round=True)
    icon_round.save(os.path.join(out_dir, "test_grok_blackhole_round.png"), "PNG")
    print("Saved test_grok_blackhole_round.png")
