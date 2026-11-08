# -*- coding: utf-8 -*-
"""v232 - build 157 -> 158"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 157, 158
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

TITLE = '\u89c6\u91ce\u6e05\u7406\uff1a\u79fb\u9664\u5f39\u5f13\u8f90\u5c04\u6d41\u5149\uff0c\u9884\u6d4b\u5f27\u7ebf\u6536\u655b'
CHANGELOG = (
    '1. \u79fb\u9664\u5f15\u529b\u5f39\u5f13\u6fc0\u6d3b\u65f6\u4ece\u5c4f\u5e55\u4e2d\u5fc3\u5411\u56db\u9762\u516b\u65b9\u8f90\u5c04\u7684 18 \u6761\u9752\u8272\u6d41\u5149'
    '\uff08\u906e\u6321\u89c6\u91ce\u4e14\u65e0\u4fe1\u606f\u91cf\uff0c\u901f\u5ea6\u611f\u6539\u7531\u661f\u5c18\u62d6\u5c3e\u627f\u62c5\uff09\uff1b'
    '2. \u5f39\u5f13\u9884\u6d4b\u5f27\u7ebf\u6536\u655b\uff1a\u7ebf\u5bbd 2.2 -> 1.1\u3001\u900f\u660e\u5ea6 0.72 -> 0.34\u3001'
    '\u5149\u6655 12 -> 5\uff0c\u4e0d\u518d\u62a2\u89c6\u91ce\u3002'
)

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-08T12:45:00+08:00'
meta['title'] = TITLE
meta['changelog'] = CHANGELOG
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))