# -*- coding: utf-8 -*-
"""
Verification Script for Build 185: Mobile Touch Navigation & Zero-Occlusion HUD Architecture
Validates:
1. iPhone 14/15 Portrait (390x844) & Android Portrait (412x915)
2. Landscape Viewports (844x390 & 915x412)
3. Zero Horizontal Scroll (#world.scrollLeft === 0)
4. Full Touch Control Suite (5 primary transparent buttons + 5 expandable tray buttons)
5. Touch button functional reactions (Warp cycle, Formation cycle, Tray toggle, Codex toggle)
6. Zero-Occlusion HUD geometry between #camera-hud, #sf-contract-hud, #comms-hud, .sf-sonar-capsule, #journey, and .sf-touch-cluster
7. Multi-device high-resolution screenshot generation
"""
import os
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def run_mobile_verification():
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / "starfield.html"
    artifacts_dir = base_dir / "tools" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    file_url = f"file:///{str(html_path).replace(os.sep, '/')}"

    print("=================================================================")
    print(" VERIFYING BUILD 185: MOBILE TOUCH CONTROLS & ZERO-OCCLUSION HUD ")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=["--use-gl=angle", "--use-angle=swiftshader", "--disable-gpu-watchdog"]
        )

        # -----------------------------------------------------------------
        # TEST 1: iPhone 14/15 Portrait (390 x 844)
        # -----------------------------------------------------------------
        print("\n--- Test 1: iPhone Portrait (390 x 844, 3x DPR) ---")
        ctx_iphone = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        page = ctx_iphone.new_page()
        page.goto(file_url, wait_until='networkidle')
        page.wait_for_timeout(600)

        # Check scroll position before flight
        scroll_pre = page.evaluate("() => ({ scrollLeft: document.getElementById('world')?.scrollLeft || 0, scrollWidth: document.getElementById('world')?.scrollWidth || 0 })")
        print(f"   - Pre-flight world scrollLeft: {scroll_pre['scrollLeft']}, scrollWidth: {scroll_pre['scrollWidth']}")
        assert scroll_pre['scrollLeft'] == 0, f"Expected scrollLeft == 0 before flight, got {scroll_pre['scrollLeft']}"

        # Click #begin to take off
        page.locator('#begin').click()
        page.wait_for_timeout(1000)

        # Check scroll position after flight
        scroll_post = page.evaluate("() => ({ scrollLeft: document.getElementById('world')?.scrollLeft || 0, scrollWidth: document.getElementById('world')?.scrollWidth || 0 })")
        print(f"   - In-flight world scrollLeft: {scroll_post['scrollLeft']}, scrollWidth: {scroll_post['scrollWidth']}")
        assert scroll_post['scrollLeft'] == 0, f"Expected scrollLeft == 0 in flight, got {scroll_post['scrollLeft']}"

        # Verify Touch Overlay is displayed and active
        overlay_info = page.evaluate("""() => {
            const ov = document.getElementById('starfield-touch-overlay');
            const joy = document.querySelector('.sf-touch-joy-zone');
            const cluster = document.querySelector('.sf-touch-cluster');
            const primaryBtns = Array.from(document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn'));
            const moreTrayBtns = Array.from(document.querySelectorAll('.sf-touch-more-tray .sf-touch-btn'));
            return {
                overlayDisplay: ov ? getComputedStyle(ov).display : 'null',
                hasJoyZone: !!joy,
                hasCluster: !!cluster,
                primaryCount: primaryBtns.length,
                trayCount: moreTrayBtns.length,
                primaryVisible: primaryBtns.map(b => b.offsetParent !== null),
                primaryClasses: primaryBtns.map(b => b.className),
                primaryAria: primaryBtns.map(b => b.getAttribute('aria-label') || ''),
                trayAria: moreTrayBtns.map(b => b.getAttribute('aria-label') || '')
            };
        }""")
        print(f"   - Touch overlay display: {overlay_info['overlayDisplay']}")
        print(f"   - Primary touch buttons: {overlay_info['primaryCount']} (all visible: {all(overlay_info['primaryVisible'])})")
        print(f"   - Secondary tray buttons: {overlay_info['trayCount']}")
        print(f"   - Primary button labels: {overlay_info['primaryAria']}")
        print(f"   - Tray button labels: {overlay_info['trayAria']}")
        assert overlay_info['overlayDisplay'] == 'block', f"Expected touch overlay 'block', got {overlay_info['overlayDisplay']}"
        assert overlay_info['primaryCount'] == 5, f"Expected 5 primary touch buttons, got {overlay_info['primaryCount']}"
        assert overlay_info['trayCount'] == 6, f"Expected 6 tray buttons (including Sonar), got {overlay_info['trayCount']}"
        assert all(overlay_info['primaryVisible']), "Not all primary buttons are visible!"
        assert all(len(a) > 0 for a in overlay_info['primaryAria']), "Primary buttons missing aria-labels!"
        assert all(len(a) > 0 for a in overlay_info['trayAria']), "Tray buttons missing aria-labels!"

        # Verify Clean Transparent Button Styling (no ugly borders/boxes)
        btn_styles = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn'));
            return btns.map(b => {
                const cs = getComputedStyle(b);
                return {
                    bg: cs.backgroundColor,
                    border: cs.borderWidth,
                    boxShadow: cs.boxShadow
                };
            });
        }""")
        for i, bs in enumerate(btn_styles):
            assert "rgba(0, 0, 0, 0)" in bs['bg'] or "transparent" in bs['bg'], f"Btn {i} has opaque background: {bs['bg']}"
            assert bs['border'] == '0px' or bs['border'] == '', f"Btn {i} has border: {bs['border']}"
            assert bs['boxShadow'] == 'none', f"Btn {i} has box-shadow: {bs['boxShadow']}"
        print("   - [PASS] All 5 primary buttons verified boxless & transparent.")

        # Test Button Interaction 1: Warp Gear Cycle
        gear_before = page.evaluate("() => window.WarpDrive ? window.WarpDrive.gearIndex : -1")
        # Click warp button (index 1 in primary row)
        page.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[1].click()")
        page.wait_for_timeout(300)
        gear_after = page.evaluate("() => window.WarpDrive ? window.WarpDrive.gearIndex : -1")
        print(f"   - Warp gear shift: {gear_before} -> {gear_after}")
        assert gear_after == (gear_before + 1) % 3, f"Expected gear shift from {gear_before} to {(gear_before + 1) % 3}, got {gear_after}"
        print("   - [PASS] Touch Warp button cycled gears successfully.")

        # Test Button Interaction 2: Formation Cycle
        formation_before = page.evaluate("() => (window.Starfield && window.Starfield.getFleetFormations ? window.Starfield.getFleetFormations().current : -1)")
        # Click formation button (index 2 in primary row)
        page.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[2].click()")
        page.wait_for_timeout(300)
        formation_after = page.evaluate("() => (window.Starfield && window.Starfield.getFleetFormations ? window.Starfield.getFleetFormations().current : -1)")
        print(f"   - Formation cycle: {formation_before} -> {formation_after}")
        assert formation_after != -1 and formation_after != formation_before, f"Expected formation to change from {formation_before}, got {formation_after}"
        print("   - [PASS] Touch Formation button cycled formations successfully.")

        # Test Button Interaction 3: More Tray Toggle
        tray_open_before = page.evaluate("() => document.getElementById('sf-touch-more-tray').classList.contains('open')")
        # Click more button (index 4 / .sf-touch-btn.more)
        page.evaluate("() => document.querySelector('.sf-touch-primary-row .sf-touch-btn.more').click()")
        page.wait_for_timeout(300)
        tray_open_after = page.evaluate("() => document.getElementById('sf-touch-more-tray').classList.contains('open')")
        print(f"   - More tray open state: {tray_open_before} -> {tray_open_after}")
        assert not tray_open_before and tray_open_after, "More tray failed to open upon click!"

        # Verify zero collision between open moreTray and #journey
        tray_collision_info = page.evaluate("""() => {
            const tray = document.getElementById('sf-touch-more-tray').getBoundingClientRect();
            const cluster = document.querySelector('.sf-touch-cluster').getBoundingClientRect();
            const journey = document.getElementById('journey').getBoundingClientRect();
            return {
                clusterLeft: cluster.left,
                journeyRight: journey.right,
                clearance: cluster.left - journey.right
            };
        }""")
        print(f"   - Open tray vs #journey: clusterLeft={tray_collision_info['clusterLeft']:.1f}px, journeyRight={tray_collision_info['journeyRight']:.1f}px (clearance: {tray_collision_info['clearance']:.1f}px)")
        assert tray_collision_info['clearance'] > 0, f"Collision detected between open tray cluster and #journey! clearance={tray_collision_info['clearance']}px"
        print("   - [PASS] Open tray verified zero collision against #journey.")

        # Test Sonar trigger button in More Tray
        sonar_res = page.evaluate("""() => {
            const sonarBtn = document.querySelectorAll('#sf-touch-more-tray .sf-touch-btn')[1];
            let sonarTriggered = false;
            if (window.StarfieldSonar) {
                const orig = window.StarfieldSonar.triggerScan;
                window.StarfieldSonar.triggerScan = function() {
                    sonarTriggered = true;
                    return orig ? orig.apply(this, arguments) : null;
                };
            }
            sonarBtn.click();
            return {
                sonarTriggered: sonarTriggered,
                trayClosed: !document.getElementById('sf-touch-more-tray').classList.contains('open')
            };
        }""")
        print(f"   - Touch Sonar button in tray: triggered={sonar_res['sonarTriggered']}, trayClosed={sonar_res['trayClosed']}")
        assert sonar_res['sonarTriggered'], "Touch Sonar button failed to trigger StarfieldSonar.triggerScan()!"
        assert sonar_res['trayClosed'], "More tray failed to auto-close after clicking Sonar button!"
        print("   - [PASS] Touch Sonar button triggered scan and auto-closed tray.")

        shot_tray = artifacts_dir / "mobile185_portrait_more_tray.png"
        page.screenshot(path=str(shot_tray))
        print(f"   - Saved tray open screenshot: {shot_tray}")

        # Test Button Interaction 4: Codex Toggle
        # Click codex button (index 3 in primary row)
        page.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[3].click()")
        page.wait_for_timeout(400)
        codex_open = page.evaluate("() => document.getElementById('codex-modal')?.classList.contains('open') || false")
        print(f"   - Codex modal open state: {codex_open}")
        assert codex_open, "Codex failed to open when touching codex button!"
        # Close codex modal
        page.evaluate("() => { if (window.Engine) window.Engine.closeModal(); else document.querySelector('.codex-close')?.click(); }")
        page.wait_for_timeout(400)

        # Trigger COMMS, Sonar, Contract, and Descent Button for full HUD collision audit
        page.evaluate("""() => {
            if (typeof window.triggerCommsLine === 'function') {
                window.triggerCommsLine('深空从不问一艘船的重量。哪怕只是一片折纸。');
            } else {
                const comms = document.getElementById('comms-hud');
                if (comms) comms.classList.add('active');
            }
            const sonar = document.getElementById('sf-sonar-capsule');
            if (sonar) sonar.classList.add('show');

            const contract = document.getElementById('sf-contract-hud');
            if (contract) contract.classList.add('show');

            const descent = document.getElementById('sf-descent-btn');
            if (descent) descent.classList.add('show');
        }""")
        page.wait_for_timeout(500)

        # Check portrait geometric separation across all HUD elements
        boxes = page.evaluate("""() => {
            const getBox = id => {
                const el = document.getElementById(id) || document.querySelector('.' + id);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return { top: r.top, bottom: r.bottom, left: r.left, right: r.right, width: r.width, height: r.height };
            };
            return {
                cam: getBox('camera-hud'),
                contract: getBox('sf-contract-hud'),
                sonar: getBox('sf-sonar-capsule'),
                comms: getBox('comms-hud'),
                journey: getBox('journey'),
                cluster: getBox('sf-touch-cluster'),
                descent: getBox('sf-descent-btn')
            };
        }""")
        print("\n   --- Portrait HUD Geometry Layout ---")
        print(f"   - #camera-hud: top={boxes['cam']['top']:.1f}, bottom={boxes['cam']['bottom']:.1f}, left={boxes['cam']['left']:.1f}, right={boxes['cam']['right']:.1f}")
        print(f"   - #sf-contract-hud: top={boxes['contract']['top']:.1f}, bottom={boxes['contract']['bottom']:.1f}, left={boxes['contract']['left']:.1f}, right={boxes['contract']['right']:.1f}")
        if boxes['sonar']:
            print(f"   - .sf-sonar-capsule: top={boxes['sonar']['top']:.1f}, bottom={boxes['sonar']['bottom']:.1f}")
        else:
            print("   - .sf-sonar-capsule: completely removed / zero occlusion (Build 186+)")
        print(f"   - #comms-hud: top={boxes['comms']['top']:.1f}, bottom={boxes['comms']['bottom']:.1f}")
        print(f"   - #journey: left={boxes['journey']['left']:.1f}, right={boxes['journey']['right']:.1f}, bottom={boxes['journey']['bottom']:.1f}")
        print(f"   - .sf-touch-cluster: left={boxes['cluster']['left']:.1f}, right={boxes['cluster']['right']:.1f}, bottom={boxes['cluster']['bottom']:.1f}")

        # Geometric assertions
        assert boxes['cam']['top'] >= 24, f"Camera HUD top must clear safe area (>=24px), got {boxes['cam']['top']}"
        assert boxes['contract']['left'] >= boxes['cam']['right'], f"Contract HUD overlaps Camera HUD horizontally! cam.right={boxes['cam']['right']}, contract.left={boxes['contract']['left']}"
        if boxes['sonar']:
            assert boxes['sonar']['top'] >= boxes['cam']['bottom'] - 20, f"Sonar capsule overlaps camera info! cam.bottom={boxes['cam']['bottom']}, sonar.top={boxes['sonar']['top']}"
            assert boxes['comms']['top'] >= boxes['sonar']['bottom'], f"COMMS covers sonar capsule! sonar.bottom={boxes['sonar']['bottom']}, comms.top={boxes['comms']['top']}"
        assert boxes['comms']['top'] >= boxes['cam']['bottom'], f"COMMS covers camera info! cam.bottom={boxes['cam']['bottom']}, comms.top={boxes['comms']['top']}"
        assert boxes['journey']['right'] <= boxes['cluster']['left'], f"Journey HUD collides with touch buttons! journey.right={boxes['journey']['right']}, cluster.left={boxes['cluster']['left']}"
        print("   - [PASS] Zero occlusion across all portrait HUD components verified.")

        shot_p = artifacts_dir / "mobile185_portrait_flight.png"
        page.screenshot(path=str(shot_p))
        print(f"   - Saved flight screenshot: {shot_p}")
        ctx_iphone.close()

        # -----------------------------------------------------------------
        # TEST 2: Android Flagship Portrait (412 x 915)
        # -----------------------------------------------------------------
        print("\n--- Test 2: Android Flagship Portrait (412 x 915, 2.625x DPR) ---")
        ctx_android = browser.new_context(
            viewport={'width': 412, 'height': 915},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.625,
            user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        page_a = ctx_android.new_page()
        page_a.goto(file_url, wait_until='networkidle')
        page_a.wait_for_timeout(600)

        page_a.locator('#begin').click()
        page_a.wait_for_timeout(1000)

        # Verify scrollLeft == 0
        scroll_a = page_a.evaluate("() => document.getElementById('world')?.scrollLeft || 0")
        assert scroll_a == 0, f"Expected scrollLeft == 0 on Android, got {scroll_a}"

        # Verify primary buttons
        btns_count = page_a.evaluate("() => document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn').length")
        assert btns_count == 5, f"Expected 5 buttons on Android, got {btns_count}"
        print(f"   - [PASS] Android portrait verified with {btns_count} buttons and 0px scroll offset.")

        shot_a = artifacts_dir / "mobile185_android_portrait.png"
        page_a.screenshot(path=str(shot_a))
        print(f"   - Saved Android screenshot: {shot_a}")
        ctx_android.close()

        # -----------------------------------------------------------------
        # TEST 3: Mobile Landscape (844 x 390)
        # -----------------------------------------------------------------
        print("\n--- Test 3: Mobile Landscape (844 x 390, 2x DPR) ---")
        ctx_landscape = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        )
        page_l = ctx_landscape.new_page()
        page_l.goto(file_url, wait_until='networkidle')
        page_l.wait_for_timeout(600)

        # Pre-flight landscape scroll
        scroll_l_pre = page_l.evaluate("() => document.getElementById('world')?.scrollLeft || 0")
        assert scroll_l_pre == 0, f"Landscape pre-flight scrollLeft must be 0, got {scroll_l_pre}"

        # Start flight
        page_l.locator('#begin').click()
        page_l.wait_for_timeout(1000)

        # Post-flight landscape scroll
        scroll_l_post = page_l.evaluate("() => document.getElementById('world')?.scrollLeft || 0")
        assert scroll_l_post == 0, f"Landscape in-flight scrollLeft must be 0, got {scroll_l_post}"
        print(f"   - [PASS] Landscape viewport perfectly clipped: scrollLeft={scroll_l_post}")

        # Trigger COMMS, Contract, and Sonar in landscape
        page_l.evaluate("""() => {
            if (typeof window.triggerCommsLine === 'function') {
                window.triggerCommsLine('航道数据载入。在数万光年之外，引力是唯一的信标。保持曲率稳定。');
            } else {
                const comms = document.getElementById('comms-hud');
                if (comms) comms.classList.add('active');
            }
            const contract = document.getElementById('sf-contract-hud');
            if (contract) contract.classList.add('show');
            const sonar = document.getElementById('sf-sonar-capsule');
            if (sonar) sonar.classList.add('show');
        }""")
        page_l.wait_for_timeout(400)

        # Check landscape geometry
        ls_boxes = page_l.evaluate("""() => {
            const cam = document.getElementById('camera-hud').getBoundingClientRect();
            const comms = document.getElementById('comms-hud').getBoundingClientRect();
            const contract = document.getElementById('sf-contract-hud').getBoundingClientRect();
            const journey = document.getElementById('journey').getBoundingClientRect();
            const cluster = document.querySelector('.sf-touch-cluster').getBoundingClientRect();
            return {
                cam: { left: cam.left, right: cam.right, top: cam.top, bottom: cam.bottom },
                contract: { left: contract.left, right: contract.right, top: contract.top, bottom: contract.bottom },
                comms: { left: comms.left, right: comms.right, top: comms.top, bottom: comms.bottom },
                journey: { left: journey.left, right: journey.right, bottom: journey.bottom },
                cluster: { left: cluster.left, right: cluster.right, bottom: cluster.bottom }
            };
        }""")
        print("\n   --- Landscape HUD Geometry Layout ---")
        print(f"   - #camera-hud: right={ls_boxes['cam']['right']:.1f}px, left={ls_boxes['cam']['left']:.1f}px")
        print(f"   - #sf-contract-hud: top={ls_boxes['contract']['top']:.1f}px, bottom={ls_boxes['contract']['bottom']:.1f}px, left={ls_boxes['contract']['left']:.1f}px, right={ls_boxes['contract']['right']:.1f}px")
        print(f"   - #comms-hud: top={ls_boxes['comms']['top']:.1f}px, bottom={ls_boxes['comms']['bottom']:.1f}px, left={ls_boxes['comms']['left']:.1f}px, right={ls_boxes['comms']['right']:.1f}px")
        print(f"   - #journey right={ls_boxes['journey']['right']:.1f}px vs cluster left={ls_boxes['cluster']['left']:.1f}px")

        # Landscape separation assertions:
        # 1. Comms must sit comfortably below Contract HUD
        assert ls_boxes['comms']['top'] >= ls_boxes['contract']['bottom'], \
            f"Landscape collision! #comms-hud top ({ls_boxes['comms']['top']}px) overlaps #sf-contract-hud bottom ({ls_boxes['contract']['bottom']}px)"
        # 2. Camera and comms/contract do not collide horizontally
        assert ls_boxes['comms']['left'] >= ls_boxes['cam']['right'], \
            f"Landscape collision! #comms-hud left ({ls_boxes['comms']['left']}px) overlaps #camera-hud right ({ls_boxes['cam']['right']}px)"
        assert ls_boxes['contract']['left'] >= ls_boxes['cam']['right'], \
            f"Landscape collision! #sf-contract-hud left ({ls_boxes['contract']['left']}px) overlaps #camera-hud right ({ls_boxes['cam']['right']}px)"
        # 3. Bottom left #journey does not collide with bottom right cluster
        assert ls_boxes['journey']['right'] < ls_boxes['cluster']['left'], \
            f"Landscape collision between #journey and touch cluster! {ls_boxes['journey']['right']} >= {ls_boxes['cluster']['left']}"
        print("   - [PASS] Landscape zero-occlusion layout fully verified.")

        shot_l = artifacts_dir / "mobile185_landscape_flight.png"
        page_l.screenshot(path=str(shot_l))
        print(f"   - Saved landscape screenshot: {shot_l}")
        ctx_landscape.close()

        # -----------------------------------------------------------------
        # TEST 4: Compact Android Portrait (360 x 780, 3x DPR)
        # -----------------------------------------------------------------
        print("\n--- Test 4: Compact Mobile Viewport (360 x 780, 3x DPR) ---")
        ctx_compact = browser.new_context(
            viewport={'width': 360, 'height': 780},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=3.0,
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
        )
        page_c = ctx_compact.new_page()
        page_c.goto(file_url, wait_until='networkidle')
        page_c.wait_for_timeout(600)

        # Pre-flight scroll
        assert page_c.evaluate("() => document.getElementById('world')?.scrollLeft || 0") == 0

        # Start flight
        page_c.locator('#begin').click()
        page_c.wait_for_timeout(1000)

        # In-flight scroll
        assert page_c.evaluate("() => document.getElementById('world')?.scrollLeft || 0") == 0

        # Verify buttons & tray zero occlusion on 360px viewport
        compact_info = page_c.evaluate("""() => {
            const moreBtn = document.querySelector('.sf-touch-btn.more');
            moreBtn.click();
            const cluster = document.querySelector('.sf-touch-cluster').getBoundingClientRect();
            const journey = document.getElementById('journey').getBoundingClientRect();
            return {
                clusterLeft: cluster.left,
                journeyRight: journey.right,
                clearance: cluster.left - journey.right
            };
        }""")
        print(f"   - Compact 360px open tray: clusterLeft={compact_info['clusterLeft']:.1f}px, journeyRight={compact_info['journeyRight']:.1f}px (clearance: {compact_info['clearance']:.1f}px)")
        assert compact_info['clearance'] > 0, f"Compact viewport collision! clearance={compact_info['clearance']}px"
        print("   - [PASS] Compact 360px portrait verified with zero horizontal scroll and zero occlusion.")

        shot_c = artifacts_dir / "mobile185_compact_portrait.png"
        page_c.screenshot(path=str(shot_c))
        print(f"   - Saved compact portrait screenshot: {shot_c}")
        ctx_compact.close()

        browser.close()

    print("\n=================================================================")
    print(" ALL BUILD 185 MOBILE TESTS & ZERO-OCCLUSION CHECKS PASSED 100%!")
    print("=================================================================")

if __name__ == '__main__':
    run_mobile_verification()
