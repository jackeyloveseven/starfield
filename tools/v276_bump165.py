
# -*- coding: utf-8 -*-
"""v276 - build 164 -> 165：地表飞行模式。"""
import json, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 164, 165
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
meta['updated_at'] = '2026-11-09T00:50:00+08:00'
meta['title'] = '\\u65b0\\u6a21\\u5f0f\\uff1a\\u8fdb\\u5165\\u661f\\u7403\\u8868\\u9762\\u98de\\u884c'
meta['changelog'] = (
    '1. \\u65b0\\u589e\\u5730\\u8868\\u98de\\u884c\\u6a21\\u5f0f\\uff1a\\u9760\\u8fd1\\u884c\\u661f\\u65f6\\u6309 L \\u4e0b\\u964d\\u5230\\u4f4e\\u7a7a\\uff0c'
    '\\u8d34\\u7740\\u5730\\u8868\\u98de\\u884c\\uff1bESC / L \\u8fd4\\u56de\\u592a\\u7a7a\\uff1b'
    '2. \\u5730\\u8868\\u73af\\u5883\\u4e0e\\u661f\\u7403\\u5f62\\u6001\\u7ed1\\u5b9a\\uff1a'
    '\\u7c7b\\u5730\\u6587\\u660e / \\u53d1\\u8fbe\\u57ce\\u5e02 / \\u672a\\u6765\\u79d1\\u6280 / \\u539f\\u59cb\\u6709\\u673a / '
    '\\u8352\\u6f20 / \\u707e\\u53d8\\u5e9f\\u589f / \\u5e7d\\u51a5\\u865a\\u7a7a\\u7b49\\uff0c'
    '\\u5efa\\u7b51\\u79cd\\u7c7b\\u4e0e\\u68f1\\u88ab\\u5bc6\\u5ea6\\u968f\\u6587\\u660e\\u7b49\\u7ea7\\u53d8\\u5316\\uff1b'
    '3. \\u590d\\u7528 three.js LivingPlanet \\u5730\\u5f62\\u4e0e\\u690d\\u88ab\\uff0c'
    '\\u5efa\\u7b51\\u843d\\u5728\\u771f\\u5b9e\\u5730\\u5f62\\u9876\\u70b9\\u4e0a\\uff1b'
    '4. \\u8fdb\\u5165\\u5730\\u8868\\u65f6\\u5de1\\u822a\\u6682\\u505c\\uff0c\\u9000\\u51fa\\u6062\\u590d\\uff0c\\u4e0d\\u5f71\\u54cd\\u539f\\u6709\\u73a9\\u6cd5\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
