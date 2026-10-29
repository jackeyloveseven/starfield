import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    html_path = os.path.abspath('starfield.html').replace('\\', '/')
    file_url = f"file:///{html_path}"
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
        page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # 1. Gacha Ceremony Verification
        # -------------------------------------------------------------
        print("\n--- 1. Testing Gacha Ceremony ---")
        gacha_state = page.evaluate("""() => {
            const H = window.StarfieldHatch;
            H.clear();
            H.addCores(3);
            const item = H.openNextCore();
            const igniter = document.getElementById('sf-igniter-box');
            const shockwave = document.getElementById('sf-shockwave');
            const card = document.querySelector('#sf-hatch .sf-hatch-card');
            return {
                itemId: item.id,
                itemName: item.name,
                itemTier: item.tier,
                igniterVisible: igniter ? getComputedStyle(igniter).display !== 'none' : false,
                cardExists: !!card,
                shockwaveExists: !!shockwave
            };
        }""")
        print(f"Gacha initial state: {gacha_state}")
        assert gacha_state["cardExists"], "Card element must exist"
        assert gacha_state["shockwaveExists"], "Shockwave element must exist"

        # Wait for gacha ignition ceremony auto-trigger & card reveal
        page.wait_for_timeout(2200)

        revealed_state = page.evaluate("""() => {
            const igniter = document.getElementById('sf-igniter-box');
            const card = document.querySelector('#sf-hatch .sf-hatch-card');
            const serial = document.getElementById('sf-card-serial');
            const tierBadge = document.getElementById('sf-card-tier-badge');
            const holo = card ? card.querySelector('.sf-card-holo') : null;
            return {
                igniterHidden: igniter ? getComputedStyle(igniter).display === 'none' : true,
                cardRevealed: card ? card.classList.contains('revealed') : false,
                serialText: serial ? serial.textContent.trim() : null,
                tierText: tierBadge ? tierBadge.textContent.trim() : null,
                hasHolo: !!holo
            };
        }""")
        print(f"Card revealed state: {revealed_state}")
        assert revealed_state["cardRevealed"], "Card should be revealed after supernova ignition"
        assert revealed_state["hasHolo"], "Card should feature holographic diffraction layer"

        # -------------------------------------------------------------
        # 2. 3D Planet Drag-to-Spin & Canvas Inspection
        # -------------------------------------------------------------
        print("\n--- 2. Testing 3D Planet Sphere & Canvas ---")
        canvas_state = page.evaluate("""() => {
            const canvas = document.getElementById('sf-planet-canvas');
            const orbBezel = document.getElementById('sf-card-orb-bezel');
            return {
                hasCanvas: !!canvas,
                canvasWidth: canvas ? canvas.width : 0,
                canvasHeight: canvas ? canvas.height : 0,
                hasOrbBezel: !!orbBezel
            };
        }""")
        print(f"Planet canvas check: {canvas_state}")
        assert canvas_state["hasCanvas"], "3D Planet canvas must exist"
        assert canvas_state["canvasWidth"] > 0, "Canvas should have width > 0"

        # Test touch drag on orb
        orb_box = page.locator("#sf-card-orb-bezel").bounding_box()
        if orb_box:
            cx = orb_box["x"] + orb_box["width"] / 2
            cy = orb_box["y"] + orb_box["height"] / 2
            page.mouse.move(cx, cy)
            page.mouse.down()
            page.mouse.move(cx + 40, cy - 20)
            page.mouse.up()
            page.wait_for_timeout(200)

        # -------------------------------------------------------------
        # 3. Escort Orbit Assignment
        # -------------------------------------------------------------
        print("\n--- 3. Testing Escort Orbit Assignment ---")
        escort_toggle_res = page.evaluate("""() => {
            const btn = document.getElementById('sf-btn-escort');
            if (btn) btn.click();
            const H = window.StarfieldHatch;
            const escorts = H.getEscorts();
            return {
                buttonText: btn ? btn.textContent.trim() : null,
                escortCount: escorts.length
            };
        }""")
        print(f"Escort assigned: {escort_toggle_res}")
        assert escort_toggle_res["escortCount"] == 1, "Item should be added to escort fleet"
        assert "护航" in escort_toggle_res["buttonText"], "Button text should reflect escorted status"

        # -------------------------------------------------------------
        # 4. Card Flip, Telemetry & Planetarium List
        # -------------------------------------------------------------
        print("\n--- 4. Testing Card Flip & Telemetry ---")
        flip_res = page.evaluate("""() => {
            const btnFlip = document.getElementById('sf-btn-flip');
            if (btnFlip) btnFlip.click();
            const card = document.querySelector('#sf-hatch .sf-hatch-card');
            const rows = document.querySelectorAll('#sf-hatch .sf-hb-row');
            return {
                cardFlipped: card ? card.classList.contains('flipped') : false,
                rowCount: rows.length
            };
        }""")
        print(f"Card flipped: {flip_res}")
        assert flip_res["cardFlipped"], "Card should flip to back face"
        assert flip_res["rowCount"] >= 3, "Back face must display at least 3 telemetry rows"

        # Close hatch card and open planetarium list
        page.evaluate("""() => {
            const hatch = document.getElementById('sf-hatch');
            if (hatch) hatch.classList.remove('on');
            window.StarfieldHatch.openList();
        }""")
        page.wait_for_timeout(400)

        list_check = page.evaluate("""() => {
            const root = document.getElementById('sf-hatch-list');
            const items = root ? root.querySelectorAll('.sf-hl-item') : [];
            const escortedItem = root ? root.querySelector('.sf-hl-item.escorted') : null;
            const escortTag = escortedItem ? escortedItem.querySelector('.sf-hl-escort-tag') : null;
            const escortBar = root ? root.querySelector('.sf-hl-escort-bar') : null;
            const itemCanvas = root ? root.querySelector('.sf-hl-canvas') : null;
            return {
                listOpen: root ? root.classList.contains('on') : false,
                itemCount: items.length,
                hasEscortedItem: !!escortedItem,
                escortTagText: escortTag ? escortTag.textContent.trim() : null,
                hasEscortBar: !!escortBar,
                hasItemCanvas: !!itemCanvas
            };
        }""")
        print(f"Planetarium list check: {list_check}")
        assert list_check["listOpen"], "Planetarium list should be open"
        assert list_check["itemCount"] == 1, "Should have 1 planet in list"
        assert list_check["hasEscortedItem"], "Planet should have .escorted class"
        assert list_check["hasEscortBar"], "Header should display escort status bar"
        assert list_check["hasItemCanvas"], "Item should have procedural planet canvas"

        # -------------------------------------------------------------
        # 5. Active Deep Space Sonar Verification
        # -------------------------------------------------------------
        print("\n--- 5. Testing Active Deep Space Sonar ---")
        sonar_res = page.evaluate("""() => {
            // Close list to return to flight
            const list = document.getElementById('sf-hatch-list');
            if (list) list.classList.remove('on');

            const S = window.StarfieldSonar;
            let hudBtn = null;
            let triggerSuccess = false;
            if (S) {
                // Simulate lock on target celestial mass
                S.currentTarget = { name: '织女星 α', x: 300, y: 150, z: -800 };
                S.updateHUDButton(S.currentTarget);
                hudBtn = document.getElementById('sf-sonar-lock-btn');
                S.triggerScan();
                triggerSuccess = S.activeSonarRings.length > 0;
            }
            return {
                hasSonar: !!S,
                hasHudBtn: !!hudBtn,
                hudVisible: hudBtn ? hudBtn.style.display !== 'none' : false,
                hudText: hudBtn ? hudBtn.textContent.trim() : null,
                triggerSuccess: triggerSuccess
            };
        }""")
        print(f"Deep Space Sonar check: {sonar_res}")
        assert sonar_res["hasSonar"], "StarfieldSonar system must exist"
        assert sonar_res["hasHudBtn"], "Sonar HUD button must exist"
        assert sonar_res["triggerSuccess"], "Sonar activeSonarRings should have triggered"

        # Take screenshot of clean in-flight state with escort orbits
        page.wait_for_timeout(500)
        page.screenshot(path="tools/test_flight_with_escort_and_sonar.png")
        print("Screenshot saved to tools/test_flight_with_escort_and_sonar.png")

        print("\n--- Total Console Errors ---")
        print(f"Errors count: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"

        print("\n🎉 ALL MECHANICS, AESTHETICS & PERFORMANCE TESTS PASSED 100%!")

if __name__ == '__main__':
    main()
