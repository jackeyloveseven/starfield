
# -*- coding: utf-8 -*-
"""v283 - 进入星球的平滑下降过渡（goal 要求：太空->大气->低空不能硬切）。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 相机：从高空 60 下降到 9，2.4 秒 ease-out
rep("""    var R = planet.cfg.radius;
    var alt = 9.0;
    if (!dragging) autoTh += dt * 0.055;""",
    """    var R = planet.cfg.radius;
    /* 下降过渡：前 2.4 秒从高空 60 降到 9，ease-out。
       直接进入会硬切，没有"穿过大气层"的感觉。 */
    var sinceEnter = (performance.now() - t0) / 1000;
    var dp = Math.min(1, sinceEnter / 2.4);
    var ease = 1 - Math.pow(1 - dp, 3);
    var alt = 60 - (60 - 9.0) * ease;
    if (!dragging && dp >= 1) autoTh += dt * 0.055;""",
    'descent')

# UI：淡入
rep("      active = true;\n      autoTh = 0; userTh = 0; userPhi = 1.12; lastT = 0; dragging = false;",
    """      container.style.opacity = '0';
      container.style.transition = 'opacity 1.1s ease';
      requestAnimationFrame(function () { if (container) container.style.opacity = '1'; });

      active = true;
      autoTh = 0; userTh = 0; userPhi = 1.12; lastT = 0; dragging = false;""",
    'fadeIn')

# 退出也淡出（简化：直接移除，但先给个短淡出）
rep("    exit: function () {\n      if (!active) return;\n      active = false;",
    """    exit: function () {
      if (!active) return;
      if (container) { container.style.transition = 'opacity .35s ease'; container.style.opacity = '0'; }
      active = false;""",
    'fadeOut')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
