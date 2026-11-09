
# -*- coding: utf-8 -*-
"""v326 - 星灵水晶浮空 + 能量光束连接。"""
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

# 1) 水晶簇浮空（R+3 -> R+9），保存引用并加能量光束
rep("""          var c = gltf.scene;
          c.scale.setScalar(100);
          var cp = sph(0.16, 1.12, 36 + 3);
          c.position.copy(cp);
          c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), cp.clone().normalize());
          scene.add(c);""",
    """          var c = gltf.scene;
          c.scale.setScalar(100);
          /* 星灵的建筑是浮空的，不是立在地上 */
          var cp = sph(0.16, 1.12, 36 + 9);
          c.position.copy(cp);
          c.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), cp.clone().normalize());
          scene.add(c);
          crystalGroup = c;
          crystalBase = cp.clone();

          /* 能量连接：主晶到周围三个悬浮点，青色光束 */
          var beamMat = new THREE.LineBasicMaterial({
            color: 0x66e0ff, transparent: true, opacity: 0.55,
            blending: THREE.AdditiveBlending, depthWrite: false
          });
          for (var bi = 0; bi < 3; bi++) {
            var ang = bi / 3 * Math.PI * 2;
            var top = cp.clone().add(new THREE.Vector3(Math.cos(ang) * 6, 3 + bi, Math.sin(ang) * 6));
            var node = new THREE.Mesh(
              new THREE.OctahedronGeometry(0.8, 0),
              new THREE.MeshBasicMaterial({ color: 0x9beeff })
            );
            node.position.copy(top);
            scene.add(node);
            crystalNodes.push(node);
            var lg = new THREE.BufferGeometry().setFromPoints([cp, top]);
            var line = new THREE.Line(lg, beamMat);
            scene.add(line);
            crystalBeams.push(line);
          }""",
    'float')

# 2) 声明变量
rep("  var oceanMesh = null, oceanBase = null, dockGroup = null;",
    "  var oceanMesh = null, oceanBase = null, dockGroup = null;\n  var crystalGroup = null, crystalBase = null, crystalNodes = [], crystalBeams = [];",
    'decl')

# 3) 帧循环：浮动 + 节点脉动 + 光束呼吸
rep("    if (dockGroup) dockGroup.rotation.y = t * 0.03;",
    """    /* 星灵：水晶悬浮浮动，能量光束呼吸 */
    if (crystalGroup && crystalBase) {
      crystalGroup.position.y = crystalBase.y + Math.sin(t * 1.1) * 1.2;
      for (var ni = 0; ni < crystalNodes.length; ni++) {
        crystalNodes[ni].position.y = crystalBase.y + 3 + ni + Math.sin(t * 1.1 + ni) * 1.2;
        crystalNodes[ni].rotation.y = t * 0.8 + ni;
      }
      for (var li = 0; li < crystalBeams.length; li++) {
        crystalBeams[li].material.opacity = 0.35 + 0.25 * Math.sin(t * 2.2 + li * 1.3);
      }
    }
    if (dockGroup) dockGroup.rotation.y = t * 0.03;""",
    'animate')

# 4) 退出清理
rep("      oceanMesh = null; oceanBase = null; dockGroup = null;",
    "      oceanMesh = null; oceanBase = null; dockGroup = null;\n      crystalGroup = null; crystalBase = null; crystalNodes = []; crystalBeams = [];",
    'cleanup')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
