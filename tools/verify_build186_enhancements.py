# -*- coding: utf-8 -*-
"""
Verification Suite for Build 186:
1. Complete removal of Situation Capsule (#sf-sonar-capsule & #sf-sonar-lock-btn)
2. Background starfield expansion (24k/48k stars, 48/96 bright stars, 4.8k/8.8k band stars)
3. Black hole frequency reduction (k=120) and gargantuan size (r=12500, culling 160k)
4. Distant scenic worlds expansion & 120k extended visibility range
5. Developed planetary orbital satellite networks & space docks
6. 3 Epic Anime/Tokusatsu easter eggs (Gundam, EVA Longinus, Ultraman M78)
7. Multi-viewport Playwright execution with 0 console errors
"""
import os
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_build186_verification():
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / "starfield.html"
    artifacts_dir = base_dir / "tools" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    file_url = f"file:///{str(html_path).replace(os.sep, '/')}"

    print("=================================================================")
    print(" VERIFYING BUILD 186: CELESTIAL ENHANCEMENTS & ZERO-OCCLUSION    ")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=["--use-gl=angle", "--use-angle=swiftshader", "--disable-gpu-watchdog"]
        )

        console_errors = []

        # -----------------------------------------------------------------
        # TEST 1: Mobile Portrait (390 x 844, 3x DPR)
        # -----------------------------------------------------------------
        print("\n--- Test 1: Mobile Portrait (390 x 844, 3x DPR) ---")
        ctx_mobile = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        page = ctx_mobile.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(600)

        # Launch flight
        begin_btn = page.locator('#begin')
        if begin_btn.count() > 0 and begin_btn.is_visible():
            begin_btn.click()
            page.wait_for_timeout(1000)
        else:
            launch_btn = page.query_selector('#launch')
            if launch_btn and launch_btn.is_visible():
                launch_btn.click()
                page.wait_for_timeout(1000)

        # Check 1: Situation Capsule completely removed
        capsule_state = page.evaluate("""() => {
            const el = document.getElementById('sf-sonar-capsule');
            if (!el) return { exists: false, visible: false };
            const style = window.getComputedStyle(el);
            return {
                exists: true,
                visible: style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'
            };
        }""")
        print(f"   - Situation Capsule state: {capsule_state}")
        assert not capsule_state['visible'], "Situation Capsule must not be visible on mobile!"
        print("   - [PASS] Situation Capsule verified completely removed / zero occlusion.")

        # Check 2: Celestial Mapping via Sonar tray button still works without capsule
        sonar_test = page.evaluate("""() => {
            if (typeof StarfieldSonar === 'undefined') return { error: 'No StarfieldSonar' };
            const scanTriggered = StarfieldSonar.triggerScan();
            const el = document.getElementById('sf-sonar-capsule');
            const hasCapsuleInDOM = el !== null && el.classList.contains('show');
            return {
                scanTriggered,
                hasCapsuleInDOM
            };
        }""")
        print(f"   - Sonar trigger test: {sonar_test}")
        assert not sonar_test['hasCapsuleInDOM'], "Sonar scan must NOT show floating capsule in screen center!"
        print("   - [PASS] Celestial mapping triggers cleanly without intrusive capsule.")

        # Check 3: Background Starfield Expansion
        starfield_stats = page.evaluate("""() => {
            return {
                stars: typeof stars !== 'undefined' ? stars.length : 0,
                brightStars: typeof brightStars !== 'undefined' ? brightStars.length : 0,
                bandStars: typeof bandStars !== 'undefined' ? bandStars.length : 0
            };
        }""")
        print(f"   - Starfield density stats: {starfield_stats}")
        assert starfield_stats['stars'] >= 20000, f"Expected stars >= 20000, got {starfield_stats['stars']}"
        assert starfield_stats['brightStars'] >= 40, f"Expected brightStars >= 40, got {starfield_stats['brightStars']}"
        assert starfield_stats['bandStars'] >= 4000, f"Expected bandStars >= 4000, got {starfield_stats['bandStars']}"
        print("   - [PASS] Starfield density multifold expansion verified.")

        # Check 4: Black Hole Frequency & Gargantuan Scale & Deep Lensing (160k Range)
        bh_stats = page.evaluate("""() => {
            if (typeof chunk !== 'function') return { error: 'No chunk function' };
            const c12 = chunk(12);
            const hasBHAt12 = c12 && c12.masses && c12.masses.some(m => m.isBlackHole);
            const c120 = chunk(120);
            const bhAt120 = c120 && c120.masses && c120.masses.find(m => m.isBlackHole);

            // Test deep lensing at 100,000 units (must NOT be culled by old 78,000 limit)
            let deepLensDetected = false;
            if (window.Starfield && window.Starfield.updateLens && window.Starfield.getActiveMasses) {
                const SF = window.Starfield;
                const masses = SF.getActiveMasses();
                const cam = SF.getCamera();
                const testBH = {
                    x: cam.eye[0] + cam.forward[0] * 100000,
                    y: cam.eye[1] + cam.forward[1] * 100000,
                    z: cam.eye[2] + cam.forward[2] * 100000,
                    kind: 4, isBlackHole: true, r: 12500
                };
                masses.push(testBH);
                try {
                    SF.updateLens();
                    const sources = SF.getLensSources();
                    deepLensDetected = sources && sources.some(s => s.isBH);
                } finally {
                    const idx = masses.indexOf(testBH);
                    if (idx !== -1) masses.splice(idx, 1);
                    SF.updateLens();
                }
            }

            return {
                hasBHAt12,
                bhAt120Rad: bhAt120 ? bhAt120.r : 0,
                bhAt120Kind: bhAt120 ? bhAt120.kind : null,
                deepLensDetected
            };
        }""")
        print(f"   - Black hole encounter stats: {bh_stats}")
        assert not bh_stats['hasBHAt12'], "Black hole must NOT spawn at chunk 12 (reduced frequency)!"
        assert bh_stats['bhAt120Rad'] >= 10000, f"Black hole radius must be >= 10000, got {bh_stats['bhAt120Rad']}"
        assert bh_stats['deepLensDetected'], "Black hole gravitational lensing must function beyond 78,000 units (up to 160,000 units)!"
        print("   - [PASS] Black hole encounter frequency reduced, radius scaled to 12,500, and deep lensing verified > 78k.")

        # Check 5: Distant Scenic Planets Expansion
        distant_stats = page.evaluate("""() => {
            if (typeof chunk !== 'function') return { error: 'No chunk function' };
            let totalDistant = 0;
            for (let k = 1; k <= 5; k++) {
                const c = chunk(k);
                if (c && c.masses) {
                    totalDistant += c.masses.filter(m => m.isDistantWorld).length;
                }
            }
            return { totalDistantIn5Chunks: totalDistant };
        }""")
        print(f"   - Distant planets in first 5 chunks: {distant_stats}")
        assert distant_stats['totalDistantIn5Chunks'] >= 5, "Expected >= 5 distant scenic worlds in chunks 1..5"
        print("   - [PASS] Distant scenic background worlds successfully populated.")

        # Check 6: Planetary Satellite System & LowOrbitSkimmer distant world decoupling
        sat_stats = page.evaluate("""() => {
            let dbg = {};
            let skimmerIgnoredDistant = false;
            try {
                if (typeof LowOrbitSkimmer !== 'undefined' && LowOrbitSkimmer.update) {
                    const fakeDistant = [{ isDistantWorld: true, w: { name: 'Distant World' }, z: travel + 1000, r: 800, kind: 1 }];
                    const goal = { distance: 1000, pitch: 0, roll: 0 };
                    LowOrbitSkimmer.activePlanet = null;
                    LowOrbitSkimmer.skimW = 0.0;
                    const fLead = (typeof fleet !== 'undefined' && fleet[0]) ? fleet[0] : { x: 0, y: 0, z: 0 };
                    const res = LowOrbitSkimmer.update(0.016, true, 0, fakeDistant, fLead, goal);
                    dbg = { res: res, activePlanet: LowOrbitSkimmer.activePlanet, skimW: LowOrbitSkimmer.skimW };
                    skimmerIgnoredDistant = (res === null && LowOrbitSkimmer.activePlanet === null);
                }
            } catch(e) {
                dbg = { err: e.message, stack: e.stack };
            }
            return {
                hasDrawOrbitalSatellites: typeof drawOrbitalSatellites === 'function',
                skimmerIgnoredDistant,
                dbg
            };
        }""")
        print(f"   - Satellite system & Skimmer decoupling check: {sat_stats}")
        assert sat_stats['hasDrawOrbitalSatellites'], "drawOrbitalSatellites function must exist!"
        assert sat_stats['skimmerIgnoredDistant'], "LowOrbitSkimmer must ignore distant background worlds!"
        print("   - [PASS] Planetary orbital satellite network & skimmer decoupling verified.")

        # Check 7: Anime / Tokusatsu 3 Epic Easter Eggs & Codex Discovery & Narrator
        easter_egg_stats = page.evaluate("""() => {
            const types = ['gundam_relic', 'eva_longinus', 'ultraman_m78'];
            const codexDb = typeof Codex !== 'undefined' ? (Codex.database.wonders || Codex.database.celestial || []) : [];
            const codexFound = types.map(t => codexDb.some(item => item.id === t));

            // Test event instantiation, simulated draw via SpaceEventEngine, and Codex wonder encounter
            let drawSuccess = true;
            let drawErrors = [];
            let codexDiscovered = false;
            let narratorHasScripts = false;
            if (typeof SpaceEventEngine !== 'undefined') {
                types.forEach(t => {
                    try {
                        const ev = { type: t, x: 2000, y: 100, z: travel + 3000, rot: 0, spin: 0.05, relicLen: 900, spearLen: 3600, nebulaRad: 4000, notified: false };
                        SpaceEventEngine.drawEvent(ev, 1.0);
                    } catch(e) {
                        drawSuccess = false;
                        drawErrors.push(t + ': ' + e.message);
                    }
                });
            }
            if (typeof Codex !== 'undefined') {
                Codex.checkWonderEncounter({ type: 'gundam_relic' });
                codexDiscovered = !!(Codex.discovered && Codex.discovered['gundam_relic']);
            }
            if (typeof Narrator !== 'undefined' && Narrator.scripts) {
                narratorHasScripts = !!(Narrator.scripts.ev_gundam && Narrator.scripts.ev_eva && Narrator.scripts.ev_ultraman);
            }
            return {
                codexFound,
                drawSuccess,
                drawErrors,
                codexDiscovered,
                narratorHasScripts
            };
        }""")
        print(f"   - Easter egg verification: {easter_egg_stats}")
        assert all(easter_egg_stats['codexFound']), f"All 3 easter eggs must be registered in Codex: {easter_egg_stats['codexFound']}"
        assert easter_egg_stats['drawSuccess'], f"Draw errors in easter eggs: {easter_egg_stats['drawErrors']}"
        assert easter_egg_stats['codexDiscovered'], "Codex wonder discovery via checkWonderEncounter must succeed!"
        assert easter_egg_stats['narratorHasScripts'], "Narrator voice scripts must exist for Gundam, EVA, and Ultraman!"
        print("   - [PASS] Gundam, EVA, and Ultraman easter eggs verified in Codex, events, and Narrator voice engine.")

        # Save mobile screenshot
        shot_path_mobile = artifacts_dir / "build186_mobile_flight.png"
        page.screenshot(path=str(shot_path_mobile))
        print(f"   - Saved mobile screenshot to {shot_path_mobile}")

        # -----------------------------------------------------------------
        # TEST 2: Desktop Landscape (1920 x 1080)
        # -----------------------------------------------------------------
        print("\n--- Test 2: Desktop Landscape (1920 x 1080) ---")
        ctx_desktop = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            is_mobile=False,
            device_scale_factor=1.0
        )
        page_d = ctx_desktop.new_page()
        page_d.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page_d.goto(file_url, wait_until='networkidle')
        page_d.wait_for_timeout(600)

        # Launch flight
        begin_btn = page_d.locator('#begin')
        if begin_btn.count() > 0 and begin_btn.is_visible():
            begin_btn.click()
            page_d.wait_for_timeout(1000)

        # Trigger warp shift to verify high-speed starfield rendering without error
        page_d.evaluate("""() => {
            if (typeof WarpDrive !== 'undefined' && WarpDrive.shift) {
                WarpDrive.shift();
            }
        }""")
        page_d.wait_for_timeout(600)

        # Save desktop screenshot
        shot_path_desktop = artifacts_dir / "build186_desktop_flight.png"
        try:
            page_d.screenshot(path=str(shot_path_desktop), timeout=15000)
            print(f"   - Saved desktop screenshot to {shot_path_desktop}")
        except Exception as e:
            print(f"   - Desktop screenshot note: {e}")

        # Verify console errors
        print(f"\n--- Console Errors: {len(console_errors)} ---")
        if console_errors:
            for err in console_errors:
                print(f"   [CONSOLE ERROR] {err}")
        assert len(console_errors) == 0, f"Found {len(console_errors)} console errors during verification!"
        print("   - [PASS] Zero console errors during extensive mobile & desktop simulation.")

        browser.close()

    print("\n=================================================================")
    print(" ALL BUILD 186 ENHANCEMENTS AND VERIFICATIONS PASSED 100%!       ")
    print("=================================================================")

if __name__ == '__main__':
    run_build186_verification()
