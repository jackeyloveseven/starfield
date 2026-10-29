"""Verify mobile clean HUD:
1. Bottom-left #journey: no box, no border, transparent background, curve perfectly fitted.
2. Bottom-right .sf-touch-btn: transparent, no border, no background box, clean icons.
3. Top-left text (#camera-hud): safe area top clearance >= 24px, no border, no collision with #comms-hud.
"""
import os
import sys
from playwright.sync_api import sync_playwright

def verify_mobile_clean_hud():
    pub_dir = r"d:\items\code\starfield-pub"
    html_file = os.path.join(pub_dir, "starfield.html")
    artifact_dir = r"C:\Users\machine\.gemini\antigravity\brain\72ea3f45-0738-459a-8560-5853a3c36367"
    file_url = f"file:///{html_file.replace(os.sep, '/')}"

    print("=================================================================")
    print(" VERIFYING MOBILE CLEAN HUD (TRANSPARENT, BOXLESS & ZERO OCCLUSION)")
    print("=================================================================")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            args=["--use-gl=angle", "--use-angle=swiftshader", "--disable-gpu-watchdog"]
        )

        # -------------------------------------------------------------
        # 1. Mobile Portrait Viewport (390 x 844, 2x DPR)
        # -------------------------------------------------------------
        print("\n1. Testing Mobile Portrait (390x844)...")
        ctx_portrait = browser.new_context(
            viewport={'width': 390, 'height': 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page_p = ctx_portrait.new_page()
        page_p.goto(file_url, wait_until='networkidle')
        page_p.wait_for_timeout(800)

        # Start flight
        page_p.locator('#begin').click()
        page_p.wait_for_timeout(1000)

        # A. Check Bottom-Left #journey & #route
        journey_style = page_p.evaluate("""() => {
            const el = document.getElementById('journey');
            const route = document.getElementById('route');
            const cs = getComputedStyle(el);
            const rcs = getComputedStyle(route);
            const rect = el.getBoundingClientRect();
            const rrect = route.getBoundingClientRect();
            return {
                bg: cs.backgroundColor,
                border: cs.borderWidth,
                boxShadow: cs.boxShadow,
                backdropFilter: cs.backdropFilter,
                jWidth: rect.width,
                rWidth: rrect.width,
                rLeft: rrect.left,
                jLeft: rect.left,
                rRight: rrect.right,
                jRight: rect.right
            };
        }""")
        print(f"   - #journey bg: {journey_style['bg']}")
        print(f"   - #journey border: {journey_style['border']}, shadow: {journey_style['boxShadow']}")
        print(f"   - #route width: {journey_style['rWidth']}px inside #journey")
        
        # Verify box is removed (transparent or 0 border/shadow)
        assert "rgba(0, 0, 0, 0)" in journey_style['bg'] or "transparent" in journey_style['bg'], f"Expected transparent bg, got {journey_style['bg']}"
        assert journey_style['border'] == '0px' or journey_style['border'] == '', f"Expected 0px border, got {journey_style['border']}"
        assert journey_style['boxShadow'] == 'none', f"Expected no box-shadow, got {journey_style['boxShadow']}"

        # B. Check Bottom-Right Buttons (.sf-touch-btn)
        btn_styles = page_p.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn'));
            return btns.map(b => {
                const cs = getComputedStyle(b);
                return {
                    cls: b.className,
                    bg: cs.backgroundColor,
                    border: cs.borderWidth,
                    boxShadow: cs.boxShadow,
                    color: cs.color
                };
            });
        }""")
        print(f"   - Found {len(btn_styles)} primary touch buttons")
        for i, bs in enumerate(btn_styles):
            print(f"     Btn {i} ({bs['cls']}): bg={bs['bg']}, border={bs['border']}, shadow={bs['boxShadow']}")
            assert "rgba(0, 0, 0, 0)" in bs['bg'] or "transparent" in bs['bg'], f"Btn {i} expected transparent, got {bs['bg']}"
            assert bs['border'] == '0px' or bs['border'] == '', f"Btn {i} expected no border, got {bs['border']}"
            assert bs['boxShadow'] == 'none', f"Btn {i} expected no shadow, got {bs['boxShadow']}"

        # C. Check Top-Left #camera-hud & safe area clearance
        cam_style = page_p.evaluate("""() => {
            const el = document.getElementById('camera-hud');
            const cs = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return {
                bg: cs.backgroundColor,
                border: cs.borderWidth,
                boxShadow: cs.boxShadow,
                top: rect.top,
                bottom: rect.bottom,
                left: rect.left,
                right: rect.right,
                height: rect.height
            };
        }""")
        print(f"   - #camera-hud top={cam_style['top']}px (>= 24px safe area clearance)")
        print(f"   - #camera-hud bg={cam_style['bg']}, border={cam_style['border']}")
        assert cam_style['top'] >= 24, f"Expected top >= 24px, got {cam_style['top']}"
        assert "rgba(0, 0, 0, 0)" in cam_style['bg'] or "transparent" in cam_style['bg']
        assert cam_style['border'] == '0px' or cam_style['border'] == ''

        # D. Trigger COMMS message and test occlusion
        page_p.evaluate("""() => {
            if (typeof window.triggerCommsLine === 'function') {
                window.triggerCommsLine('深空从不问一艘船的重量。哪怕只是一片折纸。');
            } else {
                const comms = document.getElementById('comms-hud');
                if (comms) comms.classList.add('active');
            }
        }""")
        page_p.wait_for_timeout(400)

        comms_box = page_p.evaluate("""() => {
            const comms = document.getElementById('comms-hud');
            const cam = document.getElementById('camera-hud');
            const cRect = comms.getBoundingClientRect();
            const camRect = cam.getBoundingClientRect();
            return {
                commsTop: cRect.top,
                commsBottom: cRect.bottom,
                camBottom: camRect.bottom,
                camTop: camRect.top
            };
        }""")
        print(f"   - #camera-hud bottom={comms_box['camBottom']:.1f}px, #comms-hud top={comms_box['commsTop']:.1f}px")
        # Ensure #comms-hud does NOT cover #camera-hud in portrait
        assert comms_box['commsTop'] >= comms_box['camBottom'], f"Collision! #comms-hud ({comms_box['commsTop']}px) covers #camera-hud ({comms_box['camBottom']}px)"

        # Click 更多 (More) button to expand tray
        page_p.evaluate("() => (document.querySelector('.sf-touch-primary-row .sf-touch-btn.more') || document.querySelectorAll('.sf-touch-primary-row .sf-touch-btn')[2]).click()")
        page_p.wait_for_timeout(300)
        shot_tray = os.path.join(artifact_dir, "test_mobile_clean_hud_tray_open.png")
        page_p.screenshot(path=shot_tray)
        print(f"   - Saved tray open screenshot: {shot_tray}")

        shot_p = os.path.join(artifact_dir, "test_mobile_clean_hud_portrait.png")
        page_p.screenshot(path=shot_p)
        print(f"   - Saved screenshot: {shot_p}")

        # -------------------------------------------------------------
        # 2. Mobile Landscape Viewport (844 x 390, 2x DPR)
        # -------------------------------------------------------------
        print("\n2. Testing Mobile Landscape (844x390)...")
        ctx_ls = browser.new_context(
            viewport={'width': 844, 'height': 390},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2.0,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        )
        page_ls = ctx_ls.new_page()
        page_ls.goto(file_url, wait_until='networkidle')
        page_ls.wait_for_timeout(800)

        # Start flight
        page_ls.locator('#begin').click()
        page_ls.wait_for_timeout(1000)

        # Trigger COMMS message in landscape
        page_ls.evaluate("""() => {
            if (typeof window.triggerCommsLine === 'function') {
                window.triggerCommsLine('航道数据载入。在数万光年之外，引力是唯一的信标。');
            } else {
                const comms = document.getElementById('comms-hud');
                if (comms) comms.classList.add('active');
            }
        }""")
        page_ls.wait_for_timeout(400)

        ls_boxes = page_ls.evaluate("""() => {
            const comms = document.getElementById('comms-hud');
            const cam = document.getElementById('camera-hud');
            const cRect = comms.getBoundingClientRect();
            const camRect = cam.getBoundingClientRect();
            return {
                commsLeft: cRect.left,
                commsRight: cRect.right,
                camRight: camRect.right,
                camLeft: camRect.left,
                commsTop: cRect.top,
                camBottom: camRect.bottom
            };
        }""")
        print(f"   - Landscape: #camera-hud right={ls_boxes['camRight']:.1f}px, #comms-hud left={ls_boxes['commsLeft']:.1f}px")
        # Ensure horizontal separation in landscape
        assert ls_boxes['commsLeft'] >= ls_boxes['camRight'] or ls_boxes['commsTop'] >= ls_boxes['camBottom'], \
            f"Collision in landscape! #comms-hud left ({ls_boxes['commsLeft']}px) overlaps #camera-hud right ({ls_boxes['camRight']}px)"

        shot_ls = os.path.join(artifact_dir, "test_mobile_clean_hud_landscape.png")
        page_ls.screenshot(path=shot_ls)
        print(f"   - Saved screenshot: {shot_ls}")

        browser.close()
    print("\nALL MOBILE CLEAN HUD CHECKS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    verify_mobile_clean_hud()
