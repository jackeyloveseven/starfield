
# -*- coding: utf-8 -*-
"""v316 - 母舰放到相机正前方同高度（之前在头顶上看不到）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "          var th = 0.05, ph = 1.12;\n          var pos = sph(th, ph, 36 + 20);"
new = "          var th = 0.20, ph = 1.12;\n          var pos = sph(th, ph, 36 + 9);"
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('ship now ahead of camera at same height')
