
# -*- coding: utf-8 -*-
"""v195 — 委托卡移动端不越界；窄屏字号回收。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* 委托卡：容器不越界（容器没有 id/class，用 :has 定位） */
div:has(> .sc-head){
  right:calc(env(safe-area-inset-right,0px) + 24px) !important;
  max-width:calc(100vw - 48px) !important;
  text-align:right !important;
}
@media (max-width:520px){
  .sc-name{font-size:13px !important;letter-spacing:.12em !important}
  .sc-kicker{font-size:7.5px !important;letter-spacing:.24em !important}
  .sc-time{font-size:8.5px !important;letter-spacing:.16em !important}
  .sc-bar{width:104px !important}
  .sc-meta{font-size:7.5px !important;letter-spacing:.18em !important}
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-contract">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('contract card contained')
