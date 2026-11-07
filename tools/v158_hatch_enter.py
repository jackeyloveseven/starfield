
# -*- coding: utf-8 -*-
"""v158 — 斑块分布加密 + 卡片浮起入场（由 0.985 → 1）。"""
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
    c = src.count(o)
    assert c == 1, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


rep('patches',
    """    var PATCHES = [
      { lon: 12,  lat: 26,  rx: 0.30, ry: 0.20 },
      { lon: 96,  lat: -12, rx: 0.34, ry: 0.17 },
      { lon: 158, lat: 44,  rx: 0.19, ry: 0.13 },
      { lon: 224, lat: -34, rx: 0.26, ry: 0.16 },
      { lon: 288, lat: 8,   rx: 0.21, ry: 0.25 },
      { lon: 340, lat: -52, rx: 0.17, ry: 0.11 }
    ];""",
    """    var PATCHES = [
      { lon: 8,   lat: 30,  rx: 0.28, ry: 0.17 },
      { lon: 58,  lat: -6,  rx: 0.22, ry: 0.26 },
      { lon: 104, lat: -40, rx: 0.18, ry: 0.12 },
      { lon: 146, lat: 16,  rx: 0.24, ry: 0.19 },
      { lon: 188, lat: 52,  rx: 0.16, ry: 0.10 },
      { lon: 226, lat: -22, rx: 0.26, ry: 0.15 },
      { lon: 268, lat: 6,   rx: 0.20, ry: 0.24 },
      { lon: 306, lat: -48, rx: 0.15, ry: 0.10 },
      { lon: 342, lat: 38,  rx: 0.19, ry: 0.13 }
    ];""")

rep('enter-scale',
    "  transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));\n  transform-style:preserve-3d;",
    "  transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) scale(var(--sc,.986));\n  transform-style:preserve-3d;")

rep('enter-scale-on',
    "#sf-hatch .sf-hatch-card.revealed{opacity:1;filter:none;pointer-events:auto}",
    "#sf-hatch .sf-hatch-card.revealed{opacity:1;filter:none;pointer-events:auto;--sc:1}")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
