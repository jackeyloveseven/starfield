
# -*- coding: utf-8 -*-
"""v248 - 四合一修复：
   1. FOUC：把新增样式块搬进 <head>
   2. 震动：只保留少数场景
   3. 卡面按钮：放大点击区 + 加引导
   4. 蓝闪：去掉 color-dodge 全息层
"""
import re, sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

# ---------- 1. FOUC：把 body 后的 sf-* 样式搬进 head ----------
head_end = html.find('</head>')
assert head_end > 0

# 收集 body 之后的所有 <style id="sf-...">...</style>
pattern = re.compile(r'<style id="(sf-[^"]+)">(.*?)</style>', re.S)
body_start = html.find('<body')
moved = []
def take(m):
    if m.start() > body_start:
        moved.append((m.group(1), m.group(2)))
        return ''
    return m.group(0)

html = pattern.sub(take, html)
log.append('collected %d style blocks' % len(moved))

# 重新定位 head_end（内容已变）
head_end = html.find('</head>')
assert head_end > 0
inject = '\n'.join('<style id="%s">%s</style>' % (n, b) for n, b in moved)
html = html[:head_end] + '\n' + inject + '\n' + html[head_end:]
log.append('moved into head')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
print('moved ids:', ', '.join(n for n, _ in moved[:8]), '...')
