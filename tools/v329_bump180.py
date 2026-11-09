
# -*- coding: utf-8 -*-
"""v329 - build 178 -> 180：城市建筑群（本阶段收尾）。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 178, 180

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
meta['updated_at'] = '2026-11-09T11:40:00+08:00'
meta['title'] = 'sand3d \\u57ce\\u5e02\\u5efa\\u7b51\\u7fa4'
meta['changelog'] = (
    '\\u7528 sand3d \\u5efa\\u57ce\\u5e02\\u5efa\\u7b51\\u7fa4\\uff1a\\u4e3b\\u5854 + \\u9521\\u841d\\u677f\\u697c + \\u5c16\\u9876\\u697c + '
    '\\u914d\\u697c + \\u7a7a\\u4e2d\\u8fde\\u5eca + \\u5929\\u7ebf\\uff0c\\u9ad8\\u4f4e\\u9519\\u843d\\u6709\\u7ed3\\u6784\\u5c42\\u6b21\\uff0c'
    '\\u4f5c\\u4e3a\\u53d1\\u8fbe\\u57ce\\u5e02\\u7684\\u5730\\u6807\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
