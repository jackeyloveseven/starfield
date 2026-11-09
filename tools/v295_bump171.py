
# -*- coding: utf-8 -*-
"""v295 - build 170 -> 171：声音签名。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 170, 171

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
meta['updated_at'] = '2026-11-09T09:50:00+08:00'
meta['title'] = '\\u58f0\\u97f3\\u7b7e\\u540d\\uff1a\\u6bcf\\u9897\\u661f\\u7403\\u81ea\\u5df1\\u7684\\u5e95\\u566a'
meta['changelog'] = (
    '\\u6bcf\\u79cd\\u661f\\u7403\\u5f62\\u6001\\u4e00\\u79cd\\u5e95\\u566a\\uff1a'
    '\\u6c34\\u4e16\\u754c\\u662f\\u6d41\\u52a8\\u3001\\u90fd\\u5e02\\u662f\\u4f4e\\u9891\\u55e1\\u9e23\\u3001'
    '\\u6c34\\u6676\\u662f\\u6cdb\\u97f3\\u5171\\u9e23\\u3001\\u83cc\\u6bef\\u50cf\\u547c\\u5438\\u3001\\u865a\\u7a7a\\u8fd1\\u4e4e\\u9759\\u97f3\\u3002'
    '\\u5168\\u90e8 Web Audio \\u5408\\u6210\\uff0c\\u4e0d\\u52a0\\u8f7d\\u4efb\\u4f55\\u97f3\\u9891\\u6587\\u4ef6\\uff1b'
    '\\u5f00\\u5361\\u4e0e\\u8fdb\\u5165\\u5730\\u8868\\u65f6\\u6de1\\u5165\\u64ad\\u653e\\uff0c\\u79bb\\u5f00\\u505c\\u6b62\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
