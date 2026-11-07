
# -*- coding: utf-8 -*-
"""v186 — 档案打开时星球上移缩小，不被 sheet 切掉。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{opacity:.40 !important}""")
new = N("""#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{
  top:23% !important;
  width:min(34vh,44vw) !important;
  height:min(34vh,44vw) !important;
  opacity:.72 !important;
  transition:top .56s var(--ui-ease),width .56s var(--ui-ease),
             height .56s var(--ui-ease),opacity .42s ease !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('orb repositioned in archive mode')
