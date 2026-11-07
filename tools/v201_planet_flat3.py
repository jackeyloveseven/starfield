
# -*- coding: utf-8 -*-
"""v201 — 光源压侧向：终止线退到球的边缘；斑块减到 3 块分布更开。"""
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


rep('light',
    "    '    vec3 L = normalize(vec3(-0.58, 0.40, 0.71));',",
    "    '    vec3 L = normalize(vec3(-0.88, 0.30, 0.36));',")

rep('blobs',
    """    '  m = max(m, blob(nw, vec3( 0.45,  0.62,  0.64), 0.26));',
    '  m = max(m, blob(nw, vec3(-0.70, -0.10,  0.50), 0.22));',
    '  m = max(m, blob(nw, vec3( 0.05, -0.78, -0.35), 0.20));',
    '  m = max(m, blob(nw, vec3(-0.15,  0.55, -0.75), 0.18));',
    '  m = max(m, blob(nw, vec3( 0.86, -0.25, -0.30), 0.16));',""",
    """    '  m = max(m, blob(nw, vec3( 0.52,  0.62,  0.58), 0.23));',
    '  m = max(m, blob(nw, vec3(-0.58,  0.06,  0.70), 0.20));',
    '  m = max(m, blob(nw, vec3( 0.06, -0.76,  0.55), 0.17));',""")

rep('day',
    "    '    float band = mix(0.42, 1.0, day);',",
    "    '    float band = mix(0.30, 1.0, day);',")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
