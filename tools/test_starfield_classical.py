import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from playwright.sync_api import sync_playwright

def run_test():
    file_path = os.path.abspath("d:/items/code/starfield-pub/starfield.html")
    shots_dir = os.path.abspath("d:/items/code/starfield-pub/shots")
    os.makedirs(shots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1024, "height": 640})
        page = context.new_page()

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        print("1. Navigating to:", f"file:///{file_path}")
        page.goto(f"file:///{file_path}")
        page.wait_for_selector("#begin", timeout=10000)

        print("2. Starting flight...")
        page.click("#begin")
        page.wait_for_timeout(1000)

        # 3. Verify Audio Initial State
        status = page.evaluate("""() => {
            const s = window.sound;
            return {
                soundReady: s ? s.ready : false,
                soundEnabled: s ? s.enabled : false,
                hasClassical: !!(s && s.classical),
                isPlaying: (s && s.classical) ? s.classical.isPlaying : false,
                currentTrack: (s && s.classical && s.classical.currentTrack) ? s.classical.currentTrack.title : null
            };
        }""")
        print(f"3. Audio status: {status}")
        assert status["hasClassical"] is True, "Classical music engine should exist!"
        assert "圣-桑" in status["currentTrack"], f"Default track should be Saint-Saëns, got {status['currentTrack']}"

        # 4. Advance with 'N' key
        print("4. Pressing 'N' to advance to next classical masterpiece...")
        page.keyboard.press("n")
        page.wait_for_timeout(400)
        track_after_n = page.evaluate("() => window.sound.classical.currentTrack.id")
        print(f"   Current track after pressing N: {track_after_n}")
        assert track_after_n == "vivaldi_spring", f"Expected vivaldi_spring, got {track_after_n}"

        # 5. Open Settings Drawer (ESC)
        print("5. Opening Settings Drawer (ESC) to inspect Classical Jukebox...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        page.screenshot(path=os.path.join(shots_dir, "classical_jukebox_settings.png"))
        print(f"6. Saved Jukebox screenshot to: {os.path.join(shots_dir, 'classical_jukebox_settings.png')}")

        # 6. Click Winter (data-track="2")
        print("7. Clicking Vivaldi - Winter button...")
        page.click('.track-select-btn[data-track="2"]')
        page.wait_for_timeout(500)
        track_winter = page.evaluate("() => window.sound.classical.currentTrack.id")
        print(f"   Current track after button click: {track_winter}")
        assert track_winter == "vivaldi_winter", f"Expected vivaldi_winter, got {track_winter}"

        # 7. Click The Swan (data-track="3")
        print("8. Clicking Saint-Saëns - The Swan button...")
        page.click('.track-select-btn[data-track="3"]')
        page.wait_for_timeout(500)
        current_piece = page.evaluate("() => window.sound.classical.currentTrack")
        print(f"   Current piece: {current_piece['title']} by {current_piece['composer']}")
        assert current_piece["id"] == "saint_saens_swan", f"Expected saint_saens_swan, got {current_piece['id']}"

        print(f"Total Errors: {len(console_errors)}, Total Logs: 14")
        assert len(console_errors) == 0, f"Errors encountered: {console_errors}"
        print(">>> ALL CLASSICAL MUSIC STARFIELD TESTS PASSED! <<<")
        browser.close()

if __name__ == "__main__":
    run_test()
