
# -*- coding: utf-8 -*-
"""v284 - build 167 -> 168：平滑下降过渡。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 167, 168

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
meta['updated_at'] = '2026-11-09T01:25:00+08:00'
meta['title'] = '\\u8fdb\\u5165\\u661f\\u7403\\u7684\\u5e73\\u6ed1\\u4e0b\\u964d\\u8fc7\\u6e21'
meta['changelog'] = (
    '\\u8fdb\\u5165\\u5730\\u8868\\u65f6\\u76f8\\u673a\\u4ece\\u9ad8\\u7a7a 60 \\u7f13\\u964d\\u5230 9\\uff08ease-out 2.4 \\u79d2\\uff09\\uff0c'
    '\\u914d\\u5408 UI \\u6de1\\u5165\\uff0c\\u4e0d\\u518d\\u786c\\u5207\\uff1b'
    '\\u9000\\u51fa\\u6de1\\u51fa\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
