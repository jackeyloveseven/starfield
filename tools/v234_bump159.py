# -*- coding: utf-8 -*-
"""v234 - build 158 -> 159"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 158, 159
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
meta['updated_at'] = '2026-11-08T13:10:00+08:00'
meta['title'] = '\u4fee\u590d\u8bbe\u7f6e\u91cc\u7248\u672c\u53f7\u663e\u793a\u9519\u8bef'
meta['changelog'] = (
    '\u4fee\u590d\uff1a\u65e0\u539f\u751f\u6865\u65f6\uff08\u6d4f\u89c8\u5668 / PWA\uff09\uff0c'
    '\u8bbe\u7f6e\u91cc\u7684\u5ba2\u6237\u7aef\u7248\u672c\u53f7\u4e00\u76f4\u663e\u793a v1.19.1 (Build 153)\u3002'
    '\u90a3\u662f\u4e00\u4e2a\u786c\u7f16\u7801\u7684\u515c\u5e95\u503c\uff0c\u8986\u76d6\u4e86 HTML \u91cc\u7684\u6b63\u786e\u7248\u672c\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))