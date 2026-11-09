
# -*- coding: utf-8 -*-
"""v314 - 母舰放到相机正前方，并放大到可见。"""
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

rep("          ship.scale.setScalar(0.16);", "          ship.scale.setScalar(0.28);", 'scale')
rep("          var th = 0.6, ph = 1.12;", "          var th = 0.05, ph = 1.12;", 'pos')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
