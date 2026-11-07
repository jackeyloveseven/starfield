
# -*- coding: utf-8 -*-
"""v206 — 舰队折纸坞改全屏档案页：去容器/卡片底/圆角胶囊，改发丝分隔。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   舰队折纸坞（hangar）：居中弹窗 → 全屏档案页
   ============================================================ */
#hangar-modal{
  background:#05080c !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  padding:0 !important;
}
#hangar-modal .hangar-container{
  width:100% !important;max-width:none !important;
  height:100% !important;max-height:none !important;
  background:none !important;border:0 !important;box-shadow:none !important;
  padding:calc(env(safe-area-inset-top,0px) + 54px)
          max(32px, calc((100vw - 1200px) / 2))
          calc(env(safe-area-inset-bottom,0px) + 26px) !important;
  display:flex !important;flex-direction:column !important;
  overflow-y:auto !important;
}
#hangar-modal .hangar-header{
  background:none !important;
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  padding:0 0 18px 0 !important;
  align-items:flex-start !important;
}
#hangar-modal .hangar-titles h2{
  font-family:var(--ui-serif) !important;
  font-size:24px !important;font-weight:400 !important;
  letter-spacing:.22em !important;
  color:rgba(230,237,242,.95) !important;
}
#hangar-modal .icon-badge{display:none !important}
#hangar-modal .hangar-titles p{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.28em !important;
  color:rgba(230,237,242,.36) !important;
}
#hangar-modal .hangar-close-btn{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.20) !important;
  color:rgba(230,237,242,.55) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.26em !important;
  padding:9px 0 !important;
  white-space:nowrap !important;
}
#hangar-modal .hangar-close-btn:hover{color:#fff !important;border-bottom-color:rgba(230,237,242,.6) !important}
#hangar-modal .kbd-hint{opacity:.28 !important;font-size:8px !important}

/* 卡片：填充块 → 发丝分隔 */
#hangar-modal .hangar-card{
  background:none !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.08) !important;
  border-radius:0 !important;
  box-shadow:none !important;
  padding:16px 18px 16px 0 !important;
  transition:background var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
#hangar-modal .hangar-card:hover{background:rgba(255,255,255,.02) !important}
#hangar-modal .hangar-card.equipped,
#hangar-modal .hangar-card.active,
#hangar-modal .hangar-card[class*="equip"],
#hangar-modal .hangar-card[class*="selected"]{
  background:none !important;
  border-bottom-color:rgba(230,237,242,.62) !important;
}
#hangar-modal .card-id-badge{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.30) !important;
  color:rgba(230,237,242,.55) !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.22em !important;
  padding:3px 0 !important;
}
#hangar-modal .card-name{
  font-family:var(--ui-serif) !important;
  font-size:16px !important;font-weight:400 !important;
  letter-spacing:.14em !important;
  color:rgba(230,237,242,.93) !important;
}
#hangar-modal .card-sub{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.36) !important;
}
#hangar-modal .card-tag{
  color:rgba(230,237,242,.42) !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.20em !important;
}
#hangar-modal .card-desc{
  font-size:10.5px !important;line-height:1.78 !important;
  letter-spacing:.04em !important;
  color:rgba(230,237,242,.52) !important;
  border-top:0 !important;
}
#hangar-modal .card-active-pill{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.82) !important;
}
#hangar-modal .trail-swatch-bar{border-radius:0 !important;height:2px !important}

#hangar-modal .badge,
#hangar-modal .storage-badge{
  border:0 !important;border-radius:0 !important;background:none !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.42) !important;
  padding:0 !important;
}

a-placeholder-for-later
""")

CSS = CSS.replace(N("a-placeholder-for-later\n"), N("""/* 转台 */
#hangar-modal .turntable-wrapper{
  border-radius:0 !important;
  background:#07080b !important;
  border:1px solid rgba(230,237,242,.08) !important;
}
#hangar-modal .turntable-hint{
  border-radius:0 !important;background:none !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.22em !important;
  color:rgba(230,237,242,.32) !important;
}
#hangar-modal .turntable-meta{
  border-radius:0 !important;background:none !important;
  border-top:1px solid rgba(230,237,242,.08) !important;
}
#hangar-modal .turntable-meta-row{
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.18em !important;
  border-bottom:1px solid rgba(230,237,242,.05) !important;
  padding:8px 0 !important;
}
#hangar-modal .turntable-meta-row .label{
  color:rgba(230,237,242,.40) !important;
  font-size:8px !important;letter-spacing:.24em !important;
}
#hangar-modal .turntable-meta-row .val{color:rgba(230,237,242,.86) !important}

/* 分节 */
#hangar-modal .select-section-title{
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.52) !important;
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  padding-bottom:10px !important;
}
#hangar-modal .section-desc{
  font-size:8.5px !important;letter-spacing:.18em !important;
  color:rgba(230,237,242,.30) !important;
}
#hangar-modal .hangar-footer-bar{
  border-top:1px solid rgba(230,237,242,.10) !important;
  background:none !important;
  padding-top:14px !important;
}

@media (max-width:760px){
  #hangar-modal .hangar-container{
    padding-left:22px !important;padding-right:22px !important;
  }
  #hangar-modal .hangar-titles h2{font-size:18px !important;letter-spacing:.14em !important}
  #hangar-modal .hangar-card{padding-right:0 !important}
}"""))

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-hangar">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('hangar css injected', len(CSS))
