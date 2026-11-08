
# -*- coding: utf-8 -*-
"""v281 - 母舰船坞：门型框架结构。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "      cityGroup = buildCity(env, 36, rng, planet.landVertices);\n      scene.add(cityGroup);"
new = """      cityGroup = buildCity(env, 36, rng, planet.landVertices);
      scene.add(cityGroup);

      /* 母舰船坞：一排门型框架（双立柱 + 顶梁），是工业设施而非自然地貌 */
      if (env.dock) {
        dockGroup = new THREE.Group();
        var dockMat = new THREE.MeshStandardMaterial({
          color: 0x6a7a8a, roughness: 0.45, metalness: 0.65, flatShading: true
        });
        var glowMat = new THREE.MeshBasicMaterial({ color: 0x7fd8ff });
        var up = new THREE.Vector3(0, 1, 0);
        for (var d = 0; d < 6; d++) {
          var th = d * 0.42 + 0.15, ph = 1.12;
          var center = sph(th, ph, 36);
          var nrm = center.clone().normalize();
          var gate = new THREE.Group();
          gate.position.copy(center);
          gate.quaternion.setFromUnitVectors(up, nrm);
          for (var s = -1; s <= 1; s += 2) {
            var pillar = new THREE.Mesh(new THREE.BoxGeometry(1.0, 15, 1.0), dockMat);
            pillar.position.set(s * 4.5, 7.5, 0);
            gate.add(pillar);
          }
          var beam = new THREE.Mesh(new THREE.BoxGeometry(10.4, 1.0, 1.4), dockMat);
          beam.position.set(0, 15, 0);
          gate.add(beam);
          /* 梁上一道指示灯 */
          var lamp = new THREE.Mesh(new THREE.BoxGeometry(9.0, 0.16, 0.16), glowMat);
          lamp.position.set(0, 15.6, 0);
          gate.add(lamp);
          dockGroup.add(gate);
        }
        scene.add(dockGroup);
      }"""
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('dock gates added')
