
# -*- coding: utf-8 -*-
"""v235 - 用 planet_studio.html 的 three.js LivingPlanet 替换手写 WebGL shader。"""
import sys, re
from pathlib import Path

BASE = Path(r'D:\items\code\projects\starfield\starfield-pub')
HTML = BASE / 'starfield.html'
STUDIO = BASE / 'planet_studio.html'

html = HTML.read_text(encoding='utf-8', errors='replace')
studio = STUDIO.read_text(encoding='utf-8', errors='replace')


def grab(src, start_marker):
    i = src.find(start_marker)
    assert i >= 0, start_marker
    depth = 0; started = False; j = i
    while j < len(src):
        c = src[j]
        if c == '{':
            depth += 1; started = True
        elif c == '}':
            depth -= 1
            if started and depth == 0:
                return src[i:j + 1]
        j += 1
    raise AssertionError('unbalanced ' + start_marker)


simplex = grab(studio, 'class SimplexNoise')
living = grab(studio, 'class LivingPlanet')

# Presets
i = studio.find('const Presets = {')
depth = 0; started = False; j = i
while j < len(studio):
    c = studio[j]
    if c == '{':
        depth += 1; started = True
    elif c == '}':
        depth -= 1
        if started and depth == 0:
            presets = studio[i:j + 1] + ';'
            break
    j += 1

# 去掉 LivingPlanet 里对全局 PlanetConfig / Presets 的依赖，改成 this.cfg
living = living.replace('PlanetConfig.', 'this.cfg.')
living = living.replace('Presets[this.cfg.preset]', 'Presets[this.cfg.preset]')

