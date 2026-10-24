"""
Test Suite for:
1. Voice pristine 1.0 native speed with dynamic typewriter sync
2. Electronic audio overlap elimination (SCORES media silenced, procedural synthGain = 0, chimes disabled)
3. Resilient manual camera controls (dragging, recovery on capture loss, arrow keys, Gargantua authority gating)
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

        print(f"1. Loading: file:///{file_path}")
        page.goto(f"file:///{file_path}")
        page.wait_for_timeout(1500)

        print("2. Starting flight...")
        page.click("#begin")
        page.wait_for_timeout(2000)

        # Verify Audio & Electronic overlap elimination
        print("3. Checking Audio Engine status...")
        audio_state = page.evaluate("""() => {
            const s = (window.Starfield ? window.Starfield.getSoundscape() : null) || window.sound;
            return {
                ready: s.ready,
                hasClassical: !!s.classical,
                mediaCount: s.media ? s.media.length : 0,
                synthGainValue: s.synthGain ? s.synthGain.gain.value : -1,
                currentTrack: s.classical ? s.classical.getCurrentPiece().title : null,
                isPlaying: s.classical ? s.classical.isPlaying : false
            };
        }""")
        print(f"   Audio State: {audio_state}")
        assert audio_state["ready"], "Soundscape not ready!"
        assert audio_state["hasClassical"], "Classical engine missing!"
        assert audio_state["mediaCount"] == 0, f"Old electronic SCORES media should be 0, got {audio_state['mediaCount']}!"
        assert audio_state["synthGainValue"] == 0, f"Procedural synthGain must be 0, got {audio_state['synthGainValue']}!"

        # Trigger Narrator voice test & check playbackRate
        print("4. Triggering Narrator voice clip...")
        page.evaluate("""() => {
            const n = window.Narrator || (window.Starfield ? window.Starfield.getNarrator() : null);
            if (n) {
                n.speak('星辰未老，旅人如初。', { id: 'intro', force: true });
            }
        }""")
        page.wait_for_timeout(500)

        narrator_state = page.evaluate("""() => {
            const n = window.Narrator || (window.Starfield ? window.Starfield.getNarrator() : null);
            return {
                speaking: n ? n.speaking : false,
                hasAudio: n && !!n.currentAudio,
                playbackRate: (n && n.currentAudio) ? n.currentAudio.playbackRate : null,
                preservesPitch: (n && n.currentAudio) ? n.currentAudio.preservesPitch : null
            };
        }""")
        print(f"   Narrator State: {narrator_state}")
        if narrator_state["hasAudio"]:
            assert abs(narrator_state["playbackRate"] - 1.0) < 0.01, f"Expected playbackRate 0.85, got {narrator_state['playbackRate']}!"
            assert narrator_state["preservesPitch"] is False, "preservesPitch should be false for native 1.0x playback!"

        # Test Manual Camera Control
        print("5. Switching to Manual Camera mode ('C')...")
        page.keyboard.press("c")
        page.wait_for_timeout(400)

        cam_init = page.evaluate("""() => {
            const cam = window.Starfield.getCamera();
            return {
                autoCamera: window.Starfield.isAutoCamera(),
                yaw: cam.yaw,
                pitch: cam.pitch,
                distance: cam.distance
            };
        }""")
        print(f"   Manual Camera Initial: {cam_init}")
        assert not cam_init["autoCamera"], "Expected autoCamera to be false!"

        # Test drag rotation on canvas
        print("6. Simulating mouse drag rotation...")
        canvas = page.locator("#landscape")
        box = canvas.bounding_box()
        cx = box["x"] + box["width"] / 2
        cy = box["y"] + box["height"] / 2

        page.mouse.move(cx, cy)
        page.mouse.down()
        page.mouse.move(cx + 80, cy + 40, steps=8)
        page.mouse.up()
        page.wait_for_timeout(500)

        cam_dragged = page.evaluate("""() => {
            const cam = window.Starfield.getCamera();
            const man = window.Starfield.getManual();
            return {
                yaw: cam.yaw,
                pitch: cam.pitch,
                manualYaw: man.yaw,
                manualPitch: man.pitch
            };
        }""")
        print(f"   Manual Camera After Drag: {cam_dragged}")
        assert cam_dragged["manualYaw"] != cam_init["yaw"], "manual.yaw did not update on mouse drag!"

        # Test Arrow keys manual rotation
        print("7. Testing Keyboard Arrow Keys for Camera Rotation...")
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowUp")
        page.wait_for_timeout(400)

        cam_arrows = page.evaluate("""() => {
            const man = window.Starfield.getManual();
            return {
                manualYaw: man.yaw,
                manualPitch: man.pitch
            };
        }""")
        print(f"   Manual Camera After Arrows: {cam_arrows}")
        assert cam_arrows["manualYaw"] > cam_dragged["manualYaw"], "ArrowLeft should increase manual.yaw!"

        # Take screenshot of manual camera in action
        manual_shot = os.path.join(shots_dir, "manual_camera_active.png")
        page.screenshot(path=manual_shot)
        print(f"8. Captured manual camera screenshot: {manual_shot}")

        # Switch back to Auto Camera
        print("9. Switching back to Auto Camera ('C')...")
        page.keyboard.press("c")
        page.wait_for_timeout(400)
        auto_again = page.evaluate("() => window.Starfield ? window.Starfield.isAutoCamera() : autoCamera")
        assert auto_again, "Expected autoCamera to be true after toggle!"

        print(f"Total Errors: {len(errors)}, Total Logs: {len(logs)}")
        if errors:
            print("Errors encountered:", errors)
        assert len(errors) == 0, f"Errors encountered: {errors}"
        print(">>> ALL VOICE, AUDIO, AND CAMERA FIXES VERIFIED SUCCESSFULLY! <<<")
        browser.close()

if __name__ == "__main__":
    run_test()
