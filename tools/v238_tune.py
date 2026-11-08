
# -*- coding: utf-8 -*-
"""v238 - 相机拉远 + 降低 myth 饱和度 + 树木缩小。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 1. 相机拉远：z 118 -> 178，让星球占画面约 55%
rep("camera.position.set(0, 0, 118);", "camera.position.set(0, 0, 178);", 'camera')

# 2. 饱和度收敛
rep("var satBoost = tier === 'myth' ? 1.45 : tier === 'legend' ? 1.3 : tier === 'epic' ? 1.18 : 1.0;",
    "var satBoost = tier === 'myth' ? 1.16 : tier === 'legend' ? 1.10 : tier === 'epic' ? 1.05 : 1.0;",
    'satBoost')
rep("var lightBoost = tier === 'myth' ? 1.22 : tier === 'legend' ? 1.12 : 1.0;",
    "var lightBoost = tier === 'myth' ? 1.10 : tier === 'legend' ? 1.05 : 1.0;",
    'lightBoost')

# 3. 树木缩小：buildFlora 里 0.7~1.3 -> 0.32~0.62
rep("const scale = (0.7 + Math.random() * 0.6) * (pt.isBeach ? 0.8 : 1.1);",
    "const scale = (0.30 + Math.random() * 0.30) * (pt.isBeach ? 0.8 : 1.1);",
    'treeScale')

# 4. 树木数量收敛（太多像刺球）
rep("common: { preset: 'archipelago',        trees: 900,",
    "common: { preset: 'archipelago',        trees: 620,", 'tree-common')
rep("rare:   { preset: 'desert_oasis',       trees: 1100,",
    "rare:   { preset: 'desert_oasis',       trees: 720,", 'tree-rare')
rep("epic:   { preset: 'forest',             trees: 2100,",
    "epic:   { preset: 'forest',             trees: 1150,", 'tree-epic')
rep("legend: { preset: 'monument',           trees: 700,",
    "legend: { preset: 'monument',           trees: 480,", 'tree-legend')
rep("myth:   { preset: 'alien',              trees: 1700,",
    "myth:   { preset: 'alien',              trees: 900,", 'tree-myth')

# 5. 环形 geometry 的 segments 降低，避免视觉噪点
rep("var rg = new THREE.RingGeometry(inner, outer, 128, 1);",
    "var rg = new THREE.RingGeometry(inner, outer, 96, 1);", 'ringSeg')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
