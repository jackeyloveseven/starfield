
# -*- coding: utf-8 -*-
"""v188 — 图鉴（codex）改全屏档案页：去容器/阴影/卡片底，改发丝分隔。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   星图手札（codex）：居中弹窗 → 全屏档案页
   ============================================================ */
#codex-modal{
  background:rgba(5,8,12,.975) !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  padding:0 !important;
  align-items:stretch !important;
  justify-content:stretch !important;
  transition:opacity .34s var(--ui-ease) !important;
}
#codex-modal .codex-container{
  width:100% !important;max-width:none !important;
  height:100% !important;max-height:none !important;
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
  padding:calc(env(safe-area-inset-top,0px) + 62px)
          max(32px, calc((100vw - 1040px) / 2))
          calc(env(safe-area-inset-bottom,0px) + 28px) !important;
  display:flex !important;flex-direction:column !important;
}
#codex-modal .codex-header{
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  padding:0 0 20px 0 !important;
  align-items:flex-start !important;
}
#codex-modal .codex-titles h2{
  font-family:var(--ui-serif) !important;
  font-size:26px !important;font-weight:400 !important;
  letter-spacing:.22em !important;
  color:rgba(230,237,242,.95) !important;
  margin:0 0 10px 0 !important;
}
#codex-modal .codex-titles p{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.30em !important;
  color:rgba(230,237,242,.36) !important;
}
#codex-modal .codex-close{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid rgba(230,237,242,.20) !important;
  color:rgba(230,237,242,.55) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.26em !important;
  padding:9px 0 !important;
  white-space:nowrap !important;
}
#codex-modal .codex-close:hover{color:#fff !important;border-bottom-color:rgba(230,237,242,.6) !important}
#codex-modal .kbd-hint{font-family:var(--ui-mono) !important;font-size:8px !important;letter-spacing:.24em !important;opacity:.32 !important}

#codex-modal .codex-tabs{
  background:none !important;
  border-bottom:1px solid rgba(230,237,242,.08) !important;
  padding:0 !important;
  gap:34px !important;
  overflow-x:auto !important;
}
#codex-modal .codex-tab{
  border:0 !important;border-radius:0 !important;background:none !important;
  border-bottom:1px solid transparent !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.40) !important;
  padding:17px 0 !important;
  white-space:nowrap !important;
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
#codex-modal .codex-tab:hover{color:rgba(230,237,242,.82) !important}
#codex-modal .codex-tab.active{
  color:#fff !important;
  border-bottom-color:rgba(230,237,242,.85) !important;
}

#codex-modal .codex-body{padding:6px 0 0 0 !important}
#codex-modal .codex-grid{
  gap:0 !important;
  padding:0 !important;
}
#codex-modal .codex-card{
  background:none !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.07) !important;
  border-radius:0 !important;
  box-shadow:none !important;
  padding:22px 26px 22px 0 !important;
  transition:background var(--ui-fast) var(--ui-ease) !important;
}
#codex-modal .codex-card:hover{background:rgba(255,255,255,.02) !important}
#codex-modal .codex-card.locked{opacity:.34 !important}
#codex-modal .codex-card-tag{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.26em !important;
  color:rgba(230,237,242,.34) !important;
}
#codex-modal .codex-card-title{
  font-family:var(--ui-serif) !important;
  font-size:17px !important;font-weight:400 !important;
  letter-spacing:.12em !important;
  color:rgba(230,237,242,.93) !important;
  margin:12px 0 10px 0 !important;
}
#codex-modal .codex-card-desc{
  font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif !important;
  font-size:10.5px !important;line-height:1.8 !important;
  letter-spacing:.05em !important;
  color:rgba(230,237,242,.52) !important;
}
#codex-modal .codex-card-foot{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.22em !important;
  color:rgba(230,237,242,.32) !important;
  margin-top:14px !important;
}
#codex-modal .codex-footer{
  background:none !important;
  border-top:1px solid rgba(230,237,242,.10) !important;
  padding:16px 0 0 0 !important;
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.22em !important;
  color:rgba(230,237,242,.40) !important;
}
#codex-modal .codex-footer a{color:rgba(230,237,242,.62) !important;text-decoration:none !important;border-bottom:1px solid rgba(230,237,242,.2)}

@media (max-width:760px){
  #codex-modal .codex-container{padding-left:24px !important;padding-right:24px !important}
  #codex-modal .codex-titles h2{font-size:19px !important;letter-spacing:.16em !important}
  #codex-modal .codex-grid{grid-template-columns:1fr !important}
  #codex-modal .codex-card{padding-right:0 !important}
  #codex-modal .codex-tabs{gap:22px !important}
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-codex">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('codex css injected', len(CSS))
