
# -*- coding: utf-8 -*-
"""v215 — 清掉最后两个彩色 emoji（🪐 🛸）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()

n1 = src.count("\U0001fa90")
n2 = src.count("\U0001f6f8")
src = src.replace("\U0001fa90", "")
src = src.replace("\U0001f6f8 ", "").replace("\U0001f6f8", "")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('removed planet emoji x%d, ufo emoji x%d' % (n1, n2))
