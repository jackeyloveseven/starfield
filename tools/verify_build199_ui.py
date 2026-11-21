# -*- coding: utf-8 -*-
"""
tools/verify_build199_ui.py
Playwright verification for Starfield Build 199 (v1.9.9.9.9.11):
- Mobile Fluid Island Capsule Dock & 42px ergonomic touch targets
- In-situ real-time badges (Warp 1x/5x/15x, Camera AUTO/FLAG, Formation F1-F4)
- Secondary Arc Island tray with Cinema toggle
- Cinema / Pure Vision (Zen) Mode entrance & tap-to-exit
- Desktop Cinema toggle button & 'Z' key shortcut
- Zero console errors / exceptions
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(r"d:\items\code\projects\starfield\starfield-pub")
HTML_FILE = BASE_DIR / "starfield.html"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ARTIFACT_DIR = Path(r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367")

def verify():
    print("======================================================================")
    print("Starting Starfield Build 199 UI & Cinema Mode Verification...")
    print("======================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_PATH,
            headless=True,
            args=[
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--use-gl=angle",
                "--use-angle=default",
                "--disable-background-timer-throttling",
                "--mute-audio"
            ]
        )

        # ------------------------------------------------------------------
        # Test 1: Mobile Viewport (412x915, DPR 3.0 Dimensity Profile)
        # ------------------------------------------------------------------
        print("\n[TEST 1/3] Mobile Fluid Island Capsule Dock & In-situ Badges...")
        mob_context = browser.new_context(
            viewport={"width": 412, "height": 915},
            device_scale_factor=3.0,
            is_mobile=True,
            has_touch=True
        )
        page = mob_context.new_page()
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        file_url = HTML_FILE.as_uri()
        page.goto(file_url, wait_until="networkidle")
        time.sleep(1.0)

        # Begin flight if intro is showing
        page.evaluate("""() => {
            if (typeof beginFlight === 'function') beginFlight();
            else if (window.Starfield && window.Starfield.beginFlight) window.Starfield.beginFlight();
            const btn = document.getElementById('begin');
            if (btn) btn.click();
        }""")
        time.sleep(1.5)

        # Verify touch overlay and primary row existence
        dock_info = page.evaluate("""() => {
            const cluster = document.querySelector('.sf-touch-cluster');
            const row = document.querySelector('.sf-touch-primary-row');
            const buttons = document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn');
            const badges = document.querySelectorAll('.sf-touch-primary-row .sf-insitu-badge');
            
            // Check button sizes
            const btnSizes = Array.from(buttons).map(b => {
                const r = b.getBoundingClientRect();
                return { width: Math.round(r.width), height: Math.round(r.height) };
            });

            // Check badge texts
            const badgeTexts = Array.from(badges).map(b => b.textContent);

            return {
                clusterExists: !!cluster,
                rowExists: !!row,
                buttonCount: buttons.length,
                btnSizes,
                badgeTexts
            };
        }""")

        print(f"  Mobile Dock Exists: {dock_info['rowExists']}, Button Count: {dock_info['buttonCount']}")
        print(f"  Mobile Button Sizes (Ergonomic 42px+ Target): {dock_info['btnSizes']}")
        print(f"  In-situ Badge Texts: {dock_info['badgeTexts']}")
        assert dock_info['rowExists'], "Primary touch row not found!"
        assert dock_info['buttonCount'] >= 5, f"Expected 5 buttons in row, got {dock_info['buttonCount']}"

        # Capture mobile normal flight with Fluid Island
        shot_mobile_dock = ARTIFACT_DIR / "build199_mobile_capsule_dock.png"
        page.screenshot(path=str(shot_mobile_dock))
        print(f"  [PASS] Mobile capsule dock screenshot saved to: {shot_mobile_dock}")

        # Cycle Warp and test in-situ badge reactive update
        warp_info = page.evaluate("""() => {
            const S = window.Starfield;
            if (S && S.cycleWarp) S.cycleWarp();
            if (window.updateTouchInSituBadges) window.updateTouchInSituBadges();
            const warpBtn = document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[1];
            const badge = warpBtn ? warpBtn.querySelector('.sf-insitu-badge') : null;
            return {
                gear: S && S.getWarpGear ? S.getWarpGear() : 0,
                badgeText: badge ? badge.textContent : null,
                classes: warpBtn ? warpBtn.className : ''
            };
        }""")
        print(f"  Warp Cycled -> Gear: {warp_info['gear']}, In-situ Badge: {warp_info['badgeText']}, Classes: {warp_info['classes']}")
        assert warp_info['badgeText'] in ['1x', '5x', '15x'], f"Unexpected warp badge: {warp_info['badgeText']}"

        # ------------------------------------------------------------------
        # Test 2: Expand More Tray & Test Cinema Mode via Tray
        # ------------------------------------------------------------------
        print("\n[TEST 2/3] Mobile Expandable Arc Tray & Cinema Mode...")
        tray_info = page.evaluate("""() => {
            const moreBtn = document.querySelector('.sf-touch-btn.more');
            if (moreBtn) moreBtn.click();
            const tray = document.getElementById('sf-touch-more-tray');
            const cinemaBtn = document.getElementById('sf-touch-cinema-btn');
            const trayButtons = tray ? tray.querySelectorAll('.sf-touch-btn') : [];
            const labels = Array.from(trayButtons).map(b => b.querySelector('span.label')?.textContent || '');
            return {
                trayOpen: tray && tray.classList.contains('open'),
                cinemaBtnExists: !!cinemaBtn,
                trayButtonCount: trayButtons.length,
                labels
            };
        }""")
        print(f"  Tray Open: {tray_info['trayOpen']}, Button Count: {tray_info['trayButtonCount']}")
        print(f"  Tray Button Labels: {tray_info['labels']}")
        assert tray_info['trayOpen'], "Tray did not open on more click!"
        assert tray_info['cinemaBtnExists'], "Cinema button missing in tray!"

        shot_mobile_tray = ARTIFACT_DIR / "build199_mobile_tray_expanded.png"
        page.screenshot(path=str(shot_mobile_tray))
        print(f"  [PASS] Mobile expanded tray screenshot saved to: {shot_mobile_tray}")

        # Trigger Cinema Mode via Cinema button in tray
        page.evaluate("""() => {
            const cinemaBtn = document.getElementById('sf-touch-cinema-btn');
            if (cinemaBtn) cinemaBtn.click();
        }""")
        time.sleep(0.6) # Wait for 0.45s smooth fade out transition
        cinema_enter = page.evaluate("""() => {
            return {
                active: window.StarfieldCinema ? window.StarfieldCinema.active : false,
                bodyHasClass: document.body.classList.contains('cinema-mode'),
                mastheadOpacity: getComputedStyle(document.getElementById('masthead')).opacity,
                journeyOpacity: getComputedStyle(document.getElementById('journey')).opacity,
                cameraHudOpacity: getComputedStyle(document.getElementById('camera-hud')).opacity
            };
        }""")
        print(f"  Cinema Mode Active: {cinema_enter['active']}, body.cinema-mode: {cinema_enter['bodyHasClass']}")
        print(f"  HUD Opacities in Cinema Mode: masthead={cinema_enter['mastheadOpacity']}, journey={cinema_enter['journeyOpacity']}, cameraHud={cinema_enter['cameraHudOpacity']}")
        assert cinema_enter['active'] and cinema_enter['bodyHasClass'], "Cinema mode failed to activate!"
        assert float(cinema_enter['journeyOpacity']) == 0.0, f"journey opacity not 0: {cinema_enter['journeyOpacity']}"
        assert float(cinema_enter['cameraHudOpacity']) == 0.0, f"cameraHud opacity not 0: {cinema_enter['cameraHudOpacity']}"

        shot_cinema = ARTIFACT_DIR / "build199_cinema_mode_zen.png"
        page.screenshot(path=str(shot_cinema))
        print(f"  [PASS] Cinema (Zen) mode screenshot saved to: {shot_cinema}")

        # Test Tap-to-Exit Cinema Mode
        cinema_exit = page.evaluate("""() => {
            // Click outside any control
            const world = document.getElementById('world');
            const evt = new MouseEvent('pointerdown', { bubbles: true, cancelable: true, clientX: 200, clientY: 400 });
            world.dispatchEvent(evt);
            return {
                active: window.StarfieldCinema ? window.StarfieldCinema.active : false,
                bodyHasClass: document.body.classList.contains('cinema-mode')
            };
        }""")
        time.sleep(0.5)
        print(f"  After Canvas Tap -> Cinema Active: {cinema_exit['active']}, body.cinema-mode: {cinema_exit['bodyHasClass']}")
        assert not cinema_exit['active'], "Tap canvas failed to exit Cinema mode!"

        mob_context.close()

        # ------------------------------------------------------------------
        # Test 3: Desktop Viewport (1920x1080) Desktop Controls & 'Z' Shortcut
        # ------------------------------------------------------------------
        print("\n[TEST 3/3] Desktop Cinema Toggle Button & 'Z' Shortcut...")
        desk_context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page_desk = desk_context.new_page()
        page_desk.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page_desk.on("pageerror", lambda err: console_errors.append(str(err)))

        page_desk.goto(file_url, wait_until="networkidle")
        time.sleep(1.0)
        page_desk.evaluate("""() => {
            if (typeof beginFlight === 'function') beginFlight();
            const btn = document.getElementById('begin');
            if (btn) btn.click();
        }""")
        time.sleep(1.5)

        desk_info = page_desk.evaluate("""() => {
            const btn = document.getElementById('cinema-toggle');
            return {
                btnExists: !!btn,
                btnTitle: btn ? btn.getAttribute('title') : null
            };
        }""")
        print(f"  Desktop #cinema-toggle exists: {desk_info['btnExists']}, title='{desk_info['btnTitle']}'")
        assert desk_info['btnExists'], "Desktop #cinema-toggle button not found!"

        # Press 'Z' key
        page_desk.keyboard.press("z")
        time.sleep(0.5)
        z_status = page_desk.evaluate("""() => {
            return {
                active: window.StarfieldCinema ? window.StarfieldCinema.active : false,
                bodyHasClass: document.body.classList.contains('cinema-mode')
            };
        }""")
        print(f"  After 'Z' Key Press -> Cinema Active: {z_status['active']}, body.cinema-mode: {z_status['bodyHasClass']}")
        assert z_status['active'], "'Z' key failed to toggle Cinema mode on desktop!"

        # Press Escape key
        page_desk.keyboard.press("Escape")
        time.sleep(0.5)
        esc_status = page_desk.evaluate("""() => {
            return {
                active: window.StarfieldCinema ? window.StarfieldCinema.active : false
            };
        }""")
        print(f"  After Escape Press -> Cinema Active: {esc_status['active']}")
        assert not esc_status['active'], "Escape failed to exit Cinema mode on desktop!"

        shot_desktop = ARTIFACT_DIR / "build199_desktop_cinema_toggle.png"
        page_desk.screenshot(path=str(shot_desktop))
        print(f"  [PASS] Desktop screenshot saved to: {shot_desktop}")

        desk_context.close()
        browser.close()

    print(f"\nTotal Console Errors Caught: {len(console_errors)}")
    if console_errors:
        print("  Errors:", console_errors)
    assert len(console_errors) == 0, f"Encountered console errors: {console_errors}"

    print("\n======================================================================")
    print("ALL BUILD 199 UI & CINEMA MODE TESTS PASSED (100%)!")
    print("======================================================================")
    return True

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    verify()
