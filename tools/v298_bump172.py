
# -*- coding: utf-8 -*-
"""v298 - build 171 -> 172：渐进式揭示。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 171, 172

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
meta['updated_at'] = '2026-11-09T10:05:00+08:00'
meta['title'] = '\\u6e10\\u8fdb\\u5f0f\\u63ed\\u793a\\uff1a\\u9760\\u8fd1\\u624d\\u80fd\\u8bc6\\u522b'
meta['changelog'] = (
    '\\u56fe\\u9274\\u4e0d\\u518d\\u300c\\u8def\\u8fc7\\u5c31\\u81ea\\u52a8\\u89e3\\u9501\\u300d\\uff1a'
    '\\u53ea\\u6709\\u9760\\u8fd1\\u5230\\u8db3\\u591f\\u8fd1\\u3001\\u771f\\u6b63\\u770b\\u6e05\\u7684\\u5929\\u4f53\\u624d\\u4f1a\\u88ab\\u8bb0\\u5f55\\u4e3a\\u5df2\\u53d1\\u73b0\\u3002'
    '\\u8fdc\\u5904\\u63a0\\u8fc7\\u4e0d\\u7b97\\u6570\\uff0c\\u63a2\\u7d22\\u624d\\u6709\\u610f\\u4e49\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
