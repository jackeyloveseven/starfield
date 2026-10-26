import sys
import os
import time
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

def main():
    html_path = os.path.abspath('starfield.html')
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
        page.wait_for_timeout(1000)

        # 1. Verify default unopened cores = 3
        cores = page.evaluate("() => window.StarfieldHatch.getUnopenedCores()")
        print(f"Initial unopened cores: {cores}")
        assert cores == 3, f"Expected 3 unopened cores, got {cores}"

        # 2. Check mobile touch HUD planet button and badges
        hud_info = page.evaluate("""() => {
            const btnMore = document.querySelector('.sf-touch-cluster .sf-touch-primary-row .sf-touch-btn:last-child');
            const moreTray = document.getElementById('sf-touch-more-tray');
            const btnPlanet = moreTray ? moreTray.querySelector('button') : null;
            const pBadge = btnPlanet ? btnPlanet.querySelector('.sf-touch-core-badge') : null;
            const mDot = btnMore ? btnMore.querySelector('.sf-more-core-dot') : null;
            return {
                hasMoreTray: !!moreTray,
                hasBtnPlanet: !!btnPlanet,
                badgeText: pBadge ? pBadge.textContent.trim() : null,
                hasMoreDot: !!mDot
            };
        }""")
        print(f"Mobile HUD check: {hud_info}")
        assert hud_info["hasBtnPlanet"], "btnPlanet must exist in moreTray"
        assert hud_info["badgeText"] == "3", f"Expected planet badge '3', got {hud_info['badgeText']}"
        assert hud_info["hasMoreDot"], "btnMore must have glowing core dot"

        # 3. Test opening Planetarium list
        page.evaluate("() => window.StarfieldHatch.openList()")
        page.wait_for_timeout(500)
        list_info = page.evaluate("""() => {
            const root = document.getElementById('sf-hatch-list');
            const openBtn = root ? root.querySelector('#sf-hl-btn-open-core') : null;
            const giftBtn = root ? root.querySelector('#sf-hl-btn-add-core') : null;
            const emptyBox = root ? root.querySelector('.sf-hl-empty-box') : null;
            return {
                isOpen: root ? root.classList.contains('on') : false,
                hasOpenBtn: !!openBtn,
                openBtnText: openBtn ? openBtn.textContent.trim() : null,
                hasGiftBtn: !!giftBtn,
                hasEmptyBox: !!emptyBox
            };
        }""")
        print(f"Planetarium list info: {list_info}")
        assert list_info["isOpen"], "Planetarium list must be open"
        assert list_info["hasOpenBtn"], "Open core button must exist"
        assert "3" in list_info["openBtnText"], f"Expected '3' in button text, got {list_info['openBtnText']}"

        # 4. Open 1 core and verify planet hatching
        hatch_res = page.evaluate("""() => {
            const item = window.StarfieldHatch.openNextCore();
            const coresLeft = window.StarfieldHatch.getUnopenedCores();
            const hatchOverlay = document.getElementById('sf-hatch');
            const nameEl = hatchOverlay ? hatchOverlay.querySelector('.sf-hatch-name') : null;
            return {
                itemId: item.id,
                itemName: item.name,
                coresLeft: coresLeft,
                overlayOpen: hatchOverlay ? hatchOverlay.classList.contains('on') : false,
                renderedName: nameEl ? nameEl.textContent.trim() : null
            };
        }""")
        print(f"Core hatched result: {hatch_res}")
        assert hatch_res["coresLeft"] == 2, f"Expected 2 cores left, got {hatch_res['coresLeft']}"
        assert hatch_res["overlayOpen"], "Hatch 3D card overlay must be open"
        assert hatch_res["renderedName"] == hatch_res["itemName"], "Rendered name should match item name"

        # 5. Check badges updated to 2
        badges_after = page.evaluate("""() => {
            const moreTray = document.getElementById('sf-touch-more-tray');
            const btnPlanet = moreTray ? moreTray.querySelector('button') : null;
            const pBadge = btnPlanet ? btnPlanet.querySelector('.sf-touch-core-badge') : null;
            return pBadge ? pBadge.textContent.trim() : null;
        }""")
        print(f"Planet badge after 1 hatch: {badges_after}")
        assert badges_after == "2", f"Expected planet badge '2', got {badges_after}"

        # 6. Test +3 test cores button
        added = page.evaluate("() => window.StarfieldHatch.addCores(3)")
        print(f"Cores after +3: {added}")
        assert added == 5, f"Expected 5 cores, got {added}"

        # 7. Close hatch overlay and re-open list to verify hatched planet card
        page.evaluate("""() => {
            const hatch = document.getElementById('sf-hatch');
            if (hatch) hatch.classList.remove('on');
            window.StarfieldHatch.openList();
        }""")
        page.wait_for_timeout(500)
        card_check = page.evaluate("""() => {
            const items = document.querySelectorAll('#sf-hatch-list .sf-hl-item');
            const nameEl = items.length ? items[0].querySelector('.sf-hl-name') : null;
            return {
                count: items.length,
                firstName: nameEl ? nameEl.textContent.trim() : null
            };
        }""")
        print(f"Card check in list: {card_check}")
        assert card_check["count"] == 1, f"Expected 1 planet in list, got {card_check['count']}"
        assert card_check["firstName"] == hatch_res["itemName"], "List item name must match hatched planet"

        # Take screenshot of Planetarium list
        page.screenshot(path="tools/test_planetarium_ui.png")
        print("Screenshot saved to tools/test_planetarium_ui.png")

        print("Total console errors:", len(console_errors))
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"
        print("ALL PLANET CORE & UI TESTS PASSED!")

if __name__ == '__main__':
    main()
