
# -*- coding: utf-8 -*-
"""v303 - 修 SFBuildup 里的双重转义。"""
import re, sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

def unesc(m):
    return chr(int(m.group(1), 16))

total = 0
for sid in ['sf-buildup', 'sf-evolution']:
    i = html.find('<script id="%s">' % sid)
    if i < 0:
        continue
    j = html.find('</script>', i)
    seg = html[i:j]
    # 双反斜杠 \\uXXXX -> 真实字符
    seg2, n = re.subn(r'\\\\u([0-9a-fA-F]{4})', unesc, seg)
    # 单反斜杠 \uXXXX（在 JS 字符串里本应被解析，但我们是当字面写入的）也还原
    seg2, n2 = re.subn(r'\\u([0-9a-fA-F]{4})', unesc, seg2)
    html = html[:i] + seg2 + html[j:]
    total += n + n2

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('unescaped', total)
