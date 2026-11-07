
# -*- coding: utf-8 -*-
"""v189 — 图鉴网格改 3 列，留白更舒展。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#codex-modal .codex-grid{
  gap:0 !important;
  padding:0 !important;
}""")
new = N("""#codex-modal .codex-grid{
  grid-template-columns:repeat(3, minmax(0, 1fr)) !important;
  column-gap:46px !important;
  row-gap:0 !important;
  padding:0 !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

old2 = "#codex-modal .codex-card.locked{opacity:.34 !important}"
assert src.count(N(old2)) == 1
src = src.replace(N(old2), N("#codex-modal .codex-card.locked{opacity:.46 !important}"))

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('grid 3 cols')
