
# -*- coding: utf-8 -*-
"""v164 — shader：behind 已是 float，三元条件要写成 behind > 0.5。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []

for tag, old, new in [
    ('rad', "    '    float rad = behind ? 0.022 : 0.036;',",
            "    '    float rad = behind > 0.5 ? 0.022 : 0.036;',"),
    ('mc',  "    '      vec3 mc = behind ? uTint * 0.28 : uTint * 1.15;',",
            "    '      vec3 mc = behind > 0.5 ? uTint * 0.28 : uTint * 1.15;',"),
]:
    o, n = N(old), N(new)
    assert src.count(o) == 1, tag
    src = src.replace(o, n)
    log.append(tag)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('fixed:', ', '.join(log))
