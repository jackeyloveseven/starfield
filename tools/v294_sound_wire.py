
# -*- coding: utf-8 -*-
"""v294 - 声音签名接入（锚点已核对原文）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

rep("LivingPlanet: LivingPlanet, Presets: Presets, SimplexNoise: SimplexNoise, tierLook: TIER_LOOK",
    "LivingPlanet: LivingPlanet, Presets: Presets, SimplexNoise: SimplexNoise, tierLook: TIER_LOOK, manifFor: sfManifFor",
    'expose')

rep("build(); cur = item;",
    """build(); cur = item;
  if (window.SFAmbience) {
    var mid = item.manif;
    if (!mid && window.SFPlanetGL && window.SFPlanetGL.manifFor) {
      try { mid = window.SFPlanetGL.manifFor(item).id; } catch (e) { mid = null; }
    }
    window.SFAmbience.start(mid || 'earth_egg');
  }""",
    'openSound')

rep("function hide(){\n    if (root) {",
    "function hide(){\n    if (window.SFAmbience) window.SFAmbience.stop();\n    if (root) {",
    'hideSound')

rep("      active = true;\n      autoTh = 0; userTh = 0; userPhi = 1.12; lastT = 0; dragging = false;",
    "      if (window.SFAmbience) window.SFAmbience.start(manif);\n      active = true;\n      autoTh = 0; userTh = 0; userPhi = 1.12; lastT = 0; dragging = false;",
    'surfaceSound')

rep("    exit: function () {\n      if (!active) return;",
    "    exit: function () {\n      if (window.SFAmbience) window.SFAmbience.stop();\n      if (!active) return;",
    'surfaceStop')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
