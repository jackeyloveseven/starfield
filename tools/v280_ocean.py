
# -*- coding: utf-8 -*-
"""v280 - ocean waves + dock frames，用 ASCII 锚点避免空格/中文问题。"""
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

# 用 sky/fog 的唯一值做锚点，避开中文与对齐空格
rep("sky: 0x0c1a26, fog: 0x18303e }",
    "sky: 0x0c1a26, fog: 0x18303e, ocean: true, land: 0.14 }", 'envWater')
rep("sky: 0x0a0e16, fog: 0x161e28 }",
    "sky: 0x0a0e16, fog: 0x161e28, dock: true }", 'envDock')

rep("        landRatio: preset.landRatio, ruggedness: preset.ruggedness,",
    "        landRatio: (env.land !== undefined ? env.land : preset.landRatio), ruggedness: preset.ruggedness,",
    'landRatio')

rep("      if (planet.cloudsMesh) planet.cloudsMesh.visible = false;",
    """      if (planet.cloudsMesh) planet.cloudsMesh.visible = false;
      if (env.ocean && planet.oceanMesh) {
        oceanMesh = planet.oceanMesh;
        oceanMesh.material.roughness = 0.06;
        oceanMesh.material.metalness = 0.45;
        oceanMesh.material.clearcoat = 1.0;
        oceanMesh.material.opacity = 0.92;
        oceanBase = oceanMesh.geometry.attributes.position.array.slice(0);
      }""",
    'oceanMat')

rep("  var active = false, renderer = null, scene = null, camera = null,",
    "  var oceanMesh = null, oceanBase = null, dockGroup = null;\n  var active = false, renderer = null, scene = null, camera = null,",
    'vars')

rep("    if (planet) planet.update(t, 1 / 60);",
    """    if (oceanMesh && oceanBase) {
      var op = oceanMesh.geometry.attributes.position;
      for (var oi = 0; oi < op.count; oi++) {
        var bx = oceanBase[oi * 3], by = oceanBase[oi * 3 + 1], bz = oceanBase[oi * 3 + 2];
        var w = Math.sin(t * 1.7 + bx * 0.32 + bz * 0.26) * 0.42
              + Math.sin(t * 2.6 + by * 0.4) * 0.18;
        var len = Math.sqrt(bx * bx + by * by + bz * bz) || 1;
        var sc = (len + w) / len;
        op.setXYZ(oi, bx * sc, by * sc, bz * sc);
      }
      op.needsUpdate = true;
    }
    if (dockGroup) dockGroup.rotation.y = t * 0.03;

    if (planet) planet.update(t, 1 / 60);""",
    'wave')

rep("      boundCv = null; handlers = null;",
    "      boundCv = null; handlers = null;\n      oceanMesh = null; oceanBase = null; dockGroup = null;",
    'cleanup')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
