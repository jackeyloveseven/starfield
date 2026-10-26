import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from playwright.sync_api import sync_playwright

def verify_thermal_and_retina():
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

    print("=================================================================")
    print(" VERIFYING THERMAL OPTIMIZATION & RETINA RESOLUTION ENGINE")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--no-sandbox']
        )

        # Emulate 120Hz high-DPR mobile phone (e.g. Galaxy S / iPhone Pro, DPR=3.0)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
        )
        page = context.new_page()
        page.on('pageerror', on_page_error)
        page.on('console', on_console)
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(1000)

        # 1. Verify Balanced Mobile Mode Defaults
        print("\n1. Verifying Mobile Balanced Defaults...")
        profile = page.evaluate("() => window.STARFIELD_QUALITY.profile")
        target_fps = page.evaluate("() => window.STARFIELD_QUALITY.getTargetFps()")
        sprite_cap = page.evaluate("() => window.STARFIELD_QUALITY.getHoleSpriteCap()")
        dpr = page.evaluate("() => window.DPR")
        raw_dpr = page.evaluate("() => window.devicePixelRatio")

        print(f"   - Profile: {profile} (Expected: balanced)")
        print(f"   - Target FPS: {target_fps} (Expected: 60)")
        print(f"   - Hole Sprite Cap: {sprite_cap} (Expected: 512)")
        print(f"   - Active DPR: {dpr} (Expected: 2.0, Raw: {raw_dpr})")

        assert profile == 'balanced', f"Expected profile 'balanced', got {profile}"
        assert target_fps == 60, f"Expected mobile target FPS 60, got {target_fps}"
        assert sprite_cap == 512, f"Expected mobile hole sprite cap 512, got {sprite_cap}"
        assert abs(dpr - 2.0) < 0.05, f"Expected mobile balanced DPR ~2.0, got {dpr}"

        # 2. Test 2K Ultra Retina Profile Switch
        print("\n2. Testing 2K Ultra Retina Mode Switch...")
        page.evaluate("() => window.STARFIELD_QUALITY.setProfile('2k')")
        page.wait_for_timeout(300)

        p2k = page.evaluate("() => window.STARFIELD_QUALITY.profile")
        dpr2k = page.evaluate("() => window.DPR")
        print(f"   - Switched Profile: {p2k} (Expected: 2k)")
        print(f"   - 2K Mode DPR: {dpr2k} (Expected: 2.75 for mobile, point-to-point Retina)")
        assert p2k == '2k', f"Expected profile 2k, got {p2k}"
        assert abs(dpr2k - 2.75) < 0.05, f"Expected 2K mobile DPR 2.75, got {dpr2k}"

        # 3. Test PowerSave Mode Switch
        print("\n3. Testing PowerSave Mode Switch...")
        page.evaluate("() => window.STARFIELD_QUALITY.setProfile('powersave')")
        page.wait_for_timeout(300)

        p_ps = page.evaluate("() => window.STARFIELD_QUALITY.profile")
        fps_ps = page.evaluate("() => window.STARFIELD_QUALITY.getTargetFps()")
        dpr_ps = page.evaluate("() => window.DPR")
        cap_ps = page.evaluate("() => window.STARFIELD_QUALITY.getHoleSpriteCap()")
        print(f"   - Switched Profile: {p_ps} (Expected: powersave)")
        print(f"   - PowerSave Target FPS: {fps_ps} (Expected: 45)")
        print(f"   - PowerSave Sprite Cap: {cap_ps} (Expected: 384)")
        print(f"   - PowerSave DPR: {dpr_ps} (Expected: 1.25)")
        assert p_ps == 'powersave', f"Expected powersave, got {p_ps}"
        assert fps_ps == 45, f"Expected 45 fps, got {fps_ps}"
        assert cap_ps == 384, f"Expected 384 cap, got {cap_ps}"
        assert abs(dpr_ps - 1.25) < 0.05, f"Expected 1.25 DPR, got {dpr_ps}"

        # Reset to balanced for flight
        page.evaluate("() => window.STARFIELD_QUALITY.setProfile('balanced')")
        page.wait_for_timeout(200)

        # 4. Test Flight Execution & WebGL Black Hole Shader Compilation
        print("\n4. Testing In-Flight Rendering & Black Hole WebGL Pipeline...")
        page.locator('#begin').click()
        page.wait_for_timeout(2000)

        # Verify holeGL exists and runs without WebGL error
        has_hole = page.evaluate("() => window.Starfield && window.Starfield.getState ? window.Starfield.getState().holeGL : false")
        print(f"   - HoleGL initialized via getState(): {has_hole}")
        assert has_hole, "ERROR: holeGL was not initialized!"

        # 5. Verify Anomaly Radar Overlay Canvas is 0px when Idle
        radar_cv = page.evaluate("""() => {
            const el = document.getElementById('scanner-overlay-canvas');
            return el ? { w: el.width, h: el.height } : null;
        }""")
        print(f"   - Scanner overlay canvas dimensions when idle: {radar_cv}")
        assert radar_cv and radar_cv['w'] == 0 and radar_cv['h'] == 0, f"Expected idle scanner canvas 0x0, got {radar_cv}"

        # 6. Verify Page Errors
        print(f"\n6. Checking Page & Console Errors (Count: {len(errors)})...")
        assert len(errors) == 0, f"Page had {len(errors)} errors: {errors}"

        # Take screenshot of sharp flight
        shot_path = os.path.join(os.environ.get("ANTIGRAVITY_ARTIFACT_DIR", r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367"), "test_retina_sharp_flight.png")
        page.screenshot(path=shot_path)
        print(f"   - Screenshot saved to: {shot_path}")

        browser.close()

    print("\n=================================================================")
    print(" ALL THERMAL & RETINA OPTIMIZATION VERIFICATIONS PASSED!")
    print("=================================================================")

if __name__ == '__main__':
    verify_thermal_and_retina()
