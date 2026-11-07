
# -*- coding: utf-8 -*-
"""v156b — 含中文的元素改中文优先族（含短族串形式）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()

SHORT = '"SFMono-Regular",Consolas,monospace'
LONG = '"SFMono-Regular",Consolas,"Liberation Mono","PingFang SC","Microsoft YaHei","Noto Sans CJK SC",monospace'
CJK = '"PingFang SC","Microsoft YaHei","Noto Sans CJK SC","SFMono-Regular",Consolas,monospace'

start = src.find('<style id="sf-hatch-flat-css">')
end = src.find('</style>', start)
assert start >= 0 and end > start
block = src[start:end]

TARGETS = [
    '.sf-card-act-btn',
    '.sf-hatch-close',
    '.sf-hatch-meta',
    '.sf-hb-name-btn',
    '.sf-hb-name-input',
    '.sf-foil',
]

log = []
for sel in TARGETS:
    needle = sel + '{'
    hits = 0
    pos = block.find(needle)
    while pos >= 0:
        e = block.find('}', pos)
        chunk = block[pos:e]
        new = chunk.replace(LONG, CJK).replace(SHORT, CJK)
        if new != chunk:
            block = block[:pos] + new + block[e:]
            hits += 1
            e = pos + len(new)
        pos = block.find(needle, e)
    log.append(sel + ' blocks=' + str(hits))

src = src[:start] + block + src[end:]
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('CJK count in block =', block.count(CJK))
