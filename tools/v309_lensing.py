
# -*- coding: utf-8 -*-
"""v309 - 引力透镜：光子环 + 螺旋拖拽星光。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   引力透镜（近似）
   黑洞周围：多重光子环 + 被引力拖拽的螺旋星光。
   不做逐像素光线追踪（Canvas 2D 做不到），而是用螺旋与偏心环
   逼近"时空被弯曲"的观感。透明度压在 0.35 以下，不遮挡视野。
   ============================================================ */
(function () {
  if (window.SFLensing) return;

  window.SFLensing = {
    draw: function (env) {
      var bh = window.__sfBH;
      if (!bh) return;
      var ctx = env.ctx, project = env.project, time = env.time;
      var q = project([bh.x, bh.y, bh.z]);
      if (!q) return;
      var cx = q[0], cy = q[1], rad = (bh.r || 3000) * q[3];
      if (rad < 24 || rad > Math.max(env.W, env.H) * 3) return;
      if (cx < -rad * 2 || cx > env.W + rad * 2 || cy < -rad * 2 || cy > env.H + rad * 2) return;

      /* 事件视界：一圈纯黑，把后面的光"吃掉" */
      ctx.save();
      var voidG = ctx.createRadialGradient(cx, cy, rad * 0.2, cx, cy, rad * 1.05);
      voidG.addColorStop(0, 'rgba(0,0,0,0.92)');
      voidG.addColorStop(0.75, 'rgba(0,0,0,0.55)');
      voidG.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = voidG;
      ctx.beginPath(); ctx.arc(cx, cy, rad * 1.05, 0, Math.PI * 2); ctx.fill();

      /* 多重光子环：略偏心，模拟被引力扭曲的像 */
      for (var i = 0; i < 3; i++) {
        var rr = rad * (1.02 + i * 0.07);
        var off = rad * 0.03 * (i + 1);
        ctx.beginPath();
        ctx.ellipse(cx + off, cy - off * 0.4, rr, rr * (0.94 - i * 0.03), time * 0.05, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(255,236,200,' + (0.30 - i * 0.08).toFixed(3) + ')';
        ctx.lineWidth = Math.max(0.8, rad * (0.012 - i * 0.003));
        ctx.stroke();
      }

      /* 螺旋拖拽的星光：半径随角度增大，像被卷入时空 */
      ctx.save();
      ctx.globalAlpha = 0.32;
      for (var arm = 0; arm < 2; arm++) {
        ctx.beginPath();
        var phase = time * 0.22 + arm * Math.PI;
        for (var a = 0; a < Math.PI * 2.2; a += 0.06) {
          var rr2 = rad * (1.12 + a * 0.42);
          var ang = a + phase;
          var x = cx + Math.cos(ang) * rr2;
          var y = cy + Math.sin(ang) * rr2 * 0.9;
          if (a === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        var g = ctx.createLinearGradient(cx, cy, cx + rad * 2.4, cy);
        g.addColorStop(0, 'rgba(255,240,210,0.55)');
        g.addColorStop(1, 'rgba(255,240,210,0)');
        ctx.strokeStyle = g;
        ctx.lineWidth = Math.max(0.7, rad * 0.006);
        ctx.stroke();
      }
      ctx.restore();
      ctx.restore();
    }
  };
})();
'''

body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-lensing">' + MODULE + '\n</script>\n' + html[body_end:]

# 在 frame() 的 bodies() 之后调用，注入环境
old = "drawSkyEvents(); if(window.SFPassersby)"
new = "if(window.SFLensing) window.SFLensing.draw({ctx:ctx, project:project, time:time, W:W, H:H}); drawSkyEvents(); if(window.SFPassersby)"
assert html.count(old) == 1, 'call count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('lensing module added and wired')
