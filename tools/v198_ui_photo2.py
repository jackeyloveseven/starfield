
# -*- coding: utf-8 -*-
"""v198 — 摄影模式下隐藏航行 HUD，退出键独立定位。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* 摄影模式：航行 HUD 全部让位（画面要干净才拍得出东西） */
body:has(#photo-ui.active) #camera-hud,
body:has(#photo-ui.active) #journey,
body:has(#photo-ui.active) #comms-hud,
body:has(#photo-ui.active) #slingshot-toast,
body:has(#photo-ui.active) *:has(> .sc-head),
body:has(#photo-ui.active) .sf-touch-cluster{
  opacity:0 !important;
  pointer-events:none !important;
  transition:opacity .3s ease !important;
}
/* 退出键独立定位，不与品牌行抢位置 */
body:has(#photo-ui.active) #photo-exit-btn{
  position:fixed !important;
  top:calc(env(safe-area-inset-top,0px) + 16px) !important;
  right:calc(env(safe-area-inset-right,0px) + 22px) !important;
  left:auto !important;
  z-index:120 !important;
}
body:has(#photo-ui.active) #edition,
body:has(#photo-ui.active) #edition-seed{
  right:auto !important;
  left:calc(env(safe-area-inset-left,0px) + 22px) !important;
  opacity:.42 !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-photo2">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('photo mode isolation')
