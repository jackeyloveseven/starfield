
# -*- coding: utf-8 -*-
"""v237 - 修正 LivingPlanet 构造函数：接收 cfg。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')

old = "class LivingPlanet {\n  constructor(scene) {\n    this.scene = scene;\n    this.group = new THREE.Group();\n    this.scene.add(this.group);\n\n    this.noise = new SimplexNoise(this.cfg.seed);"
new = ("class LivingPlanet {\n  constructor(scene, cfg) {\n"
       "    this.cfg = cfg || { radius: 36, seed: 1, preset: 'archipelago',\n"
       "      landRatio: 0.38, ruggedness: 1.2, treeCount: 800, monumentLevel: 1,\n"
       "      faunaLevel: 1, cloudCoverage: 0.4, spinSpeed: 1, colors: Presets.archipelago.colors };\n"
       "    this.scene = scene;\n    this.group = new THREE.Group();\n"
       "    this.scene.add(this.group);\n\n    this.noise = new SimplexNoise(this.cfg.seed);")
assert html.count(old) == 1, 'ctor count=%d' % html.count(old)
html = html.replace(old, new)

old2 = "    planet = new LivingPlanet(scene);\n    planet.cfg = cfg;\n    planet.build();"
new2 = "    planet = new LivingPlanet(scene, cfg);\n    planet.build();"
assert html.count(old2) == 1, 'call count=%d' % html.count(old2)
html = html.replace(old2, new2)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('cfg passed via constructor')
