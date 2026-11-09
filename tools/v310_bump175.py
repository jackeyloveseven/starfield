
# -*- coding: utf-8 -*-
"""v310 - build 174 -> 175：引力透镜。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 174, 175

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
meta['updated_at'] = '2026-11-09T10:50:00+08:00'
meta['title'] = '\\u5f15\\u529b\\u900f\\u955c'
meta['changelog'] = (
    '\\u9ed1\\u6d1e\\u5468\\u56f4\\u52a0\\u5165\\u5f15\\u529b\\u900f\\u955c\\u6548\\u679c\\uff1a'
    '\\u4e8b\\u4ef6\\u89c6\\u754c\\u7eaf\\u9ed1\\u3001\\u4e09\\u91cd\\u5149\\u5b50\\u73af\\u3001'
    '\\u88ab\\u5f15\\u529b\\u62d6\\u62fd\\u7684\\u87ba\\u65cb\\u661f\\u5149\\u3002'
    '\\u900f\\u660e\\u5ea6\\u538b\\u4f4e\\u4e0d\\u906e\\u6321\\u89c6\\u91ce\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
