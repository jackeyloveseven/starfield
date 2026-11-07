
# -*- coding: utf-8 -*-
"""v221 — build 154 -> 155（修复版），四处同步。"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 154, 155
log = []

with open(HTML, 'r', encoding='utf-8', newline='') as f:
    html = f.read()
for old, new, tag in [
    ('id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, OLD_B),
     'id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, NEW_B), 'tag'),
    ('const localBuild = %d;' % OLD_B, 'const localBuild = %d;' % NEW_B, 'localBuild'),
]:
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(html)

with open(SW, 'r', encoding='utf-8', newline='') as f:
    sw = f.read()
old = "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, OLD_B)
assert sw.count(old) == 1
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, NEW_B))
with open(SW, 'w', encoding='utf-8', newline='') as f:
    f.write(sw)
log.append('CACHE_VERSION')

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-08T01:10:00+08:00'
meta['changelog'] = (
    '\u4fee\u590d\uff1a\u624b\u673a\u7aef\u5361\u5728\u8d77\u822a\u9875\u65e0\u6cd5\u8fdb\u5165\u3002'
    '\u4e0a\u4e00\u7248\u7ed9\u8d22\u7eb8\u575e\u52a0\u4e86 opacity:1 !important\uff0c'
    '\u628a\u5173\u95ed\u6001\u7684 opacity:0 \u4e5f\u8986\u76d6\u4e86\uff0c'
    '\u8d22\u7eb8\u575e\u4ece\u52a0\u8f7d\u8d77\u5c31\u5168\u5c4f\u76d6\u5728\u6700\u4e0a\u5c42\uff08z-index:9999\uff09\uff0c'
    '\u8d77\u822a\u9875\u6240\u6709\u70b9\u51fb\u90fd\u843d\u5728\u5b83\u4e0a\u9762\u3002'
    '\u540c\u65f6\u628a\u8d77\u822a\u9875\u538b\u6697\u5c42\u4ece ::after \u79fb\u5230 ::before\uff0c'
    '\u907f\u514d\u4f2a\u5143\u7d20\u5728 iOS Safari \u4e0a\u5076\u53d1\u963b\u6321\u89e6\u6478\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
