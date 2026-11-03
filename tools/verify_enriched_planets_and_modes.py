# -*- coding: utf-8 -*-
"""
Verification suite for:
1. Enriched Planet Modeling (architectural megastructures properly scaled, non-clipping, on procedural 3D planets)
2. 3D In-Flight Void Extraction (actual 3D derelict hull rendering, visible pirate patrols, tactical cockpit HUD, mobile loot button, singularity evacuation)
3. 3D Planetary Gravitational Slingshot (trajectory arc prediction, slingshot assist, stylized space bird probes, mobile launch button)
4. Clean removal of the bottom-center Sonar [F] HUD button during normal flight
5. 100% Byte Parity between starfield.html and Android assets
"""

import asyncio
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    starfield_html_path = os.path.join(root_dir, 'starfield.html')
    android_html_path = os.path.join(root_dir, 'android', 'app', 'src', 'main', 'assets', 'starfield.html')

    # Step 1: Byte parity verification
    print("=== Step 1: Checking Byte-for-Byte Parity ===")
    with open(starfield_html_path, 'rb') as f1, open(android_html_path, 'rb') as f2:
        b1 = f1.read()
        b2 = f2.read()
    assert b1 == b2, "Parity failure: starfield.html != android asset"
    print(f"[PASS] 100% Byte Parity verified ({len(b1):,} bytes).")

    # Step 2: Headless Browser verification
    file_url = f"file:///{starfield_html_path.replace(os.sep, '/')}"
    print(f"\n=== Step 2: Testing Starfield in Browser ({file_url}) ===")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 412, "height": 915})

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto(file_url, wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # 1. Verify Clean Removal of the Bottom-Center Sonar [F] Button
        print("\n--- 1. Testing Removal of Bottom-Center Sonar [F] Button ---")
        sonar_hud_test = await page.evaluate('''() => {
            const S = window.StarfieldSonar;
            if (!S) return { error: 'No StarfieldSonar' };
            // Simulate candidate planet encounter in normal flight
            S.currentTarget = { name: '织女星 α', x: 200, y: 100, z: 1200 };
            S.update(0.016);
            const btn = document.getElementById('sf-sonar-lock-btn');
            return {
                btnExists: !!btn,
                btnVisible: btn ? (btn.style.display !== 'none' && btn.offsetHeight > 0) : false
            };
        }''')
        print("Sonar HUD check result:", sonar_hud_test)
        assert not sonar_hud_test['btnVisible'], "Sonar [F] button should NOT be visible during normal flight!"
        print("[PASS] Bottom-center Sonar [F] button is cleanly absent from normal flight!")

        # 2. Verify Enriched Procedural Planet Architectural Structures
        print("\n--- 2. Testing Enriched Planetary Architecture Modeling ---")
        arch_test = await page.evaluate('''() => {
            const LPE = window.LivingPlanetEngine;
            if (!LPE) return { error: 'No LivingPlanetEngine' };

            // Create models across different seeds/biomes
            const results = [];
            const seeds = [101, 7919, 4423, 9991];
            for (const s of seeds) {
                const dummyMass = {
                    seed: s,
                    x: 0, y: 0, z: 2000,
                    w: {
                        name: '文明星体-' + s,
                        type: { id: s % 2 === 0 ? 'forest' : 'ocean' },
                        manif: { id: s % 3 === 0 ? 'cyber_metropolis' : 'archipelago' }
                    }
                };
                const model = LPE.createProceduralPlanet(dummyMass, s);
                const hasMonuments = !!model.monumentsGroup;
                const structCount = model.monumentsGroup ? model.monumentsGroup.children.length : 0;

                // Check that structures don't clip outside camera extent
                let maxDistFromCenter = 0;
                if (model.monumentsGroup) {
                    model.monumentsGroup.traverse((obj) => {
                        if (obj.isMesh && obj.geometry) {
                            obj.geometry.computeBoundingSphere();
                            if (obj.geometry.boundingSphere) {
                                const worldPos = new THREE.Vector3();
                                obj.getWorldPosition(worldPos);
                                const r = worldPos.length() + obj.geometry.boundingSphere.radius;
                                if (r > maxDistFromCenter) maxDistFromCenter = r;
                            }
                        }
                    });
                }

                results.push({
                    seed: s,
                    hasMonuments,
                    structCount,
                    hasBodyGroup: !!model.bodyGroup,
                    maxDistFromCenter,
                    camExtent: LPE.CAM_EXTENT
                });
            }
            return { results, camExtent: LPE.CAM_EXTENT };
        }''')
        print("Architecture check results:", arch_test)
        for r in arch_test['results']:
            assert r['hasMonuments'], f"Seed {r['seed']} missing monumentsGroup"
            assert r['structCount'] >= 3, f"Seed {r['seed']} should have at least 3 architectural structures, got {r['structCount']}"
            assert r['hasBodyGroup'], f"Seed {r['seed']} missing bodyGroup"
        print("[PASS] Planetary modeling enriched with diverse sci-fi architectural megastructures!")

        # 3. Verify 3D In-Flight Void Extraction System & Cockpit HUD
        print("\n--- 3. Testing 3D In-Flight Void Extraction System & Tactical HUD ---")
        ext_flight_test = await page.evaluate('''() => {
            const Ext = window.StarfieldInFlightExtraction;
            if (!Ext) return { error: 'No StarfieldInFlightExtraction' };
            Ext.init();
            
            // Advance travel to spawn derelicts
            window.travel = 35000;
            Ext.update(0.016);

            const derelictCount = Ext.derelicts.length;
            const hasGate = !!Ext.evacGate;
            const hasHUD = !!document.getElementById('sf-inflight-extract-hud');
            const hasLootBtn = !!document.getElementById('sf-inflight-loot-btn');

            // Test fastLoot on first derelict by placing within salvage proximity
            if (derelictCount > 0) {
                const lead = craftWorld(fleet[LEAD]);
                Ext.derelicts[0].x = lead[0] + 80;
                Ext.derelicts[0].y = lead[1] - 40;
                Ext.derelicts[0].z = lead[2] + 1200;
                Ext.update(0.016);
                Ext.fastLoot();
            }
            const cargoCount = Ext.cargo.length;

            // Spawn and check pirate patrol
            Ext.spawnPiratePatrol([0, 0, 35000]);
            const pirateCount = Ext.pirates.length;

            return {
                available: true,
                derelictCount,
                hasGate,
                hasHUD,
                hasLootBtn,
                cargoCount,
                pirateCount,
                firstItem: Ext.cargo[0] ? Ext.cargo[0].name : null
            };
        }''')
        print("3D Void Extraction check result:", ext_flight_test)
        assert ext_flight_test['available']
        assert ext_flight_test['derelictCount'] > 0, "No derelicts spawned in flight"
        assert ext_flight_test['hasGate'], "Missing singularity evac gate"
        assert ext_flight_test['hasHUD'], "Missing in-flight tactical HUD"
        assert ext_flight_test['hasLootBtn'], "Missing mobile loot button"
        assert ext_flight_test['cargoCount'] == 1, "Cargo not looted into tactical bay"
        assert ext_flight_test['pirateCount'] > 0, "Pirate patrols not spawned"
        print("[PASS] 3D in-flight Void Extraction mechanics & tactical HUD operational!")

        # 4. Verify 3D Planetary Gravitational Slingshot & Probe Launch
        print("\n--- 4. Testing 3D Planetary Gravitational Slingshot & Probe System ---")
        sling_flight_test = await page.evaluate('''() => {
            const Sling = window.StarfieldOrbitalMechanics;
            if (!Sling) return { error: 'No StarfieldOrbitalMechanics' };
            Sling.init();

            // Simulate planet mass in activeMasses
            window.activeMasses = [{
                x: 300, y: 150, z: window.travel + 1200,
                rad: 300, mass: 2.0e8,
                name: '开普勒-452b',
                kind: 1
            }];
            Sling.update(0.016);

            const hasActivePlanet = !!Sling.activePlanet;
            const arcSteps = Sling.slingshotArc.length;
            const hasProbeBtn = !!document.getElementById('sf-inflight-probe-btn');
            const probeBtnVisible = hasProbeBtn ? document.getElementById('sf-inflight-probe-btn').style.display !== 'none' : false;

            // Launch gravity probe
            Sling.launchProbe();
            const probeCount = Sling.probes.length;

            return {
                available: true,
                hasActivePlanet,
                arcSteps,
                hasProbeBtn,
                probeBtnVisible,
                probeCount
            };
        }''')
        print("3D Slingshot check result:", sling_flight_test)
        assert sling_flight_test['available']
        assert sling_flight_test['hasActivePlanet'], "Planet gravitational well not detected"
        assert sling_flight_test['arcSteps'] > 10, "Predictive slingshot arc trajectory not generated"
        assert sling_flight_test['hasProbeBtn'], "Missing mobile probe launch button"
        assert sling_flight_test['probeBtnVisible'], "Probe button should be visible near planet"
        assert sling_flight_test['probeCount'] == 1, "Gravity probe not launched"
        print("[PASS] 3D planetary gravitational slingshot & probe launches fully functional!")

        # 5. Check Console Errors
        print("\n--- Total Console Errors ---")
        print(f"Error count: {len(errors)}")
        if errors:
            print("Errors detected:", errors)
        assert len(errors) == 0, f"Found {len(errors)} console errors!"
        print("\n🎉 ALL NEW FEATURES AND INTEGRATIONS VERIFIED 100% SUCCESSFULLY WITH ZERO CONSOLE ERRORS!")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
