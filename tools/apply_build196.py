# -*- coding: utf-8 -*-
"""
Build 196 (v1.9.9.9.9.8) Comprehensive Bug Fix & Optimization Script:
1. Fix 1 (P0: chunk(k) recursion stack overflow):
   In starfield.html (~L9705 & ~L9746), change chunks.has(pk) ? chunks.get(pk) : (pk >= 0 ? chunk(pk) : null)
   to chunks.get(pk) || null.
2. Fix 2 (P0: SpaceEventEngine float array index disabling all cosmic events):
   In starfield.html (~L8565), wrap evTypeIdx with Math.floor(hash(k, 239) * types.length).
3. Fix 3 (P0: TESS_IN / TESS_OUT float index crash):
   In starfield.html (~L12360 & ~L19082), wrap indices with Math.floor(hash(...) * TESS_IN.length).
4. Fix 4 (P1: encIndex O(k) linear loop):
   In starfield.html (~L9648-L9654), optimize linear loop with an O(1) 120-cycle lookup table.
5. Fix 5 (P1: SFPlanetGL facilityGroup GPU memory leak):
   In starfield.html (~L27655), traverse and dispose all geometries/materials and remove facilityGroup from scene in disposePlanet().
6. Fix 6 (P1: LivingPlanet monuments/whales deep dispose):
   In starfield.html (~L26819 & ~L27657), use obj.traverse(...) to dispose all nested geometries and materials.
7. Fix 7 (P2: GLB cache duplication):
   In starfield.html (~L28138-L28183), remove the duplicated _glbCache and scheduleGLBPrecompile declaration block.
8. Fix 8 (P1: ScannerRadar cyclic audio graph leak):
   In starfield.html (~L21110-L21142), schedule disconnection of delay/feedback/merger nodes after 3.2s.
9. Fix 9 (P1: WarpDrive permanent overclock lockup):
   In starfield.html (~L18535), allow WarpDrive.setHold(false) on keyup even if modal is open, and add blur & visibilitychange listeners.
10. Fix 10 (P2: Touch gesture touchcancel):
    In starfield.html (~L6198 & ~L22230), bind touchcancel alongside touchend.
11. Fix 11 (P1: Mobile orientationchange missing resize):
    In starfield.html (~L20216), call resize(); layoutTouch(); in the orientationchange timeout.
12. Fix 12 (P1: Android MainActivity.java lifecycle & constants):
    In MainActivity.java, implement onPause(), onResume(), and onDestroy() webView lifecycle cleanup, and replace hardcoded 500000 with MIN_HTML_BYTES.
13. Version bump to Build 196 (v1.9.9.9.9.8) across version.json, starfield.html, service-worker.js, and Android assets.
"""
import os
import sys
import json
import re
import shutil
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT, "starfield.html")
ANDROID_HTML = os.path.join(ROOT, "android", "app", "src", "main", "assets", "starfield.html")
VERSION_FILE = os.path.join(ROOT, "version.json")
ANDROID_VERSION = os.path.join(ROOT, "android", "app", "src", "main", "assets", "version.json")
SW_FILE = os.path.join(ROOT, "service-worker.js")
ANDROID_SW = os.path.join(ROOT, "android", "app", "src", "main", "assets", "service-worker.js")
STUDIO_FILE = os.path.join(ROOT, "planet_studio.html")
ANDROID_STUDIO = os.path.join(ROOT, "android", "app", "src", "main", "assets", "planet_studio.html")
JAVA_FILE = os.path.join(ROOT, "android", "app", "src", "main", "java", "com", "starfield", "focus", "MainActivity.java")


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def apply_step(content, target, repl, step_name):
    if repl in content:
        print(f"  [OK-ALREADY] {step_name}")
        return content
    elif target in content:
        print(f"  [APPLY] {step_name}")
        return content.replace(target, repl, 1)
    else:
        raise AssertionError(f"Target not found for step: {step_name}")


