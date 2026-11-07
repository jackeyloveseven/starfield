
# -*- coding: utf-8 -*-
"""bump v1.19.1 (Build 153) -> v1.9.9.9.9 (Build 154)，四处（含 OTA 比较常量）。"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML = BASE / 'starfield.html'
SW = BASE / 'service-worker.js'
VER = BASE / 'version.json'

OLD_VER, OLD_BUILD = '1.19.1', 153
NEW_VER, NEW_BUILD = '1.9.9.9.9', 154
log = []

with open(HTML, 'r', encoding='utf-8', newline='') as f:
    html = f.read()

# 1) 版本标签
old = 'id="sf-version-tag">v%s (Build %d)</span>' % (OLD_VER, OLD_BUILD)
assert html.count(old) == 1, 'version tag count=%d' % html.count(old)
html = html.replace(old, 'id="sf-version-tag">v%s (Build %d)</span>' % (NEW_VER, NEW_BUILD))
log.append('version tag')

# 2) OTA 比较常量
old = 'const localBuild = %d;' % OLD_BUILD
assert html.count(old) == 1, 'localBuild count=%d' % html.count(old)
html = html.replace(old, 'const localBuild = %d;' % NEW_BUILD)
log.append('localBuild 153 -> 154')

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(html)

# 3) service-worker CACHE_VERSION
with open(SW, 'r', encoding='utf-8', newline='') as f:
    sw = f.read()
old = "const CACHE_VERSION = 'v%s-b%d';" % (OLD_VER, OLD_BUILD)
assert sw.count(old) == 1, 'CACHE_VERSION count=%d' % sw.count(old)
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (NEW_VER, NEW_BUILD))
with open(SW, 'w', encoding='utf-8', newline='') as f:
    f.write(sw)
log.append('CACHE_VERSION')

# 4) version.json
meta = json.loads(VER.read_text(encoding='utf-8'))
meta['version'] = NEW_VER
meta['build'] = NEW_BUILD
meta['updated_at'] = '2026-11-08T00:15:00+08:00'
meta['title'] = '\u5168\u7ad9\u5185\u90e8\u754c\u9762\u91cd\u5236\uff1a\u53d1\u4e1d\u7ebf\u76f4\u89d2\u8bed\u8a00\u3001WebGL \u7eaf\u8272\u661f\u7403\u4e0e\u5371\u9669\u4f53\u7cfb'
meta['changelog'] = (
    '1. \u65b0\u589e\u5371\u9669\u4e0e\u635f\u4f24\uff1a\u788e\u7247\u5e26 / \u6052\u661f\u8000\u6591 / \u9ed1\u6d1e\u6f6e\u6c50\uff0c'
    '\u5171\u7528\u4e00\u5957\u5b8c\u6574\u5ea6\uff08<25% \u9501\u66f2\u7387\u3001\u81ea\u52a8\u7ef4\u4fee\uff09\uff1b'
    '2. \u65b0\u589e\u822a\u884c\u59d4\u6258\uff1a5 \u79cd\u76ee\u6807 + \u8fde\u51fb\u500d\u7387\uff0c\u8fc7\u671f\u4e0d\u60e9\u7f5a\uff1b'
    '3. \u79fb\u9664\u7ea2\u8272\u8b66\u6212 RTS \u4e0e\u6234\u68ee\u7403\u4e24\u4e2a\u4eff\u5236\u73a9\u6cd5\uff1b'
    '4. \u5168\u7ad9\u5185\u90e8 UI \u91cd\u5236\uff1a\u65b0\u589e sf-ui-system \u5c42\uff08\u53d1\u4e1d\u7ebf + \u76f4\u89d2 + \u5355\u8272\uff09\uff0c'
    '\u8d77\u822a\u9875 / \u5f00\u5361 / \u8bbe\u7f6e\u62bd\u5c49 / \u5929\u8c61\u9986 / \u6863\u6848\u4e0e\u547d\u540d / \u56fe\u9274 / \u98de\u884c HUD / '
    '\u6444\u5f71 / \u6298\u7eb8\u575e \u5168\u90e8\u91cd\u505a\uff1b'
    '5. \u5f00\u5361\u661f\u7403\u6539 WebGL \u7eaf\u8272\u51e0\u4f55\uff08\u7403\u51a0\u6591\u5757 + \u786c\u8fb9\u663c\u591c + \u53d1\u4e1d\u8f6e\u5ed3\uff09\uff1b'
    '6. \u6e05\u638917\u5904\u5f69\u8272 emoji\uff0c\u4fdd\u7559\u51e0\u4f55\u4e0e\u661f\u8c61\u7b26\u53f7\uff1b'
    '7. \u4fee\u590d\u547d\u540d\u94fe\u65ad\u88c2\u3001\u89e6\u6478\u7c07\u906e\u6321\u5f39\u7a97\u3001\u59d4\u6258\u5361\u8d8a\u754c\u4e0e\u4e2d\u6587\u5b57\u4f53\u56de\u9000\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('bumped to v%s (Build %d)' % (NEW_VER, NEW_BUILD))
