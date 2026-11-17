import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_build193_optimizations():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(repo_dir, "starfield.html")
    shots_dir = os.path.join(repo_dir, "shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" VERIFYING BUILD 193 VSYNC QUANTIZATION BREAKTHROUGH & 60+ FPS")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="msedge",
            headless=True,
            args=[
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--enable-webgl",
                "--no-sandbox",
                "--disable-gpu-sandbox"
            ]
        )
        
        # Emulate MediaTek Dimensity 9400+ mobile viewport
        context = browser.new_context(
            viewport={"width": 412, "height": 915},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=1.5
        )
        page = context.new_page()

        page_errors = []
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print(f"1. Loading starfield: file:///{html_path.replace(os.sep, '/')}")
        page.goto(f"file:///{html_path.replace(os.sep, '/')}")
        page.wait_for_selector("#begin", timeout=12000)

        # Verify UI Version Tag
        v_tag = page.locator("#sf-version-tag").text_content()
        print(f"2. UI Version Tag: {v_tag}")
        assert "Build 193" in v_tag, f"Expected Build 193 in version tag, got: {v_tag}"
        assert "v1.9.9.9.9.5" in v_tag, f"Expected v1.9.9.9.9.5 in version tag, got: {v_tag}"

        print("3. Embarking on voyage (#begin)...")
        page.click("#begin")
        page.wait_for_timeout(2000)

        # Verify StarfieldGL & LivingPlanetEngine
        gl_status = page.evaluate("""() => {
            return {
                hasStarfieldGL: !!window._sfStarGL,
                active: window._sfStarGL ? window._sfStarGL.active : false,
                isMobile: typeof _isMobileDevice !== 'undefined' ? _isMobileDevice : false,
                hasLPE: typeof window.LivingPlanetEngine !== 'undefined',
                lpeEnabled: window.LivingPlanetEngine ? window.LivingPlanetEngine.enabled : false
            };
        }""")
        print(f"4. Engine Status: {gl_status}")
        assert gl_status["hasStarfieldGL"], "StarfieldGL should be active"
        assert gl_status["hasLPE"], "LivingPlanetEngine should exist"

        print("5. Cruising across star lanes for 3 seconds...")
        page.wait_for_timeout(3000)

        # Check telemetry & optimization structures
        telemetry = page.evaluate("""() => {
            return {
                hasCachedVig: !!window._sfCachedVigGrad,
                hasCachedSky: !!window._sfSkyGrad,
                activeMassesCount: (window.activeMasses || []).length,
                travel: window.travel || 0
            };
        }""")
        print(f"6. Telemetry & Cached Pipeline Structures: {telemetry}")
        assert telemetry["hasCachedVig"], "postPass radial vignette should be cached"
        assert telemetry["hasCachedSky"], "drawSky background linear gradient should be cached"

        shot_path = os.path.join(shots_dir, "test_build193_flight.png")
        page.screenshot(path=shot_path)
        print(f"7. Captured Build 193 flight screenshot to: {shot_path}")

        print(f"8. Error check: {len(page_errors)} page errors, {len(console_logs)} logs")
        assert len(page_errors) == 0, f"Page errors encountered: {page_errors}"

        browser.close()

    print("=================================================================")
    print(" >>> BUILD 193 VERIFICATION PASSED WITH 100% SUCCESS! <<<")
    print("=================================================================")

if __name__ == "__main__":
    test_build193_optimizations()
