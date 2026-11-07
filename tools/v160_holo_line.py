
# -*- coding: utf-8 -*-
"""v160 — 扫描光带从宽雾改为 1px 细线。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 48.4%,rgba(255,255,255,.028) 50%,transparent 51.6%);""")
new = N("""  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 49.45%,rgba(255,255,255,.11) 50%,transparent 50.55%);""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('holo narrowed to hairline')
