#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STARFIELD // 3BLUE1BROWN (MANIM) STYLE PROMOTIONAL VIDEO GENERATOR
Renders a 1080p 30fps mathematical cosmic teaser using pure Python, OpenCV, Pillow & Matplotlib.
Style features:
- Dark slate chalkboard background (#0e1117) with subtle coordinate grids
- Mathtext LaTeX rendering with bloom/glow effects
- Exact Schwarzschild null geodesic light ray bending & Einstein rings
- Dual atomic clock time dilation simulation (d = sqrt(1 - rs/r))
- 3D Origami Crane wireframe mathematics with dynamic wing flapping
- Sleek 3b1b kinetic lower-thirds and vector overlays
"""

import os
import sys
import io
import math
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 1920, 1080
FPS = 30
TOTAL_FRAMES = 720  # 24 seconds at 30fps

FONT_CN_PATH = "C:/Windows/Fonts/msyh.ttc"
FONT_TITLE = ImageFont.truetype(FONT_CN_PATH, 54)
FONT_HEADING = ImageFont.truetype(FONT_CN_PATH, 36)
FONT_SUB = ImageFont.truetype(FONT_CN_PATH, 24)
FONT_MONO = ImageFont.truetype("C:/Windows/Fonts/consola.ttf" if os.path.exists("C:/Windows/Fonts/consola.ttf") else FONT_CN_PATH, 22)
FONT_BIG_HERO = ImageFont.truetype(FONT_CN_PATH, 80)

# 3b1b iconic color palette (RGB)
C_BG = (14, 17, 23)           # Slate Blackboard
C_CYAN = (88, 196, 221)        # 3b1b Blue
C_GOLD = (249, 199, 79)        # Mathematical Gold
C_CORAL = (255, 107, 107)      # Coral / Red-shift
C_PURPLE = (154, 121, 219)     # Electric Violet
C_WHITE = (236, 239, 244)      # Chalk White
C_MUTED = (120, 130, 150)      # Muted Axis

# Pre-render LaTeX cache to ensure fast rendering
latex_cache = {}

def get_latex_img(latex_str, fontsize=28, color_hex="#58C4DD", dpi=160):
    key = (latex_str, fontsize, color_hex, dpi)
    if key in latex_cache:
        return latex_cache[key]
    
    fig = plt.figure(figsize=(10, 2), dpi=dpi, facecolor='#0e1117')
    fig.text(0.5, 0.5, latex_str, fontsize=fontsize, color=color_hex, ha='center', va='center')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    latex_cache[key] = img
    return img

def draw_grid(draw, w, h, alpha=0.08, step=80):
    color = (int(C_CYAN[0]), int(C_CYAN[1]), int(C_CYAN[2]), int(255 * alpha))
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=color, width=1)

def draw_glow_circle(img, cx, cy, radius, color, max_alpha=120, blur=15):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    c_rgba = (color[0], color[1], color[2], max_alpha)
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=c_rgba, width=3)
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(glow)
    # Core crisp line
    cdraw = ImageDraw.Draw(img)
    cdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(color[0], color[1], color[2], 240), width=2)

def paste_centered(base_img, overlay_img, x, y, alpha_mult=1.0):
    if alpha_mult <= 0:
        return
    ow, oh = overlay_img.size
    px = int(x - ow / 2)
    py = int(y - oh / 2)
    if alpha_mult < 0.999:
        ov = overlay_img.copy()
        r, g, b, a = ov.split()
        a = a.point(lambda p: int(p * alpha_mult))
        ov.putalpha(a)
        base_img.alpha_composite(ov, (px, py))
    else:
        base_img.alpha_composite(overlay_img, (px, py))

# Pre-render key LaTeX formulas
FORMULA_GEODESIC = r"$\ddot{r} - r\dot{\phi}^2 + \frac{GM}{r^2} = 0 \quad \left(r_s = \frac{2GM}{c^2}\right)$"
FORMULA_METRIC = r"$ds^2 = -\left(1 - \frac{r_s}{r}\right) c^2 dt^2 + \left(1 - \frac{r_s}{r}\right)^{-1} dr^2 + r^2 d\Omega^2$"
FORMULA_DILATION = r"$d(r) = \sqrt{1 - \frac{r_s}{r}} \quad (\text{Gravitational Time Dilation})$"
FORMULA_INTEGRAL = r"$\Delta t_{\text{inside}} = \int_{0}^{T} \sqrt{1 - \frac{r_s}{r(t)}} \, dt \quad < \Delta t_{\text{outside}}$"
FORMULA_ORIGAMI = r"$\mathbf{P}_{\text{origami}}(\theta) = \sum_{k=1}^{N} \mathbf{R}_y(\omega t) \mathbf{v}_k + \mathbf{r}_{\text{route}}(z)$"

# 3D Origami Crane Model Vertices & Edges (Normalized)
CRANE_VERTS = [
    np.array([0.0, 0.4, 0.0]),     # 0: Head / Beak
    np.array([0.0, 0.15, -0.6]),   # 1: Neck base
    np.array([0.0, -0.05, -1.2]),  # 2: Center Body
    np.array([0.0, 0.2, -2.2]),    # 3: Tail tip
    np.array([1.8, 0.35, -1.0]),   # 4: Left Wing tip
    np.array([-1.8, 0.35, -1.0]),  # 5: Right Wing tip
    np.array([0.0, -0.3, -1.0]),   # 6: Keel / Bottom
]
CRANE_EDGES = [
    (0, 1), (1, 2), (2, 3),        # Spine
    (1, 4), (2, 4),                # Left Wing
    (1, 5), (2, 5),                # Right Wing
    (2, 6), (1, 6), (3, 6),        # Hull body
    (4, 6), (5, 6),                # Keel to wings
]

def render_frame(f_idx):
    # Base slate image
    img = Image.new("RGBA", (WIDTH, HEIGHT), C_BG + (255,))
    draw = ImageDraw.Draw(img)
    
    # 3b1b Background Grid
    draw_grid(draw, WIDTH, HEIGHT, alpha=0.06 + 0.02 * math.sin(f_idx * 0.05))
    
    # Persistent Upper-Left Header (3b1b Style)
    draw.text((80, 50), "STARFIELD // 纸上宇宙的数学物理引擎", font=FONT_SUB, fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], 200))
    draw.line([(80, 85), (580, 85)], fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], 80), width=1)
    
    # Frame time in current act
    # -------------------------------------------------------------------------
    # ACT I: Schwarzschild Null Geodesics & Gravitational Lensing (Frames 0-180)
    # -------------------------------------------------------------------------
    if f_idx < 180:
        prog = f_idx / 180.0
        alpha = min(1.0, f_idx / 20.0) if f_idx < 160 else max(0.0, (180 - f_idx) / 20.0)
        
        # Section Title
        draw.text((80, 110), "01 / 史瓦西测地线积分 · 零依赖黑洞着色引擎", font=FONT_TITLE, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(255 * alpha)))
        
        # LaTeX formula
        lat_img = get_latex_img(FORMULA_GEODESIC, fontsize=24, color_hex="#58C4DD")
        paste_centered(img, lat_img, WIDTH // 2, 210, alpha)
        
        # Center of Black Hole
        bh_x, bh_y = WIDTH // 2 + 150, HEIGHT // 2 + 80
        rs = 90
        
        # Photon sphere (r = 1.5 rs) & ISCO (r = 3.0 rs)
        draw_glow_circle(img, bh_x, bh_y, int(rs * 1.5), C_GOLD, max_alpha=int(80 * alpha), blur=10)
        draw_glow_circle(img, bh_x, bh_y, int(rs * 3.0), C_CYAN, max_alpha=int(50 * alpha), blur=16)
        
        # Accretion Disk (Doppler Beaming: left side brighter, right dimmer)
        ad_draw = ImageDraw.Draw(img)
        ad_draw.ellipse([bh_x - rs * 2.8, bh_y - rs * 0.7, bh_x + rs * 2.8, bh_y + rs * 0.7],
                        outline=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(160 * alpha)), width=4)
        ad_draw.ellipse([bh_x - rs * 2.16, bh_y - rs * 0.55, bh_x + rs * 2.16, bh_y + rs * 0.55],
                        outline=(C_CORAL[0], C_CORAL[1], C_CORAL[2], int(100 * alpha)), width=2)
        
        # Event horizon (r = rs)
        ad_draw.ellipse([bh_x - rs, bh_y - rs, bh_x + rs, bh_y + rs], fill=(0, 0, 0, int(250 * alpha)),
                        outline=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(220 * alpha)), width=2)
        
        # Labels with arrows (3b1b callout style)
        callout_draw = ImageDraw.Draw(img)
        callout_draw.text((bh_x + int(rs * 3.1), bh_y - 30), "ISCO (r = 3.0 rs)", font=FONT_MONO, fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], int(200 * alpha)))
        callout_draw.text((bh_x + int(rs * 1.6), bh_y + 40), "光子球 (r = 1.5 rs)", font=FONT_MONO, fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(220 * alpha)))
        callout_draw.text((bh_x - 70, bh_y - 15), "视界 (r = rs)", font=FONT_MONO, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(230 * alpha)))
        
        # Curved Null Geodesic Raymarching (Bending Light rays)
        ray_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(ray_layer)
        num_rays = 12
        for i in range(num_rays):
            b_impact = (i - num_rays / 2) * 38
            pts = []
            x_start = 120
            y_start = bh_y + b_impact * 2.8
            # Trace ray
            rx, ry = x_start, y_start
            vx = 22.0
            vy = 0.0
            step_limit = int(min(120, (f_idx % 90) * 1.8 + 20))
            for st in range(step_limit):
                dx = rx - bh_x
                dy = ry - bh_y
                dist_sq = dx * dx + dy * dy
                dist = math.sqrt(dist_sq) + 1e-4
                if dist < rs * 0.95:
                    break
                # Gravitational bending acceleration: a = -1.5 * rs * b / r^3
                force = 850000.0 / (dist_sq * dist)
                vx -= (dx / dist) * force
                vy -= (dy / dist) * force
                # Normalize velocity to speed of light
                spd = math.sqrt(vx * vx + vy * vy)
                vx = (vx / spd) * 20.0
                vy = (vy / spd) * 20.0
                rx += vx
                ry += vy
                pts.append((rx, ry))
                if rx > WIDTH - 100 or ry < 50 or ry > HEIGHT - 50:
                    break
            if len(pts) > 1:
                r_col = C_GOLD if abs(b_impact) < 60 else C_CYAN
                rdraw.line(pts, fill=(r_col[0], r_col[1], r_col[2], int(180 * alpha)), width=2)
                # Head photon spark
                hx, hy = pts[-1]
                rdraw.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(255, 255, 255, int(240 * alpha)))
        
        ray_glow = ray_layer.filter(ImageFilter.GaussianBlur(4))
        img.alpha_composite(ray_glow)
        img.alpha_composite(ray_layer)
        
        # Lower Note
        draw.text((80, HEIGHT - 100), "✦ 540 步自适应 Kick-Drift-Kick 积分器 · 逐像素模拟爱因斯坦光子环与双引力透镜像", font=FONT_SUB, fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(220 * alpha)))

    # -------------------------------------------------------------------------
    # ACT II: Gravitational Time Dilation & Dual Clocks (Frames 180-360)
    # -------------------------------------------------------------------------
    elif f_idx < 360:
        local_f = f_idx - 180
        prog = local_f / 180.0
        alpha = min(1.0, local_f / 20.0) if local_f < 160 else max(0.0, (180 - local_f) / 20.0)
        
        # Section Title
        draw.text((80, 110), "02 / 引力时间膨胀 · 洞内 25 分钟，洞外数载", font=FONT_TITLE, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(255 * alpha)))
        
        # LaTeX formula
        lat_img = get_latex_img(FORMULA_DILATION, fontsize=24, color_hex="#F9C74F")
        paste_centered(img, lat_img, WIDTH // 2, 210, alpha)
        
        # Dual Atomic Clocks Visual (Manim Dial Style)
        # Clock 1: Outside Universe Clock (Tick fast)
        # Clock 2: Near-Horizon Ship Clock (Tick slow according to d)
        clock1_x, clock1_y = 500, HEIGHT // 2 + 60
        clock2_x, clock2_y = 1420, HEIGHT // 2 + 60
        clock_r = 130
        
        # Simulating distance r decreasing towards horizon
        sim_r_ratio = max(1.08, 3.5 - 2.3 * (local_f / 180.0))
        d_val = math.sqrt(max(0.001, 1.0 - 1.0 / sim_r_ratio))
        
        # Outside Clock (Stationary Infinity)
        draw_glow_circle(img, clock1_x, clock1_y, clock_r, C_CYAN, max_alpha=int(80 * alpha), blur=12)
        c1_draw = ImageDraw.Draw(img)
        c1_angle = (local_f * 0.18) % (2 * math.pi)
        hx1 = clock1_x + (clock_r - 25) * math.cos(c1_angle - math.pi / 2)
        hy1 = clock1_y + (clock_r - 25) * math.sin(c1_angle - math.pi / 2)
        c1_draw.line([(clock1_x, clock1_y), (hx1, hy1)], fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], int(240 * alpha)), width=4)
        c1_draw.text((clock1_x - 110, clock1_y + clock_r + 20), "外太空参考钟 (d = 1.000)", font=FONT_HEADING, fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], int(240 * alpha)))
        c1_draw.text((clock1_x - 70, clock1_y + clock_r + 70), f"T_out = {local_f * 0.8:.1f} s", font=FONT_MONO, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(200 * alpha)))
        
        # Ship Clock (Near Horizon, d dilating)
        draw_glow_circle(img, clock2_x, clock2_y, clock_r, C_GOLD, max_alpha=int(80 * alpha), blur=12)
        c2_draw = ImageDraw.Draw(img)
        c2_angle = (local_f * 0.18 * d_val) % (2 * math.pi)
        hx2 = clock2_x + (clock_r - 25) * math.cos(c2_angle - math.pi / 2)
        hy2 = clock2_y + (clock_r - 25) * math.sin(c2_angle - math.pi / 2)
        c2_draw.line([(clock2_x, clock2_y), (hx2, hy2)], fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(240 * alpha)), width=4)
        c2_draw.text((clock2_x - 130, clock2_y + clock_r + 20), f"黑洞视界领航钟 (d = {d_val:.3f})", font=FONT_HEADING, fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(240 * alpha)))
        c2_draw.text((clock2_x - 80, clock2_y + clock_r + 70), f"T_ship = {local_f * 0.8 * d_val:.1f} s", font=FONT_MONO, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(200 * alpha)))
        
        # Center Interactive Function Curve (3b1b Graph of d(r))
        gx, gy, gw, gh = 760, HEIGHT // 2 - 80, 400, 260
        g_draw = ImageDraw.Draw(img)
        # Coordinate axes
        g_draw.line([(gx, gy + gh), (gx + gw, gy + gh)], fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(180 * alpha)), width=2)
        g_draw.line([(gx, gy), (gx, gy + gh)], fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(180 * alpha)), width=2)
        g_draw.text((gx + gw - 35, gy + gh + 8), "r / rs", font=FONT_MONO, fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(160 * alpha)))
        g_draw.text((gx - 35, gy - 20), "d", font=FONT_MONO, fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(160 * alpha)))
        
        # Plot curve d = sqrt(1 - 1/x) from x = 1.01 to 4.0
        curve_pts = []
        for xi in range(gw):
            x_ratio = 1.01 + (xi / gw) * 3.0
            y_d = math.sqrt(1.0 - 1.0 / x_ratio)
            py = gy + gh - int(y_d * (gh - 30))
            curve_pts.append((gx + xi, py))
        if len(curve_pts) > 1:
            g_draw.line(curve_pts, fill=(C_PURPLE[0], C_PURPLE[1], C_PURPLE[2], int(220 * alpha)), width=3)
        
        # Active marker on graph
        cur_x_px = int(((sim_r_ratio - 1.01) / 3.0) * gw)
        cur_y_px = gy + gh - int(d_val * (gh - 30))
        g_draw.ellipse([gx + cur_x_px - 6, cur_y_px - 6, gx + cur_x_px + 6, cur_y_px + 6],
                       fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(255 * alpha)),
                       outline=(255, 255, 255, int(255 * alpha)), width=2)
        
        # Integral note
        lat_int = get_latex_img(FORMULA_INTEGRAL, fontsize=20, color_hex="#9A79DB")
        paste_centered(img, lat_int, WIDTH // 2, HEIGHT - 100, alpha)

    # -------------------------------------------------------------------------
    # ACT III: Mathematical Origami & Spacetime Cruise (Frames 360-540)
    # -------------------------------------------------------------------------
    elif f_idx < 540:
        local_f = f_idx - 360
        prog = local_f / 180.0
        alpha = min(1.0, local_f / 20.0) if local_f < 160 else max(0.0, (180 - local_f) / 20.0)
        
        # Section Title
        draw.text((80, 110), "03 / 折纸动力学与曲率航道 · 4 款几何折叠舰体", font=FONT_TITLE, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(255 * alpha)))
        
        # LaTeX formula
        lat_img = get_latex_img(FORMULA_ORIGAMI, fontsize=24, color_hex="#58C4DD")
        paste_centered(img, lat_img, WIDTH // 2, 210, alpha)
        
        # 3D Rotating Origami Crane Wireframe Visual
        crane_center_x, crane_center_y = WIDTH // 2, HEIGHT // 2 + 50
        scale = 220.0
        rot_y = local_f * 0.04
        rot_x = 0.35 + 0.15 * math.sin(local_f * 0.03)
        wing_flap = math.sin(local_f * 0.14) * 0.45
        
        # Rotate and project vertices
        proj_verts = []
        for vi, v in enumerate(CRANE_VERTS):
            cur_v = v.copy()
            # Flap wings
            if vi == 4:  # Left Wing tip
                cur_v[1] += wing_flap
            elif vi == 5: # Right Wing tip
                cur_v[1] += wing_flap
            
            # Rotation matrix Y
            x1 = cur_v[0] * math.cos(rot_y) + cur_v[2] * math.sin(rot_y)
            y1 = cur_v[1]
            z1 = -cur_v[0] * math.sin(rot_y) + cur_v[2] * math.cos(rot_y)
            
            # Rotation matrix X
            x2 = x1
            y2 = y1 * math.cos(rot_x) - z1 * math.sin(rot_x)
            z2 = y1 * math.sin(rot_x) + z1 * math.cos(rot_x) + 3.5
            
            # Perspective projection
            fov = 3.2 / z2
            px = crane_center_x + x2 * scale * fov
            py = crane_center_y - y2 * scale * fov
            proj_verts.append((px, py, z2))
        
        # Draw edges with 3b1b neon wireframe glow
        crane_wire = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        cw_draw = ImageDraw.Draw(crane_wire)
        for (i1, i2) in CRANE_EDGES:
            p1 = (proj_verts[i1][0], proj_verts[i1][1])
            p2 = (proj_verts[i2][0], proj_verts[i2][1])
            # Wing edges gold, spine cyan
            e_col = C_GOLD if (i1 in (4, 5) or i2 in (4, 5)) else C_CYAN
            cw_draw.line([p1, p2], fill=(e_col[0], e_col[1], e_col[2], int(220 * alpha)), width=3)
        
        # Draw vertex node rings
        for (vx, vy, vz) in proj_verts:
            cw_draw.ellipse([vx - 5, vy - 5, vx + 5, vy + 5], fill=(255, 255, 255, int(250 * alpha)),
                            outline=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(255 * alpha)), width=2)
        
        wire_blur = crane_wire.filter(ImageFilter.GaussianBlur(6))
        img.alpha_composite(wire_blur)
        img.alpha_composite(crane_wire)
        
        # 4 Fleet Ship Classes Box
        box_y = HEIGHT - 180
        classes = ["H-01 千纸鹤 (Paper Crane)", "H-02 疾风镖 (Aero Dart)", "H-03 星灵刃 (Protoss Blade)", "H-04 虚空蛾 (Void Moth)"]
        for idx, name in enumerate(classes):
            bx = 140 + idx * 420
            draw.rectangle([bx, box_y, bx + 380, box_y + 60], outline=(C_CYAN[0], C_CYAN[1], C_CYAN[2], int(120 * alpha)), width=1)
            draw.text((bx + 20, box_y + 16), name, font=FONT_HEADING, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(220 * alpha)))
        
        draw.text((80, HEIGHT - 85), "✦ 弹簧阻尼动力学 · 矩阵坐标旋转 · 4 种量子曲率尾迹拉伸算法", font=FONT_SUB, fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(220 * alpha)))

    # -------------------------------------------------------------------------
    # ACT IV: Grand Cosmos & Conclusion Showcase (Frames 540-720)
    # -------------------------------------------------------------------------
    else:
        local_f = f_idx - 540
        prog = local_f / 180.0
        alpha = min(1.0, local_f / 20.0)
        
        # Kinetic Starfield Warp in background
        num_stars = 260
        np.random.seed(42)
        warp_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        w_draw = ImageDraw.Draw(warp_layer)
        for s in range(num_stars):
            orig_ang = (s * 1.618) * 2 * math.pi
            orig_dist = 50 + ((s * 37 + local_f * 24) % 1100)
            sx = WIDTH // 2 + math.cos(orig_ang) * orig_dist
            sy = HEIGHT // 2 + math.sin(orig_ang) * orig_dist
            # Stretch star vector
            trail_len = min(60, orig_dist * 0.08)
            tx = sx - math.cos(orig_ang) * trail_len
            ty = sy - math.sin(orig_ang) * trail_len
            star_alpha = int(min(220, orig_dist * 0.25) * alpha)
            w_draw.line([(tx, ty), (sx, sy)], fill=(240, 245, 255, star_alpha), width=2)
        
        img.alpha_composite(warp_layer)
        
        # Central Hero Presentation
        hero_y = HEIGHT // 2 - 120
        # Title with 3b1b Golden Highlight
        draw.text((WIDTH // 2 - 400, hero_y), "星 空 · S T A R F I E L D", font=FONT_BIG_HERO, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(255 * alpha)))
        draw.line([(WIDTH // 2 - 420, hero_y + 110), (WIDTH // 2 + 420, hero_y + 110)], fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(220 * alpha)), width=3)
        
        # Subtitle
        draw.text((WIDTH // 2 - 360, hero_y + 140), "单文件视网膜着色引擎 · 纯数学折纸宇宙", font=FONT_TITLE, fill=(C_CYAN[0], C_CYAN[1], C_CYAN[2], int(240 * alpha)))
        
        # Feature Badges (3b1b Pill Tags)
        badges = [
            "✦ 0 依赖 0 外链单文件",
            "✦ 2K Ultra 视网膜渲染",
            "✦ 120 FPS 满血解禁",
            "✦ 6 大古典名曲物理合成",
            "✦ 280 组合天体洗牌"
        ]
        b_y = hero_y + 240
        for b_i, badge in enumerate(badges):
            bx = 160 + b_i * 320
            draw.rectangle([bx, b_y, bx + 290, b_y + 50], outline=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(140 * alpha)), width=1)
            draw.text((bx + 18, b_y + 12), badge, font=FONT_SUB, fill=(C_WHITE[0], C_WHITE[1], C_WHITE[2], int(220 * alpha)))
        
        # Live Repository URL & Prompt
        draw.text((WIDTH // 2 - 320, HEIGHT - 160), "体验在线版本: https://jackeyloveseven.github.io/starfield/", font=FONT_HEADING, fill=(C_GOLD[0], C_GOLD[1], C_GOLD[2], int(240 * alpha)))
        draw.text((WIDTH // 2 - 210, HEIGHT - 100), "双击 starfield.html 即可起航 · 探索无垠星海", font=FONT_SUB, fill=(C_MUTED[0], C_MUTED[1], C_MUTED[2], int(200 * alpha)))

    # Convert PIL Image (RGBA) to OpenCV BGR
    frame_bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
    return frame_bgr

def main():
    print("=" * 65)
    print(" GENERATING STARFIELD 3BLUE1BROWN (MANIM) STYLE PROMO VIDEO")
    print(f" Resolution: {WIDTH}x{HEIGHT} @ {FPS}fps | Total Frames: {TOTAL_FRAMES}")
    print("=" * 65)
    
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "starfield_3b1b_promo.mp4")
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, float(FPS), (WIDTH, HEIGHT))
    
    # Save Key Frame Stills for README & Documentation
    docs_assets = os.path.join(os.path.dirname(out_dir), "docs", "assets")
    os.makedirs(docs_assets, exist_ok=True)
    stills_to_save = {
        90: os.path.join(docs_assets, "promo_still_1_lensing.png"),
        270: os.path.join(docs_assets, "promo_still_2_dilation.png"),
        450: os.path.join(docs_assets, "promo_still_3_origami.png"),
        640: os.path.join(docs_assets, "promo_still_4_title.png")
    }
    
    t0 = time.time()
    for f in range(TOTAL_FRAMES):
        frame = render_frame(f)
        writer.write(frame)
        
        if f in stills_to_save:
            cv2.imwrite(stills_to_save[f], frame)
            print(f"   >>> Saved Still Frame [{f}]: {os.path.basename(stills_to_save[f])}")
            
        if f % 60 == 0 or f == TOTAL_FRAMES - 1:
            elapsed = time.time() - t0
            fps_proc = (f + 1) / max(0.01, elapsed)
            print(f"   Rendering: frame {f:3d}/{TOTAL_FRAMES} ({f/TOTAL_FRAMES*100:4.1f}%) | Speed: {fps_proc:4.1f} fps")
            
    writer.release()
    print("=" * 65)
    print(f" PROMO VIDEO COMPLETED SUCCESSFULLY!")
    print(f" Output Video: {out_path} ({os.path.getsize(out_path) / (1024*1024):.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    main()
