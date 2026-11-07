
# -*- coding: utf-8 -*-
"""v192 — 飞行中 HUD：.hud 全部直角无底；委托卡去彩色改灰阶。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   飞行中 HUD：统一直角 / 无底 / 发丝
   ============================================================ */
.hud{
  border-radius:0 !important;
  background:none !important;
  box-shadow:none !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
}
#comms-hud{padding-left:0 !important;padding-right:0 !important}
#comms-hud .comms-header{
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  padding-bottom:8px !important;
}
#comms-hud .comms-title{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.28em !important;
  color:rgba(230,237,242,.42) !important;
}
#comms-hud .comms-body{
  font-size:11.5px !important;line-height:1.75 !important;
  letter-spacing:.08em !important;
  color:rgba(230,237,242,.82) !important;
}

/* 委托卡：绿/金 → 灰阶 */
.sc-kicker{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.30em !important;
  color:rgba(230,237,242,.40) !important;
}
.sc-time{
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.20em !important;
  color:rgba(230,237,242,.52) !important;
  font-variant-numeric:tabular-nums !important;
}
.sc-name{
  font-family:var(--ui-serif) !important;
  font-size:15px !important;letter-spacing:.14em !important;
  color:rgba(230,237,242,.94) !important;
  margin-top:7px !important;
}
.sc-bar{
  width:126px !important;
  height:1px !important;
  background:rgba(230,237,242,.14) !important;
  margin:9px 0 7px auto !important;
}
.sc-bar i{background:rgba(230,237,242,.78) !important}
.sc-meta{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.22em !important;
  color:rgba(230,237,242,.42) !important;
}
.sc-meta b{
  color:rgba(230,237,242,.88) !important;
  font-weight:500 !important;
  letter-spacing:.16em !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-hud">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('hud css injected', len(CSS))
