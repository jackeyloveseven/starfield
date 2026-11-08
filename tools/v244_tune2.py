
# -*- coding: utf-8 -*-
"""v244 - 描边加粗到可见；神话档降曝。"""
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

# 描边宽度：0.55 -> 1.5（半径 36，相机 178，约 3-4px）
rep("          uWidth: { value: 0.55 + L.rim * 0.35 },",
    "          uWidth: { value: 1.30 + L.rim * 0.55 },", 'outlineWidth')

# 描边颜色更实
rep("          uColor: { value: new THREE.Color(hsl(hue, 0.45, 0.30)) }",
    "          uColor: { value: new THREE.Color(hsl(hue, 0.55, 0.16)) }", 'outlineColor')

# 神话/传说降曝：envIntensity 与 sun 都收
rep("      envIntensity: 0.42 + L.rim * 0.30,",
    "      envIntensity: (0.34 + L.rim * 0.16) * (tier === 'myth' ? 0.62 : tier === 'legend' ? 0.74 : 1.0),",
    'envInt')
rep("    sun.intensity = L.light * 0.92;",
    "    sun.intensity = L.light * 0.92 * (tier === 'myth' ? 0.80 : tier === 'legend' ? 0.88 : 1.0);",
    'sunI')
rep("    amb.intensity = 0.40 + L.rim * 0.10;",
    "    amb.intensity = (0.40 + L.rim * 0.10) * (tier === 'myth' ? 0.70 : 1.0);", 'ambI')

# myth 的 light 本身调低
rep("myth:   { preset: 'alien',              trees: 900,  monuments: 4, fauna: 3, clouds: 0.52, spin: 1.7, scale: 1.00, rim: 1.45, ring: 2, moons: 3, tilt: 0.34, light: 1.55 }",
    "myth:   { preset: 'alien',              trees: 900,  monuments: 4, fauna: 3, clouds: 0.52, spin: 1.7, scale: 1.00, rim: 1.45, ring: 2, moons: 3, tilt: 0.34, light: 1.18 }",
    'mythLight')
rep("legend: { preset: 'monument',           trees: 480,  monuments: 4, fauna: 2, clouds: 0.36, spin: 1.5, scale: 0.98, rim: 1.15, ring: 2, moons: 3, tilt: 0.30, light: 1.42 }",
    "legend: { preset: 'monument',           trees: 480,  monuments: 4, fauna: 2, clouds: 0.36, spin: 1.5, scale: 0.98, rim: 1.15, ring: 2, moons: 3, tilt: 0.30, light: 1.24 }",
    'legendLight')

# 加 debug 接口便于验证
rep("    isOn: function () { return ok; }\n  };",
    """    isOn: function () { return ok; },
    debugEnv: function () { return !!scene.environment; },
    debugOutline: function () { return !!outlineMesh; }
  };""",
    'debug')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
