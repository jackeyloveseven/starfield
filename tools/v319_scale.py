
# -*- coding: utf-8 -*-
"""v319 - 母舰缩到 40 倍（120 倍挡视野）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
old = "          ship.scale.setScalar(120);"
new = "          ship.scale.setScalar(40);"
assert html.count(old) == 1
html = html.replace(old, new)
HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('scale -> 40')
