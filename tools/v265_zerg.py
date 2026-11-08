
# -*- coding: utf-8 -*-
"""v265 - 菌毯星底色改紫，和囊肿协调。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
old = "  { id: 'zerg_biomorphic',    cn: '生化菌毯星',   preset: 'abyss' },"
new = "  { id: 'zerg_biomorphic',    cn: '生化菌毯星',   preset: 'alien' },"
assert html.count(old) == 1
html = html.replace(old, new)
HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('zerg preset -> alien (purple)')
