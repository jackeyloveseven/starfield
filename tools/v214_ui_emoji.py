
# -*- coding: utf-8 -*-
"""v214 — 清掉最后一个真 emoji（🔄）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()

old = "\U0001f504 \u5207\u6362\u6a2a\u5c4f"
n = src.count(old)
src = src.replace(old, "\u5207\u6362\u6a2a\u5c4f")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('replaced', n, 'occurrence(s)')
