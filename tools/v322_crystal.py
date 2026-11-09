
# -*- coding: utf-8 -*-
"""v322 - 水晶簇 base64 内嵌并接入 protoss_crystal 地表。"""
import base64, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
GLB = BASE / 'models' / 'crystal.glb'
HTML = BASE / 'starfield.html'

b64 = base64.b64encode(GLB.read_bytes()).decode('ascii')
html = HTML.read_text(encoding='utf-8')

# 内嵌
inject = '<script>window.__crystalGLB = "' + b64 + '";</script>\n'
he = html.find('</head>')
html = html[:he] + inject + html[he:]

# 在母舰加载代码后，加水晶簇地标（protoss_crystal 环境）
anchor = "      cityGroup = buildCity(env, 36, rng, planet.landVertices);\n      scene.add(cityGroup);"
add = anchor + """

      /* 星灵环境：sand3d 折光水晶簇地标 */
      if (manif === 'protoss_crystal' && THREE.GLTFLoader && window.__crystalGLB) {
        var cbin = atob(window.__crystalGLB);
        var cbytes = new Uint8Array(cbin.length);
        for (var ci = 0; ci < cbin.length; ci++) cbytes[ci] = cbin.charCodeAt(ci);
        new THREE.GLTFLoader().parse(cbytes.buffer, '', function (gltf) {
          var c = gltf.scene;
          c.scale.setScalar(100);
          var cp = sph(0.16, 1.12, 36 + 3);
          c.position.copy(cp);
          c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), cp.clone().normalize());
          scene.add(c);
        });
      }"""
assert html.count(anchor) == 1, 'anchor count=%d' % html.count(anchor)
html = html.replace(anchor, add)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('crystal embedded and wired,', len(b64), 'b64 chars')
