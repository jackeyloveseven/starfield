
# -*- coding: utf-8 -*-
"""v264 - 修 H() 的色相 bug：形态标志色固定，不随 hue 跑。
   原 H(n)=hue+n*37，导致水晶变桃色、菌毯色乱。
   形态标志色（水晶青/菌毯紫红/霓虹青）必须固定，否则认不出形态。"""
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

rep("  function H(n) { return ((hue + n * 37) % 360 + 360) % 360; }",
    """  /* 形态标志色固定：水晶是青的、菌毯是紫红的、霓虹是青的。
   * 只有地形随 hue 变；标志色跟着 hue 跑，形态就认不出来了。
   * （原写法 hue + n*37 是笔误，会把色相甩到完全不同的颜色） */
  function H(n) { return n; }""",
    'Hfix')

# 水晶用正青蓝
rep("      color: col(H(180), 0.85, 0.62),", "      color: col(197, 0.88, 0.60),", 'crystalCol')
rep("      emissive: col(H(180), 0.9, 0.28),", "      emissive: col(197, 0.92, 0.30),", 'crystalEm')

# 霓虹用正青
rep("var neonMat = new THREE.LineBasicMaterial({ color: col(H(190), 0.95, 0.6), transparent: true, opacity: 0.55 });",
    "var neonMat = new THREE.LineBasicMaterial({ color: col(188, 0.95, 0.62), transparent: true, opacity: 0.62 });",
    'neonCol')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
