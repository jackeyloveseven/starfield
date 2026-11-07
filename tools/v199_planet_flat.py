
# -*- coding: utf-8 -*-
"""v199 — 开卡星球改纯色几何：球冠大陆 + 硬边昼夜，去掉噪声与三层明暗。"""
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
    assert src.count(o) == 1, tag + ' count=' + str(src.count(o))
    src = src.replace(o, n)
    log.append(tag)


# 1) 加入球冠斑块函数（放在 fbm 之后）
rep('blob-fn',
    "    'mat3 rotY(float a){',",
    """    '/* 球冠斑块：dot(nw,dir) 超过阈值即该点为陆地 —— 投影到屏幕上就是随自转滚动的椭圆 */',
    'float blob(vec3 nw, vec3 dir, float radius){',
    '  return smoothstep(1.0 - radius - 0.004, 1.0 - radius + 0.004, dot(nw, normalize(dir)));',
    '}',
    'float landMask(vec3 nw){',
    '  float m = 0.0;',
    '  m = max(m, blob(nw, vec3( 0.35,  0.55,  0.76), 0.44));',
    '  m = max(m, blob(nw, vec3(-0.62, -0.18,  0.52), 0.35));',
    '  m = max(m, blob(nw, vec3( 0.10, -0.72, -0.42), 0.31));',
    '  m = max(m, blob(nw, vec3(-0.20,  0.62, -0.70), 0.27));',
    '  m = max(m, blob(nw, vec3( 0.80, -0.30, -0.40), 0.23));',
    '  return m;',
    '}',
    'mat3 rotY(float a){',""")

# 2) 主函数：噪声大陆 + 极冠 + 三层明暗 → 纯色斑块 + 硬边昼夜
rep('surface',
    """    '    float f = fbm(nw * 2.05 + uSeed);',
    '    float land = smoothstep(0.545, 0.560, f);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '',
    '    /* 极冠 */',
    '    float pole = smoothstep(0.86, 0.94, abs(nw.y));',
    '    albedo = mix(albedo, vec3(0.80, 0.85, 0.92), pole * 0.55);',
    '',
    '    vec3 L = normalize(vec3(-0.58, 0.40, 0.71));',
    '    float l = dot(n, L);',
    '    /* 硬分色：三层，不做平滑渐变 */',
    '    float band = l < 0.10 ? 0.085 : (l < 0.56 ? 0.38 : 1.0);',
    '    col = albedo * band;',
    '',
    '    /* 昼面边缘一点点提亮 */',
    '    float edgeLift = smoothstep(0.30, 0.75, l) * 0.06;',
    '    col += uTint * edgeLift;',""",
    """    '    float land = landMask(nw);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '',
    '    vec3 L = normalize(vec3(-0.58, 0.40, 0.71));',
    '    float l = dot(n, L);',
    '    /* 硬边昼夜：一条终止线，不分层也不渐变 */',
    '    float day = smoothstep(0.0, 0.010, l);',
    '    float band = mix(0.13, 1.0, day);',
    '    col = albedo * band;',""")

# 3) 大陆色提亮一档，保证纯色对得出来
rep('land-color',
    "      var land = hsl(hue, 0.40, 0.205);",
    "      var land = hsl(hue, 0.46, 0.335);")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
