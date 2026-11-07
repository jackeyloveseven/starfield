
# -*- coding: utf-8 -*-
"""v182 — 标题不 grow，关闭键回到右上，计数独占第二行。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#sf-hatch-list .sf-hl-title{
  flex:1 1 auto !important;
  min-width:0 !important;""")
new = N("""#sf-hatch-list .sf-hl-title{
  flex:0 1 auto !important;
  min-width:0 !important;""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('title flex fixed')
