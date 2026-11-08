
# -*- coding: utf-8 -*-
"""v239 - 海洋壳下沉到地形之下（只填凹陷），降低 ruggedness 与地形细分。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 海洋壳：从 R+0.15 沉到 R-1.1，只有地形凹陷处才露出水面
rep("const geom = new THREE.IcosahedronGeometry(R + 0.15, 14);",
    "const geom = new THREE.IcosahedronGeometry(R - 1.1, 14);", 'oceanLevel')

# 地形细分 16 -> 12（面更整，不碎）
rep("const geom = new THREE.IcosahedronGeometry(R, 16);",
    "const geom = new THREE.IcosahedronGeometry(R, 12);", 'terrainDetail')

# 山体高度收敛
rep("const mountainH = Math.pow(landElev, 1.4) * 6.5 * this.cfg.ruggedness + ridgeNoise * 1.2;",
    "const mountainH = Math.pow(landElev, 1.5) * 3.2 * this.cfg.ruggedness + ridgeNoise * 0.5;",
    'mountain')

# 海深收敛
rep("finalR = R - depth * 3.8;", "finalR = R - depth * 2.4;", 'depth')

# ruggedness 全档降低
rep("ruggedness: basePreset.ruggedness * (tier === 'myth' ? 1.35 : tier === 'legend' ? 1.2 : 1.0),",
    "ruggedness: basePreset.ruggedness * (tier === 'myth' ? 1.1 : tier === 'legend' ? 1.05 : 0.9),",
    'rugged')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
