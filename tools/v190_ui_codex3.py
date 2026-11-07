
# -*- coding: utf-8 -*-
"""v190 — 图鉴背景不透明、移动端 footer 换行。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#codex-modal{
  background:rgba(5,8,12,.975) !important;""")
new = N("""#codex-modal{
  background:#05080c !important;""")
assert src.count(old) == 1
src = src.replace(old, new)

old2 = N("""@media (max-width:760px){
  #codex-modal .codex-container{padding-left:24px !important;padding-right:24px !important}""")
new2 = N("""@media (max-width:760px){
  #codex-modal .codex-container{padding-left:24px !important;padding-right:24px !important}
  #codex-modal .codex-footer{
    flex-wrap:wrap !important;
    row-gap:12px !important;
    column-gap:20px !important;
    justify-content:flex-start !important;
  }""")
assert src.count(old2) == 1
src = src.replace(old2, new2)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('codex opaque + footer wrap')
