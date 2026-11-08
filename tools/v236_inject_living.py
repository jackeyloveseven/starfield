
# -*- coding: utf-8 -*-
"""v236 - 把遗漏的 LivingPlanet 类补进 sf-planet-gl。"""
import sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML = BASE / 'starfield.html'
STUDIO = BASE / 'planet_studio.html'

studio = STUDIO.read_text(encoding='utf-8', errors='replace')
html = HTML.read_text(encoding='utf-8', errors='replace')

def grab(src, marker):
    i = src.find(marker)
    assert i >= 0, marker
    depth = 0; started = False; j = i
    while j < len(src):
        c = src[j]
        if c == '{':
            depth += 1; started = True
        elif c == '}':
            depth -= 1
            if started and depth == 0:
                return src[i:j + 1]
        j += 1
    raise AssertionError('unbalanced ' + marker)

living = grab(studio, 'class LivingPlanet')
living = living.replace('PlanetConfig.', 'this.cfg.')
print('LivingPlanet extracted:', len(living), 'chars')

# 插到 const Presets 之后、TIER_LOOK 之前
anchor = '  /* Tier -> preset + presentation.'
i = html.find(anchor)
assert i > 0, 'anchor not found'
html = html[:i] + living + '\n\n' + html[i:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('LivingPlanet injected before TIER_LOOK')
