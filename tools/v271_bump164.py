
# -*- coding: utf-8 -*-
"""v271 - build 163 -> 164：形态系统 + 路过景观。"""
import json, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 163, 164
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
meta['updated_at'] = '2026-11-09T00:30:00+08:00'
meta['title'] = '\\u5341\\u79cd\\u661f\\u7403\\u5f62\\u6001 + \\u8def\\u8fc7\\u666f\\u89c2'
meta['changelog'] = (
    '1. \\u62bd\\u5361\\u661f\\u7403\\u63a5\\u5165\\u6e38\\u620f\\u5185\\u5df2\\u6709\\u7684 10 \\u79cd\\u5f62\\u6001'
    '\\uff08\\u6c34\\u4e16\\u754c/\\u6c34\\u6676/\\u83cc\\u6bef/\\u90fd\\u5e02/\\u6c99\\u4e18/\\u64d5\\u88c2/\\u96f7\\u66b4/\\u865a\\u7a7a\\u7b49\\uff09\\uff0c'
    '\\u5f62\\u6001\\u72ec\\u7acb\\u4e8e\\u54c1\\u9636\\uff0c\\u4e0d\\u518d\\u53ea\\u662f\\u6362\\u8272\\uff1b'
    '2. \\u65b0\\u589e\\u8def\\u8fc7\\u666f\\u89c2\\uff1a\\u5f57\\u661f\\uff08\\u53cc\\u8272\\u5c3e\\uff09\\u3001'
    '\\u6697\\u661f\\u4e91\\uff08\\u906e\\u80cc\\u666f\\u661f\\u5149\\u7684\\u526a\\u5f71\\uff09\\u3001\\u884c\\u661f\\u72b6\\u661f\\u4e91\\uff08\\u58f3\\u5c42\\u73af+\\u4e2d\\u5fc3\\u4eae\\u661f\\uff09\\uff0c'
    '\\u7eaf\\u89c6\\u89c9\\u4e0d\\u53ef\\u4ea4\\u4e92\\uff0c\\u4e2d\\u592e\\u822a\\u9053\\u4e0d\\u753b\\uff1b'
    '3. \\u5929\\u8c61\\u4e8b\\u4ef6\\u5bc6\\u5ea6\\u63d0\\u9ad8 40 \\u500d\\uff08\\u539f\\u6765\\u7ea6 2 \\u5c0f\\u65f6\\u624d\\u6709\\u4e00\\u6b21\\uff09\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
