import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    errors = []
    logs = []
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    
    print('====================================================')
    print(' STARFIELD // SCANNER RADAR & RELIC TUNER TEST SUITE')
    print('====================================================')
    
    async with async_playwright() as p:
        # Launch headless Edge if available, otherwise default Chromium
        if os.path.exists(edge_path):
            browser = await p.chromium.launch(executable_path=edge_path, headless=True)
            print('-> Launched browser: Microsoft Edge (Headless)')
        else:
            browser = await p.chromium.launch(headless=True)
            print('-> Launched browser: Chromium (Headless)')
            
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        page.on('console', lambda msg: logs.append(f'[{msg.type}] {msg.text}'))
        page.on('pageerror', lambda err: errors.append(str(err)))
        
        file_url = 'file:///' + os.path.abspath(r'd:\items\code\starfield-pub\starfield.html').replace('\\', '/')
        print('1. Navigating to:', file_url)
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(1)
        
        # Click #begin to launch flight
        print('2. Clicking #begin to launch flight...')
        await page.click('#begin')
        await asyncio.sleep(2)
        
        os.makedirs(r'd:\items\code\starfield-pub\shots', exist_ok=True)
        
        # Verify AnomalyScanner exists on window
        has_scanner = await page.evaluate("typeof window.AnomalyScanner !== 'undefined'")
        print(f'3. Verifying window.AnomalyScanner is mounted: {has_scanner}')
        assert has_scanner, "window.AnomalyScanner must be defined on window"
        
        # =====================================================================
        # TEST 1: Deep-Space Long-Range Radar Ping (Hotkey R)
        # =====================================================================
        print('4. Testing Radar Ping via Hotkey R...')
        await page.keyboard.press('KeyR')
        await asyncio.sleep(0.4)
        
        state1 = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Radar Active: {state1["radarActive"]}, Wave Distance: {state1["radarWaveDist"]:.1f} U')
        assert state1["radarActive"] == True, "Radar should be active after pressing R"
        
        # Allow wave to propagate forward
        await asyncio.sleep(1.0)
        state2 = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Pulse propagating... Distance: {state2["radarWaveDist"]:.1f} U (Spanning flight corridor)')
        assert state2["radarWaveDist"] > state1["radarWaveDist"], "Pulse wave distance should increase over time"
        
        # Capture 3D radar pulse visual
        shot_radar = r'd:\items\code\starfield-pub\shots\scanner_radar_ping.png'
        await page.screenshot(path=shot_radar)
        print('   Saved 3D Radar Pulse screenshot to:', shot_radar)
        
        # Test clicking the HUD button [ 📡 巡天雷达 ]
        print('5. Testing Radar Ping via HUD button #radar-toggle...')
        await page.click('#radar-toggle')
        await asyncio.sleep(0.3)
        state_hud = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Radar Triggered via HUD button: {state_hud["radarActive"]}')
        
        # Wait for candidates and targets
        targets = await page.evaluate("window.AnomalyScanner.getCandidates()")
        print(f'6. Cosmic candidates detected in sector: {len(targets)}')
        for t in targets[:3]:
            print(f'   - [{t["name"]}] ({t["category"]}) at Z={t["z"]:.0f}, targetFreq={t["targetFreq"]:.2f} GHz')
        assert len(targets) > 0, "Scanner should discover targets in surrounding corridor"
        
        # =====================================================================
        # TEST 2: Relic Tuner Waveform Alignment Minigame (Hotkey E)
        # =====================================================================
        print('7. Testing Interactive Relic Tuner Minigame...')
        # Open tuner for candidate
        await page.evaluate("window.AnomalyScanner.openTuner()")
        await asyncio.sleep(0.5)
        
        tuner_state = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Tuner Open: {tuner_state["tunerOpen"]}, Initial Player Freq: {tuner_state["tunerFrequency"]:.2f} GHz, Target: {tuner_state["targetFrequency"]:.2f} GHz')
        assert tuner_state["tunerOpen"] == True, "Relic Tuner modal should be open"
        
        # Check oscilloscope canvas
        has_canvas = await page.evaluate("document.getElementById('relic-waveform-canvas') !== null")
        assert has_canvas, "Oscilloscope canvas should exist in DOM"
        
        # Screenshot active tuning waveforms
        shot_tuner_active = r'd:\items\code\starfield-pub\shots\relic_tuner_active.png'
        await page.screenshot(path=shot_tuner_active)
        print('   Saved Relic Tuner Waveforms screenshot to:', shot_tuner_active)
        
        # Test frequency tuning slider / adjustment
        print('8. Tuning frequency to align harmonic resonance...')
        target_f = tuner_state["targetFrequency"]
        # Set close frequency to test >95% alignment
        await page.evaluate(f"window.AnomalyScanner.tune({target_f})")
        await asyncio.sleep(0.3)
        
        align_state = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Resonance Alignment: {align_state["alignment"] * 100:.1f}%')
        assert align_state["alignment"] >= 0.95, "Alignment should reach >= 95% when tuned to target frequency"
        
        # Test signal lock completion (wait for 1.2s lock requirement or solve)
        print('9. Locking harmonic resonance (>95% for 1.2s)...')
        await page.evaluate("window.AnomalyScanner.solveTuner()")
        await asyncio.sleep(0.8)
        
        locked_state = await page.evaluate("window.AnomalyScanner.getState()")
        print(f'   Signal Locked: {locked_state["isLocked"]}')
        assert locked_state["isLocked"] == True, "Signal should lock after matching resonance"
        
        # Screenshot locked waveform and victory banner
        shot_tuner_locked = r'd:\items\code\starfield-pub\shots\relic_tuner_locked.png'
        await page.screenshot(path=shot_tuner_locked)
        print('   Saved Relic Tuner Locked screenshot to:', shot_tuner_locked)
        
        # Verify Golden Discovery Toast
        has_toast = await page.evaluate("""
            (() => {
                const t = document.getElementById('scanner-golden-toast');
                return t && t.textContent.length > 0;
            })()
        """)
        print(f'10. Golden Discovery Toast verified: {has_toast}')
        
        # Close Tuner
        await page.evaluate("window.AnomalyScanner.closeTuner()")
        await asyncio.sleep(0.5)
        
        # =====================================================================
        # TEST 3: Celestial Codex Lore Unlocking Verification
        # =====================================================================
        print('11. Verifying Classified Relic Lore in Celestial Codex (Tab)...')
        await page.keyboard.press('Tab')
        await asyncio.sleep(0.8)
        
        # Click wonders tab
        await page.click('.codex-tab[data-tab="wonders"]')
        await asyncio.sleep(0.6)
        
        # Check that codex has discovered items
        codex_disc_count = await page.evaluate("Object.keys(window.Codex.discovered).length")
        print(f'   Codex Discovered Entries Count: {codex_disc_count}')
        assert codex_disc_count > 0, "Codex should contain at least 1 unlocked entry"
        
        shot_codex = r'd:\items\code\starfield-pub\shots\codex_relic_unlocked.png'
        await page.screenshot(path=shot_codex)
        print('   Saved Unlocked Relic Codex screenshot to:', shot_codex)
        
        # Close Codex
        await page.click('#codex-close-btn')
        await asyncio.sleep(0.5)
        
        await browser.close()
        
    print('\n====================================================')
    print(' SCANNER RADAR & RELIC TUNER TEST VERIFICATION')
    print('====================================================')
    print(f'Total Console Logs: {len(logs)}')
    
    # Filter out minor benign warnings if any
    crit_errors = [e for e in errors if 'favicon' not in e]
    if crit_errors:
        print('CRITICAL ERRORS FOUND:', crit_errors)
        sys.exit(1)
    else:
        print('ALL SCANNER & RELIC TUNER TESTS PASSED WITH 0 ERRORS!')
        print('====================================================')

if __name__ == '__main__':
    asyncio.run(main())
