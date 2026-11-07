
# -*- coding: utf-8 -*-
"""v205 — 球边缘从菲涅尔反光改成 1px 发丝轮廓 + 极淡大气。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""    '    /* 大气菲涅尔 */',
    '    float rim = pow(1.0 - n.z, 3.6) * smoothstep(-0.15, 0.55, l);',
    '    col += uTint * rim * 0.40;',""")
new = N("""    '    /* 发丝轮廓 + 极淡大气：边缘是线，不是反光 */',
    '    float edgeLine = smoothstep(0.075, 0.0, n.z);',
    '    col = mix(col, uTint * 0.95, edgeLine * 0.70);',
    '    float halo = pow(1.0 - n.z, 7.0) * day;',
    '    col += uTint * halo * 0.14;',""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('edge -> hairline')
