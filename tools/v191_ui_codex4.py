
# -*- coding: utf-8 -*-
"""v191 — 图鉴正文可滚动，末行不被 footer 裁掉。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = "#codex-modal .codex-body{padding:6px 0 0 0 !important}"
new = ("#codex-modal .codex-body{flex:1 1 auto !important;min-height:0 !important;"
       "overflow-y:auto !important;padding:6px 0 26px 0 !important;"
       "scrollbar-width:thin !important}")
assert src.count(N(old)) == 1
src = src.replace(N(old), N(new))

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('codex body scrolls')
