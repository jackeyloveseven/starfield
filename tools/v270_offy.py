
# -*- coding: utf-8 -*-
"""v270 - 删掉过严的 offY 过滤：2046 个候选全被它拦掉。
   canvas 会自动裁剪屏外内容，不需要手动过滤；近距离景观的 y 投影必然飞出屏幕。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "        if (q[1] < -80 || q[1] > H + 80) { D.offY++; continue; }"
new = "        /* 不做 y 方向预过滤：canvas 自行裁剪屏外内容。\n           之前 2046 个候选全被这一条拦掉，导致一个景观都没画出来。 */"
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('offY filter removed')
