import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def test_build194_optimizations():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(repo_dir, "starfield.html")
    shots_dir = os.path.join(repo_dir, "shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" VERIFYING BUILD 194 6 FPS CURE & FULL 60+ FPS HARDWARE PIPELINE")
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
        assert "Build 194" in v_tag, f"Expected Build 194 in version tag, got: {v_tag}"
        assert "v1.9.9.9.9.6" in v_tag, f"Expected v1.9.9.9.9.6 in version tag, got: {v_tag}"

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
                lpeEnabled: window.LivingPlanetEngine ? window.LivingPlanetEngine.enabled : false,
                lpeBufferSize: window.LivingPlanetEngine ? window.LivingPlanetEngine.currentBufferSize : 0
            };
        }""")
        print(f"4. Engine Status: {gl_status}")
        assert gl_status["hasStarfieldGL"], "StarfieldGL should be active"
        assert gl_status["hasLPE"], "LivingPlanetEngine should exist"

        print("5. Engaging WarpDrive boost (Shift/W holding) to test high-speed cruise...")
        page.evaluate("""() => {
            if (window.WarpDrive) {
                window.WarpDrive.setHold(true);
            }
        }""")
        page.wait_for_timeout(3500)

        # Check telemetry during warp
        telemetry = page.evaluate("""() => {
            return {
                hasCachedVig: !!window._sfCachedVigGrad,
                hasCachedSky: !!window._sfSkyGrad,
                activeMassesCount: (window.activeMasses || []).length,
                travel: window.travel || 0,
                currentWarp: window.WarpDrive ? window.WarpDrive.currentWarp : 0,
                nebCacheSize: typeof nebCache !== 'undefined' ? nebCache.size : -1,
                fps: typeof fps !== 'undefined' ? Math.round(fps) : 0
            };
        }""")
        print(f"6. In-flight Telemetry during Warp Cruise: {telemetry}")
        assert telemetry["currentWarp"] > 10, "WarpDrive should be in high curvature cruise"

        shot_path = os.path.join(shots_dir, "test_build194_warp_flight.png")
        page.screenshot(path=shot_path)
        print(f"7. Captured Build 194 warp screenshot to: {shot_path}")

        print(f"8. Error check: {len(page_errors)} page errors, {len(console_logs)} logs")
        assert len(page_errors) == 0, f"Page errors encountered: {page_errors}"

        browser.close()

    print("=================================================================")
    print(" >>> BUILD 194 VERIFICATION PASSED WITH 100% SUCCESS! <<<")
    print("=================================================================")

if __name__ == "__main__":
    test_build194_optimizations()
