# -*- coding: utf-8 -*-
"""
Master Playwright Verification Suite for ALL 5 Starfield Modes:
1. 🌌 Cruise Mode (自由漫游)
2. 🚀 Void Extraction (搜打撤 · 鸭科夫)
3. 🪐 Orbital Slingshot (引力弹弓太空鸟)
4. ⚡ Red Alert RTS (红色警戒 · 前哨争霸)
5. ☀️ Dyson Sphere Program (戴森球计划 · 星系工程)
"""

import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    print("================================================================================")
    print("Testing Starfield URL: file:///D:/items/code/starfield-pub/starfield.html")
    print("================================================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto("file:///D:/items/code/starfield-pub/starfield.html")
        await page.wait_for_timeout(1200)
        await page.evaluate("() => window.StarfieldBetaLab && window.StarfieldBetaLab.setEnabled(true)")
        await page.wait_for_timeout(300)

        # 1. Check Mode Bar UI
        print("\n--- 1. Checking Mode Switcher Bar UI ---")
        bar_check = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const btns = ['cruise', 'extract', 'slingshot', 'redalert', 'dyson'].map(m => 
                document.getElementById('sf-btn-mode-' + m)
            );
            return {
                hasBar: !!bar,
                btnCount: btns.filter(Boolean).length,
                activeId: document.querySelector('#sf-mode-bar .sf-mode-btn.active')?.id
            };
        }''')
        print("Mode Bar Check:", bar_check)
        assert bar_check['hasBar']
        assert bar_check['btnCount'] == 5
        assert bar_check['activeId'] == 'sf-btn-mode-cruise'

        # 2. Test Void Extraction Mode
        print("\n--- 2. Testing Void Extraction (Duckov/Tarkov in Space) ---")
        await page.click('#sf-btn-mode-extract')
        await page.wait_for_timeout(500)
        ext_state = await page.evaluate('''() => {
            const game = window.VoidExtraction;
            return {
                active: game && game.active,
                enemies: game ? game.enemies.length : 0,
                derelicts: game ? game.derelicts.length : 0,
                cargoSlots: document.querySelectorAll('#sf-ext-cargo-grid .sf-ext-slot').length
            };
        }''')
        print("Void Extraction State:", ext_state)
        assert ext_state['active'] and ext_state['enemies'] > 0 and ext_state['cargoSlots'] == 6

        # 3. Test Orbital Slingshot Mode
        print("\n--- 3. Testing Orbital Slingshot (Angry Birds Space) ---")
        await page.click('#sf-btn-mode-slingshot')
        await page.wait_for_timeout(500)
        sling_state = await page.evaluate('''() => {
            const game = window.OrbitalSlingshot;
            return {
                active: game && game.active,
                planets: game && game.currentLevel ? game.currentLevel.planets.length : 0,
                targets: game && game.currentLevel ? game.currentLevel.targets.length : 0,
                hasBird: game && !!game.currentBird
            };
        }''')
        print("Orbital Slingshot State:", sling_state)
        assert sling_state['active'] and sling_state['planets'] > 0 and sling_state['hasBird']

        # 4. Test Red Alert RTS Mode
        print("\n--- 4. Testing Red Alert RTS (Command & Conquer Space Base) ---")
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(500)
        ra_state = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            game.credits = 10000;
            game.buildBuilding('tesla', 600);
            game.buildBuilding('prism', 750);
            game.buildBuilding('shipyard', 1000);
            game.buildBuilding('ion', 1500);
            game.produceUnit('dreadnought', 1200);
            game.spawnWave();
            game.ionCannon.ready = true;
            game.executeIonCannonStrike(2100, 800);
            return {
                active: game && game.active,
                credits: game ? game.credits : 0,
                powerGen: game ? game.powerGen : 0,
                powerReq: game ? game.powerReq : 0,
                isLowPower: game ? game.isLowPower : true,
                buildings: game ? game.buildings.length : 0,
                harvesters: game ? game.harvesters.length : 0,
                units: game ? game.units.length : 0,
                enemies: game ? game.enemies.length : 0,
                strikes: game ? game.orbitalStrikes.length : 0
            };
        }''')
        print("Red Alert State:", ra_state)
        assert ra_state['active']
        assert ra_state['buildings'] >= 7
        assert ra_state['units'] >= 3
        assert ra_state['strikes'] >= 1

        # 5. Test Dyson Sphere Program Mode
        print("\n--- 5. Testing Dyson Sphere Program (Megastructure & Logistics) ---")
        await page.click('#sf-btn-mode-dyson')
        await page.wait_for_timeout(500)
        dsp_state = await page.evaluate('''() => {
            const game = window.DysonSphereProgram;
            game.launchSolarSails();
            game.launchCarrierRocket();
            game.universeMatrix = 1000;
            game.upgradeTech('em', 100);
            game.upgradeTech('sail', 150);
            game.cycleCameraView();
            return {
                active: game && game.active,
                starLum: game ? game.star.luminosity : 0,
                planets: game ? game.planets.length : 0,
                sails: game ? game.solarSails.length : 0,
                nodes: game ? game.nodes.length : 0,
                builtNodes: game ? game.nodes.filter(n => n.built).length : 0,
                rockets: game ? game.rockets.length : 0,
                emLevel: game ? game.techLevels.em : 0,
                camMode: game ? game.camera.mode : ''
            };
        }''')
        print("Dyson Sphere Program State:", dsp_state)
        assert dsp_state['active']
        assert dsp_state['starLum'] == 2.14
        assert dsp_state['sails'] >= 100
        assert dsp_state['nodes'] == 32
        assert dsp_state['rockets'] >= 1
        assert dsp_state['emLevel'] == 1
        assert dsp_state['camMode'] == 'planet'

        # 6. Switch Back to Cruise Mode
        print("\n--- 6. Returning to Cruise Mode ---")
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(400)
        cruise_state = await page.evaluate('''() => {
            return {
                cruiseActive: document.getElementById('sf-btn-mode-cruise').classList.contains('active'),
                extStopped: !window.VoidExtraction.active,
                slingStopped: !window.OrbitalSlingshot.active,
                raStopped: !window.RedAlertRTS.active,
                dspStopped: !window.DysonSphereProgram.active,
                allOverlaysHidden: ['sf-extraction-overlay', 'sf-slingshot-overlay', 'sf-redalert-overlay', 'sf-dyson-overlay']
                    .every(id => !document.getElementById(id).classList.contains('active'))
            };
        }''')
        print("Back to Cruise State:", cruise_state)
        assert cruise_state['cruiseActive']
        assert cruise_state['extStopped'] and cruise_state['slingStopped']
        assert cruise_state['raStopped'] and cruise_state['dspStopped']
        assert cruise_state['allOverlaysHidden']

        # 7. Total Console Errors
        print("\n--- 7. Comprehensive Console Error Check ---")
        print(f"Total Errors Count: {len(errors)}")
        if errors:
            print("Errors detected:", errors)
        assert len(errors) == 0, f"Found {len(errors)} console errors!"

        print("\n================================================================================")
        print("🏆 ALL 5 STARFIELD GAMEPLAY MODES VERIFIED WITH 100% SUCCESS AND 0 CONSOLE ERRORS!")
        print("================================================================================")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
