
# -*- coding: utf-8 -*-
"""v321 - build 175 -> 176：sand3d 母舰模型接入。"""
import json, sys
from pathlib import Path
BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 175, 176

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
meta['updated_at'] = '2026-11-09T11:00:00+08:00'
meta['title'] = '\\u63a5\\u5165 sand3d\\uff1a\\u771f\\u5b9e\\u6bcd\\u8230\\u6a21\\u578b'
meta['changelog'] = (
    '\\u7528 sand3d\\uff08Blender\\uff09\\u5efa\\u9020\\u6bcd\\u8230\\u6a21\\u578b\\uff1a'
    '\\u68ad\\u5f62\\u8239\\u4f53 + \\u8230\\u6865 + \\u53cc\\u7ffc + \\u5c3e\\u7ffc + \\u53cc\\u5f15\\u64ce\\uff0c'
    '\\u5bfc\\u51fa GLB \\u540e base64 \\u5185\\u5d4c\\uff0cGLTFLoader.parse \\u52a0\\u8f7d\\u5230\\u6bcd\\u8230\\u8239\\u575e\\u5730\\u8868\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d' % NEW_B)
