
# -*- coding: utf-8 -*-
"""v176 — 抽屉加左侧遮罩（box-shadow spread）、清虚线、修播放键。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

anchor = N("""#settings-drawer .shortcut-key{""")
add = N("""/* 左侧遮罩：用 box-shadow 的 spread 铺满抽屉以外区域 */
#settings-drawer.open{
  box-shadow:-100vw 0 0 100vw rgba(4,7,10,.66) !important;
}

/* 抽屉内不再出现虚线 */
#settings-drawer *{border-style:solid !important}

/* 曲目切换键：给它们形状，不要下划线 */
#btn-prev-track,#btn-next-track{
  border:1px solid rgba(230,237,242,.18) !important;
  border-bottom:1px solid rgba(230,237,242,.18) !important;
  width:30px !important;height:26px !important;
  padding:0 !important;
  display:inline-flex !important;align-items:center;justify-content:center;
  color:rgba(230,237,242,.6) !important;
}
#btn-prev-track:hover,#btn-next-track:hover{
  border-color:rgba(230,237,242,.5) !important;
  color:#fff !important;
}

#settings-drawer .shortcut-key{""")
assert src.count(anchor) == 1
src = src.replace(anchor, add)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('drawer mask + dashed removal')
