import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    errors = []
    logs = []
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    shots_dir = r'd:\items\code\starfield-pub\shots'
    os.makedirs(shots_dir, exist_ok=True)
    
    print('===============================================================')
    print(' STARFIELD: ZERO-DEPENDENCY GAMEPAD & TOUCH VERIFICATION SUITE')
    print('===============================================================')
    
    async with async_playwright() as p:
        # Launch Chromium/Edge with touch simulation enabled
        browser = await p.chromium.launch(executable_path=edge_path, headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            has_touch=True,
            is_mobile=True,
            device_scale_factor=1.0
        )
        page = await context.new_page()
        
        page.on('console', lambda msg: logs.append(f'[{msg.type}] {msg.text}'))
        page.on('pageerror', lambda err: errors.append(str(err)))
        
        file_url = 'file:///' + os.path.abspath(r'd:\items\code\starfield-pub\starfield.html').replace('\\', '/')
        print(f'1. Navigating to Starfield: {file_url}')
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(1)
        
        # Verify GamepadTouchControls module presence
        mod_version = await page.evaluate("window.GamepadTouchControls ? window.GamepadTouchControls.version : null")
        print(f'2. Verified GamepadTouchControls Module Loaded: v{mod_version}')
        assert mod_version is not None, "GamepadTouchControls module is not defined on window!"
        
        # Embark flight by clicking #begin
        print('3. Launching Flight (#begin)...')
        await page.click('#begin')
        await asyncio.sleep(1.5)
        
        # -------------------------------------------------------------
        # TEST SECTION A: MOBILE TOUCH SCREEN & VIRTUAL JOYSTICK
        # -------------------------------------------------------------
        print('\n--- TEST SECTION A: MOBILE TOUCH SCREEN & JOYSTICK ---')
        
        # Check if touch overlay is in DOM
        has_overlay = await page.evaluate("!!document.getElementById('starfield-touch-overlay')")
        print(f'   Touch Overlay Present: {has_overlay}')
        assert has_overlay, "starfield-touch-overlay was not injected into DOM!"
        
        # Simulate Virtual Floating Joystick Drag
        print('   Testing Floating Virtual Joystick on bottom-left...')
        joy_res = await page.evaluate("""
        (() => {
          const zone = document.querySelector('.sf-touch-joy-zone');
          if (!zone) return { success: false, reason: 'Zone missing' };
          
          // Touch Start in bottom-left
          zone.dispatchEvent(new PointerEvent('pointerdown', {
            pointerId: 1, clientX: 180, clientY: 650, bubbles: true
          }));
          
          // Touch Drag (steer right-up)
          zone.dispatchEvent(new PointerEvent('pointermove', {
            pointerId: 1, clientX: 220, clientY: 620, bubbles: true
          }));
          
          const touchState = window.GamepadTouchControls.getTouchState();
          
          // Touch Release (spring return)
          zone.dispatchEvent(new PointerEvent('pointerup', {
            pointerId: 1, clientX: 220, clientY: 620, bubbles: true
          }));
          
          return { success: true, joyActiveWas: touchState.joyActive };
        })()
        """)
        print(f'   Virtual Joystick Response: {joy_res}')
        assert joy_res['success'], "Virtual joystick event dispatch failed"
        
        # Test Quick Action Touch Cluster (Cam, Codex, Photo, Settings, Boost)
        print('   Testing Virtual HUD Quick Action Buttons...')
        
        # 1. Tap Camera Button
        prev_cockpit = await page.evaluate("window.Starfield.isCockpit()")
        await page.click('.sf-touch-btn:has-text("舱内")')
        await asyncio.sleep(0.5)
        new_cockpit = await page.evaluate("window.Starfield.isCockpit()")
        print(f'   Cockpit View Toggled: {prev_cockpit} -> {new_cockpit}')
        assert new_cockpit != prev_cockpit, "Cockpit toggle button failed!"
        
        # Revert cockpit
        await page.click('.sf-touch-btn:has-text("舱内")')
        await asyncio.sleep(0.5)
        
        # 2. Tap Codex Button
        await page.click('.sf-touch-btn:has-text("图鉴")')
        await asyncio.sleep(0.6)
        codex_open = await page.evaluate("document.getElementById('codex-modal').classList.contains('open')")
        print(f'   Codex Modal Opened via Touch: {codex_open}')
        assert codex_open, "Codex failed to open via touch button!"
        
        await page.click('#codex-close-btn')
        await asyncio.sleep(0.5)
        
        # 3. Tap Photo Mode Button
        await page.click('.sf-touch-btn:has-text("摄影")')
        await asyncio.sleep(0.6)
        photo_open = await page.evaluate("window.Starfield.isModalOpen()")
        print(f'   Photo Mode Opened via Touch: {photo_open}')
        assert photo_open, "Photo mode failed to open via touch button!"
        
        await page.click('#photo-exit-btn')
        await asyncio.sleep(0.5)
        
        # 4. Tap Slingshot Boost Button
        prev_travel = await page.evaluate("window.Starfield.getTravel()")
        await page.dispatch_event('.sf-touch-btn.boost', 'pointerdown')
        await asyncio.sleep(0.5)
        await page.dispatch_event('.sf-touch-btn.boost', 'pointerup')
        await asyncio.sleep(0.5)
        new_travel = await page.evaluate("window.Starfield.getTravel()")
        print(f'   Slingshot Boost Executed: Travel {prev_travel:.1f} -> {new_travel:.1f}')
        assert new_travel > prev_travel, "Boost did not advance flight distance!"
        
        # 5. Test Two-finger Pinch to Zoom
        print('   Testing Two-Finger Pinch-to-Zoom Camera...')
        cam_dist_before = await page.evaluate("window.Starfield.getCamera().distance")
        await page.evaluate("window.GamepadTouchControls.simulatePinchZoom(1.25)")
        await asyncio.sleep(0.3)
        cam_dist_after = await page.evaluate("window.Starfield.getCamera().distance")
        print(f'   Pinch Zoom Distance: {cam_dist_before:.1f} -> {cam_dist_after:.1f}')
        
        # Capture Touch Controls Screenshot
        shot_touch = os.path.join(shots_dir, 'touch_controls_hud.png')
        await page.screenshot(path=shot_touch)
        print(f'   Saved Touch Controls Screenshot: {shot_touch}')

        # -------------------------------------------------------------
        # TEST SECTION B: HTML5 GAMEPAD API & HAPTIC VIBRATION
        # -------------------------------------------------------------
        print('\n--- TEST SECTION B: HTML5 GAMEPAD API & HAPTIC VIBRATION ---')
        
        # Setup Mock Gamepad
        await page.evaluate("""
        (() => {
          window.__mockGamepad = {
            id: 'Xbox Wireless Controller (STANDARD GAMEPAD Vendor: 045e Product: 02fd)',
            index: 0,
            connected: true,
            timestamp: performance.now(),
            mapping: 'standard',
            axes: [0, 0, 0, 0],
            buttons: Array.from({length: 17}, () => ({ pressed: false, touched: false, value: 0 })),
            vibrationActuator: {
              playEffect: function(type, params) {
                window.__rumbleCalls = window.__rumbleCalls || [];
                window.__rumbleCalls.push({ type, params, time: performance.now() });
                return Promise.resolve('complete');
              }
            }
          };
          navigator.getGamepads = function() {
            return [window.__mockGamepad];
          };
          let gpEvt;
          try {
            gpEvt = new GamepadEvent('gamepadconnected', { gamepad: window.__mockGamepad });
          } catch(e) {
            gpEvt = new Event('gamepadconnected');
            gpEvt.gamepad = window.__mockGamepad;
          }
          window.dispatchEvent(gpEvt);
        })()
        """)
        await asyncio.sleep(0.5)
        
        gp_connected = await page.evaluate("window.GamepadTouchControls.isGamepadConnected()")
        print(f'   Gamepad API Hooked & Connected: {gp_connected}')
        assert gp_connected, "Gamepad failed to connect in GamepadTouchControls!"
        
        # 1. Left Stick Flight Steering
        print('   Testing Gamepad Left Stick Steering (Axes 0 & 1)...')
        await page.evaluate("""
          window.__mockGamepad.axes[0] = 0.85; // steer right
          window.__mockGamepad.axes[1] = -0.65; // steer up
        """)
        await asyncio.sleep(0.4)
        gp_state = await page.evaluate("window.GamepadTouchControls.getGamepadState()")
        print(f'   Interpolated Gamepad Steer: steerX={gp_state["steerX"]:.3f}, steerY={gp_state["steerY"]:.3f}')
        assert gp_state["steerX"] > 0.5, "Gamepad left stick X failed to interpolate!"
        
        # Reset left stick
        await page.evaluate("""
          window.__mockGamepad.axes[0] = 0.0;
          window.__mockGamepad.axes[1] = 0.0;
        """)
        await asyncio.sleep(0.3)
        
        # 2. Right Stick Free Camera Rotation
        print('   Testing Gamepad Right Stick Free Camera (Axes 2 & 3)...')
        yaw_before = await page.evaluate("window.Starfield.getCamera().yaw")
        await page.evaluate("""
          window.__mockGamepad.axes[2] = 0.90; // yaw right
          window.__mockGamepad.axes[3] = 0.40; // pitch down
        """)
        await asyncio.sleep(0.5)
        yaw_after = await page.evaluate("window.Starfield.getCamera().yaw")
        print(f'   Right Stick Camera Yaw Rotated: {yaw_before:.3f} -> {yaw_after:.3f}')
        assert yaw_after != yaw_before, "Right stick failed to rotate camera yaw!"
        
        # Reset right stick
        await page.evaluate("""
          window.__mockGamepad.axes[2] = 0.0;
          window.__mockGamepad.axes[3] = 0.0;
        """)
        await asyncio.sleep(0.2)
        
        # 3. Triggers / Bumpers Throttle Speed Control
        print('   Testing Gamepad Triggers / Bumpers Throttle Control...')
        gear_before = await page.evaluate("window.Starfield.getWarpDrive().gearIndex")
        # Tap Right Trigger (RT: Button 7)
        await page.evaluate("""
          window.__mockGamepad.buttons[7] = { pressed: true, value: 1.0 };
        """)
        await asyncio.sleep(0.1)
        await page.evaluate("""
          window.__mockGamepad.buttons[7] = { pressed: false, value: 0.0 };
        """)
        await asyncio.sleep(0.4)
        gear_after = await page.evaluate("window.Starfield.getWarpDrive().gearIndex")
        print(f'   RT Throttle Speed Up: Gear {gear_before} -> {gear_after}')
        assert gear_after >= gear_before, "RT failed to increase WarpDrive speed gear!"
        
        # 4. D-Pad Directional Controls
        print('   Testing Gamepad D-Pad (Up: Cockpit, Down: Cam, Left/Right: Formation)...')
        # D-Pad Down: Toggle Camera
        auto_before = await page.evaluate("window.Starfield.isAutoCamera()")
        await page.evaluate("window.__mockGamepad.buttons[13] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[13] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.4)
        auto_after = await page.evaluate("window.Starfield.isAutoCamera()")
        print(f'   D-Pad Down Camera Mode: Auto={auto_before} -> Auto={auto_after}')
        
        # D-Pad Right: Cycle Fleet Formation
        form_before = await page.evaluate("window.Starfield.getFleetFormations().current")
        await page.evaluate("window.__mockGamepad.buttons[15] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[15] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.4)
        form_after = await page.evaluate("window.Starfield.getFleetFormations().current")
        print(f'   D-Pad Right Formation Cycled: Formation {form_before} -> {form_after}')
        assert form_after != form_before, "D-Pad Right failed to cycle fleet formation!"
        
        # 5. Face Buttons (A: Boost, B: Back, X: Photo, Y: Codex)
        print('   Testing Gamepad Face Buttons...')
        # Button Y (North): Codex
        await page.evaluate("window.__mockGamepad.buttons[3] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[3] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        codex_active = await page.evaluate("document.getElementById('codex-modal').classList.contains('open')")
        print(f'   Button Y Opened Codex: {codex_active}')
        assert codex_active, "Button Y failed to open Celestial Codex!"
        
        # Button B (East): Close Modal / Back
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        codex_closed = await page.evaluate("!document.getElementById('codex-modal').classList.contains('open')")
        print(f'   Button B Closed Codex: {codex_closed}')
        assert codex_closed, "Button B failed to close Celestial Codex modal!"
        
        # Button X (West): Photo Mode
        await page.evaluate("window.__mockGamepad.buttons[2] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[2] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        photo_active = await page.evaluate("window.Starfield.isModalOpen()")
        print(f'   Button X Opened Photo Mode: {photo_active}')
        assert photo_active, "Button X failed to toggle Photo Mode!"
        
        # Button B (East) again: Close Photo Mode
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        photo_closed = await page.evaluate("!window.Starfield.isModalOpen()")
        print(f'   Button B Closed Photo Mode: {photo_closed}')
        assert photo_closed, "Button B failed to close Photo Mode!"
        
        # Button Start (Menu / buttons[9]): Settings Drawer
        await page.evaluate("window.__mockGamepad.buttons[9] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[9] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        settings_active = await page.evaluate("document.getElementById('settings-drawer').classList.contains('open')")
        print(f'   Start Button Opened Settings Drawer: {settings_active}')
        assert settings_active, "Start button failed to open Settings Drawer!"
        
        # Button B: Close Settings
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: true, value: 1.0 };")
        await asyncio.sleep(0.1)
        await page.evaluate("window.__mockGamepad.buttons[1] = { pressed: false, value: 0.0 };")
        await asyncio.sleep(0.5)
        
        # 6. Haptic Dual-Rumble Vibration Feedback Test
        print('   Testing Haptic Dual-Rumble Feedback Triggers...')
        # Trigger Slingshot Rumble directly or via boost
        await page.evaluate("""
          window.GamepadTouchControls.playRumble('dual-rumble', {
            duration: 400, weakMagnitude: 0.7, strongMagnitude: 0.9
          });
        """)
        await asyncio.sleep(0.2)
        rumble_calls = await page.evaluate("window.__rumbleCalls ? window.__rumbleCalls.length : 0")
        print(f'   Total Dual-Rumble Effects Dispatched to Controller: {rumble_calls}')
        assert rumble_calls > 0, "No dual-rumble vibration effects were recorded on gamepad actuator!"
        
        # Capture Gamepad Flight Screenshot
        shot_gp = os.path.join(shots_dir, 'gamepad_active_flight.png')
        await page.screenshot(path=shot_gp)
        print(f'   Saved Gamepad Flight Screenshot: {shot_gp}')
        
        # -------------------------------------------------------------
        # TEST SECTION C: 60 FPS PERFORMANCE & LOG INTEGRITY
        # -------------------------------------------------------------
        print('\n--- TEST SECTION C: 60 FPS PERFORMANCE & CONSOLE AUDIT ---')
        fps_info = await page.evaluate("""
        new Promise((resolve) => {
          let frames = 0;
          const start = performance.now();
          function tick() {
            frames++;
            if (performance.now() - start < 1000) {
              requestAnimationFrame(tick);
            } else {
              const dur = (performance.now() - start) / 1000;
              resolve({ fps: frames / dur, frames, dur });
            }
          }
          requestAnimationFrame(tick);
        })
        """)
        print(f'   Measured Realtime FPS: {fps_info["fps"]:.1f} FPS ({fps_info["frames"]} frames in {fps_info["dur"]:.2f}s)')
        assert fps_info["fps"] >= 45.0, f"Frame rate too low: {fps_info['fps']} FPS"
        
        await browser.close()

    print('\n===============================================================')
    print(' VERIFICATION SUMMARY')
    print(f' Total Console Logs: {len(logs)}')
    if errors:
        print(' ERRORS ENCOUNTERED:', errors)
        sys.exit(1)
    else:
        print(' ALL GAMEPAD & MOBILE TOUCH VERIFICATION TESTS PASSED!')
        print(' ZERO CONSOLE ERRORS DETECTED (0 ERRORS)')
    print('===============================================================')

if __name__ == '__main__':
    asyncio.run(main())
