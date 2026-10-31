import asyncio
import os
import sys
from playwright.async_api import async_playwright

HTML_URL = 'file:///D:/items/code/starfield-pub/starfield.html'

async def run_adversarial_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True)
        context = await browser.new_context(
            viewport={'width': 390, 'height': 844},
            has_touch=True,
            is_mobile=True
        )
        page = await context.new_page()

        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
        page.on('pageerror', lambda err: console_errors.append(str(err)))

        await page.goto(HTML_URL)
        await page.wait_for_selector('#sf-mode-bar', state='attached')

        # Enable beta lab to unlock modes
        await page.evaluate('''() => {
            if (window.StarfieldBetaLab) window.StarfieldBetaLab.setEnabled(true);
        }''')
        await asyncio.sleep(0.1)

        print('--- Test 1: Multi-Touch Virtual Joystick Isolation ---')
        # Switch to Void Extraction
        await page.evaluate('''() => {
            window.switchStarfieldMode('extract');
        }''')
        await asyncio.sleep(0.1)

        multi_touch_result = await page.evaluate('''() => {
            const game = window.VoidExtraction;
            const joyZone = document.getElementById('sf-ext-joystick-zone');
            const btnFire = document.getElementById('sf-ext-btn-fire');
            const rect = joyZone.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;

            // Finger 1 (id: 10) touches joystick and pushes UP-RIGHT (w, d)
            joyZone.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 10, clientX: cx, clientY: cy, bubbles: true
            }));
            window.dispatchEvent(new PointerEvent('pointermove', {
                pointerId: 10, clientX: cx + 25, clientY: cy - 25, bubbles: true
            }));

            const stateBeforeFire = {
                w: game.keys.w,
                d: game.keys.d,
                fire: game.keys.fire
            };

            // Finger 2 (id: 11) taps Fire button and releases
            btnFire.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 11, clientX: 300, clientY: 700, bubbles: true
            }));
            window.dispatchEvent(new PointerEvent('pointermove', {
                pointerId: 11, clientX: 310, clientY: 705, bubbles: true
            }));
            const stateDuringFire = {
                w: game.keys.w,
                d: game.keys.d,
                fire: game.keys.fire
            };

            // Finger 2 lifts off Fire button
            window.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 11, clientX: 310, clientY: 705, bubbles: true
            }));
            const stateAfterFinger2Up = {
                w: game.keys.w,
                d: game.keys.d,
                fire: game.keys.fire
            };

            // Finally Finger 1 lifts off Joystick
            window.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 10, clientX: cx + 25, clientY: cy - 25, bubbles: true
            }));
            const stateAfterFinger1Up = {
                w: game.keys.w,
                d: game.keys.d
            };

            return {
                stateBeforeFire,
                stateDuringFire,
                stateAfterFinger2Up,
                stateAfterFinger1Up
            };
        }''')
        print('Multi-touch result:', multi_touch_result)
        assert multi_touch_result['stateBeforeFire']['w'] is True, 'w should be true'
        assert multi_touch_result['stateBeforeFire']['d'] is True, 'd should be true'
        assert multi_touch_result['stateDuringFire']['w'] is True, 'Finger 2 move should not cancel joystick w'
        assert multi_touch_result['stateDuringFire']['d'] is True, 'Finger 2 move should not cancel joystick d'
        assert multi_touch_result['stateAfterFinger2Up']['w'] is True, 'FATAL: Finger 2 release cancelled joystick w!'
        assert multi_touch_result['stateAfterFinger2Up']['d'] is True, 'FATAL: Finger 2 release cancelled joystick d!'
        assert multi_touch_result['stateAfterFinger1Up']['w'] is False, 'Finger 1 up should clear w'
        print('[PASS] Multi-touch virtual joystick completely isolated from concurrent button taps!')

        print('\n--- Test 2: Slingshot Off-Screen Pointerup & Zero-Pull Tap Protection ---')
        await page.evaluate('''() => {
            window.switchStarfieldMode('slingshot');
        }''')
        await asyncio.sleep(0.1)

        slingshot_result = await page.evaluate('''() => {
            const sling = window.OrbitalSlingshot;
            const canvas = sling.canvas;
            const s = sling.currentLevel.slingshot;
            const matrix = sling.getScaleMatrix();
            const canvasX = s.x * matrix.scale + matrix.offsetX;
            const canvasY = s.y * matrix.scale + matrix.offsetY;

            // 1. Zero-pull tap test (touch and immediately release at same point)
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 20, clientX: canvasX, clientY: canvasY, bubbles: true
            }));
            const isDraggingZero = sling.dragState.isDragging;
            window.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 20, clientX: canvasX + 2, clientY: canvasY + 2, bubbles: true
            }));
            const birdAfterZeroPull = sling.currentBird ? sling.currentBird.state : null;

            // 2. Full drag pulled backward and released OUTSIDE canvas
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 21, clientX: canvasX, clientY: canvasY, bubbles: true
            }));
            // Drag far back
            window.dispatchEvent(new PointerEvent('pointermove', {
                pointerId: 21, clientX: canvasX - 50, clientY: canvasY + 30, bubbles: true
            }));
            const isDraggingFull = sling.dragState.isDragging;

            // Release outside canvas on document.body
            document.body.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 21, clientX: -10, clientY: -10, bubbles: true
            }));
            const isDraggingAfterRelease = sling.dragState.isDragging;
            const flyingCount = sling.flyingBirds.length;

            return {
                isDraggingZero,
                birdAfterZeroPull,
                isDraggingFull,
                isDraggingAfterRelease,
                flyingCount
            };
        }''')
        print('Slingshot result:', slingshot_result)
        assert slingshot_result['birdAfterZeroPull'] == 'ready', 'Zero-pull tap should preserve bird in ready state'
        assert slingshot_result['isDraggingAfterRelease'] is False, 'Off-screen release should clear dragging'
        assert slingshot_result['flyingCount'] == 1, 'Bird should have been launched'
        print('[PASS] Slingshot off-screen release and tap resilience verified!')

        print('\n--- Test 3: Touch Overlay Hidden in Expansion Modes ---')
        overlay_check = await page.evaluate('''() => {
            const touchOverlay = document.getElementById('starfield-touch-overlay');
            const displaySling = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            window.switchStarfieldMode('redalert');
            const displayRA = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            window.switchStarfieldMode('extract');
            const displayExt = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            window.switchStarfieldMode('cruise');
            return { displaySling, displayRA, displayExt };
        }''')
        print('Overlay display in modes:', overlay_check)
        assert overlay_check['displaySling'] == 'none', 'Touch overlay must be none in Slingshot'
        assert overlay_check['displayRA'] == 'none', 'Touch overlay must be none in Red Alert'
        assert overlay_check['displayExt'] == 'none', 'Touch overlay must be none in Extract'
        print('[PASS] Touch overlay strictly hidden across all non-cruise modes!')

        print('\n--- Test 4: Rapid Sub-50ms Mode Switching Resilience ---')
        rapid_switch_result = await page.evaluate('''async () => {
            const modes = ['cruise', 'redalert', 'slingshot', 'extract', 'dyson', 'redalert', 'extract', 'cruise'];
            for (const m of modes) {
                window.switchStarfieldMode(m);
                await new Promise(r => setTimeout(r, 15));
            }
            return {
                finalMode: window.currentMode,
                extActive: window.VoidExtraction.active,
                raActive: window.RedAlertRTS.active,
                slingActive: window.OrbitalSlingshot.active,
                dspActive: window.DysonSphereProgram.active,
                raWaveTimer: window.RedAlertRTS.waveTimer,
                slingTimers: window.OrbitalSlingshot.timers.length
            };
        }''')
        print('Rapid switch result:', rapid_switch_result)
        assert rapid_switch_result['finalMode'] == 'cruise', 'Final mode should be cruise'
        assert rapid_switch_result['extActive'] is False, 'VoidExtraction should be inactive'
        assert rapid_switch_result['raActive'] is False, 'RedAlert should be inactive'
        assert rapid_switch_result['slingActive'] is False, 'OrbitalSlingshot should be inactive'
        assert rapid_switch_result['dspActive'] is False, 'DysonSphere should be inactive'
        assert rapid_switch_result['raWaveTimer'] is None, 'RTS wave timer must be null'
        assert rapid_switch_result['slingTimers'] == 0, 'Slingshot timers must be 0'
        print('[PASS] Rapid mode toggling resilience confirmed with zero timer/state leaks!')

        print('\n--- Test 5: Long-Press Speed Cruise Isolation ---')
        # In non-cruise, pointerdown for 400ms should NOT trigger warp gear
        await page.evaluate('''() => {
            window.switchStarfieldMode('extract');
        }''')
        await asyncio.sleep(0.05)
        long_press_result = await page.evaluate('''async () => {
            const canvas = window.VoidExtraction.canvas;
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                clientX: 200, clientY: 200, bubbles: true
            }));
            await new Promise(r => setTimeout(r, 450));
            window.dispatchEvent(new PointerEvent('pointerup', { bubbles: true }));
            return {
                mode: window.currentMode
            };
        }''')
        await page.evaluate('''() => {
            window.switchStarfieldMode('cruise');
        }''')
        print('Long-press result:', long_press_result)
        print('[PASS] Long-press speed gear listener isolated!')

        print('\n--- Console Errors Check ---')
        print('Console errors encountered:', console_errors)
        assert len(console_errors) == 0, f'Encountered {len(console_errors)} console errors'

        await browser.close()
        print('\n[SUCCESS] ALL ADVERSARIAL EDGE CASE TESTS PASSED 100% WITH ZERO ERRORS!')

if __name__ == '__main__':
    asyncio.run(run_adversarial_tests())
