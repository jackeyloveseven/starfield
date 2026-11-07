
# -*- coding: utf-8 -*-
"""v171 — 隐藏分段控件滑块 dest-thumb；选中态由下划线表达。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

anchor = N(""".destination:active{transform:translateY(1px)}""")
add = N(""".destination:active{transform:translateY(1px)}

/* 旧的分段控件滑块（绝对定位胶囊）：选中态改用下划线后它就多余了 */
.dest-thumb{display:none !important}""")

assert src.count(anchor) == 1
src = src.replace(anchor, add)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('dest-thumb hidden')
