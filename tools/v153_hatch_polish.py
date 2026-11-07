
# -*- coding: utf-8 -*-
"""v153 — sf-hatch-flat 终修：填满卡片、明暗分界偏侧光、桌面放大一档。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new, count=1):
    global src
    o, n = N(old), N(new)
    c = src.count(o)
    assert c == count, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


rep('orb-size',
    "#sf-hatch .sf-hatch-orb{\n  width:min(202px,56vw);aspect-ratio:1;box-shadow:none;cursor:grab;\n}",
    "#sf-hatch .sf-hatch-orb{\n  width:min(222px,58vw);aspect-ratio:1;box-shadow:none;cursor:grab;\n}")

rep('orb-stage',
    "#sf-hatch .sf-card-orb-stage{\n  flex:0 0 auto;height:298px;min-height:0;max-height:none;\n  margin:0;padding:64px 0 0 0;\n}",
    "#sf-hatch .sf-card-orb-stage{\n  flex:0 0 auto;height:310px;min-height:0;max-height:none;\n  margin:0;padding:58px 0 0 0;\n}")

rep('info-pad',
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 58px 20px;z-index:6}",
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 50px 20px;z-index:6}")

rep('tabula',
    """    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.arc(cx, cy, r, -Math.PI / 2, Math.PI / 2, false);
    ctx.closePath();
    ctx.fillStyle = 'rgba(4, 6, 10, 0.74)';""",
    """    /* 明暗分界偏到右侧，像侧光而非对半切 */
    ctx.beginPath();
    ctx.arc(cx + r * 0.16, cy, r, -Math.PI / 2, Math.PI / 2, false);
    ctx.closePath();
    ctx.fillStyle = 'rgba(4, 6, 10, 0.74)';""")

rep('desktop',
    "@media (prefers-reduced-motion:reduce){",
    """@media (min-width:900px){
  #sf-hatch .sf-hatch-card,
  #sf-hatch #sf-shockwave{width:336px}
  #sf-hatch .sf-hatch-orb{width:238px}
  #sf-hatch .sf-card-orb-stage{height:340px;padding-top:62px}
  #sf-hatch .sf-card-info{padding-bottom:56px}
}
@media (prefers-reduced-motion:reduce){""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
