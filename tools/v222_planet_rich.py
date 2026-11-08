
# -*- coding: utf-8 -*-
"""v222 — 开卡星球提精致度：球外大气辉光 + 大陆内二级地块 + 柔和高光；自转加快。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new):
    global src
    o, n = N(old), N(new)
    assert src.count(o) == 1, tag + ' count=%d' % src.count(o)
    src = src.replace(o, n)
    log.append(tag)


# 1) 二级地块函数（大陆内部更亮的一档）
rep('blob2',
    "    'float landMask(vec3 nw){',",
    """    '/* 二级地块：落在大陆内部的更亮小块，给出层次 */',
    'float landMask2(vec3 nw){',
    '  float m = 0.0;',
    '  m = max(m, blob(nw, vec3( 0.62,  0.30,  0.72), 0.085));',
    '  m = max(m, blob(nw, vec3(-0.44, -0.36,  0.82), 0.075));',
    '  m = max(m, blob(nw, vec3( 0.18, -0.60,  0.78), 0.065));',
    '  m = max(m, blob(nw, vec3(-0.70,  0.44,  0.56), 0.060));',
    '  m = max(m, blob(nw, vec3( 0.34,  0.86,  0.38), 0.055));',
    '  return m;',
    '}',
    'float landMask(vec3 nw){',""")

# 2) uniform
rep('uniform-decl',
    "    'uniform vec3  uLand;',",
    "    'uniform vec3  uLand;',\n    'uniform vec3  uLand2;',")

rep('uniform-binding',
    "['uRes', 'uTime', 'uTint', 'uBase', 'uLand', 'uRotX', 'uRotY', 'uSeed', 'uRing', 'uMoon']",
    "['uRes', 'uTime', 'uTint', 'uBase', 'uLand', 'uLand2', 'uRotX', 'uRotY', 'uSeed', 'uRing', 'uMoon']")

# 3) 表面：叠二级地块 + 柔和高光
rep('surface',
    """    '    float land = landMask(nw);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '',""",
    """    '    float land = landMask(nw);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '    float sub = landMask2(nw) * land;',
    '    albedo = mix(albedo, uLand2, sub);',
    '',""")

rep('specular',
    """    '    float halo = pow(1.0 - n.z, 7.0) * day;',
    '    col += uTint * halo * 0.14;',""",
    """    '    float halo = pow(1.0 - n.z, 7.0) * day;',
    '    col += uTint * halo * 0.14;',
    '    /* 柔和高光：只有一点点，让球面不是死板的纯色 */',
    '    vec3 hN = normalize(vec3(-0.58, 0.40, 0.71) + vec3(0.0, 0.0, 1.0));',
    '    float spec = pow(max(dot(n, hN), 0.0), 26.0) * 0.16 * day;',
    '    col += uTint * spec;',""")

# 4) 球外大气辉光（放在环和卫星之前统一加）
rep('atmo',
    """    '  /* ---- front half of ring ---- */',""",
    """    '  /* ---- 球外大气辉光：让边缘之外还有一层软光 ---- */',
    '  {',
    '    float dd = sqrt(r2);',
    '    float outside = smoothstep(R - 0.006, R + 0.002, dd);',
    '    float glow = exp(-(dd - R) * 15.0) * outside;',
    '    col += uTint * glow * 0.55;',
    '    alpha = max(alpha, glow * 0.55);',
    '  }',
    '',
    '  /* ---- front half of ring ---- */',""")

# 5) 传 uLand2 + 加快自转
rep('land2-color',
    "      var tint = hsl(hue, 0.58, 0.60);",
    "      var tint = hsl(hue, 0.58, 0.60);\n      var land2 = hsl(hue, 0.55, 0.640);")

rep('land2-uniform',
    "      gl.uniform3f(uni.uLand, land[0], land[1], land[2]);",
    "      gl.uniform3f(uni.uLand, land[0], land[1], land[2]);\n      gl.uniform3f(uni.uLand2, land2[0], land2[1], land2[2]);")

rep('spin',
    "    this.spinSpeed = 0.004;",
    "    this.spinSpeed = 0.016;")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
