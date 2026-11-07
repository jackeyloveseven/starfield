
# -*- coding: utf-8 -*-
"""v177 — 撤回全局 border-style，改为精准只改 .settings-section 内直系行的虚线。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""/* 抽屉内不再出现虚线 */
#settings-drawer *{border-style:solid !important}""")
new = N("""/* 只把设置行下方的虚线换成极淡实线（不能全局改 border-style，会把所有元素的边框激活） */
#settings-drawer .settings-section > div,
#settings-drawer .shortcut-row{
  border-bottom-style:solid !important;
  border-bottom-color:rgba(230,237,242,.07) !important;
}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('reverted global border-style')
