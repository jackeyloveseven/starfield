import os
from PIL import Image, ImageDraw

def generate_grok_icons():
    src_path = r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367\grok3_singularity_app_icon_1792898207507.jpg"
    im_raw = Image.open(src_path).convert("RGBA")
    w, h = im_raw.size

    # 1. Generate Crisp Master Squircle (1024x1024)
    # Modern squircle mask with subtle 1px specular edge
    squircle_mask = Image.new("L", (w, h), 0)
    d_sq = ImageDraw.Draw(squircle_mask)
    corner_r = int(w * 0.22)
    d_sq.rounded_rectangle([0, 0, w, h], radius=corner_r, fill=255)

    master_squircle = im_raw.copy()
    master_squircle.putalpha(squircle_mask)

    # 2. Generate Crisp Master Round (1024x1024)
    round_mask = Image.new("L", (w, h), 0)
    d_rd = ImageDraw.Draw(round_mask)
    pad = int(w * 0.02)
    d_rd.ellipse([pad, pad, w - pad, h - pad], fill=255)

    master_round = im_raw.copy()
    master_round.putalpha(round_mask)

    # Target directories
    brain_dir = r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367"
    master_squircle.resize((512, 512), Image.Resampling.LANCZOS).save(os.path.join(brain_dir, "grok_blackhole_squircle_512.png"))
    master_round.resize((512, 512), Image.Resampling.LANCZOS).save(os.path.join(brain_dir, "grok_blackhole_round_512.png"))
    print("Master 512 previews saved to brain dir.")

    # Density specifications for Android
    densities = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192
    }

    res_base = r"d:\items\code\starfield-pub\android\app\src\main\res"
    for folder, sz in densities.items():
        out_dir = os.path.join(res_base, folder)
        os.makedirs(out_dir, exist_ok=True)
        
        sq_icon = master_squircle.resize((sz, sz), Image.Resampling.LANCZOS)
        sq_icon.save(os.path.join(out_dir, "ic_launcher.png"), "PNG")

        rd_icon = master_round.resize((sz, sz), Image.Resampling.LANCZOS)
        rd_icon.save(os.path.join(out_dir, "ic_launcher_round.png"), "PNG")
        print(f"Generated {folder}: {sz}x{sz}")

    # Root PWA and assets icons
    root_dir = r"d:\items\code\starfield-pub"
    assets_dir = os.path.join(root_dir, "android", "app", "src", "main", "assets")
    
    icon_192 = master_squircle.resize((192, 192), Image.Resampling.LANCZOS)
    icon_512 = master_squircle.resize((512, 512), Image.Resampling.LANCZOS)

    for d in [root_dir, assets_dir]:
        icon_192.save(os.path.join(d, "icon-192.png"), "PNG")
        icon_512.save(os.path.join(d, "icon-512.png"), "PNG")
        print(f"Updated icon-192.png and icon-512.png in {d}")

if __name__ == "__main__":
    generate_grok_icons()
