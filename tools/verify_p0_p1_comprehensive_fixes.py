# -*- coding: utf-8 -*-
"""
Comprehensive automated verification script for Starfield v1.18.0 P0 and P1 fixes.
Verifies all 9 audited fixes and checks 0 console errors and 100% byte parity.
"""
import asyncio
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT_DIR, 'starfield.html')
ANDROID_HTML = os.path.join(ROOT_DIR, 'android', 'app', 'src', 'main', 'assets', 'starfield.html')
ROOT_SW = os.path.join(ROOT_DIR, 'service-worker.js')
ANDROID_SW = os.path.join(ROOT_DIR, 'android', 'app', 'src', 'main', 'assets', 'service-worker.js')

def verify_file_parity():
    print("\n=== STEP 1: Verifying File Parity & Version Sync ===")
    with open(HTML_FILE, 'rb') as f1, open(ANDROID_HTML, 'rb') as f2:
        b1 = f1.read()
        b2 = f2.read()
        assert b1 == b2, f"Byte mismatch! root: {len(b1)} bytes, android: {len(b2)} bytes"
        print(f"✓ 100% Byte-for-Byte Parity Confirmed between root and Android assets ({len(b1):,} bytes)")

    with open(ROOT_SW, 'r', encoding='utf-8') as f1, open(ANDROID_SW, 'r', encoding='utf-8') as f2:
        sw1 = f1.read()
        sw2 = f2.read()
        assert "v1.19.1-b153" in sw1, "Root service worker missing v1.19.1-b153"
        assert "v1.19.1-b153" in sw2, "Android service worker missing v1.19.1-b153"
        assert sw1 == sw2, "service-worker.js mismatch between root and android"
        print("✓ service-worker.js synchronized to v1.19.1-b153 on both root and Android assets")

