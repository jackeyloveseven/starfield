
# -*- coding: utf-8 -*-
"""v183 — 计数绝对定位到标题下方，关闭键回到右上。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#sf-hatch-list .sf-hl-head{
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
}""")
new = N("""#sf-hatch-list .sf-hl-head{
  position:relative !important;
  flex-wrap:nowrap !important;
  column-gap:18px !important;
  padding-bottom:24px !important;
  align-items:baseline !important;
}
#sf-hatch-list .sf-hl-head > div{
  flex:0 1 auto !important;
  min-width:0 !important;
}
#sf-hatch-list .sf-hl-title{flex:0 1 auto !important}
#sf-hatch-list .sf-hl-close{margin-left:auto !important;flex:0 0 auto !important}
#sf-hatch-list .sf-hl-count{
  position:absolute !important;
  left:0 !important;bottom:2px !important;
  margin:0 !important;
  flex:0 0 auto !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('head count repositioned')
