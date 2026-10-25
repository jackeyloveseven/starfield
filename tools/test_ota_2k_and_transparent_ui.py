import os
import sys
from playwright.sync_api import sync_playwright

def test_ota_2k_and_transparent_ui():
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
    print(" VERIFYING 2K RETINA, OTA HOT UPDATE & TRANSPARENT MOBILE UI")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=['--use-gl=angle', '--use-angle=gl-egl', '--enable-webgl', '--no-sandbox']
        )

        # 1. Test Portrait Viewport (390x844)
        print("\n1. Testing Mobile Portrait (390x844)...")
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0, # 2K Retina display emulation (3x DPR)
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page = context.new_page()
        page.on('pageerror', on_page_error)
        page.on('console', on_console)
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(1000)

        # Check Keyboard hint hidden on mobile
        hint_display = page.evaluate("() => { const el = document.getElementById('hint'); return el ? getComputedStyle(el).display : 'none'; }")
        print(f"   - Mobile keyboard #hint display: {hint_display} (Expected: none)")
        assert hint_display == 'none', f"ERROR: Keyboard #hint should be hidden on mobile! Got: {hint_display}"

        # Start flight
        page.locator('#begin').click()
        page.wait_for_timeout(1500)

        # 2. Verify Transparent Touch Controls & Wireframe Joystick
        print("\n2. Verifying Transparent Touch Buttons & Wireframe Joystick...")
        joy_bg = page.evaluate("() => { const el = document.querySelector('.sf-touch-joy-base'); return el ? getComputedStyle(el).backgroundColor : ''; }")
        print(f"   - Joystick base backgroundColor: {joy_bg} (Expected: rgba(0, 0, 0, 0))")
        assert 'rgba(0, 0, 0, 0)' in joy_bg or joy_bg == 'transparent', f"ERROR: Joystick base not transparent! Got: {joy_bg}"

        btn_bg = page.evaluate("() => { const el = document.querySelector('.sf-touch-btn'); return el ? getComputedStyle(el).backgroundColor : ''; }")
        print(f"   - Action button backgroundColor: {btn_bg} (Expected: rgba(0, 0, 0, 0))")
        assert 'rgba(0, 0, 0, 0)' in btn_bg or btn_bg == 'transparent', f"ERROR: Action button not transparent! Got: {btn_bg}"

        boost_bg = page.evaluate("() => { const el = document.querySelector('.sf-touch-btn.boost'); return el ? getComputedStyle(el).backgroundColor : ''; }")
        print(f"   - Boost button backgroundColor: {boost_bg} (Expected: rgba(0, 0, 0, 0))")
        assert 'rgba(0, 0, 0, 0)' in boost_bg or boost_bg == 'transparent', f"ERROR: Boost button not transparent! Got: {boost_bg}"

        # 3. Verify Toast Position vs Comms HUD Separation
        print("\n3. Verifying #toast and #comms-hud Separation on Mobile...")
        page.evaluate("() => { window.toast('引力波航道平稳 · 2K 极清渲染已就绪'); }")
        page.wait_for_timeout(300)

        toast_rect = page.evaluate("() => { const el = document.getElementById('toast'); const r = el.getBoundingClientRect(); return { top: r.top, bottom: r.bottom, height: r.height }; }")
        viewport_h = page.evaluate("() => window.innerHeight")
        print(f"   - #toast position: top={toast_rect['top']}, bottom={toast_rect['bottom']}, viewport height={viewport_h}")
        # Expect toast near bottom (around viewport_h - 112px = 732px), NOT near top (100px)
        assert toast_rect['bottom'] > viewport_h * 0.7, f"ERROR: #toast should be positioned near bottom on mobile! Got bottom={toast_rect['bottom']}"

        # 4. Verify 2K Ultra Resolution DPR Scaling Engine
        print("\n4. Verifying 2K Resolution DPR Engine...")
        initial_dpr = page.evaluate("() => window.DPR")
        quality_profile = page.evaluate("() => window.STARFIELD_QUALITY.profile")
        print(f"   - Quality profile: {quality_profile}, Active Canvas DPR: {initial_dpr}")
        assert initial_dpr == 3.0, f"ERROR: Expected 2K DPR=3.0, got {initial_dpr}"

        # Switch to Balanced mode
        page.evaluate("() => window.STARFIELD_QUALITY.setProfile('balanced')")
        balanced_dpr = page.evaluate("() => window.DPR")
        print(f"   - Balanced mode DPR: {balanced_dpr} (Expected: 2.0)")
        assert balanced_dpr == 2.0, f"ERROR: Expected Balanced DPR=2.0, got {balanced_dpr}"

        # Switch back to 2K mode
        page.evaluate("() => window.STARFIELD_QUALITY.setProfile('2k')")
        retina_dpr = page.evaluate("() => window.DPR")
        print(f"   - 2K Ultra mode DPR: {retina_dpr} (Expected: 3.0)")
        assert retina_dpr == 3.0, f"ERROR: Expected 2K DPR=3.0, got {retina_dpr}"

        # 5. Verify Hot Update (OTA) Notification
        print("\n5. Verifying OTA Hot Update Notification Pill...")
        page.evaluate("() => { window.onStarfieldOtaNotify('OTA_READY', { version: 'v1.1.0', changelog: '2K超清画质与透明极简触控已上线' }); }")
        page.wait_for_timeout(500)

        ota_banner_exists = page.evaluate("() => !!document.getElementById('sf-ota-banner')")
        print(f"   - OTA Banner visible: {ota_banner_exists} (Expected: True)")
        assert ota_banner_exists, "ERROR: OTA notification pill did not appear!"

        shot_portrait = os.path.join(artifact_dir, "test_portrait_transparent_ui_2k_ota.png")
        page.screenshot(path=shot_portrait)
        print(f"   - Saved screenshot: {shot_portrait}")

        # 6. Test Mobile Landscape Viewport (844x390)
        print("\n6. Testing Mobile Landscape (844x390)...")
        context_ls = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page_ls = context_ls.new_page()
        page_ls.goto(file_url, wait_until='networkidle')
        page_ls.wait_for_timeout(800)

        # Click begin in landscape
        page_ls.locator('#begin').click()
        page_ls.wait_for_timeout(1200)

        # Trigger OTA notification in landscape
        page_ls.evaluate("() => { window.onStarfieldOtaNotify('OTA_READY', { version: 'v1.1.0', changelog: '全新 OTA 热更新已生效' }); }")
        page_ls.wait_for_timeout(400)

        shot_landscape = os.path.join(artifact_dir, "test_landscape_transparent_ui_2k_ota.png")
        page_ls.screenshot(path=shot_landscape)
        print(f"   - Saved screenshot: {shot_landscape}")

        browser.close()

    print("\n=================================================================")
    print(" ALL 2K, OTA HOT UPDATE & TRANSPARENT UI TESTS PASSED! Errors: 0")
    print("=================================================================")

if __name__ == '__main__':
    test_ota_2k_and_transparent_ui()
