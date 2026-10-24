import os
import sys
import time

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from playwright.sync_api import sync_playwright

def test_planet_studio():
    html_path = os.path.abspath(r"d:\items\code\starfield-pub\planet_studio.html")
    shots_dir = os.path.abspath(r"d:\items\code\starfield-pub\shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" STARFIELD THREE.JS LIVING PLANET STUDIO AUTOMATED TEST SUITE")
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

        # Check canvas
        canvas = page.locator("#webgl-canvas")
        assert canvas.is_visible(), "Canvas not visible!"
        print("2. WebGL Canvas verified and active.")

        # Test Archipelago Preset
        print("3. Testing Archipelago Preset (🏝️ 蔚蓝群岛)...")
        archipelago_shot = os.path.join(shots_dir, "planet_archipelago_islands.png")
        page.screenshot(path=archipelago_shot)
        print(f"   Saved Archipelago screenshot: {archipelago_shot}")

        # Test Abyssal Ocean Preset
        print("4. Testing Abyssal Deep Ocean Preset (🌊 深渊之海)...")
        page.click(".preset-card[data-preset='abyss']")
        page.wait_for_timeout(1500)
        abyss_shot = os.path.join(shots_dir, "planet_abyss_ocean_whales.png")
        page.screenshot(path=abyss_shot)
        print(f"   Saved Abyssal Ocean screenshot: {abyss_shot}")

        # Test Gaia Forest Preset
        print("5. Testing Gaia Evergreen Forest Preset (🌲 盖亚林海)...")
        page.click(".preset-card[data-preset='forest']")
        page.wait_for_timeout(1500)
        forest_shot = os.path.join(shots_dir, "planet_forest_gaia.png")
        page.screenshot(path=forest_shot)
        print(f"   Saved Forest screenshot: {forest_shot}")

        # Test Ancient Monument Preset
        print("6. Testing Ancient Monument World Preset (🏛️ 古神遗迹)...")
        page.click(".preset-card[data-preset='monument']")
        page.wait_for_timeout(1500)
        monument_shot = os.path.join(shots_dir, "planet_monument_ruins.png")
        page.screenshot(path=monument_shot)
        print(f"   Saved Ancient Monument screenshot: {monument_shot}")

        # Test Alien Crystal Preset
        print("7. Testing Alien Psionic Crystal Preset (🌌 幽能水晶)...")
        page.click(".preset-card[data-preset='alien']")
        page.wait_for_timeout(1500)
        alien_shot = os.path.join(shots_dir, "planet_alien_psionic.png")
        page.screenshot(path=alien_shot)
        print(f"   Saved Alien Crystal screenshot: {alien_shot}")

        # Test Reroll Seed button
        print("8. Testing Seed Shuffle button...")
        page.click("#btn-shuffle-seed")
        page.wait_for_timeout(1500)
        assert page.locator("#toast").is_visible(), "Toast not shown on shuffle!"
        print("   Seed shuffled successfully.")

        # Let the simulation run for a few seconds to measure stability
        print("9. Running real-time fauna & orbit simulation for 3 seconds...")
        page.wait_for_timeout(3000)

        browser.close()

        print("\n=================================================================")
        print(f"TEST SUMMARY: Page Errors: {len(errors)}, Console Logs: {len(console_logs)}")
        if errors:
            print(f"ERRORS ENCOUNTERED:\n" + "\n".join(errors))
            sys.exit(1)
        else:
            print(">>> ALL THREE.JS PLANET GENERATOR TESTS PASSED WITH 0 ERRORS! <<<")
        print("=================================================================")

if __name__ == "__main__":
    test_planet_studio()
