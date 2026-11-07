
# -*- coding: utf-8 -*-
"""v187 — 档案改为全屏页（从下方滑入铺满），不再留半屏黑区。"""
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


rep('full-page',
    """  height:auto !important;max-height:78vh !important;
  margin:0 !important;""",
    """  top:0 !important;bottom:0 !important;
  height:auto !important;max-height:none !important;
  margin:0 !important;""")

rep('padding',
    "  padding:34px 32px calc(env(safe-area-inset-bottom,0px) + 124px) !important;",
    "  padding:calc(env(safe-area-inset-top,0px) + 76px) 32px calc(env(safe-area-inset-bottom,0px) + 128px) !important;")

rep('hide-stage',
    """#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{
  top:23% !important;
  width:min(34vh,44vw) !important;
  height:min(34vh,44vw) !important;
  opacity:.72 !important;
  transition:top .56s var(--ui-ease),width .56s var(--ui-ease),
             height .56s var(--ui-ease),opacity .42s ease !important;
}""",
    """#sf-hatch .sf-hatch-card.flipped > .sf-card-orb-stage{opacity:0 !important}""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
