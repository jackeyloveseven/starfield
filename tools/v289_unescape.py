
# -*- coding: utf-8 -*-
"""v289 - 修 SFEvolution 里的双重转义：显示成 \u5929 而不是"天"。"""
import re, sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

i = html.find('<script id="sf-evolution">')
j = html.find('</script>', i)
assert i > 0 and j > i
seg = html[i:j]

# 把 \\uXXXX（双反斜杠，JS 会显示成字面）还原为真正的字符
def unesc(m):
    return chr(int(m.group(1), 16))

new_seg, n = re.subn(r'\\\\u([0-9a-fA-F]{4})', unesc, seg)
# 单反斜杠的 \uXXXX 也一并还原
new_seg, n2 = re.subn(r'\\u([0-9a-fA-F]{4})', unesc, new_seg)

html = html[:i] + new_seg + html[j:]
HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('unescaped', n, '+', n2, 'sequences')
