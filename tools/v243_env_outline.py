
# -*- coding: utf-8 -*-
"""v243 - 环境贴图（PMREM 程序化生成）+ 卡通描边。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# ---- 环境贴图：用 PMREMGenerator 从一个渐变球生成 ----
rep("""    amb = new THREE.AmbientLight(0xffffff, 0.52);
    scene.add(amb);""",
    """    amb = new THREE.AmbientLight(0xffffff, 0.34);
    scene.add(amb);

    /* 程序化环境贴图：没有它就只剩三个平行光，物理材质会显得平。
     * 用一个上下渐变的球体做源，PMREM 预滤波后给所有材质用。 */
    try {
      var envScene = new THREE.Scene();
      var envGeo = new THREE.SphereGeometry(60, 32, 16);
      var envCols = [];
      var envPos = envGeo.attributes.position;
      var top = new THREE.Color(0xdfe9ff);
      var mid = new THREE.Color(0x8fa8c8);
      var bot = new THREE.Color(0x1a2230);
      var tmpC = new THREE.Color();
      for (var vi = 0; vi < envPos.count; vi++) {
        var yy = envPos.getY(vi) / 60;
        if (yy >= 0) tmpC.copy(mid).lerp(top, yy);
        else tmpC.copy(mid).lerp(bot, -yy);
        envCols.push(tmpC.r, tmpC.g, tmpC.b);
      }
      envGeo.setAttribute('color', new THREE.Float32BufferAttribute(envCols, 3));
      var envMat = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide });
      envScene.add(new THREE.Mesh(envGeo, envMat));

      var pmrem = new THREE.PMREMGenerator(renderer);
      pmrem.compileEquirectangularShader();
      envTarget = pmrem.fromScene(envScene, 0.04);
      scene.environment = envTarget.texture;
      envMat.dispose();
      envGeo.dispose();
      pmrem.dispose();
    } catch (e) {
      scene.environment = null;
    }""",
    'envmap')

rep("""  var host = null, renderer = null, scene = null, camera = null,
      planet = null, sun = null, rimLight = null, amb = null,
      ok = false, failed = false, curKey = '', ringMeshes = [], moonMeshes = [],
      startT = 0, look = null;""",
    """  var host = null, renderer = null, scene = null, camera = null,
      planet = null, sun = null, rimLight = null, amb = null, envTarget = null,
      outlineMesh = null,
      ok = false, failed = false, curKey = '', ringMeshes = [], moonMeshes = [],
      startT = 0, look = null;""",
    'vars')

# ---- 卡通描边：放大背面 + 法线外扩 ----
rep("""    var s = L.scale;
    planet.group.scale.setScalar(s);
    planet.group.rotation.z = L.tilt;""",
    """    /* 卡通描边：把地形网格复制一份，沿法线外扩，只渲染背面，
     * 得到一圈等宽轮廓线（比后期边缘检测便宜且稳定）。 */
    if (planet.terrainMesh && planet.terrainMesh.geometry) {
      var og = planet.terrainMesh.geometry.clone();
      var om = new THREE.ShaderMaterial({
        vertexShader: [
          'uniform float uWidth;',
          'void main() {',
          '  vec3 p = position + normalize(normal) * uWidth;',
          '  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);',
          '}'
        ].join('\\n'),
        fragmentShader: [
          'uniform vec3 uColor;',
          'void main() { gl_FragColor = vec4(uColor, 1.0); }'
        ].join('\\n'),
        uniforms: {
          uWidth: { value: 0.55 + L.rim * 0.35 },
          uColor: { value: new THREE.Color(hsl(hue, 0.45, 0.30)) }
        },
        side: THREE.BackSide,
        depthWrite: false
      });
      outlineMesh = new THREE.Mesh(og, om);
      outlineMesh.renderOrder = -1;
      planet.group.add(outlineMesh);
    }

    var s = L.scale;
    planet.group.scale.setScalar(s);
    planet.group.rotation.z = L.tilt;""",
    'outline')

# 传 clearcoat / envIntensity / iridescence 到 cfg
rep("""      spinSpeed: L.spin,
      colors: tintPreset(basePreset.colors, hue, satBoost, lightBoost)
    };""",
    """      spinSpeed: L.spin,
      colors: tintPreset(basePreset.colors, hue, satBoost, lightBoost),
      envMap: scene.environment || null,
      envIntensity: 0.42 + L.rim * 0.30,
      clearcoat: tier === 'myth' ? 1.0 : tier === 'legend' ? 0.75 : tier === 'epic' ? 0.42 : 0.16,
      iridescence: tier === 'myth' ? 1.0 : 0
    };""",
    'cfgEnv')

# dispose 时清掉描边
rep("""    ringMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    ringMeshes = [];""",
    """    if (outlineMesh) {
      if (outlineMesh.geometry) outlineMesh.geometry.dispose();
      if (outlineMesh.material) outlineMesh.material.dispose();
      outlineMesh = null;
    }
    ringMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    ringMeshes = [];""",
    'dispose')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
