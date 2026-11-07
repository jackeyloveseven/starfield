
# -*- coding: utf-8 -*-
"""v179 — 列表行高与行内元素排布修正。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ---------- 列表行内排布修正 ---------- */
#sf-hatch-list .sf-hl-head{
  display:flex !important;
  align-items:baseline !important;
  gap:18px !important;
}
#sf-hatch-list .sf-hl-head > div{
  display:flex !important;
  align-items:baseline !important;
  gap:14px !important;
  min-width:0 !important;
}
#sf-hatch-list .sf-hl-title,
#sf-hatch-list .sf-hl-count,
#sf-hatch-list .sf-hl-close{
  white-space:nowrap !important;
}
#sf-hatch-list .sf-hl-close{
  padding:9px 6px !important;
  margin-left:auto !important;
}

#sf-hatch-list .sf-hl-grid{
  grid-auto-rows:min-content !important;
  align-content:start !important;
  align-items:start !important;
}
#sf-hatch-list .sf-hl-item{
  min-height:0 !important;
  height:auto !important;
  max-height:none !important;
  align-items:center !important;
  overflow:visible !important;
}
#sf-hatch-list .sf-hl-item > *{
  min-height:0 !important;
}

/* 品阶徽章从轨道球里脱出来，靠右 */
#sf-hatch-list .sf-hl-orb-wrap{
  position:static !important;
  flex:0 0 auto !important;
  overflow:visible !important;
}
#sf-hatch-list .sf-hl-tier-badge{
  position:absolute !important;
  right:0 !important;top:50% !important;
  transform:translateY(-50%) !important;
  white-space:nowrap !important;
  width:auto !important;
  margin:0 !important;
  order:0;
}
#sf-hatch-list .sf-hl-escort-tag{
  white-space:nowrap !important;
  flex:0 0 auto !important;
  margin-right:14px;
}
#sf-hatch-list .sf-hl-meta-wrap{
  flex-direction:column !important;
  align-items:flex-start !important;
  justify-content:center !important;
  min-width:0 !important;
}
#sf-hatch-list .sf-hl-item{ padding-right:86px !important; }
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-veil2">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('list row fix injected', len(CSS))
