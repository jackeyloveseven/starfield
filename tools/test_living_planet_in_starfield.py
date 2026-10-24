import os
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from playwright.sync_api import sync_playwright

def test_living_planet_flight():
    html_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    shots_dir = os.path.abspath(r"d:\items\code\starfield-pub\shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" STARFIELD IN-FLIGHT LIVING PLANET ENGINE AUTOMATED TEST SUITE")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--no-sandbox",
                "--disable-gpu-sandbox"
            ]
        )
        page = browser.new_page(viewport={"width": 1600, "height": 900})

        console_logs = []
        errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print(f"1. Navigating to: file:///{html_path}")
        page.goto(f"file:///{html_path}")
        page.wait_for_timeout(2000)

        # Launch flight
        print("2. Clicking #begin to embark on deep-space voyage...")
        page.click("#begin")
        page.wait_for_timeout(2000)

        # Check LivingPlanetEngine
        engine_status = page.evaluate("""() => {
            return {
                hasEngine: typeof LivingPlanetEngine !== 'undefined',
                enabled: typeof LivingPlanetEngine !== 'undefined' ? LivingPlanetEngine.enabled : false,
                hasThree: typeof THREE !== 'undefined'
            };
        }""")
        print(f"3. LivingPlanetEngine status: {engine_status}")
        assert engine_status["hasEngine"], "LivingPlanetEngine not loaded!"
        assert engine_status["hasThree"], "Three.js not loaded!"

        # Warp forward to approach a planetary encounter
        print("4. Super-cruising forward to encounter celestial worlds...")
        page.evaluate("""() => {
            // Speed boost to advance chunks quickly
            if (typeof WarpDrive !== 'undefined') {
                WarpDrive.gearIndex = 2; // 15.0c hyperwarp
                WarpDrive.updateUI();
            }
        }""")

        page.wait_for_timeout(4000)

        # Check travel distance
        travel_dist = page.evaluate("() => window.Starfield ? window.Starfield.getTravel() : 0")
        print(f"5. Current travel distance: {travel_dist:.1f} units")

        # Capture in-flight screenshot with 3D living planet
        flight_shot = os.path.join(shots_dir, "living_planet_in_flight.png")
        page.screenshot(path=flight_shot)
        print(f"6. Saved in-flight screenshot to: {flight_shot}")

        # Test Settings Drawer toggle
        print("7. Testing Settings Drawer 3D Planet toggle...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)
        
        btn_toggle = page.locator("#btn-toggle-living-planet")
        assert btn_toggle.is_visible(), "Toggle button in settings not visible!"
        btn_toggle.click()
        page.wait_for_timeout(500)
        
        toggled_state = page.evaluate("() => LivingPlanetEngine.enabled")
        print(f"   Toggled LivingPlanetEngine.enabled -> {toggled_state}")
        assert toggled_state is False, "Toggle did not disable engine!"

        # Toggle back on
        btn_toggle.click()
        page.wait_for_timeout(500)
        assert page.evaluate("() => LivingPlanetEngine.enabled") is True, "Toggle did not re-enable engine!"
        print("   Re-enabled LivingPlanetEngine successfully.")

        page.keyboard.press("Escape")
        page.wait_for_timeout(500)

        # Measure FPS over 1 second
        print("8. Measuring realtime flight FPS with LivingPlanetEngine active...")
        fps = page.evaluate("""() => new Promise(resolve => {
            let frames = 0;
            const start = performance.now();
            function check() {
                frames++;
                if (performance.now() - start >= 1000) {
                    resolve(frames / ((performance.now() - start) / 1000));
                } else {
                    requestAnimationFrame(check);
                }
            }
            requestAnimationFrame(check);
        })""")
        print(f"   Measured Flight FPS: {fps:.1f} FPS")

        browser.close()

        print("\n=================================================================")
        print(f"TEST SUMMARY: Page Errors: {len(errors)}, Console Logs: {len(console_logs)}")
        if errors:
            print("ERRORS ENCOUNTERED:\n" + "\n".join(errors))
            sys.exit(1)
        else:
            print(">>> ALL IN-FLIGHT LIVING PLANET ENGINE TESTS PASSED WITH 0 ERRORS! <<<")
        print("=================================================================")

if __name__ == "__main__":
    test_living_planet_flight()
