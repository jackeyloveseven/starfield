
# -*- coding: utf-8 -*-
"""v200 — 星球：斑块缩小到 5 块分散球冠；夜面提到 0.42 保持整体感。"""
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


rep('blobs',
    """    '  m = max(m, blob(nw, vec3( 0.35,  0.55,  0.76), 0.44));',
    '  m = max(m, blob(nw, vec3(-0.62, -0.18,  0.52), 0.35));',
    '  m = max(m, blob(nw, vec3( 0.10, -0.72, -0.42), 0.31));',
    '  m = max(m, blob(nw, vec3(-0.20,  0.62, -0.70), 0.27));',
    '  m = max(m, blob(nw, vec3( 0.80, -0.30, -0.40), 0.23));',""",
    """    '  m = max(m, blob(nw, vec3( 0.45,  0.62,  0.64), 0.26));',
    '  m = max(m, blob(nw, vec3(-0.70, -0.10,  0.50), 0.22));',
    '  m = max(m, blob(nw, vec3( 0.05, -0.78, -0.35), 0.20));',
    '  m = max(m, blob(nw, vec3(-0.15,  0.55, -0.75), 0.18));',
    '  m = max(m, blob(nw, vec3( 0.86, -0.25, -0.30), 0.16));',""")

rep('night',
    "    '    float band = mix(0.13, 1.0, day);',",
    "    '    float band = mix(0.42, 1.0, day);',")

rep('base',
    "      var base = hsl(hue, 0.34, 0.085);",
    "      var base = hsl(hue, 0.38, 0.150);")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
