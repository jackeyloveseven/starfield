
# -*- coding: utf-8 -*-
"""v204 — 斑块缩小到 0.13~0.18；卫星轨道张开，不再压过球面。"""
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
    """    '  m = max(m, blob(nw, vec3( 0.52,  0.62,  0.58), 0.23));',
    '  m = max(m, blob(nw, vec3(-0.58,  0.06,  0.70), 0.20));',
    '  m = max(m, blob(nw, vec3( 0.06, -0.76,  0.55), 0.17));',
    '  m = max(m, blob(nw, vec3(-0.34, -0.16, -0.92), 0.25));',
    '  m = max(m, blob(nw, vec3( 0.66,  0.28, -0.70), 0.20));',
    '  m = max(m, blob(nw, vec3(-0.20,  0.86, -0.46), 0.17));',""",
    """    '  m = max(m, blob(nw, vec3( 0.52,  0.62,  0.58), 0.17));',
    '  m = max(m, blob(nw, vec3(-0.58,  0.06,  0.70), 0.15));',
    '  m = max(m, blob(nw, vec3( 0.06, -0.76,  0.55), 0.13));',
    '  m = max(m, blob(nw, vec3(-0.34, -0.16, -0.92), 0.18));',
    '  m = max(m, blob(nw, vec3( 0.66,  0.28, -0.70), 0.15));',
    '  m = max(m, blob(nw, vec3(-0.20,  0.86, -0.46), 0.13));',
    '  m = max(m, blob(nw, vec3( 0.88, -0.42,  0.20), 0.12));',""")

rep('moon-orbit',
    "    '    vec2 e = vec2(cos(ang) * R * 1.46, sin(ang) * R * 0.30);',",
    "    '    vec2 e = vec2(cos(ang) * R * 1.46, sin(ang) * R * 0.62);',")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
