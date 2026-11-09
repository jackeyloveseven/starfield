
# -*- coding: utf-8 -*-
"""v331 - 修好 sand3d 模型的"黑"：线性颜色回 sRGB、钳金属度、加环境贴图；
   同时把母舰从"竖插在地表"改成地表悬停，重建城市落点用地形顶点。"""
import base64, re, sys
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML = BASE / 'starfield.html'
html = HTML.read_text(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

# ---------- 1. 重新内嵌两个 GLB ----------
for var, fn in (('__cityGLB', 'city.glb'), ('__mothershipGLB', 'mothership.glb')):
    b64 = base64.b64encode((BASE / 'models' / fn).read_bytes()).decode('ascii')
    pat = re.compile(r'window\.' + var + r' = "[^"]*"')
    assert len(pat.findall(html)) == 1, var
    html = pat.sub('window.%s = "%s"' % (var, b64), html, count=1)
    print('embedded', fn, len(b64), 'b64 chars')

# ---------- 2. 材质/环境修正工具 ----------
helper_anchor = '  function buildCity(env, R, rng, landVertices) {'
assert html.count(helper_anchor) == 1
helper = '''  /* glTF 的 baseColor 是线性空间，本地表场景输出没开 sRGB，
     直接采样会比作者意图暗两档；金属度 1.0 又没有环境贴图就是纯黑。
     这里统一把颜色转回可见值、钳住金属度，并给自发光材质一点强度。 */
  function sfFixGLB(root, opt) {
    opt = opt || {};
    var metalCap = opt.metal !== undefined ? opt.metal : 0.38;
    var emis = opt.emis !== undefined ? opt.emis : 1.4;
    root.traverse(function (o) {
      if (!o.isMesh || !o.material) return;
      var mats = Array.isArray(o.material) ? o.material : [o.material];
      for (var i = 0; i < mats.length; i++) {
        var m = mats[i];
        if (m.color && m.color.convertLinearToSRGB) m.color.convertLinearToSRGB();
        if (m.emissive && m.emissive.convertLinearToSRGB) m.emissive.convertLinearToSRGB();
        if (m.metalness !== undefined && m.metalness > metalCap) m.metalness = metalCap;
        if (m.roughness !== undefined && m.roughness < 0.26) m.roughness = 0.26;
        if (m.emissive && m.emissive.getHex() !== 0) m.emissiveIntensity = emis;
        m.needsUpdate = true;
      }
      o.frustumCulled = false;
    });
  }

  /* 一次性环境贴图：金属需要东西可反射，否则再高的环境光也是黑的 */
  function sfEnvMap(skyHex, fogHex) {
    try {
      var pm = new THREE.PMREMGenerator(renderer);
      var es = new THREE.Scene();
      var geo = new THREE.SphereGeometry(20, 24, 12);
      var mat = new THREE.ShaderMaterial({
        side: THREE.BackSide, depthWrite: false, fog: false,
        uniforms: {
          cTop: { value: new THREE.Color(skyHex) },
          cHor: { value: new THREE.Color(fogHex) },
          cBot: { value: new THREE.Color(0x05070c) }
        },
        vertexShader: 'varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
        fragmentShader: 'varying vec3 vP; uniform vec3 cTop; uniform vec3 cHor; uniform vec3 cBot;' +
          'void main(){ vec3 n = normalize(vP); float h = n.y;' +
          ' vec3 c = mix(cHor, cTop, smoothstep(0.02, 0.62, h));' +
          ' c = mix(cBot, c, smoothstep(-0.45, 0.02, h));' +
          ' gl_FragColor = vec4(c, 1.0); }'
      });
      es.add(new THREE.Mesh(geo, mat));
      var sun = new THREE.Mesh(new THREE.SphereGeometry(1.4, 12, 8), new THREE.MeshBasicMaterial({ color: 0xffffff }));
      sun.position.set(-6, 7, 4.5);
      es.add(sun);
      var rt = pm.fromScene(es, 0.05);
      pm.dispose();
      geo.dispose(); mat.dispose();
      return rt.texture;
    } catch (e) { return null; }
  }

''' + helper_anchor
html = html.replace(helper_anchor, helper)

# ---------- 3. 环境贴图接上场景 ----------
env_anchor = '      scene.add(rim);'
assert html.count(env_anchor) == 1
html = html.replace(env_anchor, env_anchor + '''
      var envTex = sfEnvMap(env.sky, env.fog);
      if (envTex) scene.environment = envTex;''')

# ---------- 4. 城市：地形落点 + 朝向 + 尺度 ----------
A1 = '      /* 发达城市：sand3d 建筑群地标 */\n'
A2 = '      /* 灾变废墟：sand3d 断裂纪念碑 */'
i1, i2 = html.find(A1), html.find(A2)
assert i1 > 0 and i2 > i1
city_block = '''      /* 发达城市：sand3d 建筑群地标（座在真实地形上，正立面朝相机） */
      if (manif === 'cyber_metropolis' && THREE.GLTFLoader && window.__cityGLB) {
        var ybin = atob(window.__cityGLB);
        var ybytes = new Uint8Array(ybin.length);
        for (var yi = 0; yi < ybin.length; yi++) ybytes[yi] = ybin.charCodeAt(yi);
        new THREE.GLTFLoader().parse(ybytes.buffer, '', function (gltf) {
          var y = gltf.scene;
          sfFixGLB(y, { metal: 0.34, emis: 1.6 });
          y.scale.setScalar(62);
          var dir = sph(0.16, 1.12, 1).normalize();
          var R0 = planet.cfg.radius;
          var ground = R0 + 1.2;
          var lv = planet.landVertices || [];
          for (var li = 0; li < lv.length; li++) {
            var lp = lv[li].pos;
            if (lp.clone().normalize().dot(dir) > 0.994 && lp.length() > ground) ground = lp.length();
          }
          var anchor = dir.clone().multiplyScalar(ground - 0.25);
          y.position.copy(anchor);
          /* 基座朝上、正立面朝相机：+y=法线，+z=指向相机 */
          var camDir = sph(0, 1.12, 1).normalize();
          var t2c = camDir.clone().sub(dir.clone().multiplyScalar(camDir.dot(dir))).normalize();
          var rgt = new THREE.Vector3().crossVectors(dir, t2c).normalize();
          y.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(rgt, dir, t2c));
          scene.add(y);
          cityLandmark = y;
        });
      }

'''
html = html[:i1] + city_block + html[i2:]

# ---------- 5. 母舰：地表悬停 + 去掉手写门型框架 ----------
B1 = '      /* 母舰船坞：一排门型框架（双立柱 + 顶梁），是工业设施而非自然地貌 */\n'
B2 = '      titleEl.textContent = (opts.name || \'未命名星体\');'
j1, j2 = html.find(B1), html.find(B2)
assert j1 > 0 and j2 > j1
ship_block = '''      /* 母舰：sand3d 建模，悬停在地表上方，舰艏朝前方 */
      if (env.dock && THREE.GLTFLoader && window.__mothershipGLB) {
        var bin = atob(window.__mothershipGLB);
        var bytes = new Uint8Array(bin.length);
        for (var bi = 0; bi < bin.length; bi++) bytes[bi] = bin.charCodeAt(bi);
        new THREE.GLTFLoader().parse(bytes.buffer, '', function (gltf) {
          var ship = gltf.scene;
          sfFixGLB(ship, { metal: 0.32, emis: 1.7 });
          ship.scale.setScalar(90);
          var dir = sph(0.16, 1.12, 1).normalize();
          var R0 = planet.cfg.radius;
          var ground = R0 + 1.2;
          var lv2 = planet.landVertices || [];
          for (var li2 = 0; li2 < lv2.length; li2++) {
            var lp2 = lv2[li2].pos;
            if (lp2.clone().normalize().dot(dir) > 0.994 && lp2.length() > ground) ground = lp2.length();
          }
          var pos = dir.clone().multiplyScalar(ground + 2.6);
          /* 舰体轴：glTF +y=舰背向上，+z=舰尾 → 让 +z 指向后方 */
          var fwd = new THREE.Vector3().crossVectors(dir, new THREE.Vector3(0, 1, 0)).normalize();
          var back = fwd.clone().negate();
          var rgt = new THREE.Vector3().crossVectors(dir, back).normalize();
          ship.position.copy(pos);
          ship.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(rgt, dir, back));
          scene.add(ship);
          dockGroup = ship;
          dockBase = pos.clone();
          dockNormal = dir.clone();
          window.__shipLoaded = true;
        }, undefined, function (err) {
          if (window.console) console.warn('mothership.glb load failed', err);
        });
      }

'''
html = html[:j1] + ship_block + html[j2:]

# ---------- 6. 其它两个模型也走同一套修正 ----------
m_old = '          var m = gltf.scene;\n          m.scale.setScalar(150);'
assert html.count(m_old) == 1
html = html.replace(m_old, '          var m = gltf.scene;\n          sfFixGLB(m, { metal: 0.22, emis: 1.2 });\n          m.scale.setScalar(150);')

c_old = '          var c = gltf.scene;\n          c.scale.setScalar(100);'
assert html.count(c_old) == 1
html = html.replace(c_old, '          var c = gltf.scene;\n          sfFixGLB(c, { metal: 0.2, emis: 1.4 });\n          c.scale.setScalar(100);')

# ---------- 7. 渲染循环：母舰轻微浮动，不再原地自转 ----------
rot_old = '    if (dockGroup) dockGroup.rotation.y = t * 0.03;'
assert html.count(rot_old) == 1
html = html.replace(rot_old, '''    if (dockGroup && dockBase && dockNormal) {
      dockGroup.position.copy(dockBase).addScaledVector(dockNormal, Math.sin(t * 0.7) * 0.22);
    }''')

# 变量声明补齐
var_old = '  var crystalGroup = null, crystalBase = null, crystalNodes = [], crystalBeams = [];'
assert var_old in html, 'var block'
html = html.replace(var_old, var_old + '\n  var cityLandmark = null, dockBase = null, dockNormal = null;')

HTML.write_text(html, encoding='utf-8', newline='')
print('patched', HTML, HTML.stat().st_size, 'bytes')
