"""
Playwright Test Suite for Classical Music Integration in Starfield
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def run_test():
    file_path = os.path.abspath("d:/items/code/starfield-pub/starfield.html")
    shots_dir = os.path.abspath("d:/items/code/starfield-pub/shots")
    os.makedirs(shots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        errors = []
        logs = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: logs.append(f"[{msg.type}] {msg.text}"))

        print(f"1. Navigating to: file:///{file_path}")
        page.goto(f"file:///{file_path}")
        page.wait_for_timeout(1500)

        print("2. Starting flight...")
        page.click("#begin")
        page.wait_for_timeout(2500)

        # 3. Verify Sound and Classical Engine status
        status = page.evaluate("""() => {
            const s = (window.Starfield ? window.Starfield.getSoundscape() : null) || window.sound;
            return {
                soundReady: s ? s.ready : false,
                soundEnabled: typeof soundEnabled !== 'undefined' ? soundEnabled : false,
                hasClassical: s && !!s.classical,
                isPlaying: s && s.classical ? s.classical.isPlaying : false,
                currentTrack: s && s.classical ? s.classical.getCurrentPiece().title : null
            };
        }""")
        print(f"3. Audio status: {status}")
        assert status["hasClassical"], "ClassicalMusicEngine not mounted on sound!"

        # 4. Test 'N' key for next classical track
        print("4. Pressing 'N' to advance to next classical masterpiece...")
        page.keyboard.press("n")
        page.wait_for_timeout(1000)

        track1 = page.evaluate("() => ((window.Starfield ? window.Starfield.getSoundscape() : null) || window.sound).classical.getCurrentPiece().id")
        print(f"   Current track after pressing N: {track1}")
        assert track1 == "gymnopedie_1", f"Expected gymnopedie_1, got {track1}"

        # 5. Test Settings Drawer Jukebox UI
        print("5. Opening Settings Drawer (ESC) to inspect Classical Jukebox...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(800)

        jukebox_shot = os.path.join(shots_dir, "classical_jukebox_settings.png")
        page.screenshot(path=jukebox_shot)
        print(f"6. Saved Jukebox screenshot to: {jukebox_shot}")

        # 6. Click track 3 (Air on the G string)
        print("7. Clicking Bach - Air on the G String button...")
        btn_bach = page.locator(".track-select-btn[data-track='3']")
        assert btn_bach.is_visible(), "Bach track button not visible!"
        btn_bach.click()
        page.wait_for_timeout(800)

        track_bach = page.evaluate("() => ((window.Starfield ? window.Starfield.getSoundscape() : null) || window.sound).classical.getCurrentPiece().id")
        print(f"   Current track after button click: {track_bach}")
        assert track_bach == "air_on_g_string", f"Expected air_on_g_string, got {track_bach}"

        print(f"Total Errors: {len(errors)}, Total Logs: {len(logs)}")
        if errors:
            print("Errors encountered:", errors)
        assert len(errors) == 0, "Errors found during execution!"
        print(">>> ALL CLASSICAL MUSIC STARFIELD TESTS PASSED! <<<")
        browser.close()

if __name__ == "__main__":
    run_test()
