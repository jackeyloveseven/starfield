
# -*- coding: utf-8 -*-
"""v282 - build 166 -> 167。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 166, 167

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
meta['updated_at'] = '2026-11-09T01:15:00+08:00'
meta['title'] = '\\u6c34\\u4e16\\u754c\\u6d77\\u9762\\u4e0e\\u6bcd\\u8230\\u8239\\u575e'
meta['changelog'] = (
    '1. \\u6c34\\u4e16\\u754c\\u5730\\u8868\\uff1a\\u9646\\u5730\\u6bd4\\u4f8b\\u964d\\u5230 14%\\uff0c'
    '\\u6d77\\u9762\\u6b63\\u5f26\\u6ce2\\u52a8\\u52a8\\u753b + \\u9ad8\\u53cd\\u5c04\\u6ce2\\u5149\\uff1b'
    '2. \\u6bcd\\u8230\\u8239\\u575e\\uff1a\\u4e00\\u6392\\u95e8\\u578b\\u6846\\u67b6\\uff08\\u53cc\\u7acb\\u67f1 + \\u9876\\u6881 + \\u6307\\u793a\\u706f\\uff09\\uff0c'
    '\\u5de5\\u4e1a\\u8bbe\\u65bd\\u800c\\u975e\\u81ea\\u7136\\u5730\\u8c8c\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
