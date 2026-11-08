
# -*- coding: utf-8 -*-
"""v223 — 大气辉光扩散范围放宽；二级地块缩小到点位级。"""
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


rep('glow-range',
    """    '  {',
    '    float dd = sqrt(r2);',
    '    float outside = smoothstep(R - 0.006, R + 0.002, dd);',
    '    float glow = exp(-(dd - R) * 15.0) * outside;',
    '    col += uTint * glow * 0.55;',
    '    alpha = max(alpha, glow * 0.55);',
    '  }',""",
    """    '  {',
    '    float dd = sqrt(r2);',
    '    float outside = smoothstep(R - 0.004, R + 0.004, dd);',
    '    float glow = exp(-(dd - R) * 8.5) * outside;',
    '    col += uTint * glow * 0.72;',
    '    alpha = max(alpha, glow * 0.72);',
    '  }',""")

rep('blob2-size',
    """    '  m = max(m, blob(nw, vec3( 0.62,  0.30,  0.72), 0.085));',
    '  m = max(m, blob(nw, vec3(-0.44, -0.36,  0.82), 0.075));',
    '  m = max(m, blob(nw, vec3( 0.18, -0.60,  0.78), 0.065));',
    '  m = max(m, blob(nw, vec3(-0.70,  0.44,  0.56), 0.060));',
    '  m = max(m, blob(nw, vec3( 0.34,  0.86,  0.38), 0.055));',""",
    """    '  m = max(m, blob(nw, vec3( 0.58,  0.26,  0.77), 0.052));',
    '  m = max(m, blob(nw, vec3(-0.40, -0.34,  0.85), 0.046));',
    '  m = max(m, blob(nw, vec3( 0.14, -0.56,  0.82), 0.040));',
    '  m = max(m, blob(nw, vec3(-0.66,  0.40,  0.64), 0.038));',
    '  m = max(m, blob(nw, vec3( 0.30,  0.82,  0.49), 0.034));',
    '  m = max(m, blob(nw, vec3(-0.18,  0.10,  0.98), 0.030));',""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
