
# -*- coding: utf-8 -*-
"""v208 — 定制坞压到触摸簇之上；底部留出空间不被按钮遮挡。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#hangar-modal{
  z-index:1500 !important;""")
new = N("""#hangar-modal{
  z-index:9999 !important;
  isolation:isolate !important;
  transform:translateZ(0) !important;""")
assert src.count(old) == 1
src = src.replace(old, new)

old2 = N("""  padding:calc(env(safe-area-inset-top,0px) + 54px)
          max(32px, calc((100vw - 1200px) / 2))
          calc(env(safe-area-inset-bottom,0px) + 26px) !important;""")
new2 = N("""  padding:calc(env(safe-area-inset-top,0px) + 54px)
          max(32px, calc((100vw - 1200px) / 2))
          calc(env(safe-area-inset-bottom,0px) + 132px) !important;""")
assert src.count(old2) == 1
src = src.replace(old2, new2)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('hangar raised + padding')
