
# -*- coding: utf-8 -*-
"""v252 - build 161 -> 162。"""
import json
import sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 161, 162
log = []

html = HTML.read_text(encoding='utf-8', newline='')
for old, new, tag in [
    ('id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, OLD_B),
     'id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, NEW_B), 'tag'),
    ('const localBuild = %d;' % OLD_B, 'const localBuild = %d;' % NEW_B, 'localBuild'),
]:
    assert html.count(old) == 1, tag
    html = html.replace(old, new)
    log.append(tag)
HTML.write_text(html, encoding='utf-8', newline='')

sw = SW.read_text(encoding='utf-8', newline='')
old = "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, OLD_B)
assert sw.count(old) == 1
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, NEW_B))
SW.write_text(sw, encoding='utf-8', newline='')
log.append('CACHE_VERSION')

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-08T14:05:00+08:00'
meta['title'] = '\\u9996\\u5c4f\\u95ea\\u65e7\\u7248 / \\u9707\\u52a8\\u6536\\u655b / \\u5361\\u9762\\u6309\\u94ae\\u653e\\u5927'
meta['changelog'] = (
    '1. \\u4fee\\u590d\\u5f00\\u673a\\u77ac\\u95f4\\u95ea\\u51fa\\u6700\\u65e7\\u7248\\u754c\\u9762\\uff1a'
    '26 \\u4e2a\\u65b0\\u589e\\u6837\\u5f0f\\u5757\\u539f\\u672c\\u5728 <body> \\u4e4b\\u540e\\uff08@34MB\\uff09\\uff0c'
    '\\u6d4f\\u89c8\\u5668\\u5148\\u7528\\u6587\\u4ef6\\u5934\\u90e8\\u7684\\u65e7\\u6837\\u5f0f\\u6e32\\u67d3\\u4e00\\u904d\\u518d\\u91cd\\u7ed8\\uff1b'
    '\\u73b0\\u5df2\\u5168\\u90e8\\u642c\\u8fdb <head>\\uff1b'
    '2. \\u9707\\u52a8\\u6536\\u655b\\uff1a\\u641c\\u522e\\u53d6\\u6d88\\u9707\\u52a8\\uff08\\u9ad8\\u9891\\u52a8\\u4f5c\\uff09\\uff0c'
    '\\u5f39\\u5f13\\u6539 18ms \\u77ed\\u9707\\uff0c\\u53ea\\u6709\\u6fc0\\u6ce2\\u4fdd\\u7559\\u4e00\\u6b21\\u957f\\u9707\\uff1b'
    '3. \\u5361\\u9762\\u6309\\u94ae\\u653e\\u5927\\uff1a\\u9ad8\\u5ea6 34 -> 56px\\uff0c\\u5b57\\u53f7 8.5 -> 11px\\uff0c'
    '\\u4e3b\\u6309\\u94ae\\u52a0\\u8109\\u52a8\\u70b9\\uff1b'
    '4. \\u65b0\\u589e\\u5f15\\u5bfc\\u63d0\\u793a\\uff1a\\u300c\\u70b9\\u51fb\\u5361\\u9762\\u7ffb\\u9762 \\u00b7 '
    '\\u6216\\u7528\\u4e0b\\u65b9\\u4e09\\u4e2a\\u6309\\u94ae\\u300d\\uff1b'
    '5. \\u5f00\\u5361\\u5947\\u5f02\\u6838\\u4ece\\u84dd\\u7d2b\\u6539\\u767d\\u91d1\\uff0c\\u53bb\\u6389\\u70b9\\u51fb\\u65f6\\u7684\\u84dd\\u8272\\u95ea\\u5149\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
