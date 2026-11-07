
# -*- coding: utf-8 -*-
"""v202 — 拉开球底色与大陆的明度差。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("      var base = hsl(hue, 0.38, 0.150);\n      var land = hsl(hue, 0.46, 0.335);")
new = N("      var base = hsl(hue, 0.38, 0.115);\n      var land = hsl(hue, 0.48, 0.470);")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('contrast raised')
