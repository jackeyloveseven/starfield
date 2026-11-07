
# -*- coding: utf-8 -*-
"""v218 — 修复起航页布局：.intro-inner 的 position 是 absolute（右侧栏定位），
   我误改成 relative，导致 left:65%/top:50%/transform 全部失效、内容变全宽流式。
   手机屏幕矮时「起航」被挤出可视区 -> 点不到。只该加 z-index。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("#intro .intro-inner{position:relative;z-index:1}")
new = N("#intro .intro-inner{z-index:1}")
assert src.count(old) == 1, 'count=%d' % src.count(old)
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('fixed: .intro-inner keeps position:absolute')
