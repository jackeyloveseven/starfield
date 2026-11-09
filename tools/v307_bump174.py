
# -*- coding: utf-8 -*-
"""v307 - build 173 -> 174：地表随时间生长。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 173, 174

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
meta['updated_at'] = '2026-11-09T10:35:00+08:00'
meta['title'] = '\\u5730\\u8868\\u4e5f\\u968f\\u65f6\\u95f4\\u751f\\u957f'
meta['changelog'] = (
    '\\u8001\\u661f\\u7403\\u7684\\u5730\\u8868\\u66f4\\u8302\\u5bc6\\uff0c\\u9ad8\\u5efa\\u8bbe\\u5ea6\\u7684\\u661f\\u7403\\u66f4\\u7e41\\u534e\\uff1a'
    '\\u6309\\u6f14\\u5316\\u5929\\u6570\\u52a0\\u690d\\u88ab\\u3001\\u6309\\u5efa\\u8bbe\\u9636\\u6bb5\\u52a0\\u5efa\\u7b51\\uff1b'
    '\\u5730\\u8868 UI \\u663e\\u793a\\u5efa\\u8bbe\\u9636\\u6bb5\\u3002\\u6f14\\u5316\\u4e0e\\u5efa\\u8bbe\\u4ece\\u5361\\u7247\\u5ef6\\u4f38\\u5230\\u5b9e\\u666f\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
