import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    html_path = os.path.abspath('starfield.html')
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    print(f"Testing URL: {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 412, "height": 915},
            device_scale_factor=2.0,
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(1500)

        # 1. Check window.STARFIELD_QUALITY availability
        quality_info = page.evaluate("""() => {
            const Q = window.STARFIELD_QUALITY;
            return {
                exists: !!Q,
                profile: Q ? Q.profile : null,
                fpsMode: Q ? Q.fpsMode : null,
                targetFps: Q ? Q.getTargetFps() : null,
                perfHudEnabled: Q ? Q.perfHudEnabled : null,
                focusEcoEnabled: Q ? Q.focusEcoEnabled : null
            };
        }""")
        print(f"STARFIELD_QUALITY info: {quality_info}")
        assert quality_info["exists"], "window.STARFIELD_QUALITY must exist"
        assert quality_info["fpsMode"] == "uncapped", "Default fpsMode must be 'uncapped'"
        assert quality_info["targetFps"] == 0, "Default targetFps must be 0 (uncapped)"

        # 2. Test FPS preference switching
        fps_tests = [
            ("60", 60),
            ("45", 45),
            ("uncapped", 0)
        ]
        for mode, expected_target in fps_tests:
            page.evaluate(f"window.STARFIELD_QUALITY.setFpsMode('{mode}')")
            t_fps = page.evaluate("window.STARFIELD_QUALITY.getTargetFps()")
            cur_mode = page.evaluate("window.STARFIELD_QUALITY.fpsMode")
            print(f"Mode switch '{mode}' -> fpsMode={cur_mode}, targetFps={t_fps}")
            assert cur_mode == mode, f"fpsMode should be {mode}"
            assert t_fps == expected_target, f"targetFps should be {expected_target}"

        # 3. Test Perf HUD Toggle and UI Rendering
        page.evaluate("window.STARFIELD_QUALITY.togglePerfHud(true)")
        page.wait_for_timeout(700) # Wait for 500ms telemetry tick

        hud_state = page.evaluate("""() => {
            const hud = document.getElementById('sf-perf-hud');
            const fpsEl = document.getElementById('sf-hud-fps');
            const hzEl = document.getElementById('sf-hud-hz');
            const dprEl = document.getElementById('sf-hud-dpr');
            const msEl = document.getElementById('sf-hud-ms');
            return {
                exists: !!hud,
                visible: hud ? window.getComputedStyle(hud).display !== 'none' : false,
                fpsText: fpsEl ? fpsEl.textContent : null,
                hzText: hzEl ? hzEl.textContent : null,
                dprText: dprEl ? dprEl.textContent : null,
                msText: msEl ? msEl.textContent : null
            };
        }""")
        print(f"Perf HUD state: {hud_state}")
        assert hud_state["exists"], "Perf HUD element #sf-perf-hud should exist"
        assert hud_state["visible"], "Perf HUD should be visible when enabled"
        assert hud_state["fpsText"] != "--", "FPS should be computed and rendered"

        # 4. Test Settings Drawer Buttons
        page.evaluate("document.getElementById('settings-drawer').classList.add('open')")
        page.wait_for_timeout(300)

        btn_fps_60 = page.locator("#btn-fps-60")
        assert btn_fps_60.is_visible(), "#btn-fps-60 should be visible in drawer"
        btn_fps_60.click()
        page.wait_for_timeout(200)

        assert page.evaluate("window.STARFIELD_QUALITY.fpsMode") == "60", "Clicking #btn-fps-60 must set fpsMode to '60'"
        assert "active" in btn_fps_60.get_attribute("class"), "#btn-fps-60 must have active class"

        btn_toggle_hud = page.locator("#btn-toggle-perf-hud")
        assert btn_toggle_hud.is_visible(), "#btn-toggle-perf-hud should be visible"
        print(f"Perf HUD toggle button text: {btn_toggle_hud.inner_text()}")

        # 5. Test Focus Eco Cruise Idle Throttle
        eco_test = page.evaluate("""() => {
            const Engine = window.StarfieldFocusEngine;
            if (!Engine) return { ok: false, reason: 'no engine' };
            // Start focus
            Engine.startMission(15);
            // Simulate idle > 25s
            window.lastUserActiveTime = performance.now() - 30000;
            Engine.tick();
            const throttled = window.STARFIELD_QUALITY.isFocusEcoThrottled;
            const targetWithEco = window.STARFIELD_QUALITY.getTargetFps();
            const tickerHtml = document.getElementById('sf-focus-ticker')?.innerHTML || '';
            const hasEcoBadge = tickerHtml.includes('sf-focus-ticker-eco');
            
            // Now simulate user activity
            window.dispatchEvent(new PointerEvent('pointerdown'));
            const unthrottled = !window.STARFIELD_QUALITY.isFocusEcoThrottled;

            // Cleanup
            Engine.failMission();
            return {
                throttled,
                targetWithEco,
                hasEcoBadge,
                unthrottled
            };
        }""")
        print(f"Eco Cruise Idle test: {eco_test}")
        assert eco_test["throttled"], "Should be eco throttled after 25s idle in focus"
        assert eco_test["targetWithEco"] == 45, "getTargetFps should return 45 when eco throttled"
        assert eco_test["hasEcoBadge"], "Focus ticker should display eco badge"
        assert eco_test["unthrottled"], "User interaction must immediately cancel eco throttle"

        # 6. Check console errors
        print(f"Total console errors: {len(console_errors)}")
        if console_errors:
            print(f"Console errors: {console_errors}")
        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"

        # Take screenshot of the Perf HUD and Settings Drawer
        screenshot_path = "tools/test_perf_telemetry_hud.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()
        print("ALL TESTS PASSED!")

if __name__ == "__main__":
    main()
