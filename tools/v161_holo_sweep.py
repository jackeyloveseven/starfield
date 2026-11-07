
# -*- coding: utf-8 -*-
"""v161 — 扫描光带改为入场单次扫过（1.1s），静止时不存在。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""#sf-hatch .sf-card-holo{
  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 49.45%,rgba(255,255,255,.11) 50%,transparent 50.55%);
  mix-blend-mode:normal;
  opacity:0;transition:opacity .8s ease .3s;
  z-index:5;border-radius:6px;
}
#sf-hatch .sf-hatch-card.revealed .sf-card-holo{opacity:1}""")

new = N("""#sf-hatch .sf-card-holo{
  background:none;mix-blend-mode:normal;
  opacity:1;pointer-events:none;
  z-index:5;border-radius:6px;overflow:hidden;
}
/* 显影时一道细光带斜扫一次，之后不存在：静止的斜线在纯色面上像划痕 */
#sf-hatch .sf-card-holo::after{
  content:"";position:absolute;top:-25%;left:-40%;
  width:34%;height:150%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.13),transparent);
  transform:rotate(16deg);opacity:0;
}
#sf-hatch .sf-hatch-card.revealed .sf-card-holo::after{
  animation:sfFlatSweep 1.1s cubic-bezier(.45,0,.25,1) .30s forwards;
}
@keyframes sfFlatSweep{
  0%{left:-40%;opacity:0}
  12%{opacity:1}
  88%{opacity:1}
  100%{left:112%;opacity:0}
}""")

assert src.count(old) == 1
src = src.replace(old, new)
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('holo -> one-shot sweep')
