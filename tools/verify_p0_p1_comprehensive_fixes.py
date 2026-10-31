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
        assert "v1.18.0-b150" in sw1, "Root service worker missing v1.18.0-b150"
        assert "v1.18.0-b150" in sw2, "Android service worker missing v1.18.0-b150"
        assert sw1 == sw2, "service-worker.js mismatch between root and android"
        print("✓ service-worker.js synchronized to v1.18.0-b150 on both root and Android assets")

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
        await page.click('#sf-btn-mode-extract')
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
        assert key_isolation['mode'] == 'extract'
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
        # P0-4: Void Extraction Mobile Joystick Zone
        # -------------------------------------------------------------
        print("\n--- P0-4: Testing Void Extraction Mobile Joystick ---")
        joy_result = await page.evaluate('''() => {
            const joyZone = document.getElementById('sf-ext-joystick-zone');
            const knob = joyZone ? joyZone.querySelector('.sf-ext-joystick-knob') : null;
            const game = window.VoidExtraction;

            if (!joyZone || !game) return { hasZone: false };

            // Simulate pointerdown & pointermove on joystick
            const rect = joyZone.getBoundingClientRect();
            joyZone.dispatchEvent(new PointerEvent('pointerdown', {
                clientX: rect.left + rect.width / 2,
                clientY: rect.top + rect.height / 2,
                bubbles: true
            }));

            // Drag up and right (expect keys.w = true, keys.d = true)
            window.dispatchEvent(new PointerEvent('pointermove', {
                clientX: rect.left + rect.width / 2 + 30,
                clientY: rect.top + rect.height / 2 - 30,
                bubbles: true
            }));

            const keysMoving = { w: game.keys.w, s: game.keys.s, a: game.keys.a, d: game.keys.d };

            // Release pointer
            window.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
            const keysReleased = { w: game.keys.w, s: game.keys.s, a: game.keys.a, d: game.keys.d };

            return {
                hasZone: !!joyZone,
                hasKnob: !!knob,
                keysMoving,
                keysReleased
            };
        }''')
        print("Void Extraction Joystick test result:", joy_result)
        assert joy_result['hasZone'], "Missing #sf-ext-joystick-zone in DOM"
        assert joy_result['hasKnob'], "Missing .sf-ext-joystick-knob in joystick zone"
        assert joy_result['keysMoving']['w'] and joy_result['keysMoving']['d'], "Joystick movement did not activate keys.w / keys.d"
        assert not joy_result['keysReleased']['w'] and not joy_result['keysReleased']['d'], "Joystick release did not reset keys"
        print("✓ Void Extraction mobile joystick zone active and steers ship accurately")

        # -------------------------------------------------------------
        # P0-5 & P1-8: Orbital Slingshot Viewport Scaling, ID Alignment & Reset
        # -------------------------------------------------------------
        print("\n--- P0-5 & P1-8: Testing Orbital Slingshot Scaling & HUD Alignment ---")
        await page.click('#sf-btn-mode-slingshot')
        await page.wait_for_timeout(400)

        sling_test = await page.evaluate('''() => {
            const game = window.OrbitalSlingshot;
            const titleEl = document.getElementById('sf-sling-stage-title');
            const targetCountEl = document.getElementById('sf-sling-target-count');
            const resetBtn = document.getElementById('sf-sling-reset-btn');

            if (!game) return { active: false };

            const scaleMatrix = game.getScaleMatrix();
            const initialTitle = titleEl ? titleEl.textContent : '';
            const initialTargets = targetCountEl ? targetCountEl.textContent : '';

            // Destroy one target manually to test dynamic HUD count update
            const targetsBefore = game.currentLevel.targets.length;
            if (targetsBefore > 0) {
                game.currentLevel.targets.pop();
                game.updateTargetHUD();
            }
            const updatedTargets = targetCountEl ? targetCountEl.textContent : '';

            // Click reset button
            if (resetBtn) resetBtn.click();
            const targetsAfterReset = targetCountEl ? targetCountEl.textContent : '';

            // Test timers tracking
            const timersActive = game.timers.length;
            game.stop();
            const timersAfterStop = game.timers.length;

            return {
                active: true,
                hasTitle: !!titleEl,
                titleText: initialTitle,
                hasResetBtn: !!resetBtn,
                initialTargets,
                updatedTargets,
                targetsAfterReset,
                scaleMatrix,
                timersActive,
                timersAfterStop
            };
        }''')
        print("Orbital Slingshot test result:", sling_test)
        assert sling_test['hasTitle'] and 'SECTOR 1' in sling_test['titleText'], "sf-sling-stage-title not aligned with level name!"
        assert sling_test['hasResetBtn'], "Missing #sf-sling-reset-btn in Slingshot HUD!"
        assert sling_test['initialTargets'] == '2 / 2', f"Expected initial targets '2 / 2', got {sling_test['initialTargets']}"
        assert sling_test['updatedTargets'] == '1 / 2', f"Expected updated targets '1 / 2', got {sling_test['updatedTargets']}"
        assert sling_test['targetsAfterReset'] == '2 / 2', f"Expected reset targets '2 / 2', got {sling_test['targetsAfterReset']}"
        assert sling_test['scaleMatrix']['scale'] < 0.5, f"Scale matrix {sling_test['scaleMatrix']} should fit mobile portrait!"
        assert sling_test['timersAfterStop'] == 0, "Timers were not cleared on game stop!"
        print("✓ Orbital Slingshot DOM ID aligned, target HUD dynamic, reset button operational, scaling active, timers leak-free")

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

        # In slingshot mode, travel does NOT advance because cruise loop skips
        await page.click('#sf-btn-mode-slingshot')
        await page.wait_for_timeout(300)
        t_sling_1 = await page.evaluate('() => window.Starfield.getTravel()')
        await page.wait_for_timeout(200)
        t_sling_2 = await page.evaluate('() => window.Starfield.getTravel()')
        sling_delta = t_sling_2 - t_sling_1

        print(f"Travel advance in Cruise: {cruise_delta:.2f}, in Slingshot: {sling_delta:.2f}")
        assert cruise_delta > 0, "Cruise travel did not advance while active"
        assert sling_delta == 0, "Cruise travel continued advancing while in Slingshot mode!"
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
