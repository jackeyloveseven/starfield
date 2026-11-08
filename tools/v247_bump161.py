
# -*- coding: utf-8 -*-
"""v247 - build 160 -> 161：物理材质 + 环境贴图 + 描边。"""
import json
import sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 160, 161
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
meta['updated_at'] = '2026-11-08T13:55:00+08:00'
meta['title'] = '\\u661f\\u7403\\u8d28\\u611f\\u5347\\u7ea7\\uff1a\\u7269\\u7406\\u6750\\u8d28 + \\u73af\\u5883\\u8d34\\u56fe + \\u5361\\u901a\\u63cf\\u8fb9'
meta['changelog'] = (
    '1. \\u661f\\u7403\\u6750\\u8d28\\u4ece MeshStandardMaterial \\u5347\\u4e3a MeshPhysicalMaterial\\uff0c'
    '\\u52a0 clearcoat\\uff08\\u8868\\u9762\\u6e05\\u6f06\\uff09\\u4e0e iridescence\\uff08\\u5f69\\u8679\\u819c\\uff0c\\u795e\\u8bdd\\u6863\\u4e13\\u5c5e\\uff09\\uff1b'
    '2. \\u65b0\\u589e\\u7a0b\\u5e8f\\u5316\\u73af\\u5883\\u8d34\\u56fe\\uff08PMREMGenerator\\uff09\\uff0c'
    '\\u4e4b\\u524d\\u53ea\\u6709\\u4e09\\u4e2a\\u5e73\\u884c\\u5149\\u6240\\u4ee5\\u6750\\u8d28\\u5f88\\u5e73\\uff1b'
    '3. \\u65b0\\u589e\\u5361\\u901a\\u63cf\\u8fb9\\uff1a\\u6cbf\\u6cd5\\u7ebf\\u5916\\u6269\\u7684\\u80cc\\u9762\\u58f3\\u5c42\\uff0c'
    '\\u4e94\\u6863\\u63cf\\u8fb9\\u8272\\u4e0e\\u5bbd\\u5ea6\\u8ddf\\u54c1\\u9636\\u8d70\\uff1b'
    '4. \\u63d0\\u9ad8\\u96ea\\u7ebf\\u3001\\u538b\\u4f4e\\u4e91\\u5c42\\u900f\\u660e\\u5ea6\\u4e0e\\u73af\\u5883\\u5149\\u5f3a\\u5ea6\\uff0c'
    '\\u907f\\u514d\\u6574\\u9897\\u661f\\u7403\\u53d1\\u767d\\uff1b'
    '5. \\u53e4\\u795e\\u9057\\u8ff9\\u9884\\u8bbe\\u914d\\u8272\\u52a0\\u6df1\\uff08\\u539f\\u6765\\u5168\\u662f\\u6d45\\u8272\\uff0c\\u770b\\u4e0d\\u51fa\\u5c42\\u6b21\\uff09\\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
