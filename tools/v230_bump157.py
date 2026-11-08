
# -*- coding: utf-8 -*-
"""v230 — build 156 -> 157：开卡演出改二次元抽卡节奏。"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML, SW, VER = BASE / 'starfield.html', BASE / 'service-worker.js', BASE / 'version.json'
VER_STR, OLD_B, NEW_B = '1.9.9.9.9', 156, 157
log = []

with open(HTML, 'r', encoding='utf-8', newline='') as f:
    html = f.read()
for old, new, tag in [
    ('id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, OLD_B),
     'id="sf-version-tag">v%s (Build %d)</span>' % (VER_STR, NEW_B), 'tag'),
    ('const localBuild = %d;' % OLD_B, 'const localBuild = %d;' % NEW_B, 'localBuild'),
]:
    assert html.count(old) == 1, tag
    html = html.replace(old, new)
    log.append(tag)
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(html)

with open(SW, 'r', encoding='utf-8', newline='') as f:
    sw = f.read()
old = "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, OLD_B)
assert sw.count(old) == 1
sw = sw.replace(old, "const CACHE_VERSION = 'v%s-b%d';" % (VER_STR, NEW_B))
with open(SW, 'w', encoding='utf-8', newline='') as f:
    f.write(sw)
log.append('CACHE_VERSION')

meta = json.loads(VER.read_text(encoding='utf-8'))
meta['build'] = NEW_B
meta['updated_at'] = '2026-11-08T12:20:00+08:00'
meta['title'] = '\u5f00\u5361\u6f14\u51fa\u91cd\u505a\uff1a\u661f\u5c18\u6536\u62e2 \u2192 \u5149\u67f1 \u2192 \u7206\u95ea \u2192 \u7c92\u5b50\u56db\u6563 \u2192 \u5361\u7247\u5f39\u51fa'
meta['changelog'] = (
    '1. \u5f00\u5361\u6f14\u51fa\u6309\u62bd\u5361\u8282\u594f\u91cd\u505a\uff1a260 \u9897\u661f\u5c18\u87ba\u65cb\u6536\u62e2\u3001'
    '\u4e2d\u5fc3\u5149\u67f1\u6491\u8d77\u3001\u767d\u5149\u7206\u95ea\u3001\u7a00\u6709\u5ea6\u5f69\u8272\u706b\u82b1\u56db\u6563\u3001'
    '\u5361\u7247\u8fc7\u51b2\u5f39\u51fa\uff1b'
    '2. \u7c92\u5b50\u6570\u91cf\u4e0e\u989c\u8272\u8ddf\u54c1\u9636\u8d70\uff08\u666e\u901a 200 / \u53f2\u8bd7 200 / '
    '\u4f20\u8bf4 260 / \u795e\u8bdd 320\uff09\uff1b'
    '3. \u767d\u5149\u6539\u72ec\u7acb\u5c42\uff08\u539f #sf-hatch::after \u88ab\u65e7\u89c4\u5219\u5360\u7528\uff09\u3002'
)
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
log.append('version.json')

sys.stdout.reconfigure(encoding='utf-8')
print('bumped to Build %d :: %s' % (NEW_B, ', '.join(log)))
