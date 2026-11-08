
# -*- coding: utf-8 -*-
"""v275 - 建筑落在真实地形顶点上，不再固定高度浮空。"""
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

# buildCity 接收真实地形顶点
rep("  function buildCity(env, R, rng) {\n    var group = new THREE.Group();\n    var up = new THREE.Vector3(0, 1, 0);",
    """  function buildCity(env, R, rng, landVertices) {
    var group = new THREE.Group();
    var up = new THREE.Vector3(0, 1, 0);
    /* 用地形实际顶点，建筑才立在地上；固定 R+4.2 会浮空或埋进山里 */
    var spots = (landVertices && landVertices.length) ? landVertices : null;
    function spotFor() {
      if (!spots) return null;
      return spots[Math.floor(rng() * spots.length)];
    }""",
    'citySpots')

# 调用处传入 planet.landVertices
rep("      cityGroup = buildCity(env, 36, rng);",
    "      cityGroup = buildCity(env, 36, rng, planet.landVertices);",
    'cityCall')

# 三种建筑的落点统一改为「有地形顶点就用顶点，否则退回球面」
rep("        mesh0.position.copy(n).multiplyScalar(R + hh * 0.4 + 4);",
    "        var sp0 = spotFor();\n        mesh0.position.copy(sp0 ? sp0.pos : n.clone().multiplyScalar(R + hh * 0.4 + 4));",
    'crystalPos')
rep("        cm.position.copy(n).multiplyScalar(R + 4.4);",
    "        var spc = spotFor();\n        cm.position.copy(spc ? spc.pos : n.clone().multiplyScalar(R + 4.4));",
    'cystPos')
rep("      mesh.position.copy(n).multiplyScalar(R + 4.2);",
    "      var sp = spotFor();\n      mesh.position.copy(sp ? sp.pos : n.clone().multiplyScalar(R + 4.2));",
    'meshPos')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
