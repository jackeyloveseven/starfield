
# -*- coding: utf-8 -*-
"""v240 - 光环改成细亮线（不是灰盘），色阶收敛。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = html_in = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 光环：窄带 + 高亮 + 叠加混合
rep("""      var inner = 36 * (1.42 + r * 0.30);
      var outer = inner + 36 * (r === 0 ? 0.20 : 0.13);
      var rg = new THREE.RingGeometry(inner, outer, 96, 1);
      var rm = new THREE.MeshBasicMaterial({
        color: new THREE.Color(hsl(hue, 0.55, r === 0 ? 0.66 : 0.52)),
        side: THREE.DoubleSide, transparent: true,
        opacity: r === 0 ? 0.42 : 0.26, depthWrite: false
      });""",
    """      var inner = 36 * (1.40 + r * 0.26);
      var outer = inner + 36 * (r === 0 ? 0.045 : 0.030);
      var rg = new THREE.RingGeometry(inner, outer, 128, 1);
      var rm = new THREE.MeshBasicMaterial({
        color: new THREE.Color(hsl(hue, 0.62, r === 0 ? 0.74 : 0.62)),
        side: THREE.DoubleSide, transparent: true,
        opacity: r === 0 ? 0.80 : 0.52, depthWrite: false,
        blending: THREE.AdditiveBlending
      });""",
    'ring')

# 色阶收敛：浅滩/草地别那么荧光
rep("var satBoost = tier === 'myth' ? 1.16 : tier === 'legend' ? 1.10 : tier === 'epic' ? 1.05 : 1.0;",
    "var satBoost = tier === 'myth' ? 0.92 : tier === 'legend' ? 0.88 : tier === 'epic' ? 0.86 : 0.82;",
    'satBoost')

# 降低整体亮度，让暗面更深
rep("var lightBoost = tier === 'myth' ? 1.10 : tier === 'legend' ? 1.05 : 1.0;",
    "var lightBoost = tier === 'myth' ? 0.86 : tier === 'legend' ? 0.84 : 0.82;",
    'lightBoost')

# 太阳光弱一点，暗面更沉
rep("sun.intensity = L.light;", "sun.intensity = L.light * 0.92;", 'sun')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
