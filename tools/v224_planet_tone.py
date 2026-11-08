
# -*- coding: utf-8 -*-
"""v224 — 光晕收窄、斑块贴近底色、补晨昏线亮带（limb brightening）。"""
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


rep('glow',
    """    '    float glow = exp(-(dd - R) * 8.5) * outside;',
    '    col += uTint * glow * 0.72;',
    '    alpha = max(alpha, glow * 0.72);',""",
    """    '    float glow = exp(-(dd - R) * 13.0) * outside;',
    '    col += uTint * glow * 0.38;',
    '    alpha = max(alpha, glow * 0.38);',""")

rep('limb',
    """    '    float halo = pow(1.0 - n.z, 7.0) * day;',
    '    col += uTint * halo * 0.14;',""",
    """    '    float halo = pow(1.0 - n.z, 7.0) * day;',
    '    col += uTint * halo * 0.14;',
    '    /* 晨昏线亮带：球内侧靠近边缘一圈更亮，像真的被大气托住 */',
    '    float limb = pow(1.0 - n.z, 2.2) * day * 0.22;',
    '    col += uTint * limb;',""")

rep('land',
    "      var land = hsl(hue, 0.48, 0.470);",
    "      var land = hsl(hue, 0.46, 0.360);")

rep('land2',
    "      var land2 = hsl(hue, 0.55, 0.640);",
    "      var land2 = hsl(hue, 0.52, 0.500);")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
