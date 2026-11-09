
# -*- coding: utf-8 -*-
"""v328 - 城市建筑群 base64 内嵌并接入发达城市地表。"""
import base64, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
GLB = BASE / 'models' / 'city.glb'
HTML = BASE / 'starfield.html'

b64 = base64.b64encode(GLB.read_bytes()).decode('ascii')
html = HTML.read_text(encoding='utf-8')

inject = '<script>window.__cityGLB = "' + b64 + '";</script>\n'
he = html.find('</head>')
html = html[:he] + inject + html[he:]

anchor = "      /* 灾变废墟：sand3d 断裂纪念碑 */"
add = """      /* 发达城市：sand3d 建筑群地标 */
      if (manif === 'cyber_metropolis' && THREE.GLTFLoader && window.__cityGLB) {
        var ybin = atob(window.__cityGLB);
        var ybytes = new Uint8Array(ybin.length);
        for (var yi = 0; yi < ybin.length; yi++) ybytes[yi] = ybin.charCodeAt(yi);
        new THREE.GLTFLoader().parse(ybytes.buffer, '', function (gltf) {
          var y = gltf.scene;
          y.scale.setScalar(100);
          var yp = sph(0.16, 1.12, 36 + 3);
          y.position.copy(yp);
          y.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), yp.clone().normalize());
          /* 给楼一点自发光，像夜里亮着窗 */
          y.traverse(function (o) {
            if (o.isMesh && o.material) {
              o.material.emissive = new THREE.Color(0x1a2a3a);
              o.material.emissiveIntensity = 0.4;
              o.material.needsUpdate = true;
            }
          });
          scene.add(y);
        });
      }

""" + anchor
assert html.count(anchor) == 1, 'anchor count=%d' % html.count(anchor)
html = html.replace(anchor, add)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('city embedded and wired')
