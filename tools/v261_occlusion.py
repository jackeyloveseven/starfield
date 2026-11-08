
# -*- coding: utf-8 -*-
"""v261 - 修掉形态模块里违反「不遮挡」的两处写法。"""
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

# 1) 雷暴：整球罩壳闪光 -> 只闪两条雷暴带，且幅度受限
rep("""    var flashMat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false
    });
    var flash = new THREE.Mesh(new THREE.SphereGeometry(R * 1.02, 24, 16), flashMat);
    g.add(flash);
    extra.updaters.push(function (t) {
      flashMat.opacity = Math.sin(t * 8.5) > 0.86 ? 0.28 : 0;
      ringMat.opacity = 0.42 + 0.2 * Math.sin(t * 1.8);
    });""",
    """    /* 不罩整球：闪光只落在雷暴带上，且亮度变化幅度 <=0.15 */
    var bandMat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0,
      side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false
    });
    for (var by = -1; by <= 1; by += 2) {
      var bg2 = new THREE.TorusGeometry(R * 0.62, 1.4, 6, 48);
      var bm = new THREE.Mesh(bg2, bandMat);
      bm.rotation.x = Math.PI / 2;
      bm.position.y = by * R * 0.78;
      g.add(bm);
    }
    extra.updaters.push(function (t) {
      bandMat.opacity = Math.sin(t * 8.5) > 0.86 ? 0.15 : 0;
      ringMat.opacity = 0.42 + 0.2 * Math.sin(t * 1.8);
    });""",
    'stormFlash')

# 2) 虚空：不再把地形整体抹黑，改为只压暗到 0.62，保留地貌可读
rep("""    if (planet.terrainMesh && planet.terrainMesh.material) {
      planet.terrainMesh.material.color.multiplyScalar(0.35);
    }""",
    """    if (planet.terrainMesh && planet.terrainMesh.material) {
      planet.terrainMesh.material.color.multiplyScalar(0.62);
    }""",
    'voidDim')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
