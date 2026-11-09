
# -*- coding: utf-8 -*-
"""v290 - build 168 -> 169：星球演化。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 168, 169

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
meta['updated_at'] = '2026-11-09T09:20:00+08:00'
meta['title'] = '\\u661f\\u7403\\u4f1a\\u7b49\\u4f60\\u56de\\u6765'
meta['changelog'] = (
    '\\u6536\\u85cf\\u7684\\u661f\\u7403\\u968f\\u73b0\\u5b9e\\u65f6\\u95f4\\u7f13\\u6162\\u6f14\\u5316\\uff1a'
    '\\u81ea\\u8f6c\\u4e0e\\u536b\\u661f\\u76f8\\u4f4d\\u968f\\u5c0f\\u65f6\\u6570\\u504f\\u79fb\\u3001'
    '\\u57ce\\u5e02\\u5149\\u70b9\\u968f\\u5929\\u6570\\u589e\\u591a\\uff08\\u6709\\u4e0a\\u9650\\uff09\\uff1b'
    '\\u5361\\u9762\\u65b0\\u589e\\u6f14\\u5316\\u6ce8\\u8bb0\\uff0c\\u663e\\u793a\\u300cN \\u5929\\u524d\\u70b9\\u4eae\\u300d\\u4e0e\\u53d8\\u5316\\u3002'
    '\\u6240\\u6709\\u53d8\\u5316\\u90fd\\u662f\\u65f6\\u95f4\\u7684\\u786e\\u5b9a\\u51fd\\u6570\\uff0c\\u540c\\u4e00\\u65f6\\u523b\\u6253\\u5f00\\u5c31\\u662f\\u540c\\u4e00\\u526f\\u6837\\u5b50\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
