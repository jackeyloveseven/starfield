
# -*- coding: utf-8 -*-
"""v172 — 起航按钮与下方说明拉开距离，字距回收。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new):
    global src
    o, n = N(old), N(new)
    assert src.count(o) == 1, tag
    src = src.replace(o, n)
    log.append(tag)


rep('begin-margin',
    "  padding:20px 4px !important;\n  gap:0 !important;",
    "  padding:20px 4px !important;\n  margin:0 0 30px 0 !important;\n  gap:0 !important;")

rep('begin-track',
    "  letter-spacing:.30em !important;\n  transition:border-color var(--ui-slow) var(--ui-ease),",
    "  letter-spacing:.26em !important;\n  transition:border-color var(--ui-slow) var(--ui-ease),")

rep('begin-b',
    "  font-size:calc(14px * var(--unit)) !important;\n  letter-spacing:.30em !important;",
    "  font-size:calc(15px * var(--unit)) !important;\n  letter-spacing:.26em !important;")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
