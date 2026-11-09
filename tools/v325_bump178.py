
# -*- coding: utf-8 -*-
"""v325 - build 177 -> 178：sand3d 遗迹巨构。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 177, 178

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
meta['updated_at'] = '2026-11-09T11:20:00+08:00'
meta['title'] = 'sand3d \\u65ad\\u88c2\\u7eaa\\u5ff5\\u7891\\u9057\\u8ff9'
meta['changelog'] = (
    '\\u7528 sand3d \\u5efa\\u65ad\\u88c2\\u65b9\\u5c16\\u7891\\uff1a\\u5bbd\\u5927\\u57fa\\u5ea7 + \\u4e0b\\u67f1 + '
    '\\u6298\\u65ad\\u9519\\u5f00\\u7684\\u4e0a\\u67f1 + \\u65ad\\u53e3\\u788e\\u5757 + \\u5468\\u56f4\\u788e\\u77f3\\uff0c'
    '\\u4f5c\\u4e3a\\u707e\\u53d8\\u5e9f\\u589f\\u7684\\u9057\\u8ff9\\u5730\\u6807\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
