
# -*- coding: utf-8 -*-
"""v184 — 档案从「翻卡片背面」改为底部升起的 sheet；命名表单收纳同一套语言。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   天文档案：从翻转卡背改为底部升起的 sheet（全屏舞台下没有卡背可翻）
   ============================================================ */
#sf-hatch .sf-hatch-card .sf-hatch-back{
  display:block !important;
  position:fixed !important;
  left:0 !important;right:0 !important;bottom:0 !important;top:auto !important;
  width:100% !important;max-width:none !important;
  height:auto !important;max-height:78vh !important;
  margin:0 !important;
  border:0 !important;
  border-top:1px solid rgba(230,237,242,.16) !important;
  border-radius:0 !important;
  background:rgba(8,11,15,.988) !important;
  box-shadow:0 -1px 0 rgba(230,237,242,.04) !important;
  padding:34px 32px calc(env(safe-area-inset-bottom,0px) + 124px) !important;
  transform:translateY(103%) !important;
  opacity:1 !important;
  transition:transform .56s var(--ui-ease) !important;
  overflow-y:auto !important;
  z-index:40 !important;
  pointer-events:none !important;
}
#sf-hatch .sf-hatch-card.flipped .sf-hatch-back{
  transform:translateY(0) !important;
  pointer-events:auto !important;
}
/* 档案打开时动作条浮在 sheet 之上 */
#sf-hatch .sf-hatch-card.flipped > .sf-card-actions{
  z-index:46 !important;
  background:rgba(8,11,15,.99) !important;
  border-top-color:rgba(230,237,242,.10) !important;
}
#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{opacity:.22 !important}
#sf-hatch .sf-hatch-card.flipped > .sf-card-info,
#sf-hatch .sf-hatch-card.flipped > .sf-card-coords{opacity:.25 !important}

/* sheet 内排版 */
#sf-hatch .sf-hatch-back .sf-hb-top-seal{
  display:flex !important;flex-direction:column !important;align-items:flex-start !important;
  gap:8px !important;
  padding:0 0 16px 0 !important;
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  text-align:left !important;
}
#sf-hatch .sf-hatch-back .sf-hb-astrolabe-icon{
  font-size:9px !important;letter-spacing:.30em !important;
  color:rgba(230,237,242,.28) !important;text-shadow:none !important;
}
#sf-hatch .sf-hatch-back .sf-hb-card-title{
  font-family:var(--ui-serif) !important;
  font-size:15px !important;font-weight:400 !important;
  letter-spacing:.24em !important;color:rgba(230,237,242,.92) !important;
}
#sf-hatch .sf-hatch-back .sf-hb-card-sub{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.38) !important;
}
#sf-hatch .sf-hatch-back .sf-hb-telemetry-grid{
  display:block !important;margin:4px 0 0 0 !important;
}
#sf-hatch .sf-hatch-back .sf-hb-row{
  display:flex !important;align-items:baseline !important;justify-content:space-between !important;
  padding:11px 0 !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.055) !important;
  background:none !important;border-radius:0 !important;
  font-size:10px !important;letter-spacing:.16em !important;
}
#sf-hatch .sf-hatch-back .sf-hb-row span{
  font-family:var(--ui-mono) !important;
  color:rgba(230,237,242,.40) !important;font-size:9px !important;letter-spacing:.24em !important;
}
#sf-hatch .sf-hatch-back .sf-hb-row b{
  font-family:var(--ui-mono) !important;
  font-weight:400 !important;
  color:rgba(230,237,242,.88) !important;font-size:10px !important;letter-spacing:.16em !important;
}
#sf-hatch .sf-hatch-back .sf-hb-quote-box{
  margin:20px 0 0 0 !important;padding:0 0 0 14px !important;
  border:0 !important;border-left:1px solid rgba(230,237,242,.30) !important;
  background:none !important;border-radius:0 !important;
}
#sf-hatch .sf-hatch-back .sf-hb-line{
  font-size:10.5px !important;line-height:1.8 !important;
  letter-spacing:.10em !important;
  color:rgba(230,237,242,.55) !important;
}
#sf-hatch .sf-hatch-back .sf-hb-flip-hint{
  margin-top:16px !important;
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.26em !important;
  color:rgba(230,237,242,.24) !important;text-align:left !important;
}
#sf-hatch .sf-hatch-back .sf-foil{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.26em !important;
  color:rgba(230,237,242,.30) !important;text-shadow:none !important;
  left:auto !important;right:32px !important;top:36px !important;
}

/* 命名区 */
#sf-hatch .sf-hb-name-ui{
  margin-top:22px !important;padding-top:20px !important;
  border-top:1px solid rgba(230,237,242,.10) !important;
}
#sf-hatch .sf-hb-name-btn{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.30) !important;
  color:rgba(230,237,242,.75) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.26em !important;font-weight:400 !important;
  padding:9px 2px !important;
}
#sf-hatch .sf-hb-name-btn:hover{color:#fff !important;border-bottom-color:#fff !important}
#sf-hatch .sf-hb-name-form{
  display:none;flex-direction:column;gap:12px;
}
#sf-hatch .sf-hb-name-form.on{display:flex !important}
#sf-hatch .sf-hb-name-input{
  border:0 !important;border-radius:0 !important;
  border-bottom:1px solid rgba(230,237,242,.35) !important;
  background:none !important;
  color:#fff !important;
  font-family:var(--ui-serif) !important;
  font-size:17px !important;letter-spacing:.16em !important;
  padding:10px 0 !important;
  outline:none !important;
}
#sf-hatch .sf-hb-name-input:focus{
  border-bottom-color:#fff !important;
}
#sf-hatch .sf-hb-name-form button{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.22) !important;
  color:rgba(230,237,242,.62) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.24em !important;
  padding:9px 2px !important;
}
#sf-hatch .sf-hb-name-form button:hover{color:#fff !important;border-bottom-color:rgba(230,237,242,.7) !important}
#sf-hatch .sf-hb-name-msg{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.2em !important;
  color:rgba(230,237,242,.45) !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-archive">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('archive sheet css injected', len(CSS))
