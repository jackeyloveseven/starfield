# -*- coding: utf-8 -*-
"""
Master Playwright Verification Suite for the main cruise plus the two
Experiment Lab prototypes:
1. 🌌 Cruise Mode (主航线 · 深空漫游)
2. ⚡ Red Alert RTS (实验舱 · 前哨争霸)
3. ☀️ Dyson Sphere Program (实验舱 · 星系工程)

Void Extraction and Orbital Slingshot are no longer standalone modes —
they live inside the cruise loop, see verify_integrated_mechanics_adversarial.py.
"""

import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_URL = (BASE_DIR / 'starfield.html').as_uri()

async def main():
    print("================================================================================")
    print(f"Testing Starfield URL: {HTML_URL}")
    print("================================================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto(HTML_URL)
        await page.wait_for_timeout(1200)
        await page.evaluate("() => window.StarfieldBetaLab && window.StarfieldBetaLab.setEnabled(true)")
        await page.wait_for_timeout(300)

        # 1. 实验舱（原常驻模式栏已拆除）：主航线是唯一主屏
        print("\n--- 1. Checking Experiment Lab (no persistent mode bar) ---")
        lab_check = await page.evaluate('''() => {
            const modal = document.getElementById('sf-lab-modal');
            const items = ['cruise', 'redalert', 'dyson'].map(m =>
                document.getElementById('sf-lab-item-' + m)
            );
            return {
                hasModal: !!modal,
                labOpen: modal ? modal.classList.contains('open') : false,
                noModeBar: !document.getElementById('sf-mode-bar'),
                itemCount: items.filter(Boolean).length,
                currentId: document.querySelector('#sf-lab-modal .sf-lab-item.is-current')?.id,
                legacyExtAbsent: !document.getElementById('sf-btn-mode-extract'),
                legacySlingAbsent: !document.getElementById('sf-btn-mode-slingshot')
            };
        }''')
        print("Lab Check:", lab_check)
        assert lab_check['hasModal'] and lab_check['labOpen']
        assert lab_check['noModeBar'], "常驻模式栏必须已经拆除"
        assert lab_check['itemCount'] == 3
        assert lab_check['legacyExtAbsent'] and lab_check['legacySlingAbsent']
        assert lab_check['currentId'] == 'sf-lab-item-cruise'

        # 2. Test Red Alert RTS Mode
        print("\n--- 2. Testing Red Alert RTS (Command & Conquer Space Base) ---")
        await page.evaluate("() => window.switchStarfieldMode('redalert')")
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

        # 3. Test Dyson Sphere Program Mode
        print("\n--- 3. Testing Dyson Sphere Program (Megastructure & Logistics) ---")
        await page.evaluate("() => window.switchStarfieldMode('dyson')")
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

        # 4. Switch Back to Cruise Mode
        print("\n--- 4. Returning to Cruise Mode ---")
        await page.evaluate("() => window.switchStarfieldMode('cruise')")
        await page.wait_for_timeout(400)
        cruise_state = await page.evaluate('''() => {
            return {
                cruiseActive: document.querySelector('#sf-lab-item-cruise').classList.contains('is-current'),
                raStopped: !window.RedAlertRTS.active,
                dspStopped: !window.DysonSphereProgram.active,
                allOverlaysHidden: ['sf-redalert-overlay', 'sf-dyson-overlay']
                    .every(id => !document.getElementById(id).classList.contains('active'))
            };
        }''')
        print("Back to Cruise State:", cruise_state)
        assert cruise_state['cruiseActive']
        assert cruise_state['raStopped'] and cruise_state['dspStopped']
        assert cruise_state['allOverlaysHidden']

        # 5. Total Console Errors
        print("\n--- 5. Comprehensive Console Error Check ---")
        print(f"Total Errors Count: {len(errors)}")
        if errors:
            print("Errors detected:", errors)
        assert len(errors) == 0, f"Found {len(errors)} console errors!"

        print("\n================================================================================")
        print("🏆 ALL STARFIELD GAMEPLAY MODES VERIFIED WITH 100% SUCCESS AND 0 CONSOLE ERRORS!")
        print("================================================================================")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
