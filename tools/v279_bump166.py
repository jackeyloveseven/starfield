
# -*- coding: utf-8 -*-
"""v279 - build 165 -> 166：拖拽转向 + 前往此星入口。"""
import json, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 165, 166
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
meta['updated_at'] = '2026-11-09T01:05:00+08:00'
meta['title'] = '\\u5730\\u8868\\u62d6\\u62fd\\u8f6c\\u5411 + \\u5361\\u9762\\u76f4\\u8fbe'
meta['changelog'] = (
    '1. \\u5730\\u8868\\u98de\\u884c\\u652f\\u6301\\u62d6\\u62fd\\u8f6c\\u5411\\uff1a\\u6a2a\\u5411\\u6539\\u7ecf\\u5ea6\\u3001\\u7eb5\\u5411\\u6539\\u7eac\\u5ea6\\uff0c'
    '\\u677e\\u624b\\u7ee7\\u7eed\\u81ea\\u52a8\\u524d\\u8fdb\\uff1b'
    '2. \\u5361\\u9762\\u65b0\\u589e\\u300c\\u524d\\u5f80\\u6b64\\u661f\\u300d\\u6309\\u94ae\\uff1a'
    '\\u4ece\\u6536\\u85cf\\u76f4\\u63a5\\u8fdb\\u5165\\u8be5\\u661f\\u5730\\u8868\\uff0c\\u4e0d\\u5fc5\\u5148\\u5de1\\u822a\\u9760\\u8fd1\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
