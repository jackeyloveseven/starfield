
# -*- coding: utf-8 -*-
"""v175 — 设置抽屉接入 sf-ui-system：去玻璃模糊/圆角/白底块/彩色边。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ---------- 设置抽屉 ---------- */
#settings-drawer{
  width:386px !important;max-width:92vw !important;
  background:rgba(7,10,14,.975) !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  border-left:1px solid rgba(230,237,242,.13) !important;
  box-shadow:none !important;
  padding:calc(env(safe-area-inset-top,0px) + 38px) 32px calc(env(safe-area-inset-bottom,0px) + 48px) !important;
  gap:34px !important;
  transition:right .46s var(--ui-ease) !important;
}
.settings-header{
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  padding-bottom:16px !important;
}
.settings-header h3{
  font-size:17px !important;font-weight:400 !important;
  letter-spacing:.26em !important;
  color:rgba(230,237,242,.92) !important;
}
.settings-section{gap:18px !important}
.settings-section-title{
  font-size:9px !important;letter-spacing:.30em !important;
  color:rgba(230,237,242,.36) !important;
  font-family:var(--ui-mono) !important;
}
#settings-drawer .codex-close{
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.20) !important;
  background:none !important;
  color:rgba(230,237,242,.55) !important;
  font-size:9px !important;letter-spacing:.26em !important;
  padding:10px 0 !important;
}
#settings-drawer .codex-close:hover{
  color:#fff !important;border-bottom-color:rgba(230,237,242,.6) !important;
}

/* 滑块：细轨 + 方形游标 */
.slider-group{gap:8px !important}
.slider-header{
  font-size:11px !important;letter-spacing:.14em !important;
  color:rgba(230,237,242,.80) !important;
}
.slider-header span.val{
  font-family:var(--ui-mono) !important;
  letter-spacing:.16em !important;
  color:rgba(230,237,242,.50) !important;
}
input.range-slider{
  -webkit-appearance:none;appearance:none;
  background:none !important;
  height:22px !important;
  border-radius:0 !important;
}
input.range-slider::-webkit-slider-runnable-track{
  height:1px !important;
  background:rgba(230,237,242,.22) !important;
  border-radius:0 !important;
}
input.range-slider::-webkit-slider-thumb{
  -webkit-appearance:none;appearance:none;
  width:9px !important;height:9px !important;
  border-radius:0 !important;
  background:#e6edf2 !important;
  margin-top:-4px !important;
  box-shadow:none !important;
  cursor:ew-resize;
}
input.range-slider::-moz-range-track{
  height:1px;background:rgba(230,237,242,.22);
}
input.range-slider::-moz-range-thumb{
  width:9px;height:9px;border-radius:0;background:#e6edf2;border:0;
}

/* 唱片机：卡片 → 上下发丝夹一条带 */
.classical-jukebox{
  background:none !important;
  border:0 !important;
  border-top:1px solid rgba(230,237,242,.10) !important;
  border-bottom:1px solid rgba(230,237,242,.10) !important;
  border-radius:0 !important;
  padding:18px 0 !important;
}

/* 抽屉内所有按钮：白底块 → 透明 + 下划线 */
#settings-drawer .photo-btn{
  background:none !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.13) !important;
  border-radius:0 !important;
  color:rgba(230,237,242,.52) !important;
  font-size:11px !important;
  letter-spacing:.14em !important;
  padding:7px 10px !important;
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
#settings-drawer .photo-btn:hover{
  color:rgba(230,237,242,.92) !important;
  border-bottom-color:rgba(230,237,242,.38) !important;
}
#settings-drawer .photo-btn.active,
#settings-drawer .photo-btn.track-select-btn.active{
  background:none !important;
  color:#fff !important;
  border-bottom-color:rgba(230,237,242,.80) !important;
}
#settings-drawer .shortcut-row{
  border-bottom:1px solid rgba(230,237,242,.06) !important;
  padding:7px 0 !important;
  font-size:10.5px !important;
  letter-spacing:.12em !important;
  color:rgba(230,237,242,.55) !important;
}
#settings-drawer .shortcut-key{
  font-family:var(--ui-mono) !important;
  color:rgba(230,237,242,.80) !important;
  letter-spacing:.10em !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-settings">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('settings css injected', len(CSS))
