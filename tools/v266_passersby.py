
# -*- coding: utf-8 -*-
"""v266 - 路过景观：彗星 / 暗星云 / 行星状星云。
   纯视觉、不遮挡中心航道。HUD 是 DOM，canvas 在其下，本就不会被遮。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   路过景观（纯视觉，不可交互）
   - 彗星：小亮核 + 离子尾(蓝直) + 尘埃尾(黄弯)
   - 暗星云：黑色剪影，遮住背景星光（不遮舰队）
   - 行星状星云：环形壳层 + 中心亮星
   硬约束：中央 ±30% 屏宽不画；单元素 alpha <= 0.35；无全屏覆盖。
   ============================================================ */
(function () {
  if (window.SFPassersby) return;

  function fadeAtCenter(sx) {
    /* 中央 30% 完全不画，30%-48% 之间渐显 */
    var c = Math.abs(sx - W * 0.5) / (W * 0.5);
    if (c < 0.30) return 0;
    if (c > 0.48) return 1;
    return (c - 0.30) / 0.18;
  }

  function comet(x, y, z, side, seed, fade) {
    var head = project([x, y, z]);
    if (!head) return;
    var k = head[3];
    /* 尾端在世界坐标里向后上方延伸，投影自然成透视 */
    var tailLen = 2600 + seed * 2200;
    var t1 = project([x + side * tailLen * 0.22, y + tailLen * 0.10, z + tailLen]);
    var t2 = project([x + side * tailLen * 0.46, y + tailLen * 0.30, z + tailLen * 0.92]);
    var hx = head[0], hy = head[1];

    if (t1) {
      /* 离子尾：细、直、蓝 */
      ctx.save();
      ctx.globalAlpha = 0.32 * fade;
      var g1 = ctx.createLinearGradient(hx, hy, t1[0], t1[1]);
      g1.addColorStop(0, 'rgba(150,205,255,0.9)');
      g1.addColorStop(1, 'rgba(150,205,255,0)');
      ctx.strokeStyle = g1;
      ctx.lineWidth = Math.max(1, 5 * k);
      ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(t1[0], t1[1]); ctx.stroke();
      ctx.restore();
    }
    if (t2) {
      /* 尘埃尾：略弯、暖、更淡 */
      ctx.save();
      ctx.globalAlpha = 0.22 * fade;
      var g2 = ctx.createLinearGradient(hx, hy, t2[0], t2[1]);
      g2.addColorStop(0, 'rgba(240,220,180,0.85)');
      g2.addColorStop(1, 'rgba(240,220,180,0)');
      ctx.strokeStyle = g2;
      ctx.lineWidth = Math.max(1, 11 * k);
      ctx.beginPath();
      ctx.moveTo(hx, hy);
      ctx.quadraticCurveTo((hx + t2[0]) * 0.5, (hy + t2[1]) * 0.5 - 30 * k, t2[0], t2[1]);
      ctx.stroke();
      ctx.restore();
    }
    /* 彗核 */
    var r = Math.max(2, 26 * k);
    ctx.save();
    ctx.globalAlpha = 0.85 * fade;
    var gg = ctx.createRadialGradient(hx, hy, 0, hx, hy, r * 3);
    gg.addColorStop(0, 'rgba(255,255,255,0.95)');
    gg.addColorStop(0.25, 'rgba(210,235,255,0.5)');
    gg.addColorStop(1, 'rgba(210,235,255,0)');
    ctx.fillStyle = gg;
    ctx.beginPath(); ctx.arc(hx, hy, r * 3, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  function darkNebula(x, y, z, seed, fade) {
    var q = project([x, y, z]);
    if (!q) return;
    var k = q[3], sx = q[0], sy = q[1];
    var base = 900 * k;
    if (base < 6) return;
    ctx.save();
    /* 深色剪影：盖的是背景星光，不是舰队 */
    for (var i = 0; i < 7; i++) {
      var a = seed * 6.28 + i * 1.1;
      var rr = base * (0.55 + 0.45 * Math.sin(seed * 9 + i));
      var ox = Math.cos(a) * base * 0.42, oy = Math.sin(a) * base * 0.30;
      var g = ctx.createRadialGradient(sx + ox, sy + oy, 0, sx + ox, sy + oy, rr);
      g.addColorStop(0, 'rgba(4,7,13,' + (0.30 * fade).toFixed(3) + ')');
      g.addColorStop(0.6, 'rgba(4,7,13,' + (0.20 * fade).toFixed(3) + ')');
      g.addColorStop(1, 'rgba(4,7,13,0)');
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(sx + ox, sy + oy, rr, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }

  function planetaryNebula(x, y, z, seed, fade) {
    var q = project([x, y, z]);
    if (!q) return;
    var k = q[3], sx = q[0], sy = q[1];
    var R = 620 * k;
    if (R < 5) return;
    var hue = 150 + seed * 90;
    ctx.save();
    /* 壳层：一个薄环，不是实心圆盘 */
    var g = ctx.createRadialGradient(sx, sy, R * 0.55, sx, sy, R * 1.25);
    g.addColorStop(0, 'hsla(' + hue + ',70%,65%,0)');
    g.addColorStop(0.55, 'hsla(' + hue + ',75%,68%,' + (0.30 * fade).toFixed(3) + ')');
    g.addColorStop(0.78, 'hsla(' + hue + ',80%,72%,' + (0.20 * fade).toFixed(3) + ')');
    g.addColorStop(1, 'hsla(' + hue + ',70%,65%,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(sx, sy, R * 1.25, 0, Math.PI * 2); ctx.fill();
    /* 中心亮星 */
    var gs = ctx.createRadialGradient(sx, sy, 0, sx, sy, R * 0.16);
    gs.addColorStop(0, 'rgba(255,255,255,' + (0.9 * fade).toFixed(3) + ')');
    gs.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = gs;
    ctx.beginPath(); ctx.arc(sx, sy, R * 0.16, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  window.SFPassersby = {
    draw: function () {
      if (typeof started === 'undefined' || !started) return;
      if (typeof travel === 'undefined') return;
      var k0 = Math.floor(travel / CHUNK);
      for (var k = Math.max(1, k0 - 1); k <= k0 + 9; k++) {
        var h = hash(k, 9001);
        if (h > 0.55) continue;                 /* 约每 2 个 chunk 一处 */
        var type = Math.floor(hash(k, 9002) * 3);
        var z = k * CHUNK + CHUNK * (0.2 + hash(k, 9003) * 0.6);
        var side = hash(k, 9004) < 0.5 ? -1 : 1;
        var off = 2800 + hash(k, 9005) * 5200;  /* 永远在航道两侧 */
        var x = routeX(z) + side * off;
        var y = courseY(z) + (hash(k, 9006) - 0.5) * 1500;
        var q = project([x, y, z]);
        if (!q) continue;
        var fade = fadeAtCenter(q[0]);
        if (fade <= 0) continue;
        if (q[1] < -80 || q[1] > H + 80) continue;
        var seed = hash(k, 9007);
        if (type === 0) comet(x, y, z, side, seed, fade);
        else if (type === 1) darkNebula(x, y, z, seed, fade);
        else planetaryNebula(x, y, z, seed, fade);
      }
    }
  };
})();
'''

# 模块挂到 </head> 前不行（要在 project 等定义之后），挂到 drawSkyEvents 调用后
old = "drawSkyEvents();"
assert html.count(old) >= 1, 'drawSkyEvents not found'
# 在 frame() 内的 drawSkyEvents() 之后插入调用
new = "drawSkyEvents(); if(window.SFPassersby) window.SFPassersby.draw();"
html = html.replace(old, new, 1)

# 模块本体插到 </body> 前（运行期，此时 project/travel 已定义）
body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-passersby">' + MODULE + '\n</script>\n' + html[body_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('passersby module added,', len(MODULE), 'chars')
