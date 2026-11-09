
# -*- coding: utf-8 -*-
"""v313 - 修 GLB 加载的括号：IIFE 未闭合导致 Unexpected token 'if'。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "        (function () {\n          var bin = atob(window.__mothershipGLB);"
new = "        var bin = atob(window.__mothershipGLB);"
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('removed unclosed IIFE')
