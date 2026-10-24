import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

async def main():
    errors = []
    logs = []
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

    print('================================================================')
    print('STARFIELD FLEET CUSTOMIZER & QUANTUM WARP TRAIL TEST SUITE')
    print('================================================================')

    shots_dir = r'd:\items\code\starfield-pub\shots'
    os.makedirs(shots_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=edge_path, headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})

        page.on('console', lambda msg: logs.append(f'[{msg.type}] {msg.text}'))
        page.on('pageerror', lambda err: errors.append(str(err)))

        file_url = 'file:///' + os.path.abspath(r'd:\items\code\starfield-pub\starfield.html').replace('\\', '/')
        print('1. Navigating to:', file_url)
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(1)

        # Verify FleetCustomizer object exists on window
        customizer_exists = await page.evaluate("typeof window.FleetCustomizer !== 'undefined'")
        assert customizer_exists, "window.FleetCustomizer is not defined!"
        print('   window.FleetCustomizer loaded successfully.')

        # Click #begin to launch flight
        print('2. Embarking on cosmic flight (#begin)...')
        await page.click('#begin')
        await asyncio.sleep(2)

        # Check HUD Hangar button exists
        print('3. Verifying HUD Hangar Button [ 🚀 舰队折纸坞 ] (#hangar-toggle)...')
        hangar_btn = await page.query_selector('#hangar-toggle')
        assert hangar_btn is not None, "HUD button #hangar-toggle not found in DOM!"
        print('   HUD Hangar button verified in #controls bar.')

        # Test 1: Open Hangar with Hotkey 'H'
        print('4. Testing Hotkey "H" to open Fleet Origami Hangar...')
        await page.keyboard.press('KeyH')
        await asyncio.sleep(1)

        is_open = await page.evaluate("window.FleetCustomizer.isOpen")
        assert is_open, "Hangar modal did not open after pressing 'H'!"
        modal_has_open_class = await page.evaluate("document.getElementById('hangar-modal').classList.contains('open')")
        assert modal_has_open_class, "#hangar-modal missing 'open' class!"
        print('   Hangar modal successfully opened with frosted glass backdrop.')

        # Test 2: 3D Turntable Preview Canvas
        print('5. Testing 3D Turntable Preview Canvas...')
        canvas_info = await page.evaluate("""() => {
            const c = document.getElementById('hangar-turntable-canvas');
            if (!c) return null;
            const ctx = c.getContext('2d');
            const imgData = ctx.getImageData(0, 0, c.width, c.height).data;
            let nonZero = 0;
            for (let i = 0; i < imgData.length; i += 4) {
                if (imgData[i] > 10 || imgData[i+1] > 10 || imgData[i+2] > 10) nonZero++;
            }
            return { width: c.width, height: c.height, nonZeroPixels: nonZero };
        }""")
        assert canvas_info is not None, "Turntable canvas not found!"
        assert canvas_info['nonZeroPixels'] > 500, "Turntable canvas appears blank/unrendered!"
        print(f"   3D Turntable active: {canvas_info['width']}x{canvas_info['height']} with {canvas_info['nonZeroPixels']} rendered pixels.")

        # Test 3: Turntable Interactive Dragging
        print('6. Testing Interactive Drag Rotation on Turntable...')
        yaw_before = await page.evaluate("window.FleetCustomizer.turntable.yaw")
        bbox = await page.locator('#turntable-wrapper').bounding_box()
        assert bbox is not None, "turntable-wrapper bounding box not found"
        # Drag horizontally
        await page.mouse.move(bbox['x'] + bbox['width'] / 2, bbox['y'] + bbox['height'] / 2)
        await page.mouse.down()
        await page.mouse.move(bbox['x'] + bbox['width'] / 2 + 120, bbox['y'] + bbox['height'] / 2 - 20)
        await page.mouse.up()
        await asyncio.sleep(0.5)
        yaw_after = await page.evaluate("window.FleetCustomizer.turntable.yaw")
        assert abs(yaw_after - yaw_before) > 0.1, "Turntable dragging did not update yaw angle!"
        print(f"   Turntable drag verified: yaw changed from {yaw_before:.2f} to {yaw_after:.2f} rad.")

        # Test 4: Switching All 4 Origami Hull Geometries
        hull_names = [
            ('0', '千纸鹤', 'Paper Crane'),
            ('1', '疾风镖', 'Aero Dart'),
            ('2', '星灵刃', 'Protoss Blade'),
            ('3', '虚空蛾', 'Void Moth')
        ]

        print('7. Testing All 4 Origami Hull Geometries Switching...')
        for h_id, zh_name, en_name in hull_names:
            print(f'   -> Selecting Hull {h_id}: {zh_name} ({en_name})...')
            await page.click(f'.hangar-card[data-hull-id="{h_id}"]')
            await asyncio.sleep(0.6)

            cur_hull = await page.evaluate("window.FleetCustomizer.getHull()")
            assert cur_hull == int(h_id), f"Expected hull {h_id}, got {cur_hull}"

            # Check persistent localStorage
            stored_raw = await page.evaluate("localStorage.getItem('starfield_fleet_custom_v1')")
            assert stored_raw is not None, "localStorage['starfield_fleet_custom_v1'] is empty!"
            stored = json.loads(stored_raw)
            assert stored.get('hull') == int(h_id), f"localStorage hull mismatch: {stored}"

            # Capture screenshot of each hull
            shot_hull = os.path.join(shots_dir, f'customizer_hull_{h_id}_{en_name.lower().replace(" ", "_")}.png')
            await page.screenshot(path=shot_hull)
            print(f'      Verified {zh_name}! Saved screenshot to: {shot_hull}')

        # Test 5: Switching All 4 Quantum Warp Ribbon Trails
        trail_names = [
            ('0', '宣纸星尘', 'Paper Starlight'),
            ('1', '离子幽蓝', 'Ion Azure'),
            ('2', '虚空幻紫', 'Void Amethyst'),
            ('3', '暮光红绡', 'Twilight Crimson')
        ]

        print('8. Testing All 4 Quantum Warp Ribbon Trails Switching...')
        for t_id, zh_name, en_name in trail_names:
            print(f'   -> Selecting Trail {t_id}: {zh_name} ({en_name})...')
            await page.click(f'.trail-card[data-trail-id="{t_id}"]')
            await asyncio.sleep(0.6)

            cur_trail = await page.evaluate("window.FleetCustomizer.getTrail()")
            assert cur_trail == int(t_id), f"Expected trail {t_id}, got {cur_trail}"

            # Check persistent localStorage
            stored_raw = await page.evaluate("localStorage.getItem('starfield_fleet_custom_v1')")
            stored = json.loads(stored_raw)
            assert stored.get('trail') == int(t_id), f"localStorage trail mismatch: {stored}"

            # Capture screenshot of each trail
            shot_trail = os.path.join(shots_dir, f'customizer_trail_{t_id}_{en_name.lower().replace(" ", "_")}.png')
            await page.screenshot(path=shot_trail)
            print(f'      Verified {zh_name}! Saved screenshot to: {shot_trail}')

        # Test 6: Close Modal with Close Button
        print('9. Testing Close Button (#hangar-close-btn)...')
        await page.click('#hangar-close-btn')
        await asyncio.sleep(0.6)
        is_open_closed = await page.evaluate("window.FleetCustomizer.isOpen")
        assert not is_open_closed, "Hangar did not close on #hangar-close-btn click!"
        print('   Hangar modal successfully closed.')

        # Test 7: Open with HUD Button and Close with Escape
        print('10. Testing Open via HUD Button (#hangar-toggle) & Close via Escape key...')
        await page.click('#hangar-toggle')
        await asyncio.sleep(0.6)
        assert await page.evaluate("window.FleetCustomizer.isOpen"), "Hangar did not open via HUD button click!"
        await page.keyboard.press('Escape')
        await asyncio.sleep(0.6)
        assert not await page.evaluate("window.FleetCustomizer.isOpen"), "Hangar did not close via Escape key!"
        print('   HUD button and Escape hotkey verified.')

        # Test 8: In-flight Deep Space Fleet Rendering at Dynamic Warp Speeds
        print('11. Testing Deep Space Flight with Custom Origami Fleet at Warp Speeds...')

        # Set specific stylish combination: Hull 1 (Aero Dart) + Trail 1 (Ion Azure)
        await page.evaluate("""() => {
            window.FleetCustomizer.setHull(1); // Aero Dart
            window.FleetCustomizer.setTrail(1); // Ion Azure
        }""")

        # 1.0c Cruise
        print('   [1.0c Cruise Speed]')
        await asyncio.sleep(1.5)
        shot_flight_1x = os.path.join(shots_dir, 'customizer_flight_1x_cruise.png')
        await page.screenshot(path=shot_flight_1x)
        print('   Saved in-flight 1.0c screenshot to:', shot_flight_1x)

        # 5.0c Warp Jump
        print('   [5.0c Warp Jump]')
        await page.keyboard.press('KeyG')
        await asyncio.sleep(2)
        shot_flight_5x = os.path.join(shots_dir, 'customizer_flight_5x_warp.png')
        await page.screenshot(path=shot_flight_5x)
        print('   Saved in-flight 5.0c screenshot to:', shot_flight_5x)

        # 15.0c Hyperwarp
        print('   [15.0c Hyperwarp]')
        await page.keyboard.press('KeyG')
        await asyncio.sleep(2)
        shot_flight_15x = os.path.join(shots_dir, 'customizer_flight_15x_hyperwarp.png')
        await page.screenshot(path=shot_flight_15x)
        print('   Saved in-flight 15.0c screenshot to:', shot_flight_15x)

        # Test another combination: Hull 2 (Protoss Blade) + Trail 2 (Void Amethyst)
        print('   [Testing Protoss Blade + Void Amethyst in flight]')
        await page.evaluate("""() => {
            window.FleetCustomizer.setHull(2); // Protoss Blade
            window.FleetCustomizer.setTrail(2); // Void Amethyst
        }""")
        await asyncio.sleep(1.5)
        shot_flight_protoss = os.path.join(shots_dir, 'customizer_flight_protoss_void.png')
        await page.screenshot(path=shot_flight_protoss)
        print('   Saved Protoss Blade flight screenshot to:', shot_flight_protoss)

        # Test Void Moth + Twilight Crimson
        print('   [Testing Void Moth + Twilight Crimson in flight]')
        await page.evaluate("""() => {
            window.FleetCustomizer.setHull(3); // Void Moth
            window.FleetCustomizer.setTrail(3); // Twilight Crimson
        }""")
        await asyncio.sleep(1.5)
        shot_flight_moth = os.path.join(shots_dir, 'customizer_flight_moth_crimson.png')
        await page.screenshot(path=shot_flight_moth)
        print('   Saved Void Moth flight screenshot to:', shot_flight_moth)

        # Test drawShard direct invocation
        print('12. Verifying drawShard hook...')
        drawshard_test = await page.evaluate("""() => {
            try {
                const s = { x: 0, y: 100, z: 1000, ang: 0, spin: 0.1, w: 20, h: 20 };
                const p = { wall: [180, 190, 205], craft: [230, 237, 242], roof: [160, 170, 185] };
                window.FleetCustomizer.drawShard(s, p, 1.0);
                return true;
            } catch (e) {
                return false;
            }
        }""")
        assert drawshard_test, "FleetCustomizer.drawShard threw an error!"
        print('   FleetCustomizer.drawShard verified.')

        # Verify travel progress
        travel_dist = await page.evaluate("window.Starfield.getTravel()")
        print(f'13. Flight Active Travel Progress: {travel_dist:.1f} distance units')
        assert travel_dist > 0, "Flight travel distance did not advance!"

        await browser.close()

    error_logs = [l for l in logs if '[error]' in l]

    print('\n================================================================')
    print('VERIFICATION SUMMARY')
    print(f'Total Console Logs: {len(logs)}')
    print(f'Page Errors: {len(errors)}')
    print(f'Console Error Logs: {len(error_logs)}')

    if errors or error_logs:
        print('ERRORS DETECTED:')
        for e in errors:
            print('  Page Error:', e)
        for el in error_logs:
            print('  Log Error:', el)
        sys.exit(1)
    else:
        print('>>> ALL FLEET CUSTOMIZER TESTS PASSED WITH ZERO ERRORS! <<<')
    print('================================================================')

if __name__ == '__main__':
    asyncio.run(main())
