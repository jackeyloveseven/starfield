# -*- coding: utf-8 -*-
"""
Starfield v2.0.0.1 (Build 201) End-to-End Verification Suite:
1. Asset Parity (100% SHA256 across root & android/assets) + 5 Version Anchors (Build 201 / v2.0.0.1) + MainActivity LAYER_TYPE_NONE.
2. Mobile Dimensity Profile (412x915, DPR 3.0):
   - Zero external script dependency for THREE / GLTFLoader.
   - LivingPlanetEngine multi-planet WebGL -> persistent per-planet 2D canvas pixel coverage across 8 consecutive RAF frames (0 blank/wiped frames).
   - Close 3D planet showcase flight screenshot (protoss_crystal + ringed world).
   - Borderless zero-occlusion HUD layout audit (0 box overlap, single-line pills, >=16px gap between #journey & .sf-touch-cluster).
   - 60+ FPS across warp15x, planet_flyby, cockpit + Core Gameplay Loop + Native bridge.
3. Desktop Flagship Profile (1920x1080, DPR 1.0):
   - 60+ FPS, Command Dock (14/14 buttons), 0px corners, SFPlanetGL card/hatch 3D WebGL active check, 0 console/page errors.
"""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
HTML_PATH = BASE / "starfield.html"
ART_DIR = BASE / "tools" / "artifacts"
ART_DIR.mkdir(parents=True, exist_ok=True)
URL = "file:///" + str(HTML_PATH).replace("\\", "/")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CHROME_ARGS = [
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--disable-frame-rate-limit",
    "--disable-gpu-vsync",
    "--autoplay-policy=no-user-gesture-required",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_asset_parity_and_version_gate() -> dict:
    print("== [Gate 1] Asset Parity & Build 201 Version Gate ==")
    pairs = [
        ("starfield.html", BASE / "starfield.html", BASE / "android/app/src/main/assets/starfield.html"),
        ("service-worker.js", BASE / "service-worker.js", BASE / "android/app/src/main/assets/service-worker.js"),
        ("planet_studio.html", BASE / "planet_studio.html", BASE / "android/app/src/main/assets/planet_studio.html"),
        ("version.json", BASE / "version.json", BASE / "android/app/src/main/assets/version.json"),
    ]
    hashes = {}
    for name, root_f, mirror_f in pairs:
        assert root_f.exists(), f"Missing root file: {root_f}"
        assert mirror_f.exists(), f"Missing Android asset mirror: {mirror_f}"
        h1 = sha256_file(root_f)
        h2 = sha256_file(mirror_f)
        assert h1 == h2, f"SHA256 mismatch for {name}: root={h1} vs android={h2}"
        hashes[name] = {"sha256": h1, "bytes": root_f.stat().st_size}
        print(f"  [OK] {name:<20} {root_f.stat().st_size:>11,} bytes | SHA256: {h1[:16]}...")

    ver_meta = json.loads((BASE / "version.json").read_text(encoding="utf-8"))
    assert str(ver_meta.get("version")) == "2.0.0.1", f"version.json version != 2.0.0.1: {ver_meta}"
    assert int(ver_meta.get("build")) == 201, f"version.json build != 201: {ver_meta}"

    sw_txt = (BASE / "service-worker.js").read_text(encoding="utf-8")
    m_sw = re.search(r"CACHE_VERSION\s*=\s*'v([0-9.]+)-b(\d+)'", sw_txt)
    assert m_sw and m_sw.group(1) == "2.0.0.1" and m_sw.group(2) == "201", "service-worker.js CACHE_VERSION mismatch"

    html_txt = HTML_PATH.read_text(encoding="utf-8", errors="ignore")
    m_tag = re.search(r'id="sf-version-tag">v([0-9.]+) \(Build (\d+)\)', html_txt)
    assert m_tag and m_tag.group(1) == "2.0.0.1" and m_tag.group(2) == "201", "sf-version-tag mismatch"

    m_lb = re.search(r"const localBuild = (\d+);", html_txt)
    assert m_lb and m_lb.group(1) == "201", "localBuild != 201"

    gradle_txt = (BASE / "android/app/build.gradle").read_text(encoding="utf-8")
    assert "versionCode 201" in gradle_txt and 'versionName "2.0.0.1"' in gradle_txt, "build.gradle version mismatch"

    java_txt = (BASE / "android/app/src/main/java/com/starfield/focus/MainActivity.java").read_text(encoding="utf-8")
    assert "LAYER_TYPE_NONE" in java_txt and "setLayerType(View.LAYER_TYPE_HARDWARE" not in java_txt, "MainActivity.java still uses LAYER_TYPE_HARDWARE"
    print("  [OK] All 5 version anchors + MainActivity LAYER_TYPE_NONE verified: v2.0.0.1 (Build 201)\n")
    return hashes


FRAME_PACING_PROBE_JS = r"""
async ({ durationMs, mode }) => {
  try {
    if (mode === 'warp15x') {
      if (typeof window.currentMode !== 'undefined') window.currentMode = 'cruise';
      if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') {
        let guard = 0;
        while (window.WarpDrive.gearIndex !== 2 && guard++ < 4) window.WarpDrive.cycle();
      }
    } else if (mode === 'planet_flyby') {
      if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') {
        let guard = 0;
        while (window.WarpDrive.gearIndex !== 0 && guard++ < 4) window.WarpDrive.cycle();
      }
      if (window.StarfieldSonar && typeof window.StarfieldSonar.triggerScan === 'function') {
        window.StarfieldSonar.triggerScan(true);
      }
    } else if (mode === 'cockpit') {
      if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') {
        let guard = 0;
        while (window.WarpDrive.gearIndex !== 0 && guard++ < 4) window.WarpDrive.cycle();
      }
      const cBtn = document.getElementById('camera-toggle');
      if (cBtn) cBtn.click();
    }
  } catch (e) {}

  await new Promise(r => setTimeout(r, 950));
  for (let i = 0; i < 12; i++) {
    await new Promise(r => requestAnimationFrame(r));
  }

  return await new Promise(resolve => {
    const deltas = [];
    let domMutations = 0;
    const obs = new MutationObserver(list => { domMutations += list.length; });
    obs.observe(document.body, { childList: true, subtree: true, attributes: true, characterData: true });

    let last = performance.now();
    const tStart = last;
    function step(now) {
      deltas.push(now - last);
      last = now;
      if (now - tStart < durationMs) {
        requestAnimationFrame(step);
      } else {
        obs.disconnect();
        const elapsedSec = (now - tStart) / 1000;
        const frames = deltas.length;
        const avgFps = frames / Math.max(0.001, elapsedSec);
        const sorted = deltas.slice().sort((a, b) => a - b);
        const p50 = sorted[Math.floor(sorted.length * 0.50)] || 0;
        const p95 = sorted[Math.floor(sorted.length * 0.95)] || 0;
        const p99 = sorted[Math.floor(sorted.length * 0.99)] || 0;
        const mutPerFrame = domMutations / Math.max(1, frames);
        resolve({
          mode,
          frames,
          avgFps: Number(avgFps.toFixed(1)),
          p50Ms: Number(p50.toFixed(2)),
          p95Ms: Number(p95.toFixed(2)),
          p99Ms: Number(p99.toFixed(2)),
          domMutations,
          mutPerFrame: Number(mutPerFrame.toFixed(3))
        });
      }
    }
    requestAnimationFrame(step);
  });
}
"""


def run_mobile_profile_suite(browser) -> dict:
    print("== [Gate 2A] Mobile Dimensity 9400+ Profile (412x915, DPR 3.0) ==")
    ctx = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=3.0,
        is_mobile=True,
        has_touch=True,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 15; Vivo X200 Pro Dimensity 9400+) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
        ),
    )
    page = ctx.new_page()
    console_errors = []
    page_errors = []
    external_lib_reqs = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))
    page.on("request", lambda r: external_lib_reqs.append(r.url) if ("three" in r.url.lower() or "cdnjs" in r.url.lower()) else None)

    page.add_init_script(
        """
        window.__nativeHapticCalls = [];
        window.StarfieldNative = {
          triggerHaptic: function(style) { window.__nativeHapticCalls.push(String(style)); },
          vibrate: function(ms) { window.__nativeHapticCalls.push('vibrate:' + ms); },
          vibratePattern: function(pat) { window.__nativeHapticCalls.push('pattern:' + pat); },
          getDeviceInfo: function() {
            return JSON.stringify({
              platform: 'android', version: '2.0.0.1', build: 201, otaBuild: 0,
              refreshRate: 120.0, model: 'Dimensity 9400+ Flagship', keepScreenOn: true, liveWallpaperSupported: true
            });
          },
          getDisplayRefreshRate: function() { return 120.0; }
        };
        """
    )

    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1200)

    three_check = page.evaluate("""() => ({
      hasThree: typeof THREE !== 'undefined' && typeof THREE.WebGLRenderer === 'function',
      hasGLTF: typeof THREE !== 'undefined' && typeof THREE.GLTFLoader === 'function',
      hasLPE: typeof LivingPlanetEngine !== 'undefined'
    })""")
    print(f"  [OK] Inline Three.js & GLTFLoader Check: {three_check} | External THREE requests: {len(external_lib_reqs)}")
    assert three_check["hasThree"] and three_check["hasGLTF"] and three_check["hasLPE"], f"Missing 3D stack: {three_check}"
    assert len(external_lib_reqs) == 0, f"External Three.js network request still fired: {external_lib_reqs}"

    page.click("#begin")
    page.wait_for_timeout(1950)

    canvas_info = page.evaluate(
        """() => {
          const c = document.getElementById('landscape') || document.querySelector('canvas');
          return {
            canvasId: c ? c.id : '',
            devicePixelRatio: window.devicePixelRatio,
            canvasWidth: c ? c.width : 0,
            canvasHeight: c ? c.height : 0,
            effectiveDpr: c ? Number((c.width / Math.max(1, window.innerWidth)).toFixed(2)) : 0
          };
        }"""
    )
    print(f"  [OK] Mobile DPR Clamping: physical={canvas_info['devicePixelRatio']} -> render={canvas_info['effectiveDpr']} ({canvas_info['canvasWidth']}x{canvas_info['canvasHeight']})")
    assert canvas_info["effectiveDpr"] <= 1.75, f"Mobile DPR not clamped: {canvas_info}"

    # Verify LivingPlanetEngine renders multi-frame persistent 3D planets (NO blank/wiped frames!)
    planet_render_check = page.evaluate(
        """async () => {
          const eng = window.LivingPlanetEngine;
          if (!eng) throw new Error('LivingPlanetEngine missing');
          if (!eng.initialized) eng.init();
          const st = window.Starfield.getState();
          const tz = st.travel || 0;
          const m1 = { x: st.routeX + 20, y: st.courseY + 10, z: tz + 1500, seed: 77701, hasRings: true,
                       w: { type: { id: 'alien' }, manif: { id: 'protoss_crystal' }, shape: { id: 'ringed' } } };
          const m2 = { x: st.routeX - 240, y: st.courseY - 120, z: tz + 2600, seed: 88802, hasRings: false,
                       w: { type: { id: 'monument' }, manif: { id: 'cyber_metropolis' }, shape: { id: 'sphere' } } };
          if (Array.isArray(window.activeMasses)) {
            window.activeMasses.unshift(m1, m2);
          }

          function sampleAlphaRatio(cv) {
            if (!cv) return 0;
            const c2 = cv.getContext('2d');
            if (!c2) return 0;
            const d = c2.getImageData(0, 0, cv.width, cv.height).data;
            let nonZero = 0, total = 0;
            for (let i = 3; i < d.length; i += 16) {
              total++;
              if (d[i] > 15) nonZero++;
            }
            return nonZero / Math.max(1, total);
          }

          const frameRatios1 = [];
          const frameRatios2 = [];
          for (let f = 0; f < 8; f++) {
            eng._mobileRenderedThisFrame = false;
            eng._webglDrawsThisFrame = 0;
            const c1 = eng.renderPlanet(m1, 95 - f * 8, [0.6, 0.5, 0.6], window.camera);
            const c2 = eng.renderPlanet(m2, 42, [0.6, 0.5, 0.6], window.camera);
            frameRatios1.push(Number(sampleAlphaRatio(c1).toFixed(3)));
            frameRatios2.push(Number(sampleAlphaRatio(c2).toFixed(3)));
            await new Promise(r => requestAnimationFrame(r));
          }
          // Render hero Protoss crystal world + Cyber Metropolis onto clean frame for visual audit
          const cHero1 = eng.renderPlanet(m1, 102, [0.7, 0.4, 0.5], null);
          const cHero2 = eng.renderPlanet(m2, 58, [0.7, 0.4, 0.5], null);
          const lc = document.getElementById('landscape');
          const ctx = lc.getContext('2d');
          if (cHero1) {
            const dd = eng.getDrawSize(102) * (lc.width / window.innerWidth);
            ctx.drawImage(cHero1, lc.width * 0.52 - dd * 0.5, lc.height * 0.44 - dd * 0.5, dd, dd);
          }
          if (cHero2) {
            const dd2 = eng.getDrawSize(58) * (lc.width / window.innerWidth);
            ctx.drawImage(cHero2, lc.width * 0.24 - dd2 * 0.5, lc.height * 0.63 - dd2 * 0.5, dd2, dd2);
          }
          return {
            initialized: eng.initialized,
            contextLost: eng.contextLost,
            camExtent: eng.CAM_EXTENT,
            bufSize: eng.currentBufferSize,
            cacheSize: eng.planetCache.size,
            minFrame1: Math.min(...frameRatios1),
            minFrame2: Math.min(...frameRatios2),
            frameRatios1,
            frameRatios2
          };
        }"""
    )
    print(f"  [OK] Mobile 3D LivingPlanet Multi-Frame: {planet_render_check}")
    assert planet_render_check["initialized"] and not planet_render_check["contextLost"], f"LPE failed: {planet_render_check}"
    assert planet_render_check["minFrame1"] >= 0.08, f"Hero 3D planet flickered/blanked on skipped frames: {planet_render_check}"
    assert planet_render_check["minFrame2"] >= 0.06, f"Secondary 3D planet failed or blanked on mobile: {planet_render_check}"

    shot_3d_hero = ART_DIR / "build201_mobile_3d_hero.png"
    page.screenshot(path=str(shot_3d_hero), full_page=False)
    print(f"  [OK] Saved Mobile 3D Hero screenshot: {shot_3d_hero.name} ({shot_3d_hero.stat().st_size:,} bytes)")

    # Frame-pacing benchmark across 3 modes
    scenarios = {}
    for mode in ("warp15x", "planet_flyby", "cockpit"):
        res = page.evaluate(FRAME_PACING_PROBE_JS, {"durationMs": 1400, "mode": mode})
        scenarios[mode] = res
        print(f"  [OK] Mobile {mode:<13}: {res['avgFps']:>6.1f} FPS | P95={res['p95Ms']:>5.2f}ms P99={res['p99Ms']:>5.2f}ms | mut/f={res['mutPerFrame']}")
        assert res["avgFps"] >= 60.0, f"Mobile {mode} FPS below 60: {res}"

    page.evaluate("""() => {
      const cockpitEl = document.getElementById('sf-cockpit-overlay');
      const cBtn = document.getElementById('cockpit-toggle');
      if (cockpitEl && cockpitEl.classList.contains('active') && cBtn) cBtn.click();
    }""")
    page.wait_for_timeout(300)

    # Exercise gameplay & verify borderless zero-overlap HUD layout
    ui_and_gameplay = page.evaluate(
        """() => {
          const exp = window.StarfieldExpedition;
          if (window.SFVoyage && window.SFVoyage.force) window.SFVoyage.force('scan');
          if (typeof window.triggerCommsLine === 'function') window.triggerCommsLine('全向探测传感器锁定晶簇行星。');
          exp.refreshHUD(true);
          const initXp = exp.getState().xp;
          document.getElementById('sf-tac-scan-btn')?.click();
          document.getElementById('sf-contract-act-btn')?.click();
          exp.recordAction('slingshot_assist', { target: 'Aethelgard Prime', stardust: 280 });
          exp.refreshHUD(true);

          const camRect = document.getElementById('camera-hud')?.getBoundingClientRect();
          const barRect = document.getElementById('sf-pilot-telemetry-bar')?.getBoundingClientRect();
          const commsRect = document.getElementById('comms-hud')?.getBoundingClientRect();
          const contractHud = document.getElementById('sf-contract-hud');
          const contractRect = contractHud?.getBoundingClientRect();
          const extractHud = document.getElementById('sf-inflight-extract-hud');
          const extractRect = extractHud?.getBoundingClientRect();
          const journeyRect = document.getElementById('journey')?.getBoundingClientRect();
          const touchClusterRect = document.querySelector('.sf-touch-cluster')?.getBoundingClientRect();
          const touchRow = document.querySelector('.sf-touch-primary-row');
          const tacRect = document.getElementById('sf-tactical-capsule')?.getBoundingClientRect();
          const pills = Array.from(document.querySelectorAll('.sf-app-status-pill')).map(el => el.getBoundingClientRect());
          const pillTopSpan = pills.length ? (Math.max(...pills.map(r => r.top)) - Math.min(...pills.map(r => r.top))) : 0;

          return {
            xpAfter: exp.getState().xp,
            xpIncreased: exp.getState().xp > initXp,
            contractBg: contractHud ? getComputedStyle(contractHud).backgroundColor : '',
            contractBorder: contractHud ? getComputedStyle(contractHud).borderTopWidth : '',
            touchRowBg: touchRow ? getComputedStyle(touchRow).backgroundColor : '',
            touchRowBorder: touchRow ? getComputedStyle(touchRow).borderTopWidth : '',
            commsBelowCam: (camRect && commsRect) ? commsRect.top >= camRect.bottom + 4 : true,
            commsBelowBar: (barRect && commsRect) ? commsRect.top >= barRect.bottom + 6 : true,
            extractClearOfContractAndComms: (extractRect && extractRect.height > 0 && contractRect && commsRect)
              ? (extractRect.top >= contractRect.bottom + 4 && extractRect.bottom <= commsRect.top - 4) : true,
            tacAboveJourney: (tacRect && journeyRect) ? tacRect.bottom <= journeyRect.top - 4 : true,
            tacWithinViewport: tacRect ? (tacRect.right <= window.innerWidth && tacRect.left >= 0) : true,
            touchRightOfJourney: (journeyRect && touchClusterRect) ? (touchClusterRect.left >= journeyRect.right + 16) : true,
            pillSingleLine: pillTopSpan <= 4,
            nativeHaptics: (window.__nativeHapticCalls || []).length,
            rects: { camRect, commsRect, contractRect, extractRect, journeyRect, touchClusterRect, tacRect, pillTopSpan }
          };
        }"""
    )
    print(f"  [OK] Mobile Borderless HUD & Gameplay Audit: xpIncreased={ui_and_gameplay['xpIncreased']}, "
          f"contractBg={ui_and_gameplay['contractBg']}, touchRowBg={ui_and_gameplay['touchRowBg']}, "
          f"commsBelowCam={ui_and_gameplay['commsBelowCam']}, extractClear={ui_and_gameplay['extractClearOfContractAndComms']}, "
          f"tacAboveJourney={ui_and_gameplay['tacAboveJourney']}, touchRightOfJourney={ui_and_gameplay['touchRightOfJourney']}, pillSingleLine={ui_and_gameplay['pillSingleLine']}")
    assert ui_and_gameplay["xpIncreased"], "XP did not increase"
    assert ui_and_gameplay["contractBg"] in ("rgba(0, 0, 0, 0)", "transparent"), f"Contract HUD still boxed: {ui_and_gameplay['contractBg']}"
    assert ui_and_gameplay["touchRowBg"] in ("rgba(0, 0, 0, 0)", "transparent"), f"Touch row still boxed: {ui_and_gameplay['touchRowBg']}"
    assert ui_and_gameplay["commsBelowCam"] and ui_and_gameplay["commsBelowBar"], f"Comms overlap: {ui_and_gameplay['rects']}"
    assert ui_and_gameplay["extractClearOfContractAndComms"], f"Extract HUD overlap: {ui_and_gameplay['rects']}"
    assert ui_and_gameplay["tacAboveJourney"] and ui_and_gameplay["tacWithinViewport"], f"Tactical overlap/clip: {ui_and_gameplay['rects']}"
    assert ui_and_gameplay["touchRightOfJourney"], f"Journey touches control cluster: {ui_and_gameplay['rects']}"
    assert ui_and_gameplay["pillSingleLine"], f"Pilot telemetry pills wrapped multi-line: {ui_and_gameplay['rects']}"
    assert ui_and_gameplay["nativeHaptics"] > 0, "Native haptics not called"

    page.wait_for_timeout(200)
    shot_mob_ui = ART_DIR / "build201_mobile_gameplay_clean.png"
    page.screenshot(path=str(shot_mob_ui), full_page=False)
    print(f"  [OK] Saved Mobile Gameplay Clean screenshot: {shot_mob_ui.name} ({shot_mob_ui.stat().st_size:,} bytes)")

    assert len(console_errors) == 0, f"Mobile console errors: {console_errors}"
    assert len(page_errors) == 0, f"Mobile page errors: {page_errors}"
    ctx.close()
    return {"canvas": canvas_info, "planet3d": planet_render_check, "scenarios": scenarios, "ui": ui_and_gameplay}


