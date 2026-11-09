
# -*- coding: utf-8 -*-
"""v286 - 演化接入渲染，锚点不含缩进。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

rep("this.rotY = (((this.item && this.item.hue) || 200) % 360) * Math.PI / 180;",
    """this.rotY = (((this.item && this.item.hue) || 200) % 360) * Math.PI / 180
        + (window.SFEvolution ? window.SFEvolution.spinPhase(this.item) : 0);""",
    'spin')

rep("var a = t * ud.speed + ud.phase;",
    "var a = t * ud.speed + ud.phase + (window.__sfOrbitPhase || 0);",
    'orbit')

rep("    var manif = sfManifFor(item);",
    """    var manif = sfManifFor(item);
    window.__sfOrbitPhase = window.SFEvolution ? window.SFEvolution.orbitPhase(item) : 0;
    window.__sfCityCount = window.SFEvolution ? window.SFEvolution.cityGrowth(item, 900) : 900;""",
    'evol')

rep("    for (var ci = 0; ci < 900; ci++) {",
    "    for (var ci = 0; ci < (window.__sfCityCount || 900); ci++) {",
    'cityLoop')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
