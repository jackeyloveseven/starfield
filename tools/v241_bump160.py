
# -*- coding: utf-8 -*-
"""v241 - build 159 -> 160：three.js 星球。"""
import json
import sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 159, 160
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
meta['updated_at'] = '2026-11-08T13:40:00+08:00'
meta['title'] = '\\u661f\\u7403\\u6539 three.js \\u5efa\\u6a21\\uff0c\\u4e94\\u6863\\u54c1\\u9636\\u8d28\\u611f\\u62c9\\u5f00'
meta['changelog'] = (
    '1. \\u5f00\\u5361\\u661f\\u7403\\u4ece\\u624b\\u5199 WebGL shader \\u6539\\u4e3a three.js \\u5efa\\u6a21\\uff0c'
    '\\u590d\\u7528 planet_studio.html \\u7684 LivingPlanet\\uff1a'
    '\\u9876\\u70b9\\u7740\\u8272\\u5730\\u5f62\\u3001\\u6d77\\u6d0b\\u58f3\\u3001\\u4e91\\u5c42\\u3001Fresnel \\u5927\\u6c14\\u3001'
    '\\u5b9e\\u4f8b\\u5316\\u690d\\u88ab\\u3001\\u5de8\\u6784\\u4e0e\\u98de\\u9e1f\\u9cb8\\u9c7c\\uff1b'
    '2. \\u4e94\\u6863\\u54c1\\u9636\\u5728\\u5730\\u8c8c\\u7ec4\\u5408\\u4e0a\\u62c9\\u5f00\\uff1a'
    '\\u666e\\u901a\\u9752\\u84dd\\u6d77\\u6d0b\\u3001\\u7a00\\u6709\\u91d1\\u6a59\\u6c99\\u4e18\\u3001\\u53f2\\u8bd7\\u7fe0\\u7eff\\u6797\\u6d77\\u3001'
    '\\u4f20\\u8bf4\\u53cc\\u73af\\u9057\\u8ff9\\u3001\\u795e\\u8bdd\\u7d2b\\u7c89\\u5f02\\u661f\\uff1b'
    '3. \\u5149\\u73af\\u6539\\u7ec6\\u4eae\\u7ebf\\uff08AdditiveBlending\\uff09\\uff0c\\u5361\\u724c\\u4e0a\\u4e0d\\u518d\\u662f\\u7070\\u76d8\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
