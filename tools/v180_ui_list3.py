
# -*- coding: utf-8 -*-
"""v180 — 列表头部：标题可省略、计数与关闭不再重叠。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#sf-hatch-list .sf-hl-title,
#sf-hatch-list .sf-hl-count,
#sf-hatch-list .sf-hl-close{
  white-space:nowrap !important;
}""")
new = N("""#sf-hatch-list .sf-hl-title{
  flex:1 1 auto !important;
  min-width:0 !important;
  overflow:hidden !important;
  text-overflow:ellipsis !important;
  white-space:nowrap !important;
}
#sf-hatch-list .sf-hl-count{
  flex:0 0 auto !important;
  margin-left:0 !important;
  white-space:nowrap !important;
}
#sf-hatch-list .sf-hl-close{
  flex:0 0 auto !important;
  margin-left:0 !important;
  white-space:nowrap !important;
}
#sf-hatch-list .sf-hl-core-title,
#sf-hatch-list .sf-hl-core-badge{
  white-space:nowrap !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('list head fixed')
