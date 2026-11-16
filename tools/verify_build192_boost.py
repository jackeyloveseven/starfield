import os
import sys
import time
from playwright.sync_api import sync_playwright

def test_build192_optimizations():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_path = os.path.join(repo_dir, "starfield.html")
    shots_dir = os.path.join(repo_dir, "shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" VERIFYING BUILD 192 CPU DE-BOTTLENECK & HARDWARE PIPELINE")
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
        
        # Emulate high-end mobile (MediaTek Dimensity 9400+ viewport: 1080x2400 DPR=2.5 or 412x915 mobile viewport)
        context = browser.new_context(
            viewport={"width": 412, "height": 915},
            device_scale_factor=2.5,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.102 Mobile Safari/537.36"
        )
        page = context.new_page()

        console_logs = []
        errors = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: errors.append(str(err)))

        print(f"1. Loading starfield: file:///{html_path.replace(os.sep, '/')}")
        page.goto(f"file:///{html_path.replace(os.sep, '/')}")
        page.wait_for_timeout(2000)

        # Check version tag in UI
        version_text = page.locator("#sf-version-tag").text_content()
        print(f"2. UI Version Tag: {version_text}")
        assert "Build 192" in version_text, f"Expected Build 192 in version tag, got: {version_text}"
        assert "1.9.9.9.9.4" in version_text, f"Expected 1.9.9.9.9.4 in version tag, got: {version_text}"

        # Start flight
        print("3. Embarking on voyage (#begin)...")
        page.click("#begin")
        page.wait_for_timeout(2000)

        # Verify StarfieldGL is active
        gl_status = page.evaluate("""() => {
            const gl = window._sfStarGL || (typeof starfieldGL !== 'undefined' ? starfieldGL : null);
            return {
                hasStarfieldGL: gl !== null,
                active: gl ? gl.active : false,
                isMobile: typeof _isMobileDevice !== 'undefined' ? _isMobileDevice : false
            };
        }""")
        print(f"4. StarfieldGL Status: {gl_status}")
        print(f"   Console logs so far: {console_logs}")
        assert gl_status["hasStarfieldGL"], "starfieldGL not initialized!"
        assert gl_status["isMobile"], "_isMobileDevice not detected for mobile UA!"

        # Engage hyperwarp to cross chunks quickly and encounter multiple planetary systems
        print("5. Cruising across star lanes...")
        page.evaluate("""() => {
            if (typeof WarpDrive !== 'undefined') {
                WarpDrive.gearIndex = 2; // Hyperwarp 15c
                WarpDrive.updateUI();
            }
        }""")
        page.wait_for_timeout(3500)

        # Check telemetry and caches
        telemetry = page.evaluate("""() => {
            return {
                hasFlareCache: typeof _sfFlareCache !== 'undefined',
                flareCacheSize: typeof _sfFlareCache !== 'undefined' ? _sfFlareCache.size : 0,
                hasStarBloomWarm: typeof _starBloomWarm !== 'undefined' && _starBloomWarm !== null,
                hasStarBloomCool: typeof _starBloomCool !== 'undefined' && _starBloomCool !== null,
                activeMassesCount: typeof activeMasses !== 'undefined' ? activeMasses.length : 0,
                travel: typeof Starfield !== 'undefined' ? Starfield.getTravel() : 0
            };
        }""")
        print(f"6. Telemetry & Pre-baked Caches: {telemetry}")
        assert telemetry["hasStarBloomWarm"], "_starBloomWarm not initialized!"
        assert telemetry["hasStarBloomCool"], "_starBloomCool not initialized!"

        # Measure 60 frames timing
        print("7. Benchmarking 60 frames render loop...")
        perf_data = page.evaluate("""() => new Promise(resolve => {
            const frameTimes = [];
            let last = performance.now();
            let count = 0;
            function onFrame(now) {
                frameTimes.push(now - last);
                last = now;
                count++;
                if (count >= 60) {
                    const avg = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
                    const max = Math.max(...frameTimes);
                    const min = Math.min(...frameTimes);
                    resolve({ avg, max, min, fps: 1000 / avg });
                } else {
                    requestAnimationFrame(onFrame);
                }
            }
            requestAnimationFrame(onFrame);
        })""")
        print(f"   Benchmark Results: Avg Frame Time: {perf_data['avg']:.2f}ms (~{perf_data['fps']:.1f} FPS), Min: {perf_data['min']:.2f}ms, Max: {perf_data['max']:.2f}ms")

        # Capture in-flight screenshot
        shot_path = os.path.join(shots_dir, "test_build192_flight.png")
        page.screenshot(path=shot_path)
        print(f"8. Captured flight screenshot to: {shot_path}")

        # Verify zero console page errors
        print(f"9. Error check: {len(errors)} page errors, {len(console_logs)} logs")
        assert len(errors) == 0, f"Encountered page errors: {errors}"

        print("=================================================================")
        print(" >>> BUILD 192 VERIFICATION PASSED WITH 100% SUCCESS! <<<")
        print("=================================================================")

        browser.close()

if __name__ == "__main__":
    test_build192_optimizations()
