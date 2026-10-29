import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    html_path = os.path.abspath('tools/test_card_art_and_shader.html')
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
        page.wait_for_timeout(600)

        # Screenshot Phase 1: Singularity Igniter
        shot1 = "tools/test_phase1_singularity.png"
        page.screenshot(path=shot1)
        print(f"Phase 1 Singularity screenshot: {shot1}")

        # Trigger Ignition / Click Singularity
        page.click("#sf-igniter-box")
        page.wait_for_timeout(300)

        # Screenshot Phase 2: Shockwave / Supernova Explosion
        shot2 = "tools/test_phase2_shockwave.png"
        page.screenshot(path=shot2)
        print(f"Phase 2 Shockwave screenshot: {shot2}")

        # Wait for 3D Card to materialize
        page.wait_for_timeout(800)
        shot3 = "tools/test_phase3_card_front.png"
        page.screenshot(path=shot3)
        print(f"Phase 3 3D Card Front screenshot: {shot3}")

        # Test Drag-To-Rotate Planet
        bezel = page.locator("#sf-card-orb-bezel")
        box = bezel.bounding_box()
        if box:
            start_x = box["x"] + box["width"] * 0.5
            start_y = box["y"] + box["height"] * 0.5
            page.mouse.move(start_x, start_y)
            page.mouse.down()
            page.mouse.move(start_x + 60, start_y - 20)
            page.mouse.up()
            page.wait_for_timeout(200)

        # Test Flip to Back Face
        page.click("#sf-btn-flip")
        page.wait_for_timeout(500)
        shot4 = "tools/test_phase4_card_back.png"
        page.screenshot(path=shot4)
        print(f"Phase 4 Card Back Face screenshot: {shot4}")

        # Test Flip back & Escort toggle
        page.click("#sf-btn-flip-back")
        page.wait_for_timeout(500)
        page.click("#sf-btn-escort")
        escort_text = page.locator("#sf-btn-escort").text_content()
        print(f"Escort button text after click: {escort_text}")
        assert "随行护航" in escort_text, f"Expected escort text, got {escort_text}"

        print("Total console errors:", len(console_errors))
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Expected 0 errors, got {len(console_errors)}"
        print("ALL PROTOTYPE CEREMONY & CARD ART TESTS PASSED!")

if __name__ == '__main__':
    main()
