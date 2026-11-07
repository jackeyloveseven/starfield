
# -*- coding: utf-8 -*-
"""v155 — 修正 sf-hatch-flat 内的中文字体回退顺序（monospace 通用族会截断回退链）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

open_tag = N('<style id="sf-hatch-flat-css">')
close_tag = N('</style>')
start = src.find(open_tag)
assert start >= 0
end = src.find(close_tag, start)
assert end >= 0
block = src[start:end]

old_a = '"SFMono-Regular",Consolas,"Liberation Mono",monospace'
new_a = '"SFMono-Regular",Consolas,"Liberation Mono","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",monospace'
old_b = '"SFMono-Regular",Consolas,"Liberation Mono",monospace,"PingFang SC","Microsoft YaHei",sans-serif'
n_a = block.count(old_a)
n_b = block.count(old_b)
block = block.replace(old_b, new_a).replace(old_a, new_a)
log = ['mono fallback: plain=' + str(n_a) + ' with-sans=' + str(n_b)]

grid_old = N("""    linear-gradient(rgba(255,255,255,.038) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.038) 1px,transparent 1px);""")
grid_new = N("""    linear-gradient(rgba(255,255,255,.030) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.030) 1px,transparent 1px);""")
assert block.count(grid_old) == 1
block = block.replace(grid_old, grid_new)
log.append('grid alpha .030')

src = src[:start] + block + src[end:]
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