async def test_p0_and_p1_in_browser():
    print("\n=== STEP 2: Running Automated In-Browser Verification ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        # Mobile portrait viewport (iPhone 14/15 size: 390x844)
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        file_url = "file:///" + HTML_FILE.replace("\\", "/")
        await page.goto(file_url)
        await page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # P0-1: isBetaEnabled() safe localStorage access under SecurityError
        # -------------------------------------------------------------
        print("\n--- P0-1: Testing isBetaEnabled() SecurityError Handling ---")
        beta_safe = await page.evaluate('''() => {
            const origGet = localStorage.getItem;
            try {
                // Emulate Safari private mode throwing SecurityError
                localStorage.getItem = () => { throw new DOMException("SecurityError", "SecurityError"); };
                const res = window.StarfieldBetaLab.isEnabled();
                return { throws: false, result: res };
            } catch (err) {
                return { throws: true, error: err.message };
            } finally {
                localStorage.getItem = origGet;
            }
        }''')
        print("SecurityError test result:", beta_safe)
        assert not beta_safe['throws'], "isBetaEnabled threw an error during restricted storage access"
        assert beta_safe['result'] is False, "Expected false when localStorage throws"
        print("✓ isBetaEnabled gracefully handles SecurityError without crashing")

        # Unlock beta mode for gameplay testing
        await page.evaluate('''() => {
            if (window.StarfieldBetaLab) window.StarfieldBetaLab.setEnabled(true);
        }''')
        await page.wait_for_timeout(300)

        # -------------------------------------------------------------
        # P0-2: Global keydown isolation
        # -------------------------------------------------------------
        print("\n--- P0-2: Testing Global Keydown Isolation ---")
        # Enter Void Extraction mode
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(400)

        key_isolation = await page.evaluate('''() => {
            const pauseBtn = document.getElementById('pause-toggle');
            const pausedBefore = pauseBtn ? pauseBtn.getAttribute('aria-pressed') : 'false';

            // Dispatch Space key (which in cruise toggles pause)
            window.dispatchEvent(new KeyboardEvent('keydown', { code: 'Space', bubbles: true }));
            const pausedAfterSpace = pauseBtn ? pauseBtn.getAttribute('aria-pressed') : 'false';

            // Dispatch 'V' key (which in cruise toggles cockpit)
            const isCockpit = window.Starfield && window.Starfield.isCockpit ? window.Starfield.isCockpit() : false;
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'v', code: 'KeyV', bubbles: true }));
            const cockpitAfterV = window.Starfield && window.Starfield.isCockpit ? window.Starfield.isCockpit() : false;

            return {
                mode: window.currentMode,
                pausedBefore,
                pausedAfterSpace,
                isCockpit,
                cockpitAfterV
            };
        }''')
        print("Keydown isolation test result:", key_isolation)
        assert key_isolation['mode'] == 'redalert'
        assert key_isolation['pausedBefore'] == key_isolation['pausedAfterSpace'], "Space key leaked and toggled pause in non-cruise mode!"
        assert key_isolation['isCockpit'] == key_isolation['cockpitAfterV'], "V key leaked and toggled cockpit in non-cruise mode!"
        print("✓ Global keydown isolated: background pause and cockpit controls protected")

        # -------------------------------------------------------------
        # P0-3: Web Audio Sonar Pulse Leak Prevention
        # -------------------------------------------------------------
        print("\n--- P0-3: Testing Sonar AudioContext Reuse ---")
        sonar_result = await page.evaluate('''() => {
            const sonar = window.StarfieldSonar;
            if (!sonar) return { available: false };
            sonar.init();
            // Provide a mock celestial target to trigger pulse
            sonar.currentTarget = { x: 0, y: 0, z: 1000 };
            sonar.lastScanTime = 0;
            sonar.triggerScan();
            const ctx1 = sonar.audioCtx;
            sonar.lastScanTime = 0;
            sonar.triggerScan();
            const ctx2 = sonar.audioCtx;
            return {
                available: true,
                hasCtx: !!ctx1,
                isSameInstance: ctx1 === ctx2
            };
        }''')
        print("Sonar AudioContext test result:", sonar_result)
        assert sonar_result['available'], "StarfieldSonar not available"
        assert sonar_result['hasCtx'], "Sonar did not create audioCtx on scan"
        assert sonar_result['isSameInstance'], "AudioContext was re-instantiated on sonar pulse instead of reused!"
        print("✓ Web Audio context cleanly reused across sonar pulses without channel leak")

        # -------------------------------------------------------------
        # P0-4: 2D Extraction Removed & 3D In-Flight Scavenging Active
        # -------------------------------------------------------------
        print("\n--- P0-4: Testing 2D Extraction Removal & 3D In-Flight Scavenging ---")
        joy_result = await page.evaluate('''() => {
            const legacyJoyZone = document.getElementById('sf-ext-joystick-zone');
            const legacyOverlay = document.getElementById('sf-extraction-overlay');
            const legacyBtn = document.getElementById('sf-btn-mode-extract');
            const inflightExt = window.StarfieldInFlightExtraction;
            const lootBtn = document.getElementById('sf-inflight-loot-btn');

            let lootCollected = false;
            if (inflightExt) {
                inflightExt.init();
                const initialCargo = inflightExt.cargo.length;
                window.travel = 35000;
                inflightExt.update(0.016);
                if (inflightExt.derelicts.length > 0) {
                    const lead = craftWorld(fleet[LEAD]);
                    inflightExt.derelicts[0].x = lead[0] + 80;
                    inflightExt.derelicts[0].y = lead[1] - 40;
                    inflightExt.derelicts[0].z = lead[2] + 1200;
                    inflightExt.update(0.016);
                    inflightExt.fastLoot();
                }
                lootCollected = (inflightExt.cargo.length > initialCargo);
            }

            return {
                hasLegacyJoyZone: !!legacyJoyZone,
                hasLegacyOverlay: !!legacyOverlay,
                hasLegacyBtn: !!legacyBtn,
                hasInflightExt: !!inflightExt,
                hasObstructingBtn: !!lootBtn,
                lootCollected
            };
        }''')
        print("Extraction test result:", joy_result)
        assert not joy_result['hasLegacyJoyZone'], "Legacy #sf-ext-joystick-zone should be removed from DOM"
        assert not joy_result['hasLegacyOverlay'], "Legacy #sf-extraction-overlay should be removed from DOM"
        assert not joy_result['hasLegacyBtn'], "Legacy #sf-btn-mode-extract should be removed from mode bar"
        assert not joy_result['hasObstructingBtn'], "Bottom #sf-inflight-loot-btn should be cleanly removed"
        assert joy_result['hasInflightExt'], "3D StarfieldInFlightExtraction missing"
        assert joy_result['lootCollected'], "3D In-Flight extraction failed to collect loot into cargo"
        print("✓ Legacy 2D extraction cleanly removed, 3D in-flight scavenging mechanics active without bottom obstruction")

        # -------------------------------------------------------------
        # P0-5 & P1-8: 2D Slingshot Removed & 3D Orbital Mechanics Active
        # -------------------------------------------------------------
        print("\n--- P0-5 & P1-8: Testing 2D Slingshot Removal & 3D Orbital Mechanics ---")
        sling_test = await page.evaluate('''() => {
            const legacyOverlay = document.getElementById('sf-slingshot-overlay');
            const legacyBtn = document.getElementById('sf-btn-mode-slingshot');
            const orbitalMechanics = window.StarfieldOrbitalMechanics;
            const probeBtn = document.getElementById('sf-inflight-probe-btn');
            const sonarLockBtn = document.getElementById('sf-sonar-lock-btn');

            let orbitalArcActive = false;
            let probeLaunched = false;
            if (orbitalMechanics) {
                orbitalMechanics.init();
                window.activeMasses = [{
                    x: 300, y: 150, z: window.travel + 1200,
                    rad: 300, mass: 2.0e8,
                    name: '开普勒-452b',
                    kind: 1
                }];
                orbitalMechanics.update(0.016);
                orbitalArcActive = orbitalMechanics.slingshotArc && orbitalMechanics.slingshotArc.length > 0;
                orbitalMechanics.launchProbe();
                probeLaunched = orbitalMechanics.probes.length > 0;
            }

            return {
                hasLegacyOverlay: !!legacyOverlay,
                hasLegacyBtn: !!legacyBtn,
                hasOrbitalMechanics: !!orbitalMechanics,
                hasProbeBtn: !!probeBtn,
                hasSonarLockBtn: !!sonarLockBtn,
                orbitalArcActive,
                probeLaunched
            };
        }''')
        print("Orbital Slingshot test result:", sling_test)
        assert not sling_test['hasLegacyOverlay'], "Legacy #sf-slingshot-overlay should be removed from DOM"
        assert not sling_test['hasLegacyBtn'], "Legacy #sf-btn-mode-slingshot should be removed from mode bar"
        assert not sling_test['hasProbeBtn'], "Bottom #sf-inflight-probe-btn should be cleanly removed"
        assert not sling_test['hasSonarLockBtn'], "Bottom #sf-sonar-lock-btn should be cleanly removed"
        assert sling_test['hasOrbitalMechanics'], "3D StarfieldOrbitalMechanics missing"
        assert sling_test['orbitalArcActive'], "3D Orbital Mechanics trajectory prediction failed"
        assert sling_test['probeLaunched'], "3D Gravitational probe launch failed"
        print("✓ Legacy 2D slingshot cleanly removed, 3D gravitational orbital mechanics active without bottom obstruction")

        # -------------------------------------------------------------
        # P1-6: Cruise engine background rendering pause
        # -------------------------------------------------------------
        print("\n--- P1-6: Testing Cruise Engine Background Rendering Pause ---")
        # In cruise mode, travel advances with time
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(300)
        t_cruise_1 = await page.evaluate('() => window.Starfield.getTravel()')
        await page.wait_for_timeout(200)
        t_cruise_2 = await page.evaluate('() => window.Starfield.getTravel()')
        cruise_delta = t_cruise_2 - t_cruise_1

        # In Red Alert mode, travel does NOT advance because cruise loop skips
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(300)
        t_ra_1 = await page.evaluate('() => window.Starfield.getTravel()')
        await page.wait_for_timeout(200)
        t_ra_2 = await page.evaluate('() => window.Starfield.getTravel()')
        ra_delta = t_ra_2 - t_ra_1

        print(f"Travel advance in Cruise: {cruise_delta:.2f}, in Red Alert: {ra_delta:.2f}")
        assert cruise_delta > 0, "Cruise travel did not advance while active"
        assert ra_delta == 0, "Cruise travel continued advancing while in Red Alert mode!"
        print("✓ Cruise engine frame loop cleanly pauses during expansion gameplay")

        # -------------------------------------------------------------
        # P1-7: Red Alert RTS wave timer deadlock fix
        # -------------------------------------------------------------
        print("\n--- P1-7: Testing Red Alert RTS Wave Timer Deadlock Prevention ---")
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(400)

        ra_wave_test = await page.evaluate('''() => {
            const ra = window.RedAlertRTS;
            if (!ra) return { active: false };

            // Clear enemies to trigger wave clear logic
            ra.enemies = [];
            ra.isSpawningWave = false;
            ra.update(0.016); // Should set isSpawningWave = true and schedule waveTimer

            const waveScheduled = ra.isSpawningWave;
            const hasTimer = !!ra.waveTimer;

            // Stop RTS game while timer is pending (simulates player exiting to cruise or another mode)
            ra.stop();
            const timerAfterStop = ra.waveTimer;
            const spawningAfterStop = ra.isSpawningWave;

            // Reset and verify ready for next wave
            ra.resetGame();
            const spawningAfterReset = ra.isSpawningWave;

            return {
                active: true,
                waveScheduled,
                hasTimer,
                timerAfterStop,
                spawningAfterStop,
                spawningAfterReset
            };
        }''')
        print("Red Alert wave deadlock test result:", ra_wave_test)
        assert ra_wave_test['waveScheduled'], "Wave clear did not trigger wave spawning state"
        assert ra_wave_test['hasTimer'], "Wave timer handle was not stored"
        assert ra_wave_test['timerAfterStop'] is None, "Wave timer was not cleared on stop()"
        assert not ra_wave_test['spawningAfterStop'], "isSpawningWave remained true after stop()"
        assert not ra_wave_test['spawningAfterReset'], "isSpawningWave remained true after resetGame()"
        print("✓ Red Alert RTS wave timer deadlock eliminated")

        # -------------------------------------------------------------
        # Return to Cruise and check final console errors
        # -------------------------------------------------------------
        print("\n--- Return to Cruise and Final Stability Check ---")
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(400)

        cruise_active = await page.evaluate('() => window.currentMode === "cruise"')
        assert cruise_active, "Failed to return to cruise mode"
        print("✓ Returned to Cruise mode successfully")

        print("\n--- Console Errors Verification ---")
        print("Total Errors Count:", len(errors))
        if errors:
            print("Errors encountered:", errors)
        assert len(errors) == 0, f"Encountered {len(errors)} console errors during test run!"
        print("✓ Zero console errors confirmed across all test routines")

        await browser.close()

async def main():
    verify_file_parity()
    await test_p0_and_p1_in_browser()
    print("\n================================================================================")
    print("🏆 ALL P0 & P1 AUDITED FIXES VERIFIED 100% SUCCESSFULLY WITH ZERO CONSOLE ERRORS!")
    print("================================================================================")

if __name__ == '__main__':
    asyncio.run(main())
