
# -*- coding: utf-8 -*-
"""v178 — 抽屉连线减弱；天象馆列表改竖排清单。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

# 1. 减弱抽屉行线
old = "  border-bottom-color:rgba(230,237,242,.07) !important;\n}"
assert src.count(N(old)) == 1
src = src.replace(N(old), N("  border-bottom-color:rgba(230,237,242,.035) !important;\n}"))

# 2. 天象馆列表
CSS = N("""
/* ---------- 天象馆：卡片网格 → 竖排清单 ---------- */
#sf-hatch-list{
  background:rgba(6,9,13,.985) !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  padding:calc(env(safe-area-inset-top,0px) + 38px) 32px calc(env(safe-area-inset-bottom,0px) + 40px) !important;
}
.sf-hl-head{
  align-items:baseline !important;
  margin-bottom:6px !important;
  padding-bottom:16px !important;
  border-bottom:1px solid rgba(230,237,242,.10) !important;
}
.sf-hl-title{
  font-family:var(--ui-serif) !important;
  font-size:19px !important;font-weight:400 !important;
  letter-spacing:.24em !important;color:rgba(230,237,242,.94) !important;
}
.sf-hl-count{
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.28em !important;
  color:rgba(230,237,242,.40) !important;margin-left:14px !important;
}
.sf-hl-close{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.20) !important;
  color:rgba(230,237,242,.55) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.26em !important;
  padding:9px 0 !important;
}
.sf-hl-close:hover{color:#fff !important;border-bottom-color:rgba(230,237,242,.6) !important}

.sf-hl-core-banner{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-top:1px solid rgba(230,237,242,.08) !important;
  border-bottom:1px solid rgba(230,237,242,.08) !important;
  box-shadow:none !important;
  padding:18px 0 !important;
  margin:18px 0 8px 0 !important;
}
.sf-hl-core-icon{font-size:16px !important;filter:none !important;opacity:.8}
.sf-hl-core-title{font-size:13px !important;letter-spacing:.18em !important;color:rgba(230,237,242,.88) !important;font-weight:400 !important}
.sf-hl-core-badge{
  border-radius:0 !important;background:none !important;
  border:0 !important;border-bottom:1px solid rgba(230,237,242,.35) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.2em !important;
  color:rgba(230,237,242,.7) !important;
  padding:2px 0 !important;
}
.sf-hl-core-desc{font-size:9px !important;letter-spacing:.14em !important;color:rgba(230,237,242,.36) !important}
.sf-hl-btn-open{
  border:0 !important;border-radius:0 !important;
  border-bottom:1px solid rgba(230,237,242,.55) !important;
  background:none !important;box-shadow:none !important;color:#fff !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.26em !important;
  padding:11px 14px !important;
  animation:none !important;
}
.sf-hl-btn-open::after{content:none !important}
.sf-hl-btn-open:hover{
  border-bottom-color:#fff !important;box-shadow:none !important;
  transform:none !important;letter-spacing:.32em !important;
}
.sf-hl-btn-gift{
  border-radius:0 !important;background:none !important;
  border:0 !important;border-bottom:1px solid rgba(230,237,242,.16) !important;
  color:rgba(230,237,242,.5) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.2em !important;
  padding:9px 0 !important;
}
.sf-hl-btn-gift:hover{color:#fff !important;border-bottom-color:rgba(230,237,242,.5) !important}

.sf-hl-grid{
  grid-template-columns:1fr !important;
  gap:0 !important;
  padding-top:8px !important;
}
.sf-hl-item{
  flex-direction:row !important;
  align-items:center !important;
  justify-content:flex-start !important;
  gap:18px !important;
  padding:15px 0 !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.06) !important;
  border-radius:0 !important;
  background:none !important;
  box-shadow:none !important;
  animation:none !important;
  position:relative !important;
}
.sf-hl-item:hover{
  transform:none !important;
  background:rgba(255,255,255,.025) !important;
  box-shadow:none !important;
}
.sf-hl-item:active{transform:none !important}
.sf-hl-item.escorted{
  border-color:rgba(230,237,242,.06) !important;
  background:none !important;
  box-shadow:none !important;
}
.sf-hl-orb-wrap{
  width:38px !important;height:38px !important;flex:0 0 auto !important;
}
.sf-hl-orb{
  width:34px !important;height:34px !important;
  border:0 !important;box-shadow:none !important;
  animation:none !important;
}
.sf-hl-item:hover .sf-hl-orb{transform:none !important}
.sf-hl-canvas{width:34px !important;height:34px !important}
.sf-hl-meta-wrap{
  align-items:flex-start !important;
  flex:1 1 auto !important;
  gap:5px !important;
}
.sf-hl-name{
  font-family:var(--ui-serif) !important;
  font-size:16px !important;font-weight:400 !important;
  letter-spacing:.14em !important;
  color:rgba(230,237,242,.94) !important;
  max-width:none !important;
  text-align:left !important;
}
.sf-hl-date{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.32) !important;
}
.sf-hl-tier-badge{
  position:static !important;
  border:0 !important;border-radius:0 !important;background:none !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.24em !important;
  padding:0 !important;
  margin-left:auto !important;
}
.sf-hl-escort-tag{
  position:static !important;
  border:0 !important;border-radius:0 !important;background:none !important;
  color:rgba(230,237,242,.40) !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.2em !important;
  font-weight:400 !important;
  box-shadow:none !important;
  padding:0 !important;
  order:3;
}
.sf-hl-empty-box{padding:60px 0 !important}
.sf-hl-empty-icon{font-size:22px !important;opacity:.4}
.sf-hl-empty-title{
  font-family:var(--ui-serif) !important;font-size:16px !important;
  letter-spacing:.2em !important;font-weight:400 !important;
}
.sf-hl-empty-sub{font-size:10px !important;letter-spacing:.12em !important;color:rgba(230,237,242,.36) !important}
.sf-hl-escort-bar{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.08) !important;
  padding:12px 0 !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.2em !important;
  color:rgba(230,237,242,.55) !important;
}
.sf-hl-escort-badge{
  border:0 !important;border-radius:0 !important;background:none !important;
  color:#fff !important;
  font-family:var(--ui-mono) !important;font-size:9px !important;
  padding:0 !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-veil">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('list css injected', len(CSS))
