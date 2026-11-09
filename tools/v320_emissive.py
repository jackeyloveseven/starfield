
# -*- coding: utf-8 -*-
"""v320 - 母舰加一点自发光，避免纯剪影。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "          dockGroup = ship; window.__shipLoaded = true;"
new = """          ship.traverse(function (o) {
            if (o.isMesh && o.material) {
              o.material.emissive = new THREE.Color(0x2a3a4a);
              o.material.emissiveIntensity = 0.45;
              o.material.needsUpdate = true;
            }
          });
          dockGroup = ship; window.__shipLoaded = true;"""
assert html.count(old) == 1
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('emissive added to mothership')
