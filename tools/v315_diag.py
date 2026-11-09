
# -*- coding: utf-8 -*-
"""v315 - 诊断母舰：加加载标记、抬高放大。"""
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

rep("          ship.scale.setScalar(0.28);", "          ship.scale.setScalar(0.5);", 'scale')
rep("          var pos = sph(th, ph, 36 + 6);", "          var pos = sph(th, ph, 36 + 20);", 'pos')
rep("          dockGroup = ship;", "          dockGroup = ship; window.__shipLoaded = true;", 'mark')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
