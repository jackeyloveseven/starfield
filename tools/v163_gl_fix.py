
# -*- coding: utf-8 -*-
"""v163 — 修 SFPlanetGL shader 的 bool→float 赋值。"""
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
    c = src.count(o)
    assert c == 1, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


rep('behind-bool',
    "    '    float behind = sin(ang) < 0.0;',",
    "    '    float behind = sin(ang) < 0.0 ? 1.0 : 0.0;',")

rep('ring-branch',
    "    '  if (!front) ringBack = ringFront; else ringFront = ringFront;',",
    "    '  if (!front) { ringBack = ringFront; ringFront = 0.0; }',")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
