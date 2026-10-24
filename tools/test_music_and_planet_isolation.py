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
        # TEST B: Multi-Planet Surface Physical Buffer Isolation
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

            // Render Planet A
            const canvasA1 = eng.renderPlanet(planetA, 150, [1, -0.5, 0.5]);
            const modelA = eng.getPlanetModel(planetA);
            // Snapshot a sampling of pixels from canvas A
            const ctxA = canvasA1.getContext('2d');
            const dataA1 = ctxA.getImageData(256, 256, 20, 20).data.slice();

            // Render Planet B (new planet appearing)
            const canvasB1 = eng.renderPlanet(planetB, 200, [0.5, -1, 0.2]);
            const modelB = eng.getPlanetModel(planetB);
            const ctxB = canvasB1.getContext('2d');
            const dataB1 = ctxB.getImageData(256, 256, 20, 20).data.slice();

            // Now re-inspect Planet A's dedicated canvas without re-rendering:
            const dataA_afterB = ctxA.getImageData(256, 256, 20, 20).data.slice();

            // Check if canvas instances are completely separate objects:
            const isCanvasSeparate = (canvasA1 !== canvasB1);
            
            // Check pixel consistency: dataA_afterB must match dataA1 perfectly!
            let diffA = 0;
            for (let i = 0; i < dataA1.length; i++) {
                diffA += Math.abs(dataA1[i] - dataA_afterB[i]);
            }

            return {
                isCanvasSeparate,
                diffA,
                hasModelA: !!modelA,
                hasModelB: !!modelB,
                idA: eng.getPlanetId(planetA),
                idB: eng.getPlanetId(planetB)
            };
        }""")

        print(f"   - Dedicated Canvas physically separate: {isolation_test['isCanvasSeparate']}")
        print(f"   - Planet A pixel drift after Planet B render: {isolation_test['diffA']} (Must be 0)")
        print(f"   - Invariant IDs: Planet A = {isolation_test['idA']}, Planet B = {isolation_test['idB']}")

        assert isolation_test['isCanvasSeparate'] is True, "Each planet must have its own dedicated canvas!"
        assert isolation_test['diffA'] == 0, "Planet A surface was contaminated by Planet B!"
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
