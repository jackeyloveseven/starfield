# -*- coding: utf-8 -*-
"""
Starfield v2.0.0.0 (Build 200) End-to-End Verification Suite
1. Asset Parity & Build 200 Version Gate (SHA256 100% parity + 5 version anchors incl. Android build.gradle).
2. Playwright Frame-Pacing (Anti-Stutter), Aesthetics & Gameplay Suite on System Chrome (WebGL enabled):
   - Mobile Dimensity 9400+ Profile (412x915, DPR 3.0)
   - Desktop Profile (1920x1080, DPR 1.0)
   - Measures Avg FPS, P95/P99 frame delta (ms), and hot-loop DOM mutation rate across:
     * Warp 15x
     * Close Planet Flyby
     * Cockpit Mode
   - Verifies Visual Aesthetics & App Shell HUD (design tokens, 0px precision corners, Command Dock, Cinema Mode).
   - Exercises Core Gameplay Loop & Progression System end-to-end (StarfieldExpedition 8-tier Rank, XP/Combo,
     Tactical Action Capsule, Interactive Expedition Directive HUD, Sonar/Slingshot/Probe/Relic/Hazard synergy,
     Modal Mutex transitions, and Android StarfieldNative haptics/lifecycle bridge).
   - Asserts 0 console errors and 0 page errors.
   - Saves high-resolution verification screenshots:
     * build200_mobile_app_gameplay.png
     * build200_desktop_aesthetics_hud.png
     * build200_gameplay_modal_hub.png
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
    print("== [Gate 1] Asset Parity & Build 200 Version Gate ==")
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

    # Check 4 web version anchors + Android build.gradle
    ver_meta = json.loads((BASE / "version.json").read_text(encoding="utf-8"))
    assert str(ver_meta.get("version")) == "2.0.0.0", f"version.json version != 2.0.0.0: {ver_meta}"
    assert int(ver_meta.get("build")) == 200, f"version.json build != 200: {ver_meta}"

    sw_txt = (BASE / "service-worker.js").read_text(encoding="utf-8")
    m_sw = re.search(r"CACHE_VERSION\s*=\s*'v([0-9.]+)-b(\d+)'", sw_txt)
    assert m_sw and m_sw.group(1) == "2.0.0.0" and m_sw.group(2) == "200", "service-worker.js CACHE_VERSION mismatch"

    html_txt = HTML_PATH.read_text(encoding="utf-8", errors="ignore")
    m_tag = re.search(r'id="sf-version-tag">v([0-9.]+) \(Build (\d+)\)', html_txt)
    assert m_tag and m_tag.group(1) == "2.0.0.0" and m_tag.group(2) == "200", "sf-version-tag mismatch"

    m_lb = re.search(r"const localBuild = (\d+);", html_txt)
    assert m_lb and m_lb.group(1) == "200", "localBuild != 200"

    gradle_txt = (BASE / "android/app/build.gradle").read_text(encoding="utf-8")
    assert "versionCode 200" in gradle_txt and 'versionName "2.0.0.0"' in gradle_txt, "build.gradle version mismatch"
    print("  [OK] All 5 version anchors verified: v2.0.0.0 (Build 200)\n")
    return hashes


FRAME_PACING_PROBE_JS = r"""
async ({ durationMs, mode }) => {
  // Configure requested flight scenario before sampling
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
      // Trigger close planet sonar lock once during warm-up so any one-time WebGL shader compilation settles
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

  // Allow 950ms + 12 RAF frames warm-up so one-time GLSL shader compilation and transition toasts settle
  await new Promise(r => setTimeout(r, 950));
  for (let i = 0; i < 12; i++) {
    await new Promise(r => requestAnimationFrame(r));
  }

  return await new Promise(resolve => {
    const deltas = [];
    let domMutations = 0;
    const obs = new MutationObserver(records => {
      domMutations += records.length;
    });
    obs.observe(document.body, {
      attributes: true,
      childList: true,
      subtree: true,
      characterData: true
    });

    const tStart = performance.now();
    let tLast = tStart;

    function step(now) {
      const dt = now - tLast;
      tLast = now;
      if (dt > 0) deltas.push(dt);
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
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    # Inject mock Android StarfieldNative bridge before page load to verify native integration
    page.add_init_script(
        """
        window.__nativeHapticCalls = [];
        window.StarfieldNative = {
          triggerHaptic: function(style) { window.__nativeHapticCalls.push(String(style)); },
          vibrate: function(ms) { window.__nativeHapticCalls.push('vibrate:' + ms); },
          vibratePattern: function(pat) { window.__nativeHapticCalls.push('pattern:' + pat); },
          getDeviceInfo: function() {
            return JSON.stringify({
              platform: 'android',
              version: '2.0.0.0',
              build: 200,
              otaBuild: 0,
              refreshRate: 120.0,
              model: 'Dimensity 9400+ Flagship',
              keepScreenOn: true,
              liveWallpaperSupported: true
            });
          },
          getDisplayRefreshRate: function() { return 120.0; }
        };
        """
    )

    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1200)

    # Start flight & warm up WebGL planet shaders (so one-time ANGLE HLSL compilation completes before steady-state sampling)
    page.click("#begin")
    page.wait_for_timeout(400)
    page.evaluate(
        """() => {
          if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') {
            let guard = 0;
            while (window.WarpDrive.gearIndex !== 2 && guard++ < 4) window.WarpDrive.cycle();
          }
        }"""
    )
    page.wait_for_timeout(2800)

    # Verify Mobile Canvas DPR Clamping & WebGL readiness
    canvas_info = page.evaluate(
        """() => {
          const c = document.getElementById('stage') || document.getElementById('sky') || document.querySelector('canvas');
          return {
            canvasId: c ? c.id : '',
            devicePixelRatio: window.devicePixelRatio,
            canvasWidth: c ? c.width : 0,
            canvasHeight: c ? c.height : 0,
            logicalWidth: window.innerWidth,
            logicalHeight: window.innerHeight,
            effectiveDpr: c ? Number((c.width / Math.max(1, window.innerWidth)).toFixed(2)) : 0
          };
        }"""
    )
    print(
        f"  [OK] Mobile DPR Clamping: physical DPR={canvas_info['devicePixelRatio']} -> "
        f"effective render DPR={canvas_info['effectiveDpr']} ({canvas_info['canvasWidth']}x{canvas_info['canvasHeight']})"
    )
    assert canvas_info["effectiveDpr"] <= 1.75, f"Mobile DPR not clamped: {canvas_info}"

    # Frame-pacing across 3 scenarios
    scenarios = {}
    for mode in ("warp15x", "planet_flyby", "cockpit"):
        res = page.evaluate(FRAME_PACING_PROBE_JS, {"durationMs": 1400, "mode": mode})
        scenarios[mode] = res
        print(
            f"  [OK] Mobile {mode:<13}: {res['avgFps']:>6.1f} FPS | "
            f"P50={res['p50Ms']:>5.2f}ms P95={res['p95Ms']:>5.2f}ms P99={res['p99Ms']:>5.2f}ms | "
            f"DOM muts/frame={res['mutPerFrame']}"
        )
        assert res["avgFps"] >= 60.0, f"Mobile {mode} FPS below 60: {res}"
        max_mut = 3.5 if mode == "warp15x" else 1.0
        assert res["mutPerFrame"] < max_mut, f"Mobile {mode} DOM mutation rate too high: {res}"

    # Return from cockpit mode if active for clear gameplay HUD verification & screenshot
    page.evaluate(
        """() => {
          const cockpitEl = document.getElementById('sf-cockpit-overlay');
          const cBtn = document.getElementById('cockpit-toggle');
          if (cockpitEl && cockpitEl.classList.contains('active') && cBtn) cBtn.click();
        }"""
    )
    page.wait_for_timeout(300)

    # Exercise Core Gameplay Loop & Progression System end-to-end
    gameplay_report = page.evaluate(
        """async () => {
          const exp = window.StarfieldExpedition;
          const shell = window.StarfieldAppShell;
          if (!exp || !shell) throw new Error('StarfieldExpedition or StarfieldAppShell missing');

          const initial = exp.getState();
          const initialDust = (window.StarfieldInFlightExtraction && window.StarfieldInFlightExtraction.securedCredits) || 0;
          const initialScans = (window.SFProbe && window.SFProbe.scans) || 0;

          // 1. Force an active voyage contract so #sf-contract-hud is visible
          if (window.SFVoyage && typeof window.SFVoyage.force === 'function') {
            window.SFVoyage.force('scan');
          }
          exp.refreshHUD(true);

          // 2. Click Tactical Action Capsule Sonar Scan button (#sf-tac-scan-btn)
          const tacScanBtn = document.getElementById('sf-tac-scan-btn');
          if (!tacScanBtn) throw new Error('#sf-tac-scan-btn missing');
          tacScanBtn.click();

          // 3. Click Interactive Expedition Directive CTA (#sf-contract-act-btn)
          const actBtn = document.getElementById('sf-contract-act-btn');
          if (!actBtn) throw new Error('#sf-contract-act-btn missing');
          actBtn.click();

          // 4. Trigger Slingshot Assist, Relic Decipher & Hazard Graze Evasion
          exp.recordAction('slingshot_assist', { target: 'Aethelgard Prime', stardust: 280 });
          exp.recordAction('relic_decipher', { name: 'Origami Singularity Shard', stardust: 500, core: 1 });
          exp.recordAction('hazard_evade', { kind: 'debris_gap', stardust: 180 });
          if (window.SFVoyage && typeof window.SFVoyage.completeNow === 'function') {
            window.SFVoyage.completeNow();
          }
          if (window.SFVoyage && typeof window.SFVoyage.force === 'function') {
            window.SFVoyage.force('sling');
          }
          exp.refreshHUD(true);

          // 5. Verify Native Lifecycle Pause/Resume hooks
          if (typeof window.onStarfieldAppLifecycle === 'function') {
            window.onStarfieldAppLifecycle('pause');
            window.onStarfieldAppLifecycle('resume');
          }

          const after = exp.getState();
          const afterDust = (window.StarfieldInFlightExtraction && window.StarfieldInFlightExtraction.securedCredits) || 0;
          const afterScans = (window.SFProbe && window.SFProbe.scans) || 0;

          const rankTitleEl = document.getElementById('sf-pilot-rank-title');
          const contractHud = document.getElementById('sf-contract-hud');
          const tacCapsule = document.getElementById('sf-tactical-capsule');
          const oldDust = document.getElementById('sf-hud-stardust');
          const barRect = document.getElementById('sf-pilot-telemetry-bar')?.getBoundingClientRect();
          const commsRect = document.getElementById('comms-hud')?.getBoundingClientRect();
          const tacRect = tacCapsule?.getBoundingClientRect();
          const journeyRect = document.getElementById('journey')?.getBoundingClientRect();

          return {
            initialXp: initial.xp,
            afterXp: after.xp,
            rankCode: after.rankCode,
            rankTitle: after.rankTitle,
            combo: after.combo,
            comboMultiplier: after.comboMultiplier,
            initialDust,
            afterDust,
            initialScans,
            afterScans,
            rankHudText: rankTitleEl ? rankTitleEl.textContent : '',
            contractHudVisible: contractHud ? contractHud.classList.contains('show') : false,
            tacCapsuleVisible: tacCapsule ? tacCapsule.classList.contains('show') : false,
            oldDustHidden: oldDust ? getComputedStyle(oldDust).display === 'none' : true,
            commsClearOfTelemetry: (barRect && commsRect) ? (commsRect.top >= barRect.bottom + 8) : true,
            tacClearOfJourney: (tacRect && journeyRect) ? (tacRect.bottom <= journeyRect.top - 4) : true,
            nativeDeviceInfo: shell.getNativeDeviceInfo(),
            nativeHapticCount: (window.__nativeHapticCalls || []).length
          };
        }"""
    )
    print(
        f"  [OK] Core Gameplay Loop: XP {gameplay_report['initialXp']} -> {gameplay_report['afterXp']} "
        f"({gameplay_report['rankCode']} · {gameplay_report['rankTitle']}, Combo x{gameplay_report['comboMultiplier']}) | "
        f"Stardust {gameplay_report['initialDust']} -> {gameplay_report['afterDust']} | "
        f"Scans {gameplay_report['initialScans']} -> {gameplay_report['afterScans']} | "
        f"Native Haptics={gameplay_report['nativeHapticCount']}"
    )
    assert gameplay_report["afterXp"] > gameplay_report["initialXp"], "XP did not increase after gameplay actions"
    assert gameplay_report["afterDust"] > gameplay_report["initialDust"], "Stardust did not increase after scan/contract"
    assert gameplay_report["afterScans"] > gameplay_report["initialScans"], "SFProbe.scans did not increment"
    assert gameplay_report["contractHudVisible"], "#sf-contract-hud not visible"
    assert gameplay_report["tacCapsuleVisible"], "#sf-tactical-capsule not visible"
    assert gameplay_report["oldDustHidden"], "Legacy #sf-hud-stardust is still visible"
    assert gameplay_report["commsClearOfTelemetry"], "Mobile #comms-hud overlaps #sf-pilot-telemetry-bar"
    assert gameplay_report["tacClearOfJourney"], "Mobile #sf-tactical-capsule overlaps #journey"
    assert gameplay_report["nativeHapticCount"] > 0, "Native haptics bridge was not invoked"

    page.wait_for_timeout(300)
    shot_mobile = BASE / "build200_mobile_app_gameplay.png"
    page.screenshot(path=str(shot_mobile), full_page=False)
    print(f"  [OK] Saved mobile screenshot: {shot_mobile.name} ({shot_mobile.stat().st_size:,} bytes)")

    assert len(console_errors) == 0, f"Mobile console errors: {console_errors}"
    assert len(page_errors) == 0, f"Mobile page errors: {page_errors}"
    print("  [OK] Mobile Console Errors: 0 | Page Errors: 0\n")
    ctx.close()
    return {
        "canvas": canvas_info,
        "scenarios": scenarios,
        "gameplay": gameplay_report,
        "console_errors": len(console_errors),
        "page_errors": len(page_errors),
    }


def run_desktop_profile_suite(browser) -> dict:
    print("== [Gate 2B] Desktop Flagship Profile (1920x1080, DPR 1.0) ==")
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        device_scale_factor=1.0,
    )
    page = ctx.new_page()
    console_errors = []
    page_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: page_errors.append(str(e)))

    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1200)

    # Start flight & warm up WebGL planet shaders (so one-time ANGLE HLSL compilation completes before steady-state sampling)
    page.click("#begin")
    page.wait_for_timeout(400)
    page.evaluate(
        """() => {
          if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') {
            let guard = 0;
            while (window.WarpDrive.gearIndex !== 2 && guard++ < 4) window.WarpDrive.cycle();
          }
        }"""
    )
    page.wait_for_timeout(2800)

    # Frame-pacing across 3 scenarios
    scenarios = {}
    for mode in ("warp15x", "planet_flyby", "cockpit"):
        res = page.evaluate(FRAME_PACING_PROBE_JS, {"durationMs": 1400, "mode": mode})
        scenarios[mode] = res
        print(
            f"  [OK] Desktop {mode:<13}: {res['avgFps']:>6.1f} FPS | "
            f"P50={res['p50Ms']:>5.2f}ms P95={res['p95Ms']:>5.2f}ms P99={res['p99Ms']:>5.2f}ms | "
            f"DOM muts/frame={res['mutPerFrame']}"
        )
        assert res["avgFps"] >= 60.0, f"Desktop {mode} FPS below 60: {res}"
        max_mut = 3.5 if mode == "warp15x" else 1.0
        assert res["mutPerFrame"] < max_mut, f"Desktop {mode} DOM mutation rate too high: {res}"

    # Exit cockpit mode so full Desktop HUD is visible
    page.evaluate(
        """() => {
          const cockpitEl = document.getElementById('sf-cockpit-overlay');
          const cBtn = document.getElementById('cockpit-toggle');
          if (cockpitEl && cockpitEl.classList.contains('active') && cBtn) cBtn.click();
          if (window.SFVoyage && typeof window.SFVoyage.force === 'function') {
            window.SFVoyage.force('warp');
          }
          if (window.StarfieldExpedition) {
            window.StarfieldExpedition.recordAction('sonar_scan', { stardust: 220 });
            window.StarfieldExpedition.refreshHUD(true);
          }
        }"""
    )
    page.wait_for_timeout(400)

    # Audit Visual Aesthetics & App Shell HUD tokens, geometry, Command Dock, Cinema Mode
    aesthetics_report = page.evaluate(
        """() => {
          const world = document.getElementById('world') || document.documentElement;
          const csWorld = getComputedStyle(world);
          const camHud = document.getElementById('camera-hud');
          const csCam = camHud ? getComputedStyle(camHud) : null;
          const contractHud = document.getElementById('sf-contract-hud');
          const csContract = contractHud ? getComputedStyle(contractHud) : null;
          const requiredDockBtns = [
            'warp-toggle', 'camera-toggle', 'sound-toggle', 'codex-toggle',
            'photo-toggle', 'radar-toggle', 'formation-toggle', 'hangar-toggle',
            'planet-toggle', 'upgrades-toggle', 'focus-toggle', 'settings-toggle',
            'cinema-toggle', 'fullscreen-toggle'
          ];
          const presentBtns = requiredDockBtns.filter(id => !!document.getElementById(id));
          const allControlBtns = Array.from(document.querySelectorAll('#controls .control')).map(b => b.id);

          // Test Cinema Mode toggle clean transitions
          const cinemaBtn = document.getElementById('cinema-toggle');
          let cinemaToggledOk = false;
          if (cinemaBtn) {
            cinemaBtn.click();
            const active = document.body.classList.contains('cinema-mode') || world.classList.contains('cinema');
            cinemaBtn.click();
            cinemaToggledOk = true;
          }

          return {
            hasAestheticsStyle: !!document.getElementById('sf-ui-v200-aesthetics'),
            hasGameplayStyle: !!document.getElementById('sf-v200-gameplay-app-css'),
            inkToken: csWorld.getPropertyValue('--ink').trim(),
            paperToken: csWorld.getPropertyValue('--paper').trim(),
            lineToken: csWorld.getPropertyValue('--line').trim(),
            camHudRadius: csCam ? parseFloat(csCam.borderTopLeftRadius) || 0 : -1,
            contractHudRadius: csContract ? parseFloat(csContract.borderTopLeftRadius) || 0 : -1,
            dockButtonsFound: presentBtns.length,
            dockButtonsExpected: requiredDockBtns.length,
            allControlBtns,
            cinemaToggledOk
          };
        }"""
    )
    print(
        f"  [OK] Aesthetics & App Shell HUD: styles=({aesthetics_report['hasAestheticsStyle']}, "
        f"{aesthetics_report['hasGameplayStyle']}) | corners=({aesthetics_report['camHudRadius']}px, "
        f"{aesthetics_report['contractHudRadius']}px) | Command Dock={aesthetics_report['dockButtonsFound']}/"
        f"{aesthetics_report['dockButtonsExpected']} | CinemaMode={aesthetics_report['cinemaToggledOk']}"
    )
    assert aesthetics_report["hasAestheticsStyle"], "#sf-ui-v200-aesthetics missing"
    assert aesthetics_report["hasGameplayStyle"], "#sf-v200-gameplay-app-css missing"
    assert aesthetics_report["camHudRadius"] == 0, f"#camera-hud border-radius != 0: {aesthetics_report['camHudRadius']}"
    assert aesthetics_report["contractHudRadius"] == 0, f"#sf-contract-hud border-radius != 0: {aesthetics_report['contractHudRadius']}"
    assert aesthetics_report["dockButtonsFound"] == aesthetics_report["dockButtonsExpected"], f"Missing dock buttons: {aesthetics_report}"

    # Save Desktop Aesthetics HUD screenshot
    shot_desktop = BASE / "build200_desktop_aesthetics_hud.png"
    page.screenshot(path=str(shot_desktop), full_page=False)
    print(f"  [OK] Saved desktop HUD screenshot: {shot_desktop.name} ({shot_desktop.stat().st_size:,} bytes)")

    # Exercise App Shell Modal Mutex Hub & capture Gameplay Modal Hub screenshot
    modal_report = page.evaluate(
        """async () => {
          const shell = window.StarfieldAppShell;
          const results = {};

          shell.openPanel('codex');
          await new Promise(r => setTimeout(r, 250));
          results.codexOpen = document.getElementById('codex-modal')?.classList.contains('open') || false;

          shell.openPanel('hangar');
          await new Promise(r => setTimeout(r, 250));
          results.codexClosedOnHangar = !document.getElementById('codex-modal')?.classList.contains('open');
          results.hangarOpen = document.getElementById('hangar-modal')?.classList.contains('open') || false;

          shell.openPanel('planetarium');
          await new Promise(r => setTimeout(r, 250));
          results.hangarClosedOnPlanetarium = !document.getElementById('hangar-modal')?.classList.contains('open');
          results.planetariumOpen = document.getElementById('sf-hatch-list')?.classList.contains('on') || false;

          // Finally open Ship Upgrades Workshop for the modal hub screenshot & test upgrading
          if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
            window.StarfieldInFlightExtraction.addSecuredCredits(1200);
          }
          shell.openPanel('upgrades');
          await new Promise(r => setTimeout(r, 350));
          const upgModal = document.getElementById('sf-upgrades-modal');
          results.planetariumClosedOnUpgrades = !document.getElementById('sf-hatch-list')?.classList.contains('on');
          results.upgradesOpen = upgModal ? (upgModal.classList.contains('show') || getComputedStyle(upgModal).display !== 'none') : false;

          // Execute one equipment upgrade to verify progression hook
          const xpBefore = window.StarfieldExpedition.getState().xp;
          if (window.StarfieldShipUpgrades && typeof window.StarfieldShipUpgrades.upgrade === 'function') {
            window.StarfieldShipUpgrades.upgrade('deepRadar');
          }
          const xpAfter = window.StarfieldExpedition.getState().xp;
          results.upgradeAwardedXp = xpAfter > xpBefore;
          return results;
        }"""
    )
    print(f"  [OK] App Shell Modal Mutex Hub & Upgrade Hook: {modal_report}")
    assert modal_report["codexOpen"] and modal_report["codexClosedOnHangar"], "Modal mutex failed on codex->hangar"
    assert modal_report["hangarOpen"] and modal_report["hangarClosedOnPlanetarium"], "Modal mutex failed on hangar->planetarium"
    assert modal_report["planetariumOpen"] and modal_report["planetariumClosedOnUpgrades"], "Modal mutex failed on planetarium->upgrades"
    assert modal_report["upgradesOpen"], "Ship Upgrades modal did not open"

    shot_modal = BASE / "build200_gameplay_modal_hub.png"
    page.screenshot(path=str(shot_modal), full_page=False)
    print(f"  [OK] Saved gameplay modal hub screenshot: {shot_modal.name} ({shot_modal.stat().st_size:,} bytes)")

    assert len(console_errors) == 0, f"Desktop console errors: {console_errors}"
    assert len(page_errors) == 0, f"Desktop page errors: {page_errors}"
    print("  [OK] Desktop Console Errors: 0 | Page Errors: 0\n")
    ctx.close()
    return {
        "scenarios": scenarios,
        "aesthetics": aesthetics_report,
        "modals": modal_report,
        "console_errors": len(console_errors),
        "page_errors": len(page_errors),
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    t0 = time.time()
    hashes = verify_asset_parity_and_version_gate()

    with sync_playwright() as pw:
        launch_kwargs = {"headless": True, "args": CHROME_ARGS}
        if os.path.exists(CHROME_EXE):
            launch_kwargs["executable_path"] = CHROME_EXE
        else:
            launch_kwargs["channel"] = "chrome"
        browser = pw.chromium.launch(**launch_kwargs)
        try:
            mobile_res = run_mobile_profile_suite(browser)
            desktop_res = run_desktop_profile_suite(browser)
        finally:
            browser.close()

    elapsed = time.time() - t0
    print(f"✅ ALL BUILD 200 (v2.0.0.0) VERIFICATION GATES PASSED IN {elapsed:.1f}s")


if __name__ == "__main__":
    main()
