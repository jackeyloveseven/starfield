
# -*- coding: utf-8 -*-
"""v323 - build 176 -> 177：sand3d 水晶簇。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 176, 177

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
meta['updated_at'] = '2026-11-09T11:10:00+08:00'
meta['title'] = 'sand3d \\u661f\\u7075\\u6c34\\u6676\\u7c07'
meta['changelog'] = (
    '\\u7528 sand3d \\u5efa\\u661f\\u7075\\u6298\\u5149\\u6c34\\u6676\\u7c07\\uff1a'
    '\\u4e09\\u6839\\u516d\\u68f1\\u6676\\u4f53\\uff08\\u9876\\u90e8\\u6536\\u7a84\\u6210\\u6676\\u5c16\\uff09\\uff0c'
    '\\u9752\\u84dd\\u6298\\u5149\\u534a\\u900f\\u660e\\u81ea\\u53d1\\u5149\\uff0c'
    '\\u4f5c\\u4e3a\\u672a\\u6765\\u79d1\\u6280\\u661f\\u7403\\u7684\\u5730\\u6807\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
