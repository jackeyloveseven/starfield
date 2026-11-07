
# -*- coding: utf-8 -*-
"""v159 — 星球几何去装饰：只留「环 / 卫星 / 赤道」，删掉同心弧、刻度与短竖线。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

START = "  function drawPlanetSphere(ctx, cx, cy, r, hue, tier, rotX, rotY, cloudRot) {"
END = "  ProceduralPlanet.prototype.render = function() {"
s = src.find(START)
e = src.find(END, s)
assert s > 0 and e > s

NEW = N("""  /* 扁平几何星球：纯色球 + 硬边昼夜 + 球面椭圆斑块 + 会公转的卫星。
   * 画面上每一笔都有对应物——环是行星环，点是卫星，虚线是赤道纬度线，
   * 不再用同心弧与刻度去"堆稀有度"（那些读不出含义，只是噪音）。 */
  function drawPlanetSphere(ctx, cx, cy, r, hue, tier, rotX, rotY, cloudRot) {
    var DEG = Math.PI / 180;
    var rank = (TIERS[tier] && typeof TIERS[tier].rank === 'number') ? TIERS[tier].rank : 0;
    var base = 'hsl(' + hue + ', 30%, 15%)';
    var land = 'hsl(' + hue + ', 42%, 30%)';
    var edge = 'hsl(' + hue + ', 58%, 62%)';
    var TILT = -22 * DEG;
    var cosT = Math.cos(TILT), sinT = Math.sin(TILT);

    /* 行星环：a = rad*r, b = flat*r，沿 -22° 倾斜 */
    function ringHalf(front, rad, flat, alpha) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(TILT);
      ctx.beginPath();
      ctx.ellipse(0, 0, r * rad, r * flat, 0,
        front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
      ctx.strokeStyle = edge;
      ctx.globalAlpha = alpha;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();
    }

    /* 卫星：在环所在的椭圆轨道上公转，落球后变暗变小，落球前变亮变大 */
    function moonAt(m) {
      var ang = cloudRot * 0.9 + m * 2.1;
      var ex = Math.cos(ang) * r * 1.44;
      var ey = Math.sin(ang) * r * 0.30;
      return {
        x: cx + ex * cosT - ey * sinT,
        y: cy + ex * sinT + ey * cosT,
        front: Math.sin(ang) > 0,
        m: m
      };
    }
    function drawMoon(o) {
      var rad = r * (o.front ? 0.062 : 0.042);
      ctx.beginPath();
      ctx.arc(o.x, o.y, rad, 0, Math.PI * 2);
      ctx.fillStyle = o.front ? 'hsl(' + hue + ', 58%, 72%)' : 'hsl(' + hue + ', 34%, 26%)';
      ctx.fill();
    }

    var moons = rank >= 2 ? Math.min(3, rank - 1) : 0;
    var hasRing = rank >= 1;
    var hasRing2 = rank >= 4;

    if (hasRing2) ringHalf(false, 1.62, 0.38, 0.16);
    if (hasRing) ringHalf(false, 1.44, 0.30, 0.26);
    for (var b = 0; b < moons; b++) {
      var ob = moonAt(b);
      if (!ob.front) drawMoon(ob);
    }

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = base;
    ctx.fill();

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.clip();

    var PATCHES = [
      { lon: 8,   lat: 30,  rx: 0.28, ry: 0.17 },
      { lon: 58,  lat: -6,  rx: 0.22, ry: 0.26 },
      { lon: 104, lat: -40, rx: 0.18, ry: 0.12 },
      { lon: 146, lat: 16,  rx: 0.24, ry: 0.19 },
      { lon: 188, lat: 52,  rx: 0.16, ry: 0.10 },
      { lon: 226, lat: -22, rx: 0.26, ry: 0.15 },
      { lon: 268, lat: 6,   rx: 0.20, ry: 0.24 },
      { lon: 306, lat: -48, rx: 0.15, ry: 0.10 },
      { lon: 342, lat: 38,  rx: 0.19, ry: 0.13 }
    ];
    var spin = rotY / DEG;
    ctx.fillStyle = land;
    for (var i = 0; i < PATCHES.length; i++) {
      var p = PATCHES[i];
      var lon = (p.lon + spin) * DEG;
      var depth = Math.cos(lon);
      if (depth <= 0.05) continue;
      var lat = (p.lat + (rotX / DEG) * 42) * DEG;
      var px = Math.sin(lon) * Math.cos(lat) * r;
      var py = -Math.sin(lat) * r;
      ctx.beginPath();
      ctx.ellipse(cx + px, cy + py, p.rx * r * depth, p.ry * r * (0.55 + 0.45 * depth),
        0, 0, Math.PI * 2);
      ctx.fill();
    }

    /* 明暗分界偏到右侧，像侧光而非对半切 */
    ctx.beginPath();
    ctx.arc(cx + r * 0.16, cy, r, -Math.PI / 2, Math.PI / 2, false);
    ctx.closePath();
    ctx.fillStyle = 'rgba(4, 6, 10, 0.74)';
    ctx.fill();

    /* 赤道纬度线：跟随拖拽倾斜，越接近俯视越平 */
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rotX * 0.55);
    ctx.beginPath();
    ctx.ellipse(0, 0, r, r * Math.max(0.03, Math.abs(Math.sin(rotX))), 0, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,255,255,0.07)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    ctx.restore();

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = edge;
    ctx.globalAlpha = 0.52;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.globalAlpha = 1;

    if (hasRing) ringHalf(true, 1.44, 0.30, 0.72);
    if (hasRing2) ringHalf(true, 1.62, 0.38, 0.30);
    for (var f = 0; f < moons; f++) {
      var of = moonAt(f);
      if (of.front) drawMoon(of);
    }
  }

""")

src = src[:s] + NEW + src[e:]
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('replaced', e - s, '->', len(NEW))