NEW = '''<script id="sf-planet-gl">
/* v235 - three.js LivingPlanet planet renderer.
 * Reuses SimplexNoise + LivingPlanet from planet_studio.html:
 * vertex-colored terrain, ocean shell, clouds, fresnel atmosphere,
 * instanced flora, monuments and fauna. Replaces the hand-written
 * fullscreen fragment shader used up to v234.
 * frame(planet) returns false to let the Canvas2D path draw instead. */
(function () {
  if (window.SFPlanetGL && window.SFPlanetGL.rev === 235) return;

__SIMPLEX__

__PRESETS__

  /* Tier -> preset + presentation. This is what makes the rarities
   * read differently at a glance instead of only shifting hue. */
  var TIER_LOOK = {
    common: { preset: 'archipelago',        trees: 900,  monuments: 1, fauna: 1, clouds: 0.34, spin: 1.0, scale: 0.86, rim: 0.55, ring: 0, moons: 0, tilt: 0.18, light: 1.05 },
    rare:   { preset: 'desert_oasis',       trees: 1100, monuments: 2, fauna: 1, clouds: 0.30, spin: 1.15, scale: 0.90, rim: 0.72, ring: 1, moons: 1, tilt: 0.22, light: 1.15 },
    epic:   { preset: 'forest',             trees: 2100, monuments: 3, fauna: 2, clouds: 0.48, spin: 1.3, scale: 0.94, rim: 0.92, ring: 1, moons: 2, tilt: 0.26, light: 1.28 },
    legend: { preset: 'monument',           trees: 700,  monuments: 4, fauna: 2, clouds: 0.36, spin: 1.5, scale: 0.98, rim: 1.15, ring: 2, moons: 3, tilt: 0.30, light: 1.42 },
    myth:   { preset: 'alien',              trees: 1700, monuments: 4, fauna: 3, clouds: 0.52, spin: 1.7, scale: 1.00, rim: 1.45, ring: 2, moons: 3, tilt: 0.34, light: 1.55 }
  };

  function hexToHsl(hex) {
    var r = parseInt(hex.slice(1, 3), 16) / 255,
        g = parseInt(hex.slice(3, 5), 16) / 255,
        b = parseInt(hex.slice(5, 7), 16) / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    var l = (mx + mn) / 2, h = 0, s = 0;
    if (mx !== mn) {
      var d = mx - mn;
      s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
      if (mx === r) h = (g - b) / d + (g < b ? 6 : 0);
      else if (mx === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h /= 6;
    }
    return [h * 360, s, l];
  }

  function hsl(h, s, l) {
    h = ((h % 360) + 360) % 360 / 360;
    var a = s * Math.min(l, 1 - l);
    function f(n) {
      var k = (n + h * 12) % 12;
      return Math.round(255 * (l - a * Math.max(-1, Math.min(Math.min(k - 3, 9 - k), 1))));
    }
    var v = function (x) { return ('0' + x.toString(16)).slice(-2); };
    return '#' + v(f(0)) + v(f(8)) + v(f(4));
  }

  /* Recolor a preset toward the planet hue so every core keeps its own
   * identity while the tier still controls composition. */
  function tintPreset(baseColors, hue, satBoost, lightBoost) {
    var out = {};
    for (var k in baseColors) {
      if (k === 'waterTrans') { out[k] = baseColors[k]; continue; }
      var hslv = hexToHsl(baseColors[k]);
      var h = (hue + (hslv[0] - 200) * 0.35 + 360) % 360;
      var s = Math.min(1, hslv[1] * satBoost);
      var l = Math.min(0.98, hslv[2] * lightBoost);
      out[k] = hsl(h, s, l);
    }
    return out;
  }

  var host = null, renderer = null, scene = null, camera = null,
      planet = null, sun = null, rimLight = null, amb = null,
      ok = false, failed = false, curKey = '', ringMeshes = [], moonMeshes = [],
      startT = 0, look = null;

  function boot(canvas2d) {
    if (typeof THREE === 'undefined') return false;
    host = canvas2d.parentNode;
    if (!host) return false;

    var c = document.createElement('canvas');
    c.className = 'sf-planet-gl';
    c.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;' +
      'border-radius:50%;pointer-events:none;z-index:2;';
    host.appendChild(c);

    renderer = new THREE.WebGLRenderer({
      canvas: c, antialias: true, alpha: true, powerPreference: 'high-performance'
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    if (renderer.outputEncoding !== undefined) renderer.outputEncoding = THREE.sRGBEncoding;

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(38, 1, 0.1, 2000);
    camera.position.set(0, 0, 118);
    camera.lookAt(0, 0, 0);

    amb = new THREE.AmbientLight(0xffffff, 0.52);
    scene.add(amb);

    sun = new THREE.DirectionalLight(0xfff6e2, 1.35);
    sun.position.set(-96, 58, 92);
    scene.add(sun);

    rimLight = new THREE.DirectionalLight(0x6f9bd6, 0.62);
    rimLight.position.set(88, -46, -78);
    scene.add(rimLight);

    ok = true;
    return true;
  }

  function disposePlanet() {
    if (!planet) return;
    for (var i = 0; i < planet.group.children.length; i++) {
      var o = planet.group.children[i];
      if (o.geometry) o.geometry.dispose();
      if (o.material) {
        if (Array.isArray(o.material)) o.material.forEach(function (m) { m.dispose(); });
        else o.material.dispose();
      }
    }
    scene.remove(planet.group);
    planet = null;
    ringMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    ringMeshes = [];
    moonMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    moonMeshes = [];
  }

  function buildFor(item) {
    disposePlanet();
    var tier = item.tier || 'common';
    var L = TIER_LOOK[tier] || TIER_LOOK.common;
    var hue = item.hue || 200;

    var basePreset = Presets[L.preset] || Presets.archipelago;
    var satBoost = tier === 'myth' ? 1.45 : tier === 'legend' ? 1.3 : tier === 'epic' ? 1.18 : 1.0;
    var lightBoost = tier === 'myth' ? 1.22 : tier === 'legend' ? 1.12 : 1.0;

    var cfg = {
      radius: 36,
      seed: (item.hue || 200) * 31 + (item.id ? item.id.length * 7 : 0) + 12345,
      preset: L.preset,
      landRatio: basePreset.landRatio,
      ruggedness: basePreset.ruggedness * (tier === 'myth' ? 1.35 : tier === 'legend' ? 1.2 : 1.0),
      treeCount: L.trees,
      monumentLevel: L.monuments,
      faunaLevel: L.fauna,
      cloudCoverage: L.clouds,
      spinSpeed: L.spin,
      colors: tintPreset(basePreset.colors, hue, satBoost, lightBoost)
    };

    planet = new LivingPlanet(scene);
    planet.cfg = cfg;
    planet.build();

    var s = L.scale;
    planet.group.scale.setScalar(s);
    planet.group.rotation.z = L.tilt;

    sun.intensity = L.light;
    rimLight.intensity = 0.30 + L.rim * 0.42;
    amb.intensity = 0.40 + L.rim * 0.10;

    /* Rings: legend gets two, myth gets a bright inner band too. */
    for (var r = 0; r < L.ring; r++) {
      var inner = 36 * (1.42 + r * 0.30);
      var outer = inner + 36 * (r === 0 ? 0.20 : 0.13);
      var rg = new THREE.RingGeometry(inner, outer, 128, 1);
      var rm = new THREE.MeshBasicMaterial({
        color: new THREE.Color(hsl(hue, 0.55, r === 0 ? 0.66 : 0.52)),
        side: THREE.DoubleSide, transparent: true,
        opacity: r === 0 ? 0.42 : 0.26, depthWrite: false
      });
      var ring = new THREE.Mesh(rg, rm);
      ring.rotation.x = Math.PI / 2 - 0.30;
      ring.rotation.z = L.tilt;
      scene.add(ring);
      ringMeshes.push(ring);
    }

    /* Moons */
    for (var m = 0; m < L.moons; m++) {
      var mg = new THREE.IcosahedronGeometry(2.2 + m * 0.5, 1);
      var mm = new THREE.MeshStandardMaterial({
        color: new THREE.Color(hsl(hue, 0.28, 0.58)),
        roughness: 0.85, metalness: 0.05, flatShading: true
      });
      var moon = new THREE.Mesh(mg, mm);
      scene.add(moon);
      moon.userData = { phase: m * 2.1, orbit: 52 + m * 13, speed: 0.42 - m * 0.06 };
      moonMeshes.push(moon);
    }

    startT = performance.now();
    curKey = tier + '|' + hue;
  }

  function sizeTo(canvas2d) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var box = canvas2d.getBoundingClientRect();
    var w = Math.max(64, Math.round((box.width || 222) * dpr));
    var h = w;
    if (renderer.domElement.width !== w || renderer.domElement.height !== h) {
      renderer.setSize(w, h, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    }
  }

  window.SFPlanetGL = {
    rev: 235,
    frame: function (p) {
      if (failed) return false;
      if (!ok) {
        if (!boot(p.canvas)) { failed = true; return false; }
      }
      if (!renderer) return false;
      if (renderer.getContext().isContextLost && renderer.getContext().isContextLost()) {
        failed = true; return false;
      }

      sizeTo(p.canvas);

      var item = p.item || {};
      var key = (item.tier || 'common') + '|' + (item.hue || 200);
      if (key !== curKey) buildFor(item);

      var t = (performance.now() - startT) / 1000;

      /* Manual spin drives the planet yaw; drag still feels direct. */
      if (planet) {
        planet.group.rotation.y = p.rotY || 0;
        planet.group.rotation.x = (p.rotX || 0) * 0.35;
      }

      for (var i = 0; i < moonMeshes.length; i++) {
        var mo = moonMeshes[i], ud = mo.userData;
        var a = t * ud.speed + ud.phase;
        mo.position.set(Math.cos(a) * ud.orbit, Math.sin(a * 0.6) * 9, Math.sin(a) * ud.orbit);
      }

      planet.update(t, 1 / 60);

      renderer.render(scene, camera);
      return true;
    },
    isOn: function () { return ok; }
  };
})();
</script>
'''

NEW = NEW.replace('__SIMPLEX__', simplex)
NEW = NEW.replace('__PRESETS__', presets)

i = html.find('<script id="sf-planet-gl">')
j = html.find('</script>', i) + len('</script>')
assert i > 0 and j > i
html = html[:i] + NEW + html[j:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('replaced sf-planet-gl with three.js renderer')
print('  SimplexNoise', len(simplex), 'chars')
print('  LivingPlanet', len(living), 'chars')
print('  Presets', len(presets), 'chars')
