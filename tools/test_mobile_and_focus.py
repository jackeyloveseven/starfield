import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_mobile_and_focus_engine():
    html_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    errors = []
    def on_page_error(exc):
        print(f"[PAGE ERROR] {exc}")
        errors.append(str(exc))

    def on_console(msg):
        if msg.type == 'error':
            print(f"[CONSOLE ERROR] {msg.text}")
            errors.append(msg.text)

    artifact_dir = os.environ.get("ANTIGRAVITY_ARTIFACT_DIR", r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367")

    print("=================================================================")
    print(" VERIFYING MOBILE TOUCH CONTROLS & FOCUS POMODORO ENGINE")
    print("=================================================================")

    with sync_playwright() as p:
        # Launch installed Chrome with mobile emulation
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=[
                '--use-gl=angle',
                '--use-angle=gl-egl',
                '--enable-webgl',
                '--no-sandbox'
            ]
        )

        # 1. Test Native Portrait Viewport
        print("\n1. Testing Portrait Viewport (390x844 iPhone/Android)...")
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page = context.new_page()
        page.on('pageerror', on_page_error)
        page.on('console', on_console)

        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Check rotation class (must NOT have 'rotated' class on #world)
        has_rotated = page.evaluate("() => document.getElementById('world').classList.contains('rotated')")
        print(f"   - #world has 'rotated' class: {has_rotated} (Expected: False)")
        assert not has_rotated, "ERROR: #world should NOT have 'rotated' class in native responsive layout!"

        # Check touch overlay initial visibility (must be hidden on intro screen)
        overlay_display = page.evaluate("() => { const el = document.getElementById('starfield-touch-overlay'); return el ? getComputedStyle(el).display : 'none'; }")
        print(f"   - Touch overlay display on intro screen: {overlay_display} (Expected: none)")
        assert overlay_display == 'none', "ERROR: Touch overlay should be hidden on intro screen!"

        # Check #begin button visibility and clickability
        begin_box = page.locator('#begin').bounding_box()
        print(f"   - #begin button bounding box: {begin_box}")
        assert begin_box and begin_box['width'] > 0 and begin_box['height'] > 0, "ERROR: #begin button not visible!"

        # Click #begin to start flight
        page.locator('#begin').click()
        page.wait_for_timeout(1500)

        # Verify flight started
        is_flying = page.evaluate("() => document.getElementById('world').classList.contains('flying')")
        print(f"   - Flight started (#world has 'flying'): {is_flying}")
        assert is_flying, "ERROR: Flight did not start after clicking #begin!"

        # Check touch overlay is now visible
        overlay_display_flying = page.evaluate("() => { const el = document.getElementById('starfield-touch-overlay'); return el ? getComputedStyle(el).display : 'none'; }")
        print(f"   - Touch overlay display during flight: {overlay_display_flying} (Expected: block)")
        assert overlay_display_flying == 'block', "ERROR: Touch overlay should be visible during flight!"

        # Check desktop #controls is hidden on mobile
        controls_display = page.evaluate("() => { const el = document.getElementById('controls'); return el ? getComputedStyle(el).display : 'block'; }")
        print(f"   - Desktop #controls display on mobile: {controls_display} (Expected: none)")
        assert controls_display == 'none', "ERROR: Desktop #controls should be hidden on mobile coarse-pointer screen!"

        # Take screenshot of portrait flight
        shot1 = os.path.join(artifact_dir, "test_portrait_mobile_flight.png")
        page.screenshot(path=shot1)
        print(f"   - Saved screenshot: {shot1}")

        # 2. Test Focus Pomodoro Engine
        print("\n2. Testing Focus Pomodoro Engine...")
        engine_exists = page.evaluate("() => typeof window.StarfieldFocusEngine !== 'undefined'")
        print(f"   - window.StarfieldFocusEngine defined: {engine_exists}")
        assert engine_exists, "ERROR: StarfieldFocusEngine not defined on window!"

        # Open Focus Dashboard via button or 'O' key
        page.evaluate("() => window.StarfieldFocusEngine.openDashboard()")
        page.wait_for_timeout(500)

        modal_visible = page.evaluate("() => !!document.getElementById('sf-focus-dashboard-modal')")
        print(f"   - Focus Dashboard Modal visible: {modal_visible}")
        assert modal_visible, "ERROR: Focus Dashboard modal failed to open!"

        shot2 = os.path.join(artifact_dir, "test_focus_dashboard.png")
        page.screenshot(path=shot2)
        print(f"   - Saved screenshot: {shot2}")

        # Test selecting a preset (e.g. 30min preset idx 2)
        page.evaluate("() => document.querySelectorAll('.sf-focus-preset-card')[2].click()")
        selected_idx = page.evaluate("() => window.StarfieldFocusEngine.selectedPresetIndex")
        print(f"   - Selected preset index: {selected_idx} (Expected: 2)")
        assert selected_idx == 2, "ERROR: Preset card selection failed!"

        # Start Focus Mission
        page.locator('#sf-focus-start-btn').click()
        page.wait_for_timeout(1000)

        focus_state = page.evaluate("() => window.StarfieldFocusEngine.state")
        ticker_display = page.evaluate("() => { const el = document.getElementById('sf-focus-ticker'); return el ? getComputedStyle(el).display : 'none'; }")
        print(f"   - Focus Engine state: {focus_state} (Expected: RUNNING)")
        print(f"   - Focus HUD Ticker display: {ticker_display} (Expected: flex)")
        assert focus_state == 'RUNNING', f"ERROR: Expected RUNNING, got {focus_state}"
        assert ticker_display == 'flex', f"ERROR: Expected flex, got {ticker_display}"

        shot3 = os.path.join(artifact_dir, "test_focus_running_hud.png")
        page.screenshot(path=shot3)
        print(f"   - Saved screenshot: {shot3}")

        # Test Leaving App Warning Sequence
        print("\n3. Testing Leave-App (Tab Switch / Blur) Grace Period & Warning...")
        page.evaluate("() => window.dispatchEvent(new Event('blur'))")
        page.wait_for_timeout(500)
        warning_state = page.evaluate("() => window.StarfieldFocusEngine.state")
        print(f"   - State on blur: {warning_state} (Expected: WARNING)")
        assert warning_state == 'WARNING', f"ERROR: Expected WARNING, got {warning_state}"

        # Return to app and verify warning cleared
        page.evaluate("() => window.dispatchEvent(new Event('focus'))")
        page.wait_for_timeout(500)
        cleared_state = page.evaluate("() => window.StarfieldFocusEngine.state")
        print(f"   - State on focus resume: {cleared_state} (Expected: RUNNING)")
        assert cleared_state == 'RUNNING', f"ERROR: Expected RUNNING, got {cleared_state}"

        # Test Mission Completion & Reward Unlock
        print("\n4. Testing Mission Completion, Reward Unlocks & Tesseract Celebration...")
        # Fast-forward timer to complete mission
        page.evaluate("""() => {
            window.StarfieldFocusEngine.elapsedSec = window.StarfieldFocusEngine.targetDurationSec;
            window.StarfieldFocusEngine.tick();
        }""")
        page.wait_for_timeout(1000)

        end_state = page.evaluate("() => window.StarfieldFocusEngine.state")
        titan_unlocked = page.evaluate("() => window.StarfieldFocusEngine.stats.unlockedRewards.hull_titan")
        golden_unlocked = page.evaluate("() => window.StarfieldFocusEngine.stats.unlockedRewards.trail_golden")
        relic_unlocked = page.evaluate("() => window.StarfieldFocusEngine.stats.unlockedRewards.relic_focus")
        summary_modal = page.evaluate("() => !!document.getElementById('starfield-focus-modal')")

        print(f"   - Focus Engine state after completion: {end_state} (Expected: SUCCESS)")
        print(f"   - Unlocked Titan Gold Hull: {titan_unlocked} (Expected: True)")
        print(f"   - Unlocked Relic Focus: {relic_unlocked} (Expected: True)")
        print(f"   - Summary Modal visible: {summary_modal} (Expected: True)")

        assert end_state == 'SUCCESS', f"ERROR: Expected SUCCESS, got {end_state}"
        assert titan_unlocked, "ERROR: Titan Gold Hull should be unlocked!"
        assert summary_modal, "ERROR: Summary modal should be visible!"

        shot4 = os.path.join(artifact_dir, "test_focus_completion_rewards.png")
        page.screenshot(path=shot4)
        print(f"   - Saved screenshot: {shot4}")

        context.close()
        browser.close()

    print("\n=================================================================")
    print(f" ALL MOBILE UI & FOCUS POMODORO ENGINE TESTS PASSED! Errors: {len(errors)}")
    print("=================================================================")
    if errors:
        sys.exit(1)

if __name__ == '__main__':
    test_mobile_and_focus_engine()
