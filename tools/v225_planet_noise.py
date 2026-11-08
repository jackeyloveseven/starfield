
# -*- coding: utf-8 -*-
"""v225 — 大陆从球冠圆斑改回多频噪声，但分四档色阶：
   海洋 / 浅滩 / 陆地 / 高地，配合大气光晕与晨昏线给出层次。"""
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
    assert src.count(o) == 1, tag
    src = src.replace(o, n)
    log.append(tag)


# 1) landMask 改多频噪声
rep('landmask',
    """    'float landMask(vec3 nw){',
    '  float m = 0.0;',
    '  m = max(m, blob(nw, vec3( 0.52,  0.62,  0.58), 0.17));',
    '  m = max(m, blob(nw, vec3(-0.58,  0.06,  0.70), 0.15));',
    '  m = max(m, blob(nw, vec3( 0.06, -0.76,  0.55), 0.13));',
    '  m = max(m, blob(nw, vec3(-0.34, -0.16, -0.92), 0.18));',
    '  m = max(m, blob(nw, vec3( 0.66,  0.28, -0.70), 0.15));',
    '  m = max(m, blob(nw, vec3(-0.20,  0.86, -0.46), 0.13));',
    '  m = max(m, blob(nw, vec3( 0.88, -0.42,  0.20), 0.12));',
    '  return m;',
    '}',""",
    """    '/* 地貌：两频噪声叠加，主频给大陆轮廓，高频给海岸线的碎形 */',
    'float landField(vec3 nw, float seed){',
    '  float a = fbm(nw * 2.55 + vec3(seed, 0.0, seed * 0.7));',
    '  float b = fbm(nw * 6.30 + vec3(seed * 1.9, 0.0, seed));',
    '  return a * 0.74 + b * 0.26;',
    '}',""")

# 2) 表面四档
rep('surface',
    """    '    float land = landMask(nw);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '    float sub = landMask2(nw) * land;',
    '    albedo = mix(albedo, uLand2, sub);',
    '',""",
    """    '    float v = landField(nw, uSeed);',
    '    float shore = smoothstep(0.430, 0.468, v);',
    '    float land  = smoothstep(0.468, 0.500, v);',
    '    float high  = smoothstep(0.585, 0.655, v);',
    '    vec3 albedo = uBase;',
    '    albedo = mix(albedo, mix(uBase, uLand, 0.55), shore);',
    '    albedo = mix(albedo, uLand, land);',
    '    albedo = mix(albedo, uLand2, high * 0.85);',
    '',""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
