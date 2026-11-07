
# -*- coding: utf-8 -*-
"""v220 — 紧急修复：v207 给 #hangar-modal 加了 opacity:1 !important，
   把「关闭态 opacity:0」也覆盖了 —— 折纸坞从加载起就全屏不透明盖在最上层
   （z-index:9999），起航页所有点击都落在它上面，表现为「卡在介绍页无法跳转」。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""  padding:0 !important;
  opacity:1 !important;
}""")
new = N("""  padding:0 !important;
}""")
assert src.count(old) == 1, 'count=%d' % src.count(old)
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('removed opacity:1 !important from #hangar-modal')
