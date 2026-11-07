
# -*- coding: utf-8 -*-
"""v170 — 起航点不被 flex 压缩；起航字距回收。"""
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


rep('dest-row',
    """.destinations{
  gap:28px !important;
  margin-bottom:34px !important;
}""",
    """.destinations{
  gap:20px !important;
  row-gap:12px !important;
  margin-bottom:34px !important;
  flex-wrap:wrap !important;
  justify-content:center !important;
}
.destination{flex:0 0 auto !important}""")

rep('begin-letter',
    """#begin b{
  font-weight:400 !important;
  font-size:calc(14px * var(--unit)) !important;
  letter-spacing:.40em !important;
}""",
    """#begin b{
  font-weight:400 !important;
  font-size:calc(14px * var(--unit)) !important;
  letter-spacing:.30em !important;
}""")

rep('begin-letter2',
    "  letter-spacing:.40em !important;\n  transition:border-color var(--ui-slow) var(--ui-ease),",
    "  letter-spacing:.30em !important;\n  transition:border-color var(--ui-slow) var(--ui-ease),")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
