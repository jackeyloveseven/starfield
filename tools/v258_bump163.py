
# -*- coding: utf-8 -*-
"""v258 - build 162 -> 163。"""
import json
import sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 162, 163
log = []

html = HTML.read_text(encoding='utf-8', newline='')
for old, new, tag in [
    ('id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, OLD_B),
     'id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, NEW_B), 'tag'),
    ('const localBuild = %d;' % OLD_B, 'const localBuild = %d;' % NEW_B, 'localBuild'),
]:
    assert html.count(old) == 1, tag
    html = html.replace(old, new)
    log.append(tag)
HTML.write_text(html, encoding='utf-8', newline='')

sw = SW.read_text(encoding='utf-8', newline='')
old = "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, OLD_B)
assert sw.count(old) == 1
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, NEW_B))
SW.write_text(sw, encoding='utf-8', newline='')
log.append('CACHE_VERSION')

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-08T14:20:00+08:00'
meta['title'] = '\\u5361\\u9762\\u5e95\\u90e8\\u91cd\\u6784'
meta['changelog'] = (
    '1. \\u64cd\\u4f5c\\u680f\\u4ece\\u300c\\u5e26\\u4e0a\\u4e0b\\u8fb9\\u6846\\u7684\\u534a\\u900f\\u660e\\u677f\\u300d'
    '\\u6539\\u6210\\u8d34\\u7740\\u753b\\u9762\\u5e95\\u90e8\\u7684\\u4e09\\u6bb5\\u6587\\u5b57\\uff0c'
    '\\u80cc\\u666f\\u6539\\u4e3a\\u5411\\u4e0a\\u6e10\\u9690\\u7684\\u9ed1\\uff1b'
    '2. \\u5f15\\u5bfc\\u6587\\u5b57\\u4ece fixed \\u6539\\u4e3a\\u6d41\\u5f0f\\uff0c\\u7d27\\u8ddf\\u89c4\\u683c\\u884c\\u4e4b\\u540e\\uff0c'
    '\\u4e0d\\u518d\\u538b\\u5728\\u6587\\u5b57\\u4e0a\\uff1b'
    '3. \\u300c\\u6536\\u5165\\u5929\\u8c61\\u9986\\u300d\\u5173\\u95ed\\u952e\\u4ece\\u64cd\\u4f5c\\u680f\\u91cc\\u62bd\\u51fa\\uff0c'
    '\\u79fb\\u5230\\u64cd\\u4f5c\\u680f\\u6b63\\u4e0a\\u65b9\\uff0c\\u4e0d\\u518d\\u88ab\\u5207\\u534a\\uff1b'
    '4. \\u4e09\\u6bb5\\u4e4b\\u95f4\\u7684\\u5206\\u9694\\u7ebf\\u4ece\\u8d2f\\u7a7f\\u6574\\u680f\\u6539\\u6210 18px \\u77ed\\u7ebf\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
