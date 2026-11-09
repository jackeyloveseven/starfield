
# -*- coding: utf-8 -*-
"""v324 - 遗迹巨构 base64 内嵌并接入灾变废墟地表。"""
import base64, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
GLB = BASE / 'models' / 'monument.glb'
HTML = BASE / 'starfield.html'

b64 = base64.b64encode(GLB.read_bytes()).decode('ascii')
html = HTML.read_text(encoding='utf-8')

inject = '<script>window.__monumentGLB = "' + b64 + '";</script>\n'
he = html.find('</head>')
html = html[:he] + inject + html[he:]

anchor = "      /* 星灵环境：sand3d 折光水晶簇地标 */"
add = """      /* 灾变废墟：sand3d 断裂纪念碑 */
      if (manif === 'shattered_cataclysm' && THREE.GLTFLoader && window.__monumentGLB) {
        var mbin = atob(window.__monumentGLB);
        var mbytes = new Uint8Array(mbin.length);
        for (var mi = 0; mi < mbin.length; mi++) mbytes[mi] = mbin.charCodeAt(mi);
        new THREE.GLTFLoader().parse(mbytes.buffer, '', function (gltf) {
          var m = gltf.scene;
          m.scale.setScalar(150);
          var mp = sph(0.16, 1.12, 36 + 3);
          m.position.copy(mp);
          m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), mp.clone().normalize());
          scene.add(m);
        });
      }

""" + anchor
assert html.count(anchor) == 1, 'anchor count=%d' % html.count(anchor)
html = html.replace(anchor, add)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('monument embedded and wired')
