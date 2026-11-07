
# -*- coding: utf-8 -*-
"""v210 — 弹窗打开时直接 display:none 触摸簇（opacity 过渡被内部动画顶住）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""body:has(#hangar-modal[style*="flex"]) .sf-touch-cluster,
body:has(#codex-modal.open) .sf-touch-cluster,
body:has(#settings-drawer.open) .sf-touch-cluster,
body:has(#hangar-modal.open) .sf-touch-cluster{
  opacity:0 !important;
  pointer-events:none !important;
  z-index:0 !important;
  transition:opacity .28s ease !important;
}""")
new = N("""body:has(#hangar-modal.open) .sf-touch-cluster,
body:has(#codex-modal.open) .sf-touch-cluster,
body:has(#settings-drawer.open) .sf-touch-cluster,
body:has(#photo-ui.active) .sf-touch-cluster{
  display:none !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('touch cluster display:none under modals')
