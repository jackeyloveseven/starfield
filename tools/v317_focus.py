
# -*- coding: utf-8 -*-
"""v317 - 母舰放到相机视线的地表焦点（R+3），而非同高度。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "          var th = 0.20, ph = 1.12;\n          var pos = sph(th, ph, 36 + 9);"
new = "          var th = 0.16, ph = 1.12;\n          var pos = sph(th, ph, 36 + 3);"
assert html.count(old) == 1
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('ship at surface focus point')
