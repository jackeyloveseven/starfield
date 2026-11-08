
# -*- coding: utf-8 -*-
"""v273 - 地表飞行模式：进入星球低空，环境随形态变化。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   地表飞行模式（Surface）
   从太空巡航下降到星球低空，贴着地表飞行。
   环境类型与星球形态 manif 绑定：原始生态 / 类地文明 / 发达城市 / 未来科技。
   复用 three.js LivingPlanet 地形与植被系统。
   巡航 frame() 在 currentMode !== 'cruise' 时直接 return，互不干扰。
   ============================================================ */
(function () {
  if (window.SFSurface) return;

  /* manif -> 地表环境。建筑种类与密度是文明等级的主要区别。 */
  var ENVS = {
    earth_egg:         { label: '类地文明',   preset: 'archipelago',  trees: 1500, buildings: 70,  kind: 'tower',   sky: 0x0d1a2a, fog: 0x1c2f42 },
    cyber_metropolis:  { label: '发达城市',   preset: 'monument',     trees: 90,   buildings: 200, kind: 'tower',   sky: 0x080b14, fog: 0x141a26 },
    protoss_crystal:   { label: '未来科技',   preset: 'alien',        trees: 260,  buildings: 60,  kind: 'crystal', sky: 0x140a26, fog: 0x241238 },
    zerg_biomorphic:   { label: '原始有机',   preset: 'forest',       trees: 1100, buildings: 26,  kind: 'cyst',    sky: 0x160a12, fog: 0x28141f },
    dune_arrakis:      { label: '荒漠戈壁',   preset: 'desert_oasis', trees: 70,   buildings: 12,  kind: 'rock',    sky: 0x241a10, fog: 0x3a2a18 },
    shattered_cataclysm:{ label: '灾变废墟',  preset: 'monument',     trees: 60,   buildings: 46,  kind: 'ruin',    sky: 0x140f0f, fog: 0x241a18 },
    super_storm:       { label: '雷暴云海外', preset: 'abyss',        trees: 40,   buildings: 8,   kind: 'rock',    sky: 0x0a1418, fog: 0x14242a },
    dark_void:         { label: '幽冥虚空',   preset: 'abyss',        trees: 30,   buildings: 10,  kind: 'crystal', sky: 0x0a0812, fog: 0x161024 },
    skimming_water:    { label: '水世界浅滩', preset: 'archipelago',  trees: 700,  buildings: 20,  kind: 'tower',   sky: 0x0c1a26, fog: 0x18303e },
    mothership_fleet:  { label: '工业船坞',   preset: 'monument',     trees: 120,  buildings: 120, kind: 'tower',   sky: 0x0a0e16, fog: 0x161e28 }
  };
  var DEFAULT_ENV = { label: '原始生态', preset: 'archipelago', trees: 1600, buildings: 0, kind: 'rock', sky: 0x0e1a24, fog: 0x1c2c38 };

  var active = false, renderer = null, scene = null, camera = null,
      planet = null, cityGroup = null, raf = 0, t0 = 0,
      container = null, titleEl = null, curEnv = null;

  function sph(th, ph, r, out) {
    out = out || new THREE.Vector3();
    out.set(r * Math.sin(ph) * Math.cos(th), r * Math.cos(ph), r * Math.sin(ph) * Math.sin(th));
    return out;
  }

  /* 建筑：贴地表、法线对齐。文明等级靠它和树木密度区分。 */
  function buildCity(env, R, rng) {
    var group = new THREE.Group();
    var up = new THREE.Vector3(0, 1, 0);
    for (var i = 0; i < env.buildings; i++) {
      var u = rng() * Math.PI * 2, v = Math.acos(2 * rng() - 1);
      var n = new THREE.Vector3(Math.sin(v) * Math.cos(u), Math.cos(v), Math.sin(v) * Math.sin(u));
      var g, m;
      if (env.kind === 'tower') {
        var h = 1.5 + rng() * 5.5, w = 0.5 + rng() * 0.7;
        g = new THREE.BoxGeometry(w, h, w);
        m = new THREE.MeshStandardMaterial({
          color: new THREE.Color().setHSL(0.58, 0.18, 0.30 + rng() * 0.2),
          roughness: 0.6, metalness: 0.35,
          emissive: new THREE.Color().setHSL(0.55, 0.7, 0.10), flatShading: true
        });
      } else if (env.kind === 'crystal') {
        var hh = 2 + rng() * 5;
        g = new THREE.OctahedronGeometry(1, 0);
        m = new THREE.MeshPhysicalMaterial({
          color: new THREE.Color().setHSL(0.54, 0.85, 0.6),
          roughness: 0.06, metalness: 0.1, clearcoat: 1,
          emissive: new THREE.Color().setHSL(0.54, 0.9, 0.24), flatShading: true
        });
        var mesh0 = new THREE.Mesh(g, m);
        mesh0.scale.set(0.8 + rng() * 0.6, hh, 0.8 + rng() * 0.6);
        mesh0.position.copy(n).multiplyScalar(R + hh * 0.4 + 4);
        mesh0.quaternion.setFromUnitVectors(up, n);
        group.add(mesh0);
        continue;
      } else if (env.kind === 'cyst') {
        var cr = 0.8 + rng() * 1.4;
        g = new THREE.SphereGeometry(cr, 8, 6, 0, Math.PI * 2, 0, Math.PI * 0.6);
        m = new THREE.MeshStandardMaterial({
          color: new THREE.Color().setHSL(0.9, 0.7, 0.32),
          roughness: 0.5, emissive: new THREE.Color().setHSL(0.92, 0.8, 0.08), flatShading: true
        });
        var cm = new THREE.Mesh(g, m);
        cm.position.copy(n).multiplyScalar(R + 4.4);
        cm.quaternion.setFromUnitVectors(up, n);
        group.add(cm);
        continue;
      } else { /* rock / ruin */
        var rh = 0.8 + rng() * 2.4;
        g = new THREE.DodecahedronGeometry(rh * 0.6, 0);
        m = new THREE.MeshStandardMaterial({
          color: new THREE.Color().setHSL(0.08, 0.2, 0.26),
          roughness: 0.95, flatShading: true
        });
      }
      var mesh = new THREE.Mesh(g, m);
      mesh.position.copy(n).multiplyScalar(R + 4.2);
      mesh.quaternion.setFromUnitVectors(up, n);
      group.add(mesh);
    }
    return group;
  }

  function makeUI() {
    container = document.createElement('div');
    container.id = 'sf-surface-ui';
    container.style.cssText = 'position:fixed;inset:0;z-index:600;pointer-events:none;' +
      'font-family:var(--ui-mono,monospace);color:rgba(235,242,248,.85);';
    container.innerHTML =
      '<canvas id="sf-surface-canvas" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:auto"></canvas>' +
      '<div style="position:absolute;top:26px;left:0;right:0;text-align:center">' +
      '  <div style="font-size:9px;letter-spacing:.34em;opacity:.5">DESCENT · LOW ORBIT</div>' +
      '  <div id="sf-surface-title" style="font-size:20px;letter-spacing:.18em;margin-top:10px"></div>' +
      '  <div id="sf-surface-env" style="font-size:10px;letter-spacing:.26em;margin-top:8px;opacity:.65"></div>' +
      '</div>' +
      '<div style="position:absolute;bottom:26px;left:0;right:0;text-align:center;font-size:9px;letter-spacing:.26em;opacity:.5">' +
      'ESC / L 返回太空 · 拖动改变航向</div>';
    document.body.appendChild(container);
    titleEl = container.querySelector('#sf-surface-title');
  }

  function removeUI() {
    if (container && container.parentNode) container.parentNode.removeChild(container);
    container = null;
  }

  function frame() {
    if (!active) return;
    raf = requestAnimationFrame(frame);
    var t = (performance.now() - t0) / 1000;
    var R = planet.cfg.radius;
    var alt = 7.5;
    var th = t * 0.055, ph = 1.12;

    /* 相机贴球面低空前进，up 取球面法线 —— 地形在下方掠过 */
    var pos = sph(th, ph, R + alt);
    var ahead = sph(th + 0.06, ph, R + alt);
    camera.position.copy(pos);
    camera.up.copy(pos).normalize();
    camera.lookAt(ahead);

    if (planet) planet.update(t, 1 / 60);
    renderer.render(scene, camera);
  }

  window.SFSurface = {
    isActive: function () { return active; },

    enter: function (opts) {
      opts = opts || {};
      if (active) return false;
      var G = window.SFPlanetGL;
      if (!G || !G.LivingPlanet || typeof THREE === 'undefined') return false;

      var manif = opts.manif || 'earth_egg';
      var env = ENVS[manif] || DEFAULT_ENV;
      curEnv = env;
      var hue = opts.hue || 200;

      makeUI();
      var cv = container.querySelector('#sf-surface-canvas');
      renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.setSize(window.innerWidth, window.innerHeight, false);

      scene = new THREE.Scene();
      scene.background = new THREE.Color(env.sky);
      scene.fog = new THREE.Fog(env.fog, 40, 190);

      camera = new THREE.PerspectiveCamera(62, window.innerWidth / window.innerHeight, 0.1, 800);

      scene.add(new THREE.AmbientLight(0xffffff, 0.55));
      var sun = new THREE.DirectionalLight(0xfff2dc, 1.15);
      sun.position.set(-70, 90, 60);
      scene.add(sun);
      var rim = new THREE.DirectionalLight(0x88aaff, 0.4);
      rim.position.set(60, -40, -70);
      scene.add(rim);

      /* 地形：沿用 LivingPlanet，但关掉云层，否则低空会被云挡住 */
      var preset = G.Presets[env.preset] || G.Presets.archipelago;
      var cfg = {
        radius: 36, seed: (hue * 31 + 99) >>> 0, preset: env.preset,
        landRatio: preset.landRatio, ruggedness: preset.ruggedness,
        treeCount: env.trees, monumentLevel: 0, faunaLevel: 0,
        cloudCoverage: 0, spinSpeed: 0, colors: preset.colors
      };
      planet = new G.LivingPlanet(scene, cfg);
      planet.build();
      if (planet.cloudsMesh) planet.cloudsMesh.visible = false;
      if (planet.atmosphereMesh) planet.atmosphereMesh.visible = false;

      var rng = (function (s) { return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })((hue * 77 + 13) >>> 0);
      cityGroup = buildCity(env, 36, rng);
      scene.add(cityGroup);

      titleEl.textContent = (opts.name || '未命名星体');
      container.querySelector('#sf-surface-env').textContent = env.label + ' · SURFACE FLIGHT';

      active = true;
      t0 = performance.now();
      if (typeof currentMode !== 'undefined') { try { currentMode = 'surface'; } catch (e) {} }
      window.currentMode = 'surface';
      frame();
      return true;
    },

    exit: function () {
      if (!active) return;
      active = false;
      cancelAnimationFrame(raf);
      if (renderer) {
        try { renderer.dispose(); renderer.forceContextLoss(); } catch (e) {}
      }
      renderer = null; scene = null; camera = null; planet = null; cityGroup = null;
      removeUI();
      if (typeof currentMode !== 'undefined') { try { currentMode = 'cruise'; } catch (e) {} }
      window.currentMode = 'cruise';
    },

    toggle: function (opts) {
      if (active) this.exit();
      else this.enter(opts);
    }
  };

  /* L 进入/离开当前接近的星球；ESC 返回 */
  window.addEventListener('keydown', function (e) {
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
    if (e.key === 'Escape' && window.SFSurface.isActive()) { window.SFSurface.exit(); return; }
    if (e.key.toLowerCase() === 'l' && !e.ctrlKey && !e.altKey && !e.metaKey) {
      if (window.SFSurface.isActive()) { window.SFSurface.exit(); return; }
      var OM = window.StarfieldOrbitalMechanics;
      var ap = OM && OM.activePlanet;
      var manif = (ap && ap.w && ap.w.manif && ap.w.manif.id) || 'earth_egg';
      var hue = (ap && ap.w && ap.w.hue) || (ap && ap.hue) || 200;
      var name = (ap && (ap.name || (ap.w && ap.w.name))) || '未命名星体';
      window.SFSurface.enter({ manif: manif, hue: hue, name: name });
    }
  });
})();
'''

body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-surface">' + MODULE + '\n</script>\n' + html[body_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('surface mode added,', len(MODULE), 'chars')
