
# -*- coding: utf-8 -*-
"""v181 — 列表头部：计数换到第二行，标题不再被省略号截断。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

anchor = N("""#sf-hatch-list .sf-hl-title{
  flex:1 1 auto !important;""")
add = N("""#sf-hatch-list .sf-hl-head{
  flex-wrap:wrap !important;
  row-gap:9px !important;
  column-gap:18px !important;
}
#sf-hatch-list .sf-hl-title{order:1 !important}
#sf-hatch-list .sf-hl-close{order:2 !important;margin-left:auto !important}
#sf-hatch-list .sf-hl-count{
  order:3 !important;
  flex:0 0 100% !important;
  margin:0 !important;
}
#sf-hatch-list .sf-hl-title{
  flex:1 1 auto !important;""")
assert src.count(anchor) == 1
src = src.replace(anchor, add)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('list head wrapped')
