
# -*- coding: utf-8 -*-
"""v246 - monument 预设颜色加深（6 空格缩进）。"""
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

rep("""      deepOcean: '#1a1c29',
      coastWater: '#4a6fa5',
      sand: '#f4a261',
      grass: '#b5838d',
      forest: '#6d6875',
      rock: '#e5989b',
      snow: '#ffb4a2',
      waterTrans: 0.75""",
    """      deepOcean: '#0e1018',
      coastWater: '#3a5478',
      sand: '#c8a06a',
      grass: '#8a7a5c',
      forest: '#5c5346',
      rock: '#7a6a55',
      snow: '#cfc3a8',
      waterTrans: 0.78""",
    'monumentColors')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
