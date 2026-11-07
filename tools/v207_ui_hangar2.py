
# -*- coding: utf-8 -*-
"""v207 — 定制坞提到最上层，彻底盖住飞行 HUD 与通信条。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#hangar-modal{
  background:#05080c !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  padding:0 !important;
}""")
new = N("""#hangar-modal{
  z-index:1500 !important;
  background:#05080c !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  padding:0 !important;
  opacity:1 !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('hangar z raised')
