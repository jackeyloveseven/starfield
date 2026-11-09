
# -*- coding: utf-8 -*-
"""v318 - 母舰放大：GLB 里模型本身已是 0.001（毫米→米），需放大才可见。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "          ship.scale.setScalar(0.5);"
new = "          ship.scale.setScalar(120);"
assert html.count(old) == 1
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('ship scale 0.5 -> 120 (model itself is 0.001 from mm-to-m)')
