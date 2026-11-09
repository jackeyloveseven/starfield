
# -*- coding: utf-8 -*-
"""v327 - build 178 -> 179：星灵浮空 + 能量连接。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 178, 179

html = HTML.read_text(encoding='utf-8', newline='')
for old, new in [
    ('id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, OLD_B),
     'id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, NEW_B)),
    ('const localBuild = %d;' % OLD_B, 'const localBuild = %d;' % NEW_B),
]:
    assert html.count(old) == 1
    html = html.replace(old, new)
HTML.write_text(html, encoding='utf-8', newline='')

sw = SW.read_text(encoding='utf-8', newline='')
old = "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, OLD_B)
assert sw.count(old) == 1
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, NEW_B))
SW.write_text(sw, encoding='utf-8', newline='')

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-09T11:30:00+08:00'
meta['title'] = '\\u661f\\u7075\\u60ac\\u6d6e\\u6c34\\u6676\\u4e0e\\u80fd\\u91cf\\u8fde\\u63a5'
meta['changelog'] = (
    '\\u661f\\u7075\\u6c34\\u6676\\u7c07\\u6539\\u4e3a\\u60ac\\u6d6e\\uff08\\u6b63\\u5f26\\u4e0a\\u4e0b\\u6d6e\\u52a8\\uff09\\uff0c'
    '\\u4e3b\\u6676\\u4e0e\\u5468\\u56f4\\u4e09\\u4e2a\\u60ac\\u6d6e\\u8282\\u70b9\\u4e4b\\u95f4\\u62c9\\u9752\\u8272\\u80fd\\u91cf\\u5149\\u675f\\uff0c'
    '\\u5149\\u675f\\u968f\\u547c\\u5438\\u660e\\u6697\\u3002\\u6bd4\\u7acb\\u5728\\u5730\\u4e0a\\u66f4\\u50cf\\u661f\\u7075\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
