
# -*- coding: utf-8 -*-
"""v292 - build 169 -> 170：天象馆相对时间 + 植被生长。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 169, 170

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
meta['updated_at'] = '2026-11-09T09:35:00+08:00'
meta['title'] = '\\u5929\\u8c61\\u9986\\u76f8\\u5bf9\\u65f6\\u95f4\\u4e0e\\u690d\\u88ab\\u751f\\u957f'
meta['changelog'] = (
    '\\u5929\\u8c61\\u9986\\u5217\\u8868\\u4ece\\u7edd\\u5bf9\\u65e5\\u671f\\u6539\\u4e3a\\u76f8\\u5bf9\\u65f6\\u95f4'
    '\\uff08N \\u5929\\u524d\\uff09\\uff1b\\u690d\\u88ab\\u4e5f\\u968f\\u5929\\u6570\\u7f13\\u6162\\u751f\\u957f\\uff08\\u6709\\u4e0a\\u9650\\uff09\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
