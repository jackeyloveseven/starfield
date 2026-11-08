
# -*- coding: utf-8 -*-
"""v260 - 星球形态（manif）移植到 three.js，独立于品阶。
   第一批：水晶 / 菌毯 / 撕裂 / 雷暴 / 都市 / 虚空。
   游戏内原本就有这 10 种形态的 Canvas 分支，抽卡却一直只用 6 个预设改 hue。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   星球形态层（manif）：独立于品阶
   移植自游戏内 PLANET_MANIFESTATIONS 的 Canvas 分支。
   tier 只管光效/环/卫星；manif 决定这颗星球"是什么"。
   ============================================================ */
var SF_MANIFS = [
  { id: 'skimming_water',     cn: '掠过水世界',   preset: 'archipelago' },
  { id: 'mothership_fleet',   cn: '母舰编队',     preset: 'monument' },
  { id: 'protoss_crystal',    cn: '幽能水晶星',   preset: 'alien' },
  { id: 'zerg_biomorphic',    cn: '生化菌毯星',   preset: 'forest' },
  { id: 'earth_egg',          cn: '盖亚绿洲',     preset: 'archipelago' },
  { id: 'cyber_metropolis',   cn: '工业巨构',     preset: 'monument' },
  { id: 'dune_arrakis',       cn: '沙丘世界',     preset: 'desert_oasis' },
  { id: 'shattered_cataclysm',cn: '大撕裂',       preset: 'monument' },
  { id: 'super_storm',        cn: '雷暴木星',     preset: 'abyss' },
  { id: 'dark_void',          cn: '虚空幽冥',     preset: 'abyss' }
];

function sfManifFor(item) {
  if (item && item.manif) {
    for (var i = 0; i < SF_MANIFS.length; i++) {
      if (SF_MANIFS[i].id === item.manif) return SF_MANIFS[i];
    }
  }
  /* 没有指定就按 hue 确定性分配，保证同一颗星永远是同一形态 */
  var h = (item && item.hue) || 200;
  return SF_MANIFS[Math.floor(h) % SF_MANIFS.length];
}

/* ---- 各形态的专属几何构建，挂在 LivingPlanet.group 上 ---- */
function sfBuildManif(THREE, planet, manifId, hue, rng) {
  var g = planet.group, R = planet.cfg.radius;
  var extra = { updaters: [] };

  function H(n) { return ((hue + n * 37) % 360 + 360) % 360; }
  function col(h, s, l) {
    var c = new THREE.Color();
    c.setHSL(((h % 360) + 360) % 360 / 360, s, l);
    return c;
  }

  if (manifId === 'protoss_crystal') {
    /* 折光水晶簇：八面体，立在表面，法线对齐 */
    var cg = new THREE.OctahedronGeometry(1, 0);
    var cm = new THREE.MeshPhysicalMaterial({
      color: col(H(180), 0.85, 0.62),
      roughness: 0.05, metalness: 0.1,
      clearcoat: 1.0, clearcoatRoughness: 0.03,
      transparent: true, opacity: 0.88,
      emissive: col(H(180), 0.9, 0.28),
      flatShading: true
    });
    var gold = new THREE.LineBasicMaterial({ color: col(45, 0.95, 0.62), transparent: true, opacity: 0.72 });
    var tops = [];
    for (var i = 0; i < 9; i++) {
      var u = rng() * Math.PI * 2, v = Math.acos(2 * rng() - 1);
      var n = new THREE.Vector3(Math.sin(v) * Math.cos(u), Math.cos(v), Math.sin(v) * Math.sin(u));
      var h = 5 + rng() * 7;
      var m = new THREE.Mesh(cg, cm);
      m.position.copy(n).multiplyScalar(R + h * 0.35);
      m.scale.set(1.5 + rng(), h, 1.5 + rng());
      m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), n);
      g.add(m);
      tops.push(n.clone().multiplyScalar(R + h));
    }
    /* 金色能量矩阵：晶体之间的连线 */
    var pts = [];
    for (var a = 0; a < tops.length; a++) {
      for (var b = a + 1; b < tops.length; b++) {
        if (tops[a].distanceTo(tops[b]) < R * 1.25) { pts.push(tops[a]); pts.push(tops[b]); }
      }
    }
    if (pts.length) {
      var lg = new THREE.BufferGeometry().setFromPoints(pts);
      g.add(new THREE.LineSegments(lg, gold));
    }
    extra.updaters.push(function (t) {
      cm.emissiveIntensity = 0.55 + 0.45 * Math.sin(t * 2.1);
    });
  }

  else if (manifId === 'zerg_biomorphic') {
    /* 有机囊肿：贴在表面的半球，随时间脉动 */
    var cystMat = new THREE.MeshPhysicalMaterial({
      color: col(H(310), 0.72, 0.42),
      roughness: 0.42, metalness: 0.0,
      clearcoat: 0.85, clearcoatRoughness: 0.3,
      emissive: col(H(325), 0.8, 0.14),
      flatShading: true
    });
    var veinMat = new THREE.LineBasicMaterial({ color: col(H(285), 0.75, 0.34), transparent: true, opacity: 0.8 });
    var cysts = [];
    for (var z = 0; z < 14; z++) {
      var zu = rng() * Math.PI * 2, zv = Math.acos(2 * rng() - 1);
      var zn = new THREE.Vector3(Math.sin(zv) * Math.cos(zu), Math.cos(zv), Math.sin(zv) * Math.sin(zu));
      var cr = 1.6 + rng() * 2.6;
      var cm2 = new THREE.Mesh(new THREE.SphereGeometry(cr, 10, 8, 0, Math.PI * 2, 0, Math.PI * 0.62), cystMat);
      cm2.position.copy(zn).multiplyScalar(R + cr * 0.18);
      cm2.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), zn);
      g.add(cm2);
      cysts.push({ mesh: cm2, base: cr, phase: rng() * 6.28, n: zn });
      /* 菌丝 */
      var vp = [];
      for (var s = 0; s < 5; s++) {
        var ang = rng() * 6.28;
        var p0 = zn.clone().multiplyScalar(R + 0.4);
        var tangent = new THREE.Vector3(-Math.sin(ang), 0, Math.cos(ang)).normalize();
        var p1 = p0.clone().add(tangent.multiplyScalar(3 + rng() * 4)).normalize().multiplyScalar(R + 0.4);
        vp.push(p0); vp.push(p1);
      }
      if (vp.length) g.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(vp), veinMat));
    }
    extra.updaters.push(function (t) {
      for (var i = 0; i < cysts.length; i++) {
        var c = cysts[i];
        var s = 1 + 0.22 * Math.sin(t * 3.2 + c.phase);
        c.mesh.scale.set(s, s * (0.9 + 0.2 * Math.sin(t * 2.4 + c.phase)), s);
      }
    });
  }

  else if (manifId === 'shattered_cataclysm') {
    /* 裂开的壳：地表电弧 + 外圈碎片环 */
    var arcMat = new THREE.LineBasicMaterial({ color: col(H(190), 0.9, 0.72), transparent: true, opacity: 0.9 });
    var arcs = [];
    for (var ai = 0; ai < 7; ai++) {
      var ap = [];
      var a0 = rng() * Math.PI * 2, v0 = Math.acos(2 * rng() - 1);
      var segs = 5;
      for (var si = 0; si <= segs; si++) {
        var aa = a0 + si * 0.16;
        var jitter = 1 + (rng() - 0.5) * 0.05;
        ap.push(new THREE.Vector3(
          Math.sin(v0) * Math.cos(aa) * R * jitter,
          Math.cos(v0) * R * jitter,
          Math.sin(v0) * Math.sin(aa) * R * jitter));
      }
      var line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(ap), arcMat.clone());
      g.add(line);
      arcs.push(line);
    }
    /* 碎片环 */
    var shardGeo = new THREE.TetrahedronGeometry(1, 0);
    var shardMat = new THREE.MeshStandardMaterial({ color: col(H(30), 0.35, 0.32), roughness: 0.9, flatShading: true });
    var shards = new THREE.InstancedMesh(shardGeo, shardMat, 260);
    var dummy = new THREE.Object3D();
    for (var si2 = 0; si2 < 260; si2++) {
      var ang2 = rng() * Math.PI * 2;
      var rr = R * (1.5 + rng() * 0.65);
      dummy.position.set(Math.cos(ang2) * rr, (rng() - 0.5) * 5, Math.sin(ang2) * rr);
      dummy.rotation.set(rng() * 6.28, rng() * 6.28, rng() * 6.28);
      dummy.scale.setScalar(0.5 + rng() * 1.4);
      dummy.updateMatrix();
      shards.setMatrixAt(si2, dummy.matrix);
    }
    shards.instanceMatrix.needsUpdate = true;
    shards.rotation.x = 0.32;
    g.add(shards);
    extra.updaters.push(function (t) {
      shards.rotation.y = t * 0.16;
      for (var i = 0; i < arcs.length; i++) {
        arcs[i].material.opacity = 0.35 + 0.6 * Math.abs(Math.sin(t * 6 + i * 1.7));
      }
    });
  }

  else if (manifId === 'super_storm') {
    /* 极光冥环：上下两个亮环 + 雷暴闪光 */
    var ringMat = new THREE.MeshBasicMaterial({
      color: col(H(150), 0.95, 0.6), transparent: true, opacity: 0.55,
      side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false
    });
    for (var sy = -1; sy <= 1; sy += 2) {
      var rg = new THREE.TorusGeometry(R * 0.62, 0.9, 8, 64);
      var rm = new THREE.Mesh(rg, ringMat);
      rm.rotation.x = Math.PI / 2;
      rm.position.y = sy * R * 0.78;
      g.add(rm);
    }
    var flashMat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false
    });
    var flash = new THREE.Mesh(new THREE.SphereGeometry(R * 1.02, 24, 16), flashMat);
    g.add(flash);
    extra.updaters.push(function (t) {
      flashMat.opacity = Math.sin(t * 8.5) > 0.86 ? 0.28 : 0;
      ringMat.opacity = 0.42 + 0.2 * Math.sin(t * 1.8);
    });
  }

  else if (manifId === 'cyber_metropolis') {
    /* 霓虹网格：经纬亮线 + 夜面城市光点 */
    var neonMat = new THREE.LineBasicMaterial({ color: col(H(190), 0.95, 0.6), transparent: true, opacity: 0.55 });
    for (var lat = -3; lat <= 3; lat++) {
      var phi = lat * 0.34;
      var rr2 = Math.cos(phi) * (R + 0.5), yy = Math.sin(phi) * (R + 0.5);
      var pts2 = [];
      for (var s2 = 0; s2 <= 72; s2++) {
        var a2 = s2 / 72 * Math.PI * 2;
        pts2.push(new THREE.Vector3(Math.cos(a2) * rr2, yy, Math.sin(a2) * rr2));
      }
      g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts2), neonMat));
    }
    for (var lon = 0; lon < 12; lon++) {
      var la = lon / 12 * Math.PI * 2, pts3 = [];
      for (var s3 = 0; s3 <= 48; s3++) {
        var p3 = s3 / 48 * Math.PI;
        pts3.push(new THREE.Vector3(
          Math.sin(p3) * Math.cos(la) * (R + 0.5),
          Math.cos(p3) * (R + 0.5),
          Math.sin(p3) * Math.sin(la) * (R + 0.5)));
      }
      g.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts3), neonMat));
    }
    /* 城市光点 */
    var cityGeo = new THREE.BufferGeometry();
    var cp = [];
    for (var ci = 0; ci < 900; ci++) {
      var cu = rng() * Math.PI * 2, cv = Math.acos(2 * rng() - 1);
      cp.push(Math.sin(cv) * Math.cos(cu) * (R + 0.7),
              Math.cos(cv) * (R + 0.7),
              Math.sin(cv) * Math.sin(cu) * (R + 0.7));
    }
    cityGeo.setAttribute('position', new THREE.Float32BufferAttribute(cp, 3));
    var cityMat = new THREE.PointsMaterial({ color: col(H(45), 0.9, 0.7), size: 0.85, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false });
    g.add(new THREE.Points(cityGeo, cityMat));
    extra.updaters.push(function (t) {
      cityMat.opacity = 0.7 + 0.25 * Math.sin(t * 3.4);
      neonMat.opacity = 0.42 + 0.18 * Math.sin(t * 1.3);
    });
  }

  else if (manifId === 'dark_void') {
    /* 幽冥辉光：暗色外壳 + 紫色边缘 */
    var shellMat = new THREE.ShaderMaterial({
      vertexShader: 'varying vec3 vN; void main(){ vN = normalize(normalMatrix * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
      fragmentShader: 'varying vec3 vN; uniform vec3 uC; void main(){ float i = pow(max(0.0, 0.72 - dot(vN, vec3(0,0,1))), 3.0); gl_FragColor = vec4(uC, 1.0) * i * 1.4; }',
      uniforms: { uC: { value: col(H(270), 0.85, 0.5) } },
      blending: THREE.AdditiveBlending, side: THREE.BackSide, transparent: true, depthWrite: false
    });
    var shell = new THREE.Mesh(new THREE.SphereGeometry(R * 1.18, 32, 24), shellMat);
    g.add(shell);
    if (planet.terrainMesh && planet.terrainMesh.material) {
      planet.terrainMesh.material.color.multiplyScalar(0.35);
    }
    extra.updaters.push(function (t) {
      shell.rotation.y = -t * 0.06;
    });
  }

  return extra;
}
'''

# 插到 sf-planet-gl 的 TIER_LOOK 之前
anchor = '  /* Tier -> preset + presentation.'
i = html.find(anchor)
assert i > 0, 'anchor not found'
html = html[:i] + MODULE + '\n\n' + html[i:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('manif module injected,', len(MODULE), 'chars')
