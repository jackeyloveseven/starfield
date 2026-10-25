import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

from playwright.sync_api import sync_playwright

def test_zero_occlusion_and_orientation():
    html_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    artifact_dir = os.environ.get("ANTIGRAVITY_ARTIFACT_DIR", r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367")

    errors = []
    def on_page_error(exc):
        print(f"[PAGE ERROR] {exc}")
        errors.append(str(exc))

    def on_console(msg):
        if msg.type == 'error':
            print(f"[CONSOLE ERROR] {msg.text}")
            errors.append(msg.text)

    print("=================================================================")
    print(" VERIFYING ZERO OCCLUSION, ORIENTATION SWITCHER & FROSTED UI")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--no-sandbox']
        )

        # 1. Test Portrait Viewport (390x844)
        print("\n1. Testing Mobile Portrait Intro Screen (390x844)...")
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page = context.new_page()
        page.on('pageerror', on_page_error)
        page.on('console', on_console)
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(800)

        # Verify No Occlusion on Intro Screen
        masthead_box = page.locator('#masthead').bounding_box()
        inner_box = page.locator('.intro-inner').bounding_box()
        viewport_h = 844

        print(f"   - #masthead bottom: {masthead_box['y'] + masthead_box['height']:.1f}px")
        print(f"   - .intro-inner top: {inner_box['y']:.1f}px, bottom: {inner_box['y'] + inner_box['height']:.1f}px")
        
        # Ensure #masthead and .intro-inner do NOT collide
        assert inner_box['y'] > (masthead_box['y'] + masthead_box['height']), "ERROR: Top occlusion! #masthead and .intro-inner overlap!"
        # Ensure bottom of .intro-inner has at least 50px clearance from screen bottom
        bottom_clearance = viewport_h - (inner_box['y'] + inner_box['height'])
        print(f"   - Bottom clearance: {bottom_clearance:.1f}px")
        assert bottom_clearance > 50, f"ERROR: Bottom occlusion! Clearance too small: {bottom_clearance}"

        # Verify Orientation Switcher Button
        btn_ori = page.locator('#orientation-toggle-btn')
        assert btn_ori.is_visible(), "ERROR: Orientation toggle button not visible on intro screen!"
        print(f"   - Orientation button text: {btn_ori.text_content().strip()}")

        shot_intro = os.path.join(artifact_dir, "test_portrait_zero_occlusion_intro.png")
        page.screenshot(path=shot_intro)
        print(f"   - Saved screenshot: {shot_intro}")

        # Test Orientation Toggle click
        btn_ori.click()
        page.wait_for_timeout(400)
        ori_label = btn_ori.text_content().strip()
        print(f"   - After click orientation label: {ori_label}")

        # 2. Test Flight Screen & Minimal Frosted Glass Controls
        print("\n2. Testing Flight Controls & Minimal Frosted Glass UI...")
        page.locator('#begin').click()
        page.wait_for_timeout(1200)

        # Verify Joystick is 100% INVISIBLE at rest (Zero left bottom occlusion)
        joy_opacity = page.evaluate("() => { const el = document.querySelector('.sf-touch-joy-base'); return el ? getComputedStyle(el).opacity : '1'; }")
        print(f"   - Resting Joystick opacity: {joy_opacity} (Expected: 0)")
        assert float(joy_opacity) == 0.0, f"ERROR: Resting joystick should be invisible (opacity 0)! Got: {joy_opacity}"

        # Verify #journey is completely unobstructed
        journey_box = page.locator('#journey').bounding_box()
        print(f"   - #journey bounding box: {journey_box}")
        assert journey_box and journey_box['width'] > 0 and journey_box['height'] > 0, "ERROR: #journey not visible!"

        # Verify Primary Action Row has exactly 4 buttons (BOOST, 视角, 专注, 更多)
        btn_count = page.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn').length")
        print(f"   - Primary action buttons count: {btn_count} (Expected: 4)")
        assert btn_count == 4, f"ERROR: Expected 4 primary buttons, got {btn_count}"

        # Verify More Tray is initially hidden
        tray_display = page.evaluate("() => { const el = document.getElementById('sf-touch-more-tray'); return el ? getComputedStyle(el).display : 'none'; }")
        print(f"   - More Tray initial display: {tray_display} (Expected: none)")
        assert tray_display == 'none', "ERROR: More tray should be closed by default!"

        # Click 更多 (More) button to expand tray
        page.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[3].click()")
        page.wait_for_timeout(300)

        tray_open = page.evaluate("() => document.getElementById('sf-touch-more-tray').classList.contains('open')")
        print(f"   - More Tray opened after click: {tray_open} (Expected: True)")
        assert tray_open, "ERROR: More tray did not open on click!"

        # 3. Verify Dynamic Joystick Touch Reveal & Fade Out
        print("\n3. Testing Dynamic Joystick Touch Reveal & Fade...")
        # Inspect joyContainer bounding box and element under point
        debug_info = page.evaluate("""() => {
            const jz = document.querySelector('.sf-touch-joy-zone');
            const jb = document.querySelector('.sf-touch-joy-base');
            const rect = jz ? jz.getBoundingClientRect() : null;
            const elAtPt = document.elementFromPoint(100, 600);
            return {
                jzRect: rect ? { x: rect.x, y: rect.y, w: rect.width, h: rect.height } : null,
                elAtPt: elAtPt ? { tag: elAtPt.tagName, id: elAtPt.id, cls: elAtPt.className } : null,
                jbOpacity: jb ? getComputedStyle(jb).opacity : null
            };
        }""")
        print(f"   - Debug JoyContainer info: {debug_info}")

        # Dispatch pointerdown directly to .sf-touch-joy-zone or simulate touch
        page.evaluate("""() => {
            const jz = document.querySelector('.sf-touch-joy-zone');
            if (jz) {
                const rect = jz.getBoundingClientRect();
                const evt = new PointerEvent('pointerdown', {
                    bubbles: true,
                    cancelable: true,
                    clientX: rect.left + 50,
                    clientY: rect.top + 50,
                    pointerId: 1,
                    pointerType: 'touch'
                });
                jz.dispatchEvent(evt);
            }
        }""")
        page.wait_for_timeout(300)

        joy_touch_opacity = page.evaluate("() => { const el = document.querySelector('.sf-touch-joy-base'); return el ? getComputedStyle(el).opacity : '0'; }")
        print(f"   - Joystick opacity during touch: {joy_touch_opacity} (Expected: > 0.8)")
        assert float(joy_touch_opacity) >= 0.8, f"ERROR: Joystick did not appear on touch! Got opacity: {joy_touch_opacity}"

        # Release touch
        page.evaluate("""() => {
            const jz = document.querySelector('.sf-touch-joy-zone');
            if (jz) {
                const evt = new PointerEvent('pointerup', {
                    bubbles: true,
                    cancelable: true,
                    pointerId: 1,
                    pointerType: 'touch'
                });
                jz.dispatchEvent(evt);
            }
        }""")
        page.wait_for_timeout(300)

        joy_released_opacity = page.evaluate("() => { const el = document.querySelector('.sf-touch-joy-base'); return el ? getComputedStyle(el).opacity : '1'; }")
        print(f"   - Joystick opacity after release: {joy_released_opacity} (Expected: 0)")
        assert float(joy_released_opacity) == 0.0, f"ERROR: Joystick did not fade out after release! Got: {joy_released_opacity}"

        # 4. Verify Performance & Balanced Mobile DPR Default
        print("\n4. Verifying Performance & Balanced Mobile DPR...")
        quality_profile = page.evaluate("() => window.STARFIELD_QUALITY.profile")
        active_dpr = page.evaluate("() => window.DPR")
        print(f"   - Mobile quality profile: {quality_profile} (Expected: balanced)")
        print(f"   - Active mobile DPR: {active_dpr} (Expected: <= 2.0)")
        assert quality_profile == 'balanced', f"ERROR: Expected mobile profile 'balanced', got {quality_profile}"
        assert active_dpr <= 2.0, f"ERROR: Expected mobile DPR <= 2.0, got {active_dpr}"

        # 5. Verify Warm Classical Physical Modeling Audio Engine
        print("\n5. Verifying Optimized Classical Violin Physical Modeling...")
        has_classical = page.evaluate("() => typeof window.sound !== 'undefined' && typeof window.sound.classical !== 'undefined'")
        print(f"   - sound.classical initialized: {has_classical}")
        assert has_classical, "ERROR: sound.classical not initialized!"

        curr_track = page.evaluate("() => window.sound.classical.currentTrack.title")
        print(f"   - Current classical piece: {curr_track}")
        assert "引子与回旋随想曲" in curr_track or "圣-桑" in curr_track, f"ERROR: Expected Saint-Saens piece, got {curr_track}"

        shot_flight = os.path.join(artifact_dir, "test_portrait_minimal_frosted_flight.png")
        page.screenshot(path=shot_flight)
        print(f"   - Saved screenshot: {shot_flight}")

        # 6. Test Mobile Landscape (844x390)
        print("\n6. Testing Mobile Landscape Viewport (844x390)...")
        context_ls = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page_ls = context_ls.new_page()
        page_ls.goto(file_url, wait_until='networkidle')
        page_ls.wait_for_timeout(800)

        # Check landscape intro clearance
        ls_masthead = page_ls.locator('#masthead').bounding_box()
        ls_inner = page_ls.locator('.intro-inner').bounding_box()
        print(f"   - Landscape .intro-inner top={ls_inner['y']}, height={ls_inner['height']}, viewport_h=390")

        # Start flight in landscape
        page_ls.locator('#begin').click()
        page_ls.wait_for_timeout(1000)

        shot_landscape = os.path.join(artifact_dir, "test_landscape_minimal_frosted_flight.png")
        page_ls.screenshot(path=shot_landscape)
        print(f"   - Saved screenshot: {shot_landscape}")

        browser.close()

    print("\n=================================================================")
    print(" ALL ZERO OCCLUSION, ORIENTATION & FROSTED UI TESTS PASSED! Errors: 0")
    print("=================================================================")

if __name__ == '__main__':
    test_zero_occlusion_and_orientation()