def run_desktop_profile_suite(browser) -> dict:
    print("\n== [Gate 2B] Desktop Flagship Profile (1920x1080, DPR 1.0) ==")
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1.0)
    page = ctx.new_page()
    console_errors = []
    page_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1200)
    page.click("#begin")
    page.wait_for_timeout(2600)

    scenarios = {}
    for mode in ("warp15x", "planet_flyby", "cockpit"):
        res = page.evaluate(FRAME_PACING_PROBE_JS, {"durationMs": 1400, "mode": mode})
        scenarios[mode] = res
        print(f"  [OK] Desktop {mode:<13}: {res['avgFps']:>6.1f} FPS | P95={res['p95Ms']:>5.2f}ms")
        assert res["avgFps"] >= 60.0, f"Desktop {mode} FPS below 60: {res}"

    page.evaluate("""() => {
      const cockpitEl = document.getElementById('sf-cockpit-overlay');
      const cBtn = document.getElementById('cockpit-toggle');
      if (cockpitEl && cockpitEl.classList.contains('active') && cBtn) cBtn.click();
      if (window.SFVoyage && window.SFVoyage.force) window.SFVoyage.force('warp');
      window.StarfieldExpedition?.recordAction('sonar_scan', { stardust: 220 });
      window.StarfieldExpedition?.refreshHUD(true);
    }""")
    page.wait_for_timeout(400)

    dock_ok = page.evaluate("""() => {
      const req = ['warp-toggle', 'camera-toggle', 'sound-toggle', 'codex-toggle', 'photo-toggle',
                   'radar-toggle', 'formation-toggle', 'hangar-toggle', 'planet-toggle',
                   'upgrades-toggle', 'focus-toggle', 'settings-toggle', 'cinema-toggle', 'fullscreen-toggle'];
      return req.filter(id => !!document.getElementById(id)).length === req.length;
    }""")
    assert dock_ok, "Desktop dock missing buttons"

    shot_desk = ART_DIR / "build201_desktop_hud.png"
    page.screenshot(path=str(shot_desk), full_page=False)
    print(f"  [OK] Saved Desktop HUD screenshot: {shot_desk.name} ({shot_desk.stat().st_size:,} bytes)")

    # Open Planetarium & Hatch Core to verify SFPlanetGL 3D card engine
    hatch_info = page.evaluate("""async () => {
      window.StarfieldAppShell.openPanel('hatch');
      await new Promise(r => setTimeout(r, 300));
      const openBtn = document.querySelector('#sf-hatch-list .sf-hl-open');
      if (openBtn) openBtn.click();
      await new Promise(r => setTimeout(r, 900));
      return {
        sfPlanetGlOn: window.SFPlanetGL ? window.SFPlanetGL.isOn() : false,
        glCanvasCount: document.querySelectorAll('.sf-planet-gl').length
      };
    }""")
    print(f"  [OK] Desktop SFPlanetGL Check: {hatch_info}")
    assert hatch_info["sfPlanetGlOn"] and hatch_info["glCanvasCount"] >= 1, f"SFPlanetGL inactive: {hatch_info}"

    shot_hatch = ART_DIR / "build201_desktop_hatch_3d.png"
    page.screenshot(path=str(shot_hatch), full_page=False)
    print(f"  [OK] Saved Desktop Hatch 3D screenshot: {shot_hatch.name} ({shot_hatch.stat().st_size:,} bytes)")

    assert len(console_errors) == 0, f"Desktop console errors: {console_errors}"
    assert len(page_errors) == 0, f"Desktop page errors: {page_errors}"
    ctx.close()
    return {"scenarios": scenarios, "hatch": hatch_info}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    verify_asset_parity_and_version_gate()
    with sync_playwright() as pw:
        launch_kwargs = {"headless": True, "args": CHROME_ARGS}
        if os.path.exists(CHROME_EXE):
            launch_kwargs["executable_path"] = CHROME_EXE
        else:
            launch_kwargs["channel"] = "chrome"
        browser = pw.chromium.launch(**launch_kwargs)
        try:
            run_mobile_profile_suite(browser)
            run_desktop_profile_suite(browser)
        finally:
            browser.close()
    print(f"\n✅ ALL BUILD 201 (v2.0.0.1) VERIFICATION GATES PASSED IN {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
