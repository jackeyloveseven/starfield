
# -*- coding: utf-8 -*-
"""v196 — 委托卡宿主（非 div）也要命中；名字右对齐。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""div:has(> .sc-head){
  right:calc(env(safe-area-inset-right,0px) + 24px) !important;
  max-width:calc(100vw - 48px) !important;
  text-align:right !important;
}""")
new = N("""*:has(> .sc-head){
  right:calc(env(safe-area-inset-right,0px) + 22px) !important;
  left:auto !important;
  max-width:calc(100vw - 44px) !important;
  text-align:right !important;
}
.sc-head, .sc-name, .sc-meta{text-align:right !important}
.sc-head{justify-content:flex-end !important}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('contract host anchored')
