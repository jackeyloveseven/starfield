
# -*- coding: utf-8 -*-
"""v169 — 建立 sf-ui-system：起航页按钮去胶囊化，直角发丝 + 精确动效。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   sf-ui-system · 全站内部 UI 的统一语言
   发丝线 + 直角（或 2px）+ 无填充 + 大字距 + 精确缓动。
   只改界面层；游戏内飞行渲染不动。
   ============================================================ */
:root{
  --ui-ease:cubic-bezier(.16,1,.3,1);
  --ui-fast:.26s;
  --ui-slow:.52s;
  --ui-line:rgba(230,237,242,.26);
  --ui-line-soft:rgba(230,237,242,.12);
  --ui-ink:rgba(230,237,242,.92);
  --ui-dim:rgba(230,237,242,.46);
  --ui-mono:"SFMono-Regular",Consolas,"Liberation Mono","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",monospace;
  --ui-serif:"Iowan Old Style","Palatino Linotype","Noto Serif CJK SC","Songti SC",Georgia,serif;
}

/* ---------- 起航点：胶囊 → 下方发丝下划线 ---------- */
.destinations{
  gap:28px !important;
  margin-bottom:34px !important;
}
.destination{
  border:0 !important;
  border-bottom:1px solid transparent !important;
  background:none !important;
  border-radius:0 !important;
  padding:7px 0 6px !important;
  color:var(--ui-dim) !important;
  font-size:calc(10.5px * var(--unit)) !important;
  letter-spacing:.24em !important;
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
.destination:hover{
  color:rgba(230,237,242,.88) !important;
  border-bottom-color:rgba(230,237,242,.26) !important;
}
.destination[aria-checked=true]{
  background:none !important;
  border-color:transparent !important;
  border-bottom-color:rgba(230,237,242,.86) !important;
  color:#fff !important;
}
.destination i{
  width:4px !important;height:4px !important;
  border-radius:1px !important;
  margin-right:9px !important;
  background:currentColor !important;
  opacity:.55 !important;
}
.destination:active{transform:translateY(1px)}

/* ---------- 起航：金色胶囊 → 上下发丝夹一条词 ---------- */
#begin{
  position:relative !important;
  border:0 !important;
  border-top:1px solid var(--ui-line) !important;
  border-bottom:1px solid var(--ui-line-soft) !important;
  background:none !important;
  border-radius:0 !important;
  box-shadow:none !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  color:var(--ui-ink) !important;
  width:min(388px,76vw) !important;
  min-width:0 !important;
  padding:20px 4px !important;
  gap:0 !important;
  justify-content:space-between !important;
  letter-spacing:.40em !important;
  transition:border-color var(--ui-slow) var(--ui-ease),
             color var(--ui-fast) var(--ui-ease),
             padding var(--ui-slow) var(--ui-ease) !important;
}
#begin::after{content:none !important}
#begin b{
  font-weight:400 !important;
  font-size:calc(14px * var(--unit)) !important;
  letter-spacing:.40em !important;
}
#begin:hover{
  transform:none !important;
  box-shadow:none !important;
  border-top-color:rgba(230,237,242,.72) !important;
  border-bottom-color:rgba(230,237,242,.30) !important;
  padding-left:14px !important;
  padding-right:14px !important;
}
#begin:active{
  transform:translateY(1px) !important;
  box-shadow:none !important;
  border-top-color:rgba(230,237,242,.45) !important;
}

/* ---------- 通用按钮基线（不动尺寸，只统一质感） ---------- */
button{
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease),
             background-color var(--ui-fast) var(--ui-ease),
             opacity var(--ui-fast) var(--ui-ease);
}
button:active{transform:translateY(1px)}
button:focus-visible{
  outline:1px solid rgba(230,237,242,.55) !important;
  outline-offset:4px !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-system">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('ui-system injected', len(CSS))
