
# -*- coding: utf-8 -*-
"""v209 — 定制坞打开时把触摸簇压到最底（它和弹窗不在同一层叠上下文）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* 全屏弹窗打开时，触摸簇让位（它位于独立层叠上下文，只能压 z-index） */
body:has(#hangar-modal[style*="flex"]) .sf-touch-cluster,
body:has(#codex-modal.open) .sf-touch-cluster,
body:has(#settings-drawer.open) .sf-touch-cluster,
body:has(#hangar-modal.open) .sf-touch-cluster{
  opacity:0 !important;
  pointer-events:none !important;
  z-index:0 !important;
  transition:opacity .28s ease !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-touchhide">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('touch cluster yields')
