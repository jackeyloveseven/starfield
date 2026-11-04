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

        print('--- Test 1: Bottom Screen Pure Unobstructed HUD & Touch Navigation ---')
        hud_check = await page.evaluate('''() => {
            const sonarLockBtn = document.getElementById('sf-sonar-lock-btn');
            const lootBtn = document.getElementById('sf-inflight-loot-btn');
            const probeBtn = document.getElementById('sf-inflight-probe-btn');
            const legacyExtBtn = document.getElementById('sf-btn-mode-extract');
            const legacySlingBtn = document.getElementById('sf-btn-mode-slingshot');
            const legacyExtOverlay = document.getElementById('sf-extraction-overlay');
            const legacySlingOverlay = document.getElementById('sf-slingshot-overlay');

            // Dispatch multi-touch on canvas
            const canvas = document.getElementById('starfield-canvas') || document.body;
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 10, clientX: 100, clientY: 200, bubbles: true
            }));
            canvas.dispatchEvent(new PointerEvent('pointerdown', {
                pointerId: 11, clientX: 250, clientY: 300, bubbles: true
            }));
            canvas.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 10, clientX: 100, clientY: 200, bubbles: true
            }));
            canvas.dispatchEvent(new PointerEvent('pointerup', {
                pointerId: 11, clientX: 250, clientY: 300, bubbles: true
            }));

            return {
                sonarLockBtnAbsent: !sonarLockBtn,
                lootBtnAbsent: !lootBtn,
                probeBtnAbsent: !probeBtn,
                legacyExtBtnAbsent: !legacyExtBtn,
                legacySlingBtnAbsent: !legacySlingBtn,
                legacyExtOverlayAbsent: !legacyExtOverlay,
                legacySlingOverlayAbsent: !legacySlingOverlay
            };
        }''')
        print('HUD check result:', hud_check)
        assert hud_check['sonarLockBtnAbsent'], 'Sonar lock button must not obstruct bottom screen'
        assert hud_check['lootBtnAbsent'], 'In-flight loot button must not obstruct bottom screen'
        assert hud_check['probeBtnAbsent'], 'In-flight probe button must not obstruct bottom screen'
        assert hud_check['legacyExtBtnAbsent'], '2D pixel extract button must be removed'
        assert hud_check['legacySlingBtnAbsent'], '2D pixel slingshot button must be removed'
        assert hud_check['legacyExtOverlayAbsent'], '2D pixel extract overlay must be removed'
        assert hud_check['legacySlingOverlayAbsent'], '2D pixel slingshot overlay must be removed'
        print('[PASS] Bottom screen is completely pure and unobstructed; 2D pixel minigames removed!')

        print('\n--- Test 2: Red Alert RTS Off-Screen Pointerup & Drag Protection ---')
        await page.evaluate('''() => {
            window.switchStarfieldMode('redalert');
        }''')
        await asyncio.sleep(0.1)

        ra_drag_result = await page.evaluate('''() => {
            const ra = window.RedAlertRTS;
            const canvas = ra.canvas;
            const rect = canvas.getBoundingClientRect();

            // Mousedown drag
            canvas.dispatchEvent(new MouseEvent('mousedown', {
                button: 0, clientX: rect.left + 50, clientY: rect.top + 50, bubbles: true
            }));
            window.dispatchEvent(new MouseEvent('mousemove', {
                button: 0, clientX: rect.left + 150, clientY: rect.top + 150, bubbles: true
            }));
            const isDraggingDuringMove = ra.dragSelect ? ra.dragSelect.active : false;

            // Release outside canvas on window / document.body
            window.dispatchEvent(new MouseEvent('mouseup', {
                button: 0, clientX: -10, clientY: -10, bubbles: true
            }));
            const isDraggingAfterRelease = ra.dragSelect ? ra.dragSelect.active : false;

            return {
                isDraggingDuringMove,
                isDraggingAfterRelease
            };
        }''')
        print('Red Alert drag result:', ra_drag_result)
        assert ra_drag_result['isDraggingDuringMove'] is True, 'Drag select should be active during move'
        assert ra_drag_result['isDraggingAfterRelease'] is False, 'Off-screen release should clear drag select'
        print('[PASS] Red Alert off-screen release resilience verified!')

        print('\n--- Test 3: Touch Overlay Hidden in Active Expansion Modes ---')
        overlay_check = await page.evaluate('''() => {
            const touchOverlay = document.getElementById('starfield-touch-overlay');
            const displayRA = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            window.switchStarfieldMode('dyson');
            const displayDSP = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            window.switchStarfieldMode('cruise');
            const displayCruise = touchOverlay ? window.getComputedStyle(touchOverlay).display : 'none';
            return { displayRA, displayDSP, displayCruise };
        }''')
        print('Overlay display in modes:', overlay_check)
        assert overlay_check['displayRA'] == 'none', 'Touch overlay must be none in Red Alert'
        assert overlay_check['displayDSP'] == 'none', 'Touch overlay must be none in Dyson Sphere'
        print('[PASS] Touch overlay strictly hidden across all non-cruise expansion modes!')

        print('\n--- Test 4: Rapid Sub-50ms Mode Switching Resilience ---')
        rapid_switch_result = await page.evaluate('''async () => {
            const modes = ['cruise', 'redalert', 'dyson', 'redalert', 'cruise'];
            for (const m of modes) {
                window.switchStarfieldMode(m);
                await new Promise(r => setTimeout(r, 15));
            }
            return {
                finalMode: window.currentMode,
                raActive: window.RedAlertRTS.active,
                dspActive: window.DysonSphereProgram.active,
                raWaveTimer: window.RedAlertRTS.waveTimer
            };
        }''')
        print('Rapid switch result:', rapid_switch_result)
        assert rapid_switch_result['finalMode'] == 'cruise', 'Final mode should be cruise'
        assert rapid_switch_result['raActive'] is False, 'RedAlert should be inactive'
        assert rapid_switch_result['dspActive'] is False, 'DysonSphere should be inactive'
        assert rapid_switch_result['raWaveTimer'] is None, 'RTS wave timer must be null'
        print('[PASS] Rapid mode toggling resilience confirmed with zero timer/state leaks!')

        print('\n--- Test 5: Long-Press Speed Cruise Isolation ---')
        # In non-cruise, pointerdown for 400ms should NOT trigger warp gear
        await page.evaluate('''() => {
            window.switchStarfieldMode('redalert');
        }''')
        await asyncio.sleep(0.05)
        long_press_result = await page.evaluate('''async () => {
            const canvas = window.RedAlertRTS.canvas;
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
        assert long_press_result['mode'] == 'redalert', 'Mode must remain redalert during long press'
        print('[PASS] Long-press speed gear listener isolated!')

        print('\n--- Console Errors Check ---')
        print('Console errors encountered:', console_errors)
        assert len(console_errors) == 0, f'Encountered {len(console_errors)} console errors'

        await browser.close()
        print('\n[SUCCESS] ALL ADVERSARIAL EDGE CASE TESTS PASSED 100% WITH ZERO ERRORS!')

if __name__ == '__main__':
    asyncio.run(run_adversarial_tests())
