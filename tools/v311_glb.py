
# -*- coding: utf-8 -*-
"""v311 - 引入 GLTFLoader，母舰环境用 sand3d 模型替换门型框架。"""
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

# 1) 引入 GLTFLoader（three.min.js 之后）
rep('<script src="./libs/three.min.js">',
    '<script src="./libs/three.min.js"></script>\n<script src="./libs/GLTFLoader.js"></script>',
    'loader', ) if False else None

# three.min.js 的引入形式可能不同，直接找它
old_loader = '<script src="./libs/three.min.js"></script>'
if html.count(old_loader) == 1:
    html = html.replace(old_loader, old_loader + '\n<script src="./libs/GLTFLoader.js"></script>')
    log.append('loader')
else:
    # 兜底：在 </head> 前加
    he = html.find('</head>')
    html = html[:he] + '<script src="./libs/GLTFLoader.js"></script>\n' + html[he:]
    log.append('loader-head')

# 2) 母舰环境：加载 sand3d 母舰模型
rep("      if (env.dock) {",
    """      /* 母舰环境：用 sand3d 建的真实母舰，替换手写门型框架 */
      if (env.dock && THREE.GLTFLoader) {
        new THREE.GLTFLoader().load('models/mothership.glb', function (gltf) {
          var ship = gltf.scene;
          /* sand3d 用毫米，船体 88 单位长；地表尺度下缩到合理大小 */
          ship.scale.setScalar(0.16);
          var th = 0.6, ph = 1.12;
          var pos = sph(th, ph, 36 + 6);
          ship.position.copy(pos);
          ship.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), pos.clone().normalize());
          scene.add(ship);
          dockGroup = ship;
        }, undefined, function (err) {
          if (window.console) console.warn('mothership.glb load failed', err);
        });
      }
      if (env.dock) {""",
    'glb')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
