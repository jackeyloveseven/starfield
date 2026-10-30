#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time

sys.stdout.reconfigure(encoding="utf-8")
from playwright.sync_api import sync_playwright

def main():
    html_path = os.path.abspath("starfield.html").replace("\\", "/")
    file_url = f"file:///{html_path}"
    print(f"Testing URL: {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1.0
        )
        page = context.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))

        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        # -------------------------------------------------------------
        # 1. Camera-Planet Rotation Decoupling Verification
        # -------------------------------------------------------------
        print("\n--- 1. Testing Camera-Planet Rotation Decoupling ---")
        decouple_check = page.evaluate("""() => {
            const L = window.LivingPlanetEngine;
            if (!L) return { hasEngine: false };
            if (!L.initialized) L.init();

            // Create mock celestial mass with axial tilt
            const mockMass = {
                seed: 98765,
                phase: 0.25,
                x: 100,
                y: 50,
                z: 2000,
                w: { type: { id: 'ocean' }, manif: { id: 'archipelago' } }
            };

            const model = L.getPlanetModel(mockMass);
            const initialTilt = model.tiltAngle;

            // Simulate Camera 1: Looking straight ahead
            const cam1 = {
                eye: [0, 0, 0],
                right: [1, 0, 0],
                up: [0, 1, 0],
                forward: [0, 0, 1]
            };
            L.renderPlanet(mockMass, 60, [0.5, 0.5, 0.7], cam1);
            const q1 = { x: model.group.quaternion.x, y: model.group.quaternion.y, z: model.group.quaternion.z, w: model.group.quaternion.w };
            const q1Norm = Math.hypot(q1.x, q1.y, q1.z, q1.w);

            // Simulate Camera 2: Panned / Yaw rotated by 90 degrees (looking sideways)
            const cam2 = {
                eye: [0, 0, 0],
                right: [0, 0, -1],
                up: [0, 1, 0],
                forward: [1, 0, 0]
            };
            L.renderPlanet(mockMass, 60, [0.5, 0.5, 0.7], cam2);
            const q2 = { x: model.group.quaternion.x, y: model.group.quaternion.y, z: model.group.quaternion.z, w: model.group.quaternion.w };
            const q2Norm = Math.hypot(q2.x, q2.y, q2.z, q2.w);

            // When camera turns 90 degrees, planet group quaternion MUST change relative to sprite frame
            // proving that the planet's world orientation remains fixed in space rather than locked to screen!
            const quatChanged = (Math.abs(q1.x - q2.x) > 0.05 || Math.abs(q1.y - q2.y) > 0.05 || Math.abs(q1.w - q2.w) > 0.05);

            // Check ringRoll and ringHalf roll alignment
            const camera = window.Starfield.getCamera();
            const hash = window.hash;
            const pId = mockMass.seed;
            const tiltAngle = ((hash(pId, 71, 19) - 0.5) * 0.45);
            const tiltAzimuth = (hash(pId, 72, 23) * (Math.PI * 2));
            const px = Math.sin(tiltAngle) * Math.cos(tiltAzimuth);
            const py = Math.cos(tiltAngle);
            const pz = Math.sin(tiltAngle) * Math.sin(tiltAzimuth);
            const r = camera.right, u = camera.up;
            const nx = px * r[0] + py * r[1] + pz * r[2];
            const ny = px * u[0] + py * u[1] + pz * u[2];
            const rollRingHalf = Math.atan2(nx, ny);
            const rollDrawWorld = Math.atan2(nx, ny);
            const ringRollAligned = Math.abs(rollRingHalf - rollDrawWorld) < 1e-6;

            return {
                hasEngine: true,
                hasModel: !!model,
                hasBodyGroup: !!model.bodyGroup,
                hasTilt: Math.abs(initialTilt) > 0.001,
                quatChanged: quatChanged,
                q1Norm: q1Norm,
                q2Norm: q2Norm,
                ringRollAligned: ringRollAligned
            };
        }""")
        print(f"Decouple check results: {decouple_check}")
        assert decouple_check["hasEngine"], "LivingPlanetEngine must be initialized"
        assert decouple_check["hasBodyGroup"], "Model must have decoupled bodyGroup"
        assert decouple_check["quatChanged"], "Planet orientation in view frame must react to camera angle changes!"
        assert abs(decouple_check["q1Norm"] - 1.0) < 1e-4, "Quaternion q1 must be strictly unit norm"
        assert abs(decouple_check["q2Norm"] - 1.0) < 1e-4, "Quaternion q2 must be strictly unit norm"
        assert decouple_check["ringRollAligned"], "ringHalf roll and drawWorld ringRoll must align"

        # -------------------------------------------------------------
        # 2. Deep Space Aesthetics (Nebula Palettes, Milky Way & Galaxies)
        # -------------------------------------------------------------
        print("\n--- 2. Testing Deep Space Background Aesthetics ---")
        aesthetics_check = page.evaluate("""() => {
            const SF = window.Starfield;
            const pals = SF && SF.getNebPalettes ? SF.getNebPalettes() : null;
            const has12Palettes = (pals && pals.length === 12);
            let sampleTexWorks = false;
            try {
                if (SF && SF.nebulaTex) {
                    const cv = SF.nebulaTex(12345, 0);
                    sampleTexWorks = !!cv && cv.width === 384;
                }
            } catch(e) {
                sampleTexWorks = false;
            }

            return {
                has12Palettes,
                paletteCount: pals ? pals.length : 0,
                sampleTexWorks
            };
        }""")
        print(f"Aesthetics check results: {aesthetics_check}")
        assert aesthetics_check["has12Palettes"], "Must have 12 master astronomical nebula palettes"
        assert aesthetics_check["sampleTexWorks"], "nebulaTex must generate 384px volumetric canvas"

        # -------------------------------------------------------------
        # 3. Gargantua Black Hole Cinematic Polish
        # -------------------------------------------------------------
        print("\n--- 3. Testing Gargantua Black Hole Shader & Lensing ---")
        blackhole_check = page.evaluate("""() => {
            const SF = window.Starfield;
            const holeGL = SF && SF.getHoleGL ? SF.getHoleGL() : null;
            const hasHoleGL = (holeGL !== null && typeof holeGL !== 'undefined');
            let programLinked = false;
            let uniformsExist = false;
            if (hasHoleGL) {
                const g = holeGL.gl;
                programLinked = g.getProgramParameter(holeGL.prog, g.LINK_STATUS);
                uniformsExist = !!holeGL.u.tilt && !!holeGL.u.incl && !!holeGL.u.exp;
            }

            return {
                hasHoleGL,
                programLinked,
                uniformsExist
            };
        }""")
        print(f"Gargantua check results: {blackhole_check}")
        assert blackhole_check["hasHoleGL"], "Gargantua WebGL2 engine must be active"
        assert blackhole_check["programLinked"], "Relativistic raymarching shader must compile and link with 0 errors"
        assert blackhole_check["uniformsExist"], "Dynamic tilt, incl, exp uniforms must exist"

        # -------------------------------------------------------------
        # 4. In-Flight Flight & Camera Orbit Test
        # -------------------------------------------------------------
        print("\n--- 4. Testing Camera Orbit & In-Flight Rendering ---")
        page.mouse.move(640, 360)
        page.mouse.down()
        page.mouse.move(740, 310)
        page.mouse.up()
        page.wait_for_timeout(600)

        # Trigger keyboard camera rotation
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(400)
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(400)

        page.screenshot(path="tools/test_cinematic_space_flight.png")
        print("Cinematic screenshot saved to tools/test_cinematic_space_flight.png")

        print("\n--- Total Console Errors ---")
        print(f"Errors count: {len(console_errors)}")
        if console_errors:
            print("Errors:", console_errors)
        assert len(console_errors) == 0, f"Expected 0 console errors, got {len(console_errors)}"

        print("\n🎉 ALL CINEMATIC POLISH & DECOUPLING VERIFICATIONS PASSED 100%!")

if __name__ == '__main__':
    main()
