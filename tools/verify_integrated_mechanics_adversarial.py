# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_URL = (BASE_DIR / 'starfield.html').as_uri()

async def main():
    print(f"Testing Starfield URL: {HTML_URL}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto(HTML_URL)
        await page.wait_for_timeout(1000)

        # ---------------------------------------------------------------------
        # 1. Test Evacuation Gate Non-Duplication & Singularity Implosion
        # ---------------------------------------------------------------------
        print("\n--- 1. Testing Evacuation Gate Non-Duplication & Consumption ---")
        evac_res = await page.evaluate('''() => {
            const Ext = window.StarfieldInFlightExtraction;
            Ext.init();
            // Fill cargo with 2 high value items
            Ext.cargo = [
                { name: '反物质湮灭核心', icon: '⚛️', value: 880, tier: 'legendary' },
                { name: '暗物质折跃燃料', icon: '🌌', value: 620, tier: 'epic' }
            ];
            const lead = craftWorld(fleet[LEAD]);
            // Place evac gate right next to lead ship
            Ext.evacGate = {
                x: lead[0], y: lead[1], z: lead[2] + 200,
                radius: 1200, progress: 0.98, evacuated: false, imploding: 0
            };
            const creditsBefore = Ext.securedCredits;
            const coresBefore = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function') ? window.StarfieldHatch.getUnopenedCores() : 0;

            // Step 1: Trigger evacuation
            Ext.update(0.05); // Progress fills to 1.0, triggers evacuation
            const creditsAfter1 = Ext.securedCredits;
            const coresAfter1 = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function') ? window.StarfieldHatch.getUnopenedCores() : 0;
            const cargoAfter1 = Ext.cargo.length;
            const isEvacuated = Ext.evacGate ? Ext.evacGate.evacuated : true;
            const isImploding = Ext.evacGate ? Ext.evacGate.imploding > 0 : false;

            // Step 2: Step simulation multiple frames while still inside gate proximity
            for (let f = 0; f < 30; f++) {
                Ext.update(0.05);
            }
            const creditsAfter2 = Ext.securedCredits;
            const coresAfter2 = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function') ? window.StarfieldHatch.getUnopenedCores() : 0;

            return {
                creditsGained: creditsAfter1 - creditsBefore,
                coresGained: coresAfter1 - coresBefore,
                cargoAfter1,
                isEvacuated,
                isImploding,
                noDuplicateCredits: creditsAfter2 === creditsAfter1,
                noDuplicateCores: coresAfter2 === coresAfter1
            };
        }''')
        print("Evacuation test result:", evac_res)
        assert evac_res['creditsGained'] == 2100, f"Expected 880 + 620 + 600 bonus = 2100, got {evac_res['creditsGained']}"
        assert evac_res['coresGained'] >= 1, "Expected star cores awarded on evacuation"
        assert evac_res['cargoAfter1'] == 0, "Cargo bay should be cleared upon evacuation"
        assert evac_res['isEvacuated'], "Gate should be marked evacuated"
        assert evac_res['noDuplicateCredits'], "Gate must NOT duplicate credit rewards upon staying in proximity!"
        assert evac_res['noDuplicateCores'], "Gate must NOT duplicate star cores!"
        print("[PASS] Evacuation gate consumption & non-duplication verified successfully!")

        # ---------------------------------------------------------------------
        # 2. Test Real Planet Slingshot with canonical .r Radius
        # ---------------------------------------------------------------------
        print("\n--- 2. Testing Real Planet Slingshot (using .r property) ---")
        sling_res = await page.evaluate('''() => {
            const Sling = window.StarfieldOrbitalMechanics;
            Sling.init();
            const lead = craftWorld(fleet[LEAD]);
            // Place celestial mass with canon .r property (NO .rad!)
            window.activeMasses = [{
                x: lead[0] + 500,
                y: lead[1] + 200,
                z: lead[2] + 2200,
                r: 2800, // Large gas/terrestrial world
                name: '开普勒-22b',
                kind: 1
            }];
            Sling.slingshotCooldown = 0;
            Sling.update(0.016);

            const hasActivePlanet = !!Sling.activePlanet;
            const arcSteps = Sling.slingshotArc.length;
            const periIdx = Sling.slingshotPeriapsisIdx;
            
            // Advance past periapsis to trigger natural slingshot
            Sling.lastMinDist = 2800 * 2.5;
            Sling.update(0.016);

            return {
                hasActivePlanet,
                arcSteps,
                periIdx,
                hasGlow: Sling.slingshotGlowTimer > 0,
                cooldownActive: Sling.slingshotCooldown > 0
            };
        }''')
        print("Planet slingshot result:", sling_res)
        assert sling_res['hasActivePlanet'], "Planet should be detected via .r radius"
        assert sling_res['arcSteps'] == 36, "Trajectory arc should have 36 steps"
        assert sling_res['hasGlow'], "Slingshot relativistic glow should be triggered"
        assert sling_res['cooldownActive'], "Slingshot cooldown should be active"
        print("[PASS] Canonical .r planetary gravitational slingshot verified successfully!")

        # ---------------------------------------------------------------------
        # 3. Test Deep Space Probe Launch without initial planet target
        # ---------------------------------------------------------------------
        print("\n--- 3. Testing Deep Space Probe Telemetry & Chain Shockwaves ---")
        probe_res = await page.evaluate('''() => {
            const Sling = window.StarfieldOrbitalMechanics;
            Sling.activePlanet = null;
            window.activeMasses = [];
            Sling.probes.length = 0;
            Sling.shockwaves.length = 0;
            const coresBefore = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function') ? window.StarfieldHatch.getUnopenedCores() : 0;

            // Launch deep space probe
            Sling.launchProbe();
            const probeLaunched = Sling.probes.length === 1;

            // Simulate probe flight to expiration
            const pr = Sling.probes[0];
            pr.life = 0.01;
            Sling.update(0.05); // Expiration triggers deep-space shockwave

            const shockwavesCount = Sling.shockwaves.length;
            const coresAfter = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function') ? window.StarfieldHatch.getUnopenedCores() : 0;

            return {
                probeLaunched,
                shockwavesCount,
                coresGained: coresAfter - coresBefore
            };
        }''')
        print("Deep space probe result:", probe_res)
        assert probe_res['probeLaunched'], "Probe should be launched"
        assert probe_res['shockwavesCount'] > 0, "Deep space expiration should trigger chain shockwave"
        assert probe_res['coresGained'] >= 1, "Deep space core detection should award celestial core"
        print("[PASS] Deep space probe telemetry & shockwave resonance verified successfully!")

        # ---------------------------------------------------------------------
        # 3b. Test Active Deep Space Sonar with Injected Bodies & Gargantua
        # ---------------------------------------------------------------------
        print("\n--- 3b. Testing Deep Space Sonar (window.activeMasses & Gargantua) ---")
        sonar_res = await page.evaluate('''() => {
            const Sonar = window.StarfieldSonar;
            Sonar.init();
            const lead = craftWorld(fleet[LEAD]);

            // 1. Injected terrestrial planet
            window.activeMasses = [{
                x: lead[0] + 400,
                y: lead[1],
                z: lead[2] + 2500,
                r: 1200,
                name: '开普勒-452b',
                kind: 1
            }];
            Sonar.update(0.016);
            const planetTargetName = Sonar.currentTarget ? Sonar.currentTarget.name : null;

            // Trigger sonar scan
            Sonar.activeSonarRings.length = 0;
            Sonar.triggerScan();
            const sonarRingsCount = Sonar.activeSonarRings.length;

            // 2. Injected supermassive black hole (kind 4)
            window.activeMasses = [{
                x: lead[0] - 600,
                y: lead[1] + 100,
                z: lead[2] + 4000,
                r: 3500,
                name: '卡冈图雅奇点',
                kind: 4
            }];
            Sonar.update(0.016);
            const blackHoleTargetName = Sonar.currentTarget ? Sonar.currentTarget.name : null;

            // Reset activeMasses
            window.activeMasses = [];

            return {
                planetTargetName,
                sonarRingsCount,
                blackHoleTargetName
            };
        }''')
        print("Sonar test result:", sonar_res)
        assert sonar_res['planetTargetName'] == '开普勒-452b', f"Expected 开普勒-452b, got {sonar_res['planetTargetName']}"
        assert sonar_res['sonarRingsCount'] >= 1, "Sonar scan should generate active sonar pulse ring"
        assert sonar_res['blackHoleTargetName'] == '卡冈图雅奇点', f"Expected 卡冈图雅奇点, got {sonar_res['blackHoleTargetName']}"
        print("[PASS] Active deep space sonar target lock-on & Gargantua mapping verified successfully!")

        # ---------------------------------------------------------------------
        # 4. Test Dogfight Combat Visuals (Lasers & Bursts)
        # ---------------------------------------------------------------------
        print("\n--- 4. Testing Dogfight Combat Visuals (Lasers & Bursts) ---")
        dogfight_res = await page.evaluate('''() => {
            const Ext = window.StarfieldInFlightExtraction;
            const lead = craftWorld(fleet[LEAD]);
            Ext.spawnPiratePatrol(lead, 2);
            
            // Advance dogfight
            Ext.pirates.forEach(p => p.fireCd = 0);
            Ext.escortLaserTimer = 0;
            Ext.update(0.016);

            const lasersCount = Ext.lasers.length;
            const hasShieldFlare = Ext.fleetShieldFlare > 0;

            // Kill one pirate to test burst
            Ext.pirates[0].hp = 0;
            Ext.update(0.016);
            const burstsCount = Ext.bursts.length;
            const sparksCount = Ext.sparks.length;

            return {
                lasersCount,
                hasShieldFlare,
                burstsCount,
                sparksCount
            };
        }''')
        print("Dogfight result:", dogfight_res)
        assert dogfight_res['lasersCount'] >= 1, "Dogfight lasers should be actively generated"
        assert dogfight_res['hasShieldFlare'], "Flagship energy shield should flare on pirate fire"
        assert dogfight_res['burstsCount'] >= 1, "Explosion burst should be generated on pirate destruction"
        assert dogfight_res['sparksCount'] >= 1, "Sparks should be generated on pirate destruction"
        print("[PASS] Dogfight combat lasers, shield flares, and bursts verified successfully!")

        # ---------------------------------------------------------------------
        # 5. Final Console Errors Audit
        # ---------------------------------------------------------------------
        print("\n--- 5. Console Error Audit ---")
        print("Total Errors:", len(errors))
        if errors:
            print("Errors logged:", errors)
        assert len(errors) == 0, f"Expected 0 console errors, got {len(errors)}"
        print("\n🏆 ALL INTEGRATED MECHANICS ADVERSARIAL TESTS PASSED 100% WITH 0 CONSOLE ERRORS!")

if __name__ == '__main__':
    asyncio.run(main())
