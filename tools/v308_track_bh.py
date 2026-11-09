
# -*- coding: utf-8 -*-
"""v308 - 记录黑洞位置（正则容忍空白）。"""
import re, sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

pattern = r"if\(m\.kind === 4\)\{\s*if\(dz >= -6000 && dz <= 78000\) activeMasses\.push\(m\);\s*\}"
replacement = "if(m.kind === 4){ if(dz >= -6000 && dz <= 78000){ activeMasses.push(m); window.__sfBH = m; } }"
html, n = re.subn(pattern, replacement, html)
assert n == 1, 'replaced %d' % n

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('black hole tracked, replaced', n)
