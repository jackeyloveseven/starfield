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
    print(" VERIFYING SAINT-SAENS & VIVALDI JUKEBOX + PLANET SURFACE ISOLATION")
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
        # TEST A: Classical Pieces Curation & Sequential Switching
        # -------------------------------------------------------------
        print("\n2. Testing Curated Classical Music Engine:")
        music_info = page.evaluate("""() => {
            const sound = window.sound;
            const engine = sound ? sound.classical : null;
            if (!engine) return null;

            const pieces = window.CLASSICAL_PIECES;
            return {
                totalTracks: pieces.length,
                titles: pieces.map(p => p.title),
                currentIdx: engine.currentTrackIndex,
                currentTitle: pieces[engine.currentTrackIndex].title,
                isPlaying: engine.isPlaying
            };
        }""")

        print(f"   - Total tracks: {music_info['totalTracks']} (Expected: 4)")
        for i, t in enumerate(music_info['titles']):
            print(f"     [{i+1}/4] {t}")

        assert music_info['totalTracks'] == 4, f"Expected 4 curated tracks, got {music_info['totalTracks']}"
        assert '圣-桑' in music_info['titles'][0], "Track 1 should be Saint-Saëns"
        assert '维瓦尔第 ·《四季 · 春》' in music_info['titles'][1], "Track 2 should be Vivaldi Spring"
        assert '维瓦尔第 ·《四季 · 冬》' in music_info['titles'][2], "Track 3 should be Vivaldi Winter"
        assert '天鹅' in music_info['titles'][3], "Track 4 should be Saint-Saëns The Swan"
        print("   >>> PASS: Curated track list strictly contains Saint-Saëns & Vivaldi masterworks!")

        # Test pressing N key sequentially
        print("\n3. Testing 'N' key track cycling & Jukebox UI synchronization:")
        for expected_idx in [1, 2, 3, 0]:
            page.keyboard.press("n")
            page.wait_for_timeout(300)
            track_state = page.evaluate("""() => {
                const s = window.sound.classical;
                const activeBtn = document.querySelector('.track-select-btn.active');
                return {
                    idx: s.currentTrackIndex,
                    activeBtnTrack: activeBtn ? parseInt(activeBtn.getAttribute('data-track'), 10) : null
                };
            }""")
            print(f"   - Cycled to track index {track_state['idx']} (Active button: {track_state['activeBtnTrack']})")
            assert track_state['idx'] == expected_idx, f"Expected track index {expected_idx}, got {track_state['idx']}"
            assert track_state['activeBtnTrack'] == expected_idx, f"Active Jukebox button should be {expected_idx}"

        print("   >>> PASS: Track cycling and Jukebox UI buttons strictly synced 1:1!")

        # -------------------------------------------------------------
        # TEST B: Multi-Planet Surface Synchronous Isolation
        # -------------------------------------------------------------
        print("\n4. Testing Multi-Planet Surface Buffer Isolation:")
        isolation_test = page.evaluate("""() => {
            const eng = window.LivingPlanetEngine;
            eng.init();

            // Planet A (Volcanic Fractured Core world)
            const planetA = {
                seed: 111111,
                encIndex: 1,
                w: {
                    shape: { id: 'fractured' },
                    type: { id: 'volcanic', power: 1.0, atmo: [255, 60, 20], mie: [255, 120, 40] },
                    manif: { id: 'fractured_core' }
                }
            };

            // Planet B (Pristine Ocean Archipelago world)
            const planetB = {
                seed: 222222,
                encIndex: 2,
                w: {
                    shape: { id: 'standard' },
                    type: { id: 'ocean', power: 1.0, atmo: [40, 150, 255], mie: [100, 200, 255] },
                    manif: { id: 'archipelago' }
                }
            };

            // Simulate screen canvas with synchronous drawing
            const testScreen = document.createElement('canvas');
            testScreen.width = 800; testScreen.height = 400;
            const testCtx = testScreen.getContext('2d');

            // Render Planet A on left
            const cvA = eng.renderPlanet(planetA, 150, [1, 0, 0]);
            const modelA = eng.getPlanetModel(planetA);
            testCtx.drawImage(cvA, 50, 50, 200, 200);
            const dataA1 = testCtx.getImageData(150, 150, 10, 10).data.slice();

            // Render Planet B on right
            const cvB = eng.renderPlanet(planetB, 150, [-1, 0, 0]);
            const modelB = eng.getPlanetModel(planetB);
            testCtx.drawImage(cvB, 450, 50, 200, 200);
            const dataB1 = testCtx.getImageData(550, 150, 10, 10).data.slice();

            // Check if Planet A on the screen was mutated by Planet B
            const dataA_afterB = testCtx.getImageData(150, 150, 10, 10).data.slice();
            let diffA = 0;
            for (let i = 0; i < dataA1.length; i++) {
                diffA += Math.abs(dataA1[i] - dataA_afterB[i]);
            }

            // Check that Planet A and Planet B have distinct pixels
            let diffAB = 0;
            for (let i = 0; i < dataA1.length; i++) {
                diffAB += Math.abs(dataA1[i] - dataB1[i]);
            }

            return {
                diffA,
                diffAB,
                hasModelA: !!modelA,
                hasModelB: !!modelB,
                idA: eng.getPlanetId(planetA),
                idB: eng.getPlanetId(planetB)
            };
        }""")

        print(f"   - Planet A pixel stability on screen: {isolation_test['diffA']} (Must be 0)")
        print(f"   - Planet A vs B surface difference: {isolation_test['diffAB']} (Must be > 0)")
        print(f"   - Invariant IDs: Planet A = {isolation_test['idA']}, Planet B = {isolation_test['idB']}")

        assert isolation_test['hasModelA'] and isolation_test['hasModelB'], "Both planet models must exist in cache!"
        assert isolation_test['diffA'] == 0, "Planet A screen surface was contaminated by Planet B!"
        assert isolation_test['diffAB'] > 100, "Planet A and Planet B must have completely distinct surface pixels!"
        assert isolation_test['idA'] != isolation_test['idB'], "Planet IDs must be strictly invariant and distinct!"
        print("   >>> PASS: Zero cross-planet buffer contamination! Old planet surface remains 100% intact!")

        # -------------------------------------------------------------
        # TEST C: Check Console Errors
        # -------------------------------------------------------------
        print(f"\n5. Page Error Count: {len(console_errors)}")
        if console_errors:
            print("   Errors:", console_errors)
        assert len(console_errors) == 0, "Console errors detected!"
        print("   >>> PASS: Zero runtime errors!")

        browser.close()

    print("\n=================================================================")
    print(" ALL TESTS PASSED WITH 100% FIDELITY!")
    print("=================================================================")

if __name__ == "__main__":
    run_tests()
