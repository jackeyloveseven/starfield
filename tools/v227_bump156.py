
# -*- coding: utf-8 -*-
"""v227 — build 155 -> 156：星球噪声地貌 + 全站入场动效。"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 155, 156
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
meta['updated_at'] = '2026-11-08T11:45:00+08:00'
meta['title'] = '\u661f\u7403\u5730\u8c8c\u4e0e\u5168\u7ad9\u52a8\u6548\u5347\u7ea7\uff1a\u53cc\u9891\u566a\u58f0\u56db\u6863\u5730\u8c8c\u3001\u5927\u6c14\u8f89\u5149\u4e0e\u5206\u5c42\u5165\u573a'
meta['changelog'] = (
    '1. \u5f00\u5361\u661f\u7403\u6539\u53cc\u9891\u566a\u58f0\u5730\u8c8c\uff08\u6d77\u6d0b / \u6d45\u6ee9 / \u9646\u5730 / \u9ad8\u5730\u56db\u6863\uff09\uff0c'
    '\u5cb8\u7ebf\u6709\u788e\u5f62\uff0c\u4e0d\u518d\u662f\u7403\u51a0\u5706\u6591\uff1b'
    '2. \u52a0\u5927\u6c14\u8f89\u5149\u4e0e\u6668\u660f\u7ebf\u4eae\u5e26\uff0c\u81ea\u8f6c\u63d0\u5230 6 \u79d2\u4e00\u5708\uff1b'
    '3. \u5929\u8c61\u9986\u5217\u8868 / \u56fe\u9274 / \u6298\u7eb8\u575e / \u8bbe\u7f6e\u62bd\u5c49\u8865\u507f\u5206\u5c42\u5165\u573a\u52a8\u6548'
    '\uff08\u4e0a\u4e00\u7248\u7684 animation:none \u628a\u5165\u573a\u4e5f\u538b\u6389\u4e86\uff09\uff1b'
    '4. \u5f00\u5361\u9875\u52a0\u8f7d\u5b8c\u6210\u540e\u81ea\u8f6c\u4e0d\u518d\u50cf\u9759\u6b62\u56fe\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
