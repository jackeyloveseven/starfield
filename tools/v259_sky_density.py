
# -*- coding: utf-8 -*-
"""v259 - 天象密度：GRB 从 110 小时一次调到约 5-8 分钟一次。
   原 hash(k,7001) < .005 -> 200 chunk 一次，而 CHUNK=3200、SPEED=1.6，
   每 chunk 2000 秒，等于 110 小时才碰得到一次，玩家永远看不到。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "if (started && _skyGrbT < 0 && hash(k, 7001) < .005) skyTriggerGRB(0);"
new = "if (started && _skyGrbT < 0 && hash(k, 7001) < .20) skyTriggerGRB(0);"
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('GRB density: 0.005 -> 0.20 (40x)')
