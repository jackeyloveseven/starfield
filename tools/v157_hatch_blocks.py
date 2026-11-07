
# -*- coding: utf-8 -*-
"""v157 — 星球斑块改群岛化、卡片底色提一档、光带收窄、按钮字号微调。"""
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
      { lon: 18,  lat: 20,  rx: 0.46, ry: 0.34 },
      { lon: 124, lat: -22, rx: 0.40, ry: 0.26 },
      { lon: 236, lat: 32,  rx: 0.34, ry: 0.22 },
      { lon: 302, lat: -10, rx: 0.30, ry: 0.20 },
      { lon: 72,  lat: 54,  rx: 0.20, ry: 0.13 }
    ];""",
    """    var PATCHES = [
      { lon: 12,  lat: 26,  rx: 0.30, ry: 0.20 },
      { lon: 96,  lat: -12, rx: 0.34, ry: 0.17 },
      { lon: 158, lat: 44,  rx: 0.19, ry: 0.13 },
      { lon: 224, lat: -34, rx: 0.26, ry: 0.16 },
      { lon: 288, lat: 8,   rx: 0.21, ry: 0.25 },
      { lon: 340, lat: -52, rx: 0.17, ry: 0.11 }
    ];""")

rep('card-bg',
    "  background:#0b0d11;\n  border:1px solid rgba(255,255,255,.11);\n  border-top-color:var(--tier,#fff);",
    "  background:#0d1017;\n  border:1px solid rgba(255,255,255,.13);\n  border-top-color:var(--tier,#fff);")

rep('holo-narrow',
    "    transparent 47%,rgba(255,255,255,.030) 50%,transparent 53%);",
    "    transparent 48.4%,rgba(255,255,255,.028) 50%,transparent 51.6%);")

rep('act-font',
    """  font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC","SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.22em;font-weight:600;
  color:rgba(255,255,255,.48)!important;""",
    """  font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC","SFMono-Regular",Consolas,monospace;
  font-size:9px;line-height:1;letter-spacing:.22em;font-weight:500;
  color:rgba(255,255,255,.52)!important;""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
