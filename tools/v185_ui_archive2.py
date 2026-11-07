
# -*- coding: utf-8 -*-
"""v185 — 档案态保留星球与名字的可见度，大标题不换行。"""
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


rep('orb-dim',
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{opacity:.22 !important}\n"
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-info,\n"
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-coords{opacity:.25 !important}",
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{opacity:.40 !important}\n"
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-info{opacity:.55 !important}\n"
    "#sf-hatch .sf-hatch-card.flipped > .sf-card-coords{opacity:.20 !important}")

rep('title-size',
    """#sf-hatch .sf-hatch-back .sf-hb-card-title{
  font-family:var(--ui-serif) !important;
  font-size:15px !important;font-weight:400 !important;
  letter-spacing:.24em !important;color:rgba(230,237,242,.92) !important;
}""",
    """#sf-hatch .sf-hatch-back .sf-hb-card-title{
  font-family:var(--ui-serif) !important;
  font-size:13px !important;font-weight:400 !important;
  letter-spacing:.16em !important;color:rgba(230,237,242,.92) !important;
  white-space:nowrap !important;
}""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
