
# -*- coding: utf-8 -*-
"""v166 — 星球收敛：大陆更少更整、环更实、夜面留底。"""
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


rep('land',
    "    '    float f = fbm(nw * 2.35 + uSeed);',\n"
    "    '    float land = smoothstep(0.495, 0.515, f);',",
    "    '    float f = fbm(nw * 2.05 + uSeed);',\n"
    "    '    float land = smoothstep(0.545, 0.560, f);',")

rep('night',
    "    '    float band = l < 0.12 ? 0.05 : (l < 0.58 ? 0.34 : 1.0);',",
    "    '    float band = l < 0.10 ? 0.085 : (l < 0.56 ? 0.38 : 1.0);',")

rep('ring-shape',
    "    '    float e1 = length(vec2(q.x / (R * 1.46), q.y / (R * 0.42))) - 1.0;',\n"
    "    '    ringFront += 1.0 - smoothstep(0.0, 0.010, abs(e1));',",
    "    '    float e1 = length(vec2(q.x / (R * 1.42), q.y / (R * 0.34))) - 1.0;',\n"
    "    '    ringFront += 1.0 - smoothstep(0.0, 0.014, abs(e1));',")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