def apply_build196():
    print("=================================================================")
    print(" APPLYING BUILD 196 (v1.9.9.9.9.8) COMPREHENSIVE BUG FIXES")
    print("=================================================================")

    # -----------------------------------------------------------------
    # A. Patch starfield.html
    # -----------------------------------------------------------------
    print("1. Reading starfield.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # --- Fix 1: chunk(k) recursion stack overflow ---
    target_fix1_a = """   // Poisson Disk clearance check for encounter planet
   const prevMasses = [];
   for (let pk = k - 2; pk < k; pk++) {
     const pc = chunks.has(pk) ? chunks.get(pk) : (pk >= 0 ? chunk(pk) : null);
     if (pc && pc.masses) {
       for (let pi = 0; pi < pc.masses.length; pi++) prevMasses.push(pc.masses[pi]);
     }
   }"""
    repl_fix1_a = """   // Poisson Disk clearance check for encounter planet
   const prevMasses = [];
   for (let pk = k - 2; pk < k; pk++) {
     const pc = chunks.get(pk) || null;
     if (pc && pc.masses) {
       for (let pi = 0; pi < pc.masses.length; pi++) prevMasses.push(pc.masses[pi]);
     }
   }"""
    html = apply_step(html, target_fix1_a, repl_fix1_a, "Fix 1a: chunk(k) Poisson disk recursion removal")

    target_fix1_b = """   const numOmni = (r() < 0.35) ? 2 : 3;
   const prevMasses = [];
   for (let pk = k - 2; pk < k; pk++) {
     const pc = chunks.has(pk) ? chunks.get(pk) : (pk >= 0 ? chunk(pk) : null);
     if (pc && pc.masses) {
       for (let pi = 0; pi < pc.masses.length; pi++) prevMasses.push(pc.masses[pi]);
     }
   }"""
    repl_fix1_b = """   const numOmni = (r() < 0.35) ? 2 : 3;
   const prevMasses = [];
   for (let pk = k - 2; pk < k; pk++) {
     const pc = chunks.get(pk) || null;
     if (pc && pc.masses) {
       for (let pi = 0; pi < pc.masses.length; pi++) prevMasses.push(pc.masses[pi]);
     }
   }"""
    html = apply_step(html, target_fix1_b, repl_fix1_b, "Fix 1b: chunk(k) Omni masses recursion removal")

    # --- Fix 2: SpaceEventEngine float array index ---
    target_fix2 = """    // Deterministic variety distribution across chunks
    const evTypeIdx = (hash(k, 239) + Math.floor(r() * types.length)) % types.length;
    let type = types[evTypeIdx];"""
    repl_fix2 = """    // Deterministic variety distribution across chunks
    const evTypeIdx = (Math.floor(hash(k, 239) * types.length) + Math.floor(r() * types.length)) % types.length;
    let type = types[evTypeIdx];"""
    html = apply_step(html, target_fix2, repl_fix2, "Fix 2: SpaceEventEngine integer evTypeIdx")

    # --- Fix 3: TESS_IN / TESS_OUT float index crash ---
    target_fix3_in = """  // Once in a while the flight comes out the other side of the page.
  if(hash(cycle,707)<.45){tessT=1e-4;toast('五维空间 · TESSERACT',9);
   const L=TESS_IN[hash(cycle,707)%TESS_IN.length];Narrator.speak(L[1],{id:L[0],priority:2});}"""
    repl_fix3_in = """  // Once in a while the flight comes out the other side of the page.
  if(hash(cycle,707)<.45){tessT=1e-4;toast('五维空间 · TESSERACT',9);
   const L=TESS_IN[Math.floor(hash(cycle,707)*TESS_IN.length)];Narrator.speak(L[1],{id:L[0],priority:2});}"""
    html = apply_step(html, target_fix3_in, repl_fix3_in, "Fix 3a: TESS_IN integer index")

    target_fix3_out = """ if(tessT>0){tessT+=dt;drawTesseract();if(tessT>TESS_DUR){tessT=0;
   const L=TESS_OUT[hash(cycle,911)%TESS_OUT.length];Narrator.speak(L[1],{id:L[0],priority:1});}}"""
    repl_fix3_out = """ if(tessT>0){tessT+=dt;drawTesseract();if(tessT>TESS_DUR){tessT=0;
   const L=TESS_OUT[Math.floor(hash(cycle,911)*TESS_OUT.length)];Narrator.speak(L[1],{id:L[0],priority:1});}}"""
    html = apply_step(html, target_fix3_out, repl_fix3_out, "Fix 3b: TESS_OUT integer index")

    # --- Fix 4: encIndex O(k) linear loop optimization ---
    target_fix4_table = """function chunk(k){"""
    repl_fix4_table = """if (typeof window !== 'undefined') window.SpaceEventEngine = SpaceEventEngine;

// Precomputed O(1) 120-cycle lookup table for encounter indices (42 encounters per 120 chunks)
const _ENC_CYCLE_TABLE = (function() {
  const t = new Uint8Array(121);
  for (let c = 1; c <= 120; c++) {
    const nh = (c < 8 || c > 112);
    t[c] = t[c - 1] + ((!nh && (c % 5 === 2 || c % 5 === 4)) ? 1 : 0);
  }
  return t;
})();
if (typeof window !== 'undefined') window._ENC_CYCLE_TABLE = _ENC_CYCLE_TABLE;

function chunk(k){"""
    html = apply_step(html, target_fix4_table, repl_fix4_table, "Fix 4a: Define _ENC_CYCLE_TABLE")

    target_fix4_loop = """  let encIndex = 0;
  if(hasEncounter){
   for(let cand = 1; cand < k; cand++){
    const nh = (cand > 0 && (cand % 120 < 8 || cand % 120 > 112));
    if(!nh && (cand % 5 === 2 || cand % 5 === 4)) encIndex++;
   }
  }"""
    repl_fix4_loop = """  let encIndex = 0;
  if(hasEncounter){
   const candMax = k - 1;
   if(candMax > 0){
    encIndex = Math.floor(candMax / 120) * 42 + _ENC_CYCLE_TABLE[candMax % 120];
   }
  }"""
    html = apply_step(html, target_fix4_loop, repl_fix4_loop, "Fix 4b: O(1) encIndex calculation")

    # --- Fix 5 & 6b: SFPlanetGL facilityGroup GPU memory leak & traverse deep dispose ---
    target_fix5 = """  function disposePlanet() {
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
    if (outlineMesh) {
      if (outlineMesh.geometry) outlineMesh.geometry.dispose();
      if (outlineMesh.material) outlineMesh.material.dispose();
      outlineMesh = null;
    }
    ringMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    ringMeshes = [];
    moonMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    moonMeshes = [];
  }"""
    repl_fix5 = """  function disposePlanet() {
    if (facilityGroup) {
      facilityGroup.traverse(function (o) {
        if (o.geometry) o.geometry.dispose();
        if (o.material) {
          if (Array.isArray(o.material)) o.material.forEach(function (m) { m.dispose(); });
          else o.material.dispose();
        }
      });
      scene.remove(facilityGroup);
      facilityGroup = null;
    }
    if (!planet) return;
    for (var i = 0; i < planet.group.children.length; i++) {
      var o = planet.group.children[i];
      o.traverse(function (child) {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) child.material.forEach(function (m) { m.dispose(); });
          else child.material.dispose();
        }
      });
    }
    scene.remove(planet.group);
    planet = null;
    if (outlineMesh) {
      if (outlineMesh.geometry) outlineMesh.geometry.dispose();
      if (outlineMesh.material) outlineMesh.material.dispose();
      outlineMesh = null;
    }
    ringMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    ringMeshes = [];
    moonMeshes.forEach(function (m) { if (m.geometry) m.geometry.dispose(); if (m.material) m.material.dispose(); scene.remove(m); });
    moonMeshes = [];
  }"""
    html = apply_step(html, target_fix5, repl_fix5, "Fix 5 & 6b: SFPlanetGL facilityGroup & planet traverse deep dispose")

    # --- Fix 6a: LivingPlanet monuments/whales deep dispose ---
    target_fix6 = """    // Clean old
    while (this.group.children.length > 0) {
      const obj = this.group.children[0];
      this.group.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
        else obj.material.dispose();
      }
    }"""
    repl_fix6 = """    // Clean old
    while (this.group.children.length > 0) {
      const obj = this.group.children[0];
      this.group.remove(obj);
      obj.traverse(child => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
          else child.material.dispose();
        }
      });
    }"""
    html = apply_step(html, target_fix6, repl_fix6, "Fix 6a: LivingPlanet traverse deep dispose")

    # --- Fix 7: GLB cache duplication removal ---
    hdr = '/* GLB 缓存与空闲期预编译，消除切入地表时的 atob 与 parse 帧骤降 */'
    if html.count(hdr) == 1:
        print("  [OK-ALREADY] Fix 7: Duplicate _glbCache block already removed")
    elif html.count(hdr) == 2:
        idx1 = html.find(hdr)
        idx2 = html.find(hdr, idx1 + 1)
        tail = "  scheduleGLBPrecompile();\n\n  function sph(th, ph, r, out) {"
        idx_end = html.find(tail, idx2)
        if idx_end != -1:
            end_remove = idx_end + len("  scheduleGLBPrecompile();\n")
            html = html[:idx2] + html[end_remove:]
            print("  [APPLY] Fix 7: Removed duplicated _glbCache declaration block")
        else:
            raise AssertionError("Could not find end of duplicate _glbCache block")
    else:
        raise AssertionError(f"Unexpected count of GLB cache header: {html.count(hdr)}")

    # --- Fix 8: ScannerRadar cyclic audio graph leak ---
    target_fix8_expose = """  // Expose to window
  window.AnomalyScanner = AnomalyScanner;"""
    repl_fix8_expose = """  // Expose to window
  window.AnomalyScanner = AnomalyScanner;
  window.ScannerAudio = ScannerAudio;"""
    html = apply_step(html, target_fix8_expose, repl_fix8_expose, "Fix 8: Expose window.ScannerAudio")

    # --- Fix 5b: Expose SFPlanetGL.disposePlanet ---
    target_fix5_expose = """    isOn: function () { return ok; },
    LivingPlanet: LivingPlanet, Presets: Presets, SimplexNoise: SimplexNoise, tierLook: TIER_LOOK, manifFor: sfManifFor"""
    repl_fix5_expose = """    isOn: function () { return ok; },
    disposePlanet: disposePlanet,
    LivingPlanet: LivingPlanet, Presets: Presets, SimplexNoise: SimplexNoise, tierLook: TIER_LOOK, manifFor: sfManifFor"""
    html = apply_step(html, target_fix5_expose, repl_fix5_expose, "Fix 5b: Expose SFPlanetGL.disposePlanet")
    target_fix8 = """      delayL.connect(merger, 0, 0);
      delayR.connect(merger, 0, 1);

      sonarGain.connect(this.masterGain);
      merger.connect(this.masterGain);"""
    repl_fix8 = """      delayL.connect(merger, 0, 0);
      delayR.connect(merger, 0, 1);

      sonarGain.connect(this.masterGain);
      merger.connect(this.masterGain);

      // Clean up cyclic feedback loop after sonar ping decay (3.2s)
      setTimeout(() => {
        try {
          sonarGain.disconnect();
          filter.disconnect();
          delayL.disconnect();
          delayR.disconnect();
          feedbackL.disconnect();
          feedbackR.disconnect();
          merger.disconnect();
        } catch (_) {}
      }, 3200);"""
    html = apply_step(html, target_fix8, repl_fix8, "Fix 8: ScannerRadar cyclic audio graph disconnect")

    # --- Fix 9: WarpDrive permanent overclock lockup ---
    target_fix9 = """window.addEventListener('keyup', e => {
  if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) return;
  if (window.Starfield && typeof window.Starfield.isModalOpen === 'function' && window.Starfield.isModalOpen()) return;
  if (e.key === 'Shift' || e.code === 'KeyW') {
    WarpDrive.setHold(false);
  }
});"""
    repl_fix9 = """window.addEventListener('keyup', e => {
  if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) return;
  if (e.key === 'Shift' || e.code === 'KeyW') {
    if (typeof WarpDrive !== 'undefined' && WarpDrive.setHold) WarpDrive.setHold(false);
  }
});
window.addEventListener('blur', () => {
  if (typeof WarpDrive !== 'undefined' && WarpDrive.setHold) WarpDrive.setHold(false);
});
document.addEventListener('visibilitychange', () => {
  if (document.hidden && typeof WarpDrive !== 'undefined' && WarpDrive.setHold) {
    WarpDrive.setHold(false);
  }
});"""
    html = apply_step(html, target_fix9, repl_fix9, "Fix 9: WarpDrive modal keyup & blur/visibility protection")

    # --- Fix 10: Touch gesture touchcancel ---
    target_fix10_a = """      window.addEventListener('touchend', onEnd);
    },

    startTurntableLoop() {"""
    repl_fix10_a = """      window.addEventListener('touchend', onEnd);
      window.addEventListener('touchcancel', onEnd);
    },

    startTurntableLoop() {"""
    html = apply_step(html, target_fix10_a, repl_fix10_a, "Fix 10a: Turntable touchcancel listener")

    target_fix10_b = """        window.addEventListener('touchend', onUp);
      }

      // 6. Global Keydown Handlers (R, E, A, D, Left, Right, Escape)"""
    repl_fix10_b = """        window.addEventListener('touchend', onUp);
        window.addEventListener('touchcancel', onUp);
      }

      // 6. Global Keydown Handlers (R, E, A, D, Left, Right, Escape)"""
    html = apply_step(html, target_fix10_b, repl_fix10_b, "Fix 10b: Radar Scope touchcancel listener")

    # --- Fix 11: Mobile orientationchange missing resize ---
    target_fix11 = """  // Android fires resize before innerWidth has flipped; the delayed pass is
  // the one that lands in the new orientation.
  window.addEventListener('orientationchange', () => {
    layoutTouch();
    setTimeout(layoutTouch, 160);
  });"""
    repl_fix11 = """  // Android fires resize before innerWidth has flipped; the delayed pass is
  // the one that lands in the new orientation.
  window.addEventListener('orientationchange', () => {
    if (typeof resize === 'function') resize();
    layoutTouch();
    setTimeout(() => {
      if (typeof resize === 'function') resize();
      layoutTouch();
    }, 160);
  });"""
    html = apply_step(html, target_fix11, repl_fix11, "Fix 11: Mobile orientationchange resize + layoutTouch")

    # --- Version Bump in starfield.html ---
    target_v_tag = '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.7 (Build 195)</span>'
    repl_v_tag = '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.8 (Build 196)</span>'
    html = apply_step(html, target_v_tag, repl_v_tag, "Version Bump: UI Tag Build 196")

    target_v_build = 'const localBuild = 195;'
    repl_v_build = 'const localBuild = 196;'
    html = apply_step(html, target_v_build, repl_v_build, "Version Bump: OTA localBuild 196")

    print(f"2. Saving updated starfield.html ({len(html):,} chars)...")
    with open(HTML_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    # -----------------------------------------------------------------
    # B. Patch MainActivity.java
    # -----------------------------------------------------------------
    print("3. Reading MainActivity.java...")
    with open(JAVA_FILE, "r", encoding="utf-8") as f:
        java = f.read()

    target_j1 = """        if (activeHtml.exists() && activeHtml.length() > 500000) {
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            webView.loadUrl("file:///android_asset/starfield.html");
        }"""
    repl_j1 = """        if (activeHtml.exists() && activeHtml.length() >= MIN_HTML_BYTES) {
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            webView.loadUrl("file:///android_asset/starfield.html");
        }"""
    java = apply_step(java, target_j1, repl_j1, "Fix 12a: MainActivity activeHtml length check with MIN_HTML_BYTES")

    target_j2 = """                if (active.exists() && active.length() > 500000) {
                    webView.loadUrl("file://" + active.getAbsolutePath());
                } else {
                    webView.reload();
                }"""
    repl_j2 = """                if (active.exists() && active.length() >= MIN_HTML_BYTES) {
                    webView.loadUrl("file://" + active.getAbsolutePath());
                } else {
                    webView.reload();
                }"""
    java = apply_step(java, target_j2, repl_j2, "Fix 12b: MainActivity reloadApp length check with MIN_HTML_BYTES")

    target_j3 = """        @JavascriptInterface
        public long getOtaBuild() {
            File activeHtml = new File(getFilesDir(), "starfield_active.html");
            if (!activeHtml.exists() || activeHtml.length() <= 500000) {
                return 0L;
            }
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            return prefs.getLong(KEY_BUILD, 0L);
        }"""
    repl_j3 = """        @JavascriptInterface
        public long getOtaBuild() {
            File activeHtml = new File(getFilesDir(), "starfield_active.html");
            if (!activeHtml.exists() || activeHtml.length() < MIN_HTML_BYTES) {
                return 0L;
            }
            SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
            return prefs.getLong(KEY_BUILD, 0L);
        }"""
    java = apply_step(java, target_j3, repl_j3, "Fix 12c: MainActivity getOtaBuild length check with MIN_HTML_BYTES")

    target_j4 = """    @Override
    protected void onDestroy() {
        super.onDestroy();
        otaExecutor.shutdown();
    }"""
    repl_j4 = """    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.onPause();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        otaExecutor.shutdown();
        if (webView != null) {
            webView.onPause();
            webView.destroy();
            webView = null;
        }
    }""".replace("内", "")
    java = apply_step(java, target_j4, repl_j4, "Fix 12d: MainActivity lifecycle onPause, onResume, onDestroy")

    print(f"4. Saving updated MainActivity.java ({len(java):,} chars)...")
    with open(JAVA_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(java)

    # -----------------------------------------------------------------
    # C. Patch service-worker.js
    # -----------------------------------------------------------------
    print("5. Reading service-worker.js...")
    with open(SW_FILE, "r", encoding="utf-8") as f:
        sw = f.read()

    target_sw = "const CACHE_VERSION = 'v1.9.9.9.9.7-b195';"
    repl_sw = "const CACHE_VERSION = 'v1.9.9.9.9.8-b196';"
    sw = apply_step(sw, target_sw, repl_sw, "Version Bump: service-worker CACHE_VERSION b196")

    print("6. Saving updated service-worker.js...")
    with open(SW_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(sw)

    # -----------------------------------------------------------------
    # D. Patch version.json
    # -----------------------------------------------------------------
    print("7. Reading version.json...")
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["version"] = "1.9.9.9.9.8"
    meta["build"] = 196
    meta["updated_at"] = "2026-11-19T13:30:00+08:00"
    meta["title"] = "深度异常阻断与生命周期加固：根治区块递归爆栈与偶发崩溃，全面复苏全域宇宙事件 (Build 196)"
    meta["changelog"] = (
        "1. 根治超远航程下chunk(k)递归爆栈崩溃：解除Poisson Disk防重叠检测对前序区块的递归生成依赖，阻断RangeError最大调用栈溢出；\n"
        "2. 修复SpaceEventEngine浮点数索引导致的宇宙事件全域失效：修正evTypeIdx类型转换，全面复苏16类深空宇宙事件、雷达探测与叙事语音；\n"
        "3. 修复五维空间Tesseract出入场浮点索引未取整崩溃：防止加尔冈狂黑洞视界掠过与跃迁时报TypeError空引用异常；\n"
        "4. 优化encIndex星际遭遇索引线性检索：以O(1)的120区块周期查找表替代O(k)累加循环，大幅降低深空巡航CPU开销；\n"
        "5. 根治SFPlanetGL facilityGroup显存与对象泄漏：在disposePlanet中全面深度遍历释放地表设施网格几何体与材质，并移出场景；\n"
        "6. 强化LivingPlanet生物群系与宏伟奇观深度资源释放：在重新构建前使用obj.traverse遍历销毁所有嵌套网格、群系与材质，消除GPU显存泄漏；\n"
        "7. 清除SFPlanetGL中重复声明的_glbCache缓存字典与scheduleGLBPrecompile空闲期预编译块；\n"
        "8. 消除ScannerRadar声呐雷达探测立体声延迟环路音频图泄漏：在声呐回响衰减后（3.2s）自动切断并断开全部环路节点连接，解除WebAudio常驻累积；\n"
        "9. 根治WarpDrive超光速推进键位失焦永久超频锁死：允许弹窗激活时响应keyup释放加速，并追加window.onblur与visibilitychange安全降频保护；\n"
        "10. 补齐移动端触摸手势touchcancel事件监听，杜绝旋转底座与雷达示波器在来电或系统手势触发时永久处于拖拽吸附状态；\n"
        "11. 修复移动端屏幕旋转orientationchange未触发画布渲染重整：在延时阶段同步触发resize()与layoutTouch()，消除黑边与视口拉伸；\n"
        "12. 规范Android原生端MainActivity WebView生命周期与常量定义：实现onPause/onResume/onDestroy资源调度，以MIN_HTML_BYTES统一常量替代硬编码阈值。"
    )

    print("8. Saving updated version.json...")
    with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # -----------------------------------------------------------------
    # E. Mirror to Android assets & verify 100% SHA256 parity
    # -----------------------------------------------------------------
    print("9. Mirroring assets to Android assets folder...")
    shutil.copy2(HTML_FILE, ANDROID_HTML)
    shutil.copy2(VERSION_FILE, ANDROID_VERSION)
    shutil.copy2(SW_FILE, ANDROID_SW)
    shutil.copy2(STUDIO_FILE, ANDROID_STUDIO)

    print("10. Checking 100% SHA256 parity...")
    assert sha256_of_file(HTML_FILE) == sha256_of_file(ANDROID_HTML), "HTML SHA256 parity failed"
    assert sha256_of_file(VERSION_FILE) == sha256_of_file(ANDROID_VERSION), "VERSION SHA256 parity failed"
    assert sha256_of_file(SW_FILE) == sha256_of_file(ANDROID_SW), "SW SHA256 parity failed"
    assert sha256_of_file(STUDIO_FILE) == sha256_of_file(ANDROID_STUDIO), "STUDIO SHA256 parity failed"
    print("  [OK] 100% SHA256 Parity verified across all root and Android mirror assets!")

    print("=================================================================")
    print(" BUILD 196 (v1.9.9.9.9.8) APPLIED SUCCESSFULLY!")
    print("=================================================================")


if __name__ == "__main__":
    apply_build196()
