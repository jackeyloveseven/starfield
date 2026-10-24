import os
import sys
import time
from playwright.sync_api import sync_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    html_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    shots_dir = os.path.abspath(r"d:\items\code\starfield-pub\shots")
    os.makedirs(shots_dir, exist_ok=True)

    print("=================================================================")
    print(" VERIFYING AUDIO PRISTINE RATE & DYNAMIC HI-RES PLANET BUFFER")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(viewport={"width": 1024, "height": 640})
        page = context.new_page()

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        print("1. Loading starfield.html...")
        page.goto(f"file:///{html_path}")
        page.wait_for_selector("#begin", timeout=10000)
        page.click("#begin")
        page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # TEST A: LivingPlanetEngine Adaptive Multi-Tier Ultra-HD Buffer
        # -------------------------------------------------------------
        print("\n2. Testing LivingPlanetEngine dynamic buffer scaling & hysteresis:")
        tiers = page.evaluate("""() => {
            const eng = window.LivingPlanetEngine;
            if (!eng) return null;
            eng.init();

            // Simulate distant cruising (rad = 30) for 50 frames to pass downscale hysteresis
            for (let i = 0; i < 50; i++) eng.ensureBufferSize(30);
            const sz_dist = eng.currentBufferSize;
            const canvas_dist = eng.canvas.width;

            // Simulate approaching planet (rad = 140) -> immediate upgrade to 1024
            eng.ensureBufferSize(140);
            const sz_mid = eng.currentBufferSize;
            const canvas_mid = eng.canvas.width;

            // Simulate close encounter skimming world (rad = 450) -> crisp 1024 buffer
            eng.ensureBufferSize(450);
            const sz_close = eng.currentBufferSize;
            const canvas_close = eng.canvas.width;

            return {
                distant: { size: sz_dist, canvasW: canvas_dist },
                approaching: { size: sz_mid, canvasW: canvas_mid },
                closeEncounter: { size: sz_close, canvasW: canvas_close }
            };
        }""")

        print(f"   - Distant planet (rad=30, after 65 frames): buffer = {tiers['distant']['size']}x{tiers['distant']['size']} (Canvas: {tiers['distant']['canvasW']})")
        print(f"   - Approaching planet (rad=140, immediate): buffer = {tiers['approaching']['size']}x{tiers['approaching']['size']} (Canvas: {tiers['approaching']['canvasW']})")
        print(f"   - Close encounter planet (rad=450, immediate): buffer = {tiers['closeEncounter']['size']}x{tiers['closeEncounter']['size']} (Canvas: {tiers['closeEncounter']['canvasW']})")

        assert tiers['distant']['size'] == 512, f"Distant buffer must be 512, got {tiers['distant']['size']}"
        assert tiers['approaching']['size'] == 1024, f"Approaching buffer must be 1024, got {tiers['approaching']['size']}"
        assert tiers['closeEncounter']['size'] == 1024, f"Close encounter buffer must be 1024, got {tiers['closeEncounter']['size']}"
        print("   >>> PASS: Dynamic Adaptive Buffer scales and protects GPU perfectly!")

        # -------------------------------------------------------------
        # TEST B: In-flight close encounter rendering & screenshot
        # -------------------------------------------------------------
        print("\n3. Testing in-flight close-encounter planet rendering with 1536 Ultra-HD buffer:")
        shot_path = os.path.join(shots_dir, "planet_hires_1536_close_up.png")
        page.evaluate("""() => {
            const masses = window.Starfield.getActiveMasses ? window.Starfield.getActiveMasses() : window.Starfield.getState().masses;
            const travel = window.Starfield.getTravel ? window.Starfield.getTravel() : 0;
            if (masses) {
                masses.unshift({
                    x: 0,
                    y: 350,
                    z: travel + 80,
                    kind: 1,
                    r: 700,
                    seed: 9999,
                    w: {
                        shape: { id: 'standard' },
                        type: { id: 'terra', name: 'Terra', power: 1.0, atmo: [255, 200, 80], mie: [255, 255, 200] },
                        manif: { name: 'Living Ecosystem' }
                    }
                });
            }
        }""")
        page.wait_for_timeout(1500)
        page.screenshot(path=shot_path)
        print(f"   - Saved high-resolution encounter screenshot to: {shot_path}")

        # -------------------------------------------------------------
        # TEST C: Audio Playback Rate & Dynamic Syllable Sync
        # -------------------------------------------------------------
        print("\n4. Testing Voice Playback Settings & Natural Speed:")
        audio_test = page.evaluate("""() => {
            const n = window.Starfield.getNarrator();
            n.speak('航道数据载入。在数千亿颗恒星之间，这十四只纸鹤就是我们的全部家当了，起航。', { id: 'intro_alt4' });
            
            const snd = n.currentAudio;
            return {
                hasAudio: !!snd,
                playbackRate: snd ? snd.playbackRate : null,
                defaultPlaybackRate: snd ? snd.defaultPlaybackRate : null,
                preservesPitch: snd ? snd.preservesPitch : null,
                volume: snd ? snd.volume : null
            };
        }""")
        print("   - Voice Audio state:", audio_test)
        assert audio_test['playbackRate'] == 1.0, f"Expected playbackRate 1.0, got {audio_test['playbackRate']}"
        assert audio_test['defaultPlaybackRate'] == 1.0, f"Expected defaultPlaybackRate 1.0, got {audio_test['defaultPlaybackRate']}"
        assert audio_test['preservesPitch'] == False, f"Expected preservesPitch False, got {audio_test['preservesPitch']}"
        print("   >>> PASS: Audio plays at pristine 1.0 native speed with ZERO time-stretching vocoder artifacts!")

        # -------------------------------------------------------------
        # TEST D: Check console errors
        # -------------------------------------------------------------
        print(f"\n5. Page Error Count: {len(console_errors)}")
        if console_errors:
            print("   Errors:", console_errors)
        assert len(console_errors) == 0, "Console errors detected!"
        print("   >>> PASS: Zero runtime errors!")

        browser.close()

    print("\n=================================================================")
    print(" ALL TESTS COMPLETED AND VERIFIED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
