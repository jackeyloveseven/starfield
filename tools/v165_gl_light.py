
# -*- coding: utf-8 -*-
"""v165 — GL 星球：压暗夜面、环加厚成可见椭圆、大气只亮昼面边缘。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new, count=1):
    global src
    o, n = N(old), N(new)
    c = src.count(o)
    assert c == count, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


# ---- 环：用归一化椭圆距离定线宽，b 加厚 ----
rep('ring1',
    "    '    float e1 = length(vec2(q.x / (R * 1.46), q.y / (R * 0.30))) - 1.0;',\n"
    "    '    float d1 = abs(e1) * (R * 0.30);',\n"
    "    '    ringFront += 1.0 - smoothstep(0.0, 0.006, d1);',",
    "    '    float e1 = length(vec2(q.x / (R * 1.46), q.y / (R * 0.42))) - 1.0;',\n"
    "    '    ringFront += 1.0 - smoothstep(0.0, 0.010, abs(e1));',")

rep('ring2',
    "    '      float e2 = length(vec2(q.x / (R * 1.66), q.y / (R * 0.38))) - 1.0;',\n"
    "    '      float d2 = abs(e2) * (R * 0.38);',\n"
    "    '      ringFront += (1.0 - smoothstep(0.0, 0.005, d2)) * 0.55;',",
    "    '      float e2 = length(vec2(q.x / (R * 1.70), q.y / (R * 0.52))) - 1.0;',\n"
    "    '      ringFront += (1.0 - smoothstep(0.0, 0.009, abs(e2))) * 0.45;',")

# ---- 光照：夜面几乎全暗，昼面三档 ----
rep('light',
    "    '    vec3 L = normalize(vec3(-0.46, 0.52, 0.72));',\n"
    "    '    float l = dot(n, L);',\n"
    "    '    /* 硬分色：三层，不做平滑渐变 */',\n"
    "    '    float band = l < 0.02 ? 0.16 : (l < 0.42 ? 0.52 : 1.0);',",
    "    '    vec3 L = normalize(vec3(-0.58, 0.40, 0.71));',\n"
    "    '    float l = dot(n, L);',\n"
    "    '    /* 硬分色：三层，不做平滑渐变 */',\n"
    "    '    float band = l < 0.12 ? 0.05 : (l < 0.58 ? 0.34 : 1.0);',")

rep('rim',
    "    '    float rim = pow(1.0 - n.z, 3.2);',\n"
    "    '    col += uTint * rim * 0.55;',",
    "    '    float rim = pow(1.0 - n.z, 3.6) * smoothstep(-0.15, 0.55, l);',\n"
    "    '    col += uTint * rim * 0.40;',")

rep('edge-lift',
    "    '    float edgeLift = smoothstep(0.30, 0.75, l) * 0.10;',",
    "    '    float edgeLift = smoothstep(0.30, 0.75, l) * 0.06;',")

# ---- 调色：底更暗、陆更沉 ----
rep('palette',
    "      var base = hsl(hue, 0.30, 0.13);\n"
    "      var land = hsl(hue, 0.42, 0.27);\n"
    "      var tint = hsl(hue, 0.62, 0.66);",
    "      var base = hsl(hue, 0.34, 0.085);\n"
    "      var land = hsl(hue, 0.40, 0.205);\n"
    "      var tint = hsl(hue, 0.58, 0.60);")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
