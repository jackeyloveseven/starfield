# -*- coding: utf-8 -*-
"""
Automated Playwright verification test for:
1. Red Alert RTS (Command & Conquer Space Command)
2. Dyson Sphere Program (Megastructure & Interstellar Logistics)
"""

import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    print("Testing URL: file:///D:/items/code/starfield-pub/starfield.html")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        # Mobile viewport iPhone 14 style
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto("file:///D:/items/code/starfield-pub/starfield.html")
        await page.wait_for_timeout(1200)

        # 1. Check Mode Bar for all 5 modes
        print("\n--- 1. Checking 5 Expansion Mode Bar Tabs ---")
        mode_bar_info = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const btnCruise = document.getElementById('sf-btn-mode-cruise');
            const btnExt = document.getElementById('sf-btn-mode-extract');
            const btnSling = document.getElementById('sf-btn-mode-slingshot');
            const btnRA = document.getElementById('sf-btn-mode-redalert');
            const btnDSP = document.getElementById('sf-btn-mode-dyson');
            return {
                hasBar: !!bar,
                hasBtnCruise: !!btnCruise,
                hasBtnExt: !!btnExt,
                hasBtnSling: !!btnSling,
                hasBtnRA: !!btnRA,
                hasBtnDSP: !!btnDSP,
                cruiseActive: btnCruise ? btnCruise.classList.contains('active') : false
            };
        }''')
        print("Mode bar check:", mode_bar_info)
        assert mode_bar_info['hasBar']
        assert mode_bar_info['hasBtnCruise']
        assert mode_bar_info['hasBtnExt']
        assert mode_bar_info['hasBtnSling']
        assert mode_bar_info['hasBtnRA']
        assert mode_bar_info['hasBtnDSP']
        assert mode_bar_info['cruiseActive']

        # 2. Test Red Alert RTS Mode
        print("\n--- 2. Testing Red Alert RTS Mode (Command & Conquer Base) ---")
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(600)

        ra_init_state = await page.evaluate('''() => {
            const overlay = document.getElementById('sf-redalert-overlay');
            const game = window.RedAlertRTS;
            return {
                overlayActive: overlay ? overlay.classList.contains('active') : false,
                gameActive: game ? game.active : false,
                credits: game ? game.credits : 0,
                powerGen: game ? game.powerGen : 0,
                powerReq: game ? game.powerReq : 0,
                isLowPower: game ? game.isLowPower : true,
                buildingsCount: game ? game.buildings.length : 0,
                harvestersCount: game ? game.harvesters.length : 0,
                oreFieldsCount: game ? game.oreFields.length : 0,
                unitsCount: game ? game.units.length : 0,
                enemiesCount: game ? game.enemies.length : 0
            };
        }''')
        print("Red Alert initial state:", ra_init_state)
        assert ra_init_state['overlayActive'] and ra_init_state['gameActive']
        assert ra_init_state['credits'] >= 3000
        assert ra_init_state['powerGen'] >= 160
        assert ra_init_state['buildingsCount'] >= 3
        assert ra_init_state['harvestersCount'] >= 1
        assert ra_init_state['oreFieldsCount'] >= 3

        # Test Building Construction (Tesla Coil, Prism Beacon, Shipyard, Ion Uplink)
        print("\nTesting Base Building (Tesla, Prism, Shipyard, Ion Uplink)...")
        build_result = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            game.credits = 10000;
            game.buildBuilding('tesla', 600);
            game.buildBuilding('prism', 750);
            game.buildBuilding('shipyard', 1000);
            game.buildBuilding('ion', 1500);
            return {
                buildingsCount: game.buildings.length,
                hasTesla: game.buildings.some(b => b.type === 'tesla'),
                hasPrism: game.buildings.some(b => b.type === 'prism'),
                hasShipyard: game.buildings.some(b => b.type === 'shipyard'),
                hasIon: game.buildings.some(b => b.type === 'ion'),
                ionUnlocked: game.ionCannon.unlocked,
                powerGen: game.powerGen,
                powerReq: game.powerReq
            };
        }''')
        print("Buildings constructed:", build_result)
        assert build_result['hasTesla'] and build_result['hasPrism']
        assert build_result['hasShipyard'] and build_result['hasIon']
        assert build_result['ionUnlocked']

        # Test Warship Unit Production (Fighter, Cruiser, Dreadnought, Harvester)
        print("\nTesting Shipyard Production (Escort Fighter, Siege Dreadnought)...")
        unit_result = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            game.credits = 5000; // fund production
            game.produceUnit('fighter', 200);
            game.produceUnit('cruiser', 550);
            game.produceUnit('dreadnought', 1200);
            game.produceUnit('harvester', 400);
            return {
                unitsCount: game.units.length,
                harvestersCount: game.harvesters.length,
                hasDreadnought: game.units.some(u => u.type === 'dreadnought'),
                hasCruiser: game.units.some(u => u.type === 'cruiser')
            };
        }''')
        print("Units produced:", unit_result)
        assert unit_result['hasDreadnought'] and unit_result['hasCruiser']
        assert unit_result['harvestersCount'] >= 2

        # Test Tactical Commands (Select All, Guard, Assault)
        print("\nTesting Tactical Orders & Controls...")
        orders_result = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            game.selectAllCombatUnits();
            const selectedBefore = game.selectedUnits.length;
            game.commandDefendHQ();
            const defendTargetSet = game.units.every(u => u.targetX !== null && u.targetY !== null);
            game.commandAssaultRift();
            const assaultTargetSet = game.units.every(u => u.targetX === 2100);
            return {
                selectedCount: selectedBefore,
                defendTargetSet: defendTargetSet,
                assaultTargetSet: assaultTargetSet
            };
        }''')
        print("Orders result:", orders_result)
        assert orders_result['selectedCount'] > 0
        assert orders_result['assaultTargetSet']

        # Test Combat Wave & Superweapon (Orbital Ion Cannon Strike)
        print("\nTesting Enemy Wave & Orbital Ion Cannon Strike...")
        combat_result = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            game.spawnWave();
            const enemiesBefore = game.enemies.length;
            
            // Ready superweapon and fire at enemy wave
            game.ionCannon.ready = true;
            game.executeIonCannonStrike(2100, 800);
            
            return {
                enemiesCount: enemiesBefore,
                strikesCount: game.orbitalStrikes.length,
                strikeRadius: game.orbitalStrikes[0].radius,
                strikeStage: game.orbitalStrikes[0].stage
            };
        }''')
        print("Combat & Ion Cannon result:", combat_result)
        assert combat_result['enemiesCount'] > 0
        assert combat_result['strikesCount'] > 0

        # Let the game simulate a bit to show combat and rendering
        await page.wait_for_timeout(1000)
        await page.screenshot(path="C:/Users/machine/.gemini/antigravity/brain/72ea3f45-0738-459a-8560-5853a3c36367/test_redalert_space_command.png")
        print("Saved screenshot test_redalert_space_command.png")

        # 3. Test Dyson Sphere Program Mode
        print("\n--- 3. Testing Dyson Sphere Program Mode (Megastructure & Logistics) ---")
        await page.click('#sf-btn-mode-dyson')
        await page.wait_for_timeout(600)

        dsp_init_state = await page.evaluate('''() => {
            const overlay = document.getElementById('sf-dyson-overlay');
            const game = window.DysonSphereProgram;
            return {
                overlayActive: overlay ? overlay.classList.contains('active') : false,
                gameActive: game ? game.active : false,
                starLum: game ? game.star.luminosity : 0,
                planetsCount: game ? game.planets.length : 0,
                sailsCount: game ? game.solarSails.length : 0,
                nodesCount: game ? game.nodes.length : 0,
                builtNodes: game ? game.nodes.filter(n => n.built).length : 0,
                totalPowerGW: game ? game.totalPowerGW : 0,
                universeMatrix: game ? game.universeMatrix : 0
            };
        }''')
        print("Dyson initial state:", dsp_init_state)
        assert dsp_init_state['overlayActive'] and dsp_init_state['gameActive']
        assert dsp_init_state['starLum'] == 2.14
        assert dsp_init_state['planetsCount'] >= 3
        assert dsp_init_state['sailsCount'] >= 100
        assert dsp_init_state['nodesCount'] == 32
        assert dsp_init_state['builtNodes'] >= 8

        # Test Launching Solar Sails & Carrier Rockets
        print("\nTesting EM Catapult Solar Sails & Rocket Launch...")
        dsp_launch_result = await page.evaluate('''() => {
            const game = window.DysonSphereProgram;
            const sailsBefore = game.solarSails.length;
            game.launchSolarSails();
            const sailsAfter = game.solarSails.length;

            const rocketsBefore = game.rockets.length;
            game.launchCarrierRocket();
            const rocketsAfter = game.rockets.length;

            return {
                sailsBefore: sailsBefore,
                sailsAfter: sailsAfter,
                sailsGained: sailsAfter - sailsBefore,
                rocketsLaunched: rocketsAfter - rocketsBefore
            };
        }''')
        print("Launch results:", dsp_launch_result)
        assert dsp_launch_result['sailsGained'] >= 3
        assert dsp_launch_result['rocketsLaunched'] == 1

        # Test Cosmic Tech Tree Upgrades
        print("\nTesting Cosmic Tech Tree (White Sugar Upgrades)...")
        tech_result = await page.evaluate('''() => {
            const game = window.DysonSphereProgram;
            game.universeMatrix = 1000; // fund research
            game.upgradeTech('em', 100);
            game.upgradeTech('sail', 150);
            game.upgradeTech('rocket', 250);
            game.upgradeTech('lens', 350);
            return {
                emLevel: game.techLevels.em,
                sailLevel: game.techLevels.sail,
                rocketLevel: game.techLevels.rocket,
                lensLevel: game.techLevels.lens,
                matrixRemaining: game.universeMatrix
            };
        }''')
        print("Tech research result:", tech_result)
        assert tech_result['emLevel'] == 1
        assert tech_result['sailLevel'] == 1
        assert tech_result['rocketLevel'] == 1
        assert tech_result['lensLevel'] == 1

        # Test Camera View Mode cycling
        print("\nTesting 3D Camera Views...")
        cam_result = await page.evaluate('''() => {
            const game = window.DysonSphereProgram;
            const m0 = game.camera.mode;
            game.cycleCameraView();
            const m1 = game.camera.mode;
            game.cycleCameraView();
            const m2 = game.camera.mode;
            game.cycleCameraView();
            const m3 = game.camera.mode;
            return { m0, m1, m2, m3 };
        }''')
        print("Camera view cycle:", cam_result)
        assert cam_result['m1'] == 'planet'
        assert cam_result['m2'] == 'sphere'
        assert cam_result['m3'] == 'system'

        await page.wait_for_timeout(1000)
        await page.screenshot(path="C:/Users/machine/.gemini/antigravity/brain/72ea3f45-0738-459a-8560-5853a3c36367/test_dyson_sphere_program_megastructure.png")
        print("Saved screenshot test_dyson_sphere_program_megastructure.png")

        # 4. Test Switching back to Cruise Mode
        print("\n--- 4. Testing Switching back to Cruise Mode ---")
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(400)

        cruise_state = await page.evaluate('''() => {
            const raOverlay = document.getElementById('sf-redalert-overlay');
            const dspOverlay = document.getElementById('sf-dyson-overlay');
            const btnCruise = document.getElementById('sf-btn-mode-cruise');
            return {
                raHidden: !raOverlay.classList.contains('active'),
                dspHidden: !dspOverlay.classList.contains('active'),
                cruiseActive: btnCruise.classList.contains('active'),
                raStopped: !window.RedAlertRTS.active,
                dspStopped: !window.DysonSphereProgram.active
            };
        }''')
        print("Back to cruise state:", cruise_state)
        assert cruise_state['raHidden'] and cruise_state['dspHidden'] and cruise_state['cruiseActive']
        assert cruise_state['raStopped'] and cruise_state['dspStopped']

        # 5. Check Console Errors
        print("\n--- 5. Console Error Audit ---")
        print(f"Total Console Errors: {len(errors)}")
        if errors:
            print("Errors list:", errors)
        assert len(errors) == 0, f"Found {len(errors)} console errors!"

        print("\n🎉 ALL EXPANSION MODES (RED ALERT RTS & DYSON SPHERE PROGRAM) VERIFICATIONS PASSED 100%!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
