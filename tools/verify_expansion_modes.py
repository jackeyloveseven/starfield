# -*- coding: utf-8 -*-
import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

async def main():
    print("Testing URL: file:///D:/items/code/starfield-pub/starfield.html")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        await page.goto("file:///D:/items/code/starfield-pub/starfield.html")
        await page.wait_for_timeout(1200)

        # 1. Check Mode Bar
        mode_bar_info = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const btnCruise = document.getElementById('sf-btn-mode-cruise');
            const btnExt = document.getElementById('sf-btn-mode-extract');
            const btnSling = document.getElementById('sf-btn-mode-slingshot');
            return {
                hasBar: !!bar,
                hasBtnCruise: !!btnCruise,
                hasBtnExt: !!btnExt,
                hasBtnSling: !!btnSling,
                cruiseActive: btnCruise ? btnCruise.classList.contains('active') : false
            };
        }''')
        print("Mode bar check:", mode_bar_info)
        assert mode_bar_info['hasBar'] and mode_bar_info['hasBtnExt'] and mode_bar_info['hasBtnSling']

        # 2. Test Void Extraction Mode (Duckov/Tarkov in Space)
        print("\n--- Testing Void Extraction Mode (Duckov/Tarkov) ---")
        await page.click('#sf-btn-mode-extract')
        await page.wait_for_timeout(600)

        ext_state = await page.evaluate('''() => {
            const overlay = document.getElementById('sf-extraction-overlay');
            const game = window.VoidExtraction;
            return {
                overlayActive: overlay ? overlay.classList.contains('active') : false,
                gameActive: game ? game.active : false,
                playerHp: game ? game.player.hull : 0,
                playerShield: game ? game.player.shield : 0,
                enemiesCount: game ? game.enemies.length : 0,
                derelictsCount: game ? game.derelicts.length : 0,
                hasEvacZone: game ? !!game.evacZone : false,
                cargoSlotsCount: document.querySelectorAll('#sf-ext-cargo-grid .sf-ext-slot').length
            };
        }''')
        print("Extraction mode state:", ext_state)
        assert ext_state['overlayActive'] and ext_state['gameActive']
        assert ext_state['enemiesCount'] > 0 and ext_state['derelictsCount'] > 0
        await page.screenshot(path="C:/Users/machine/.gemini/antigravity/brain/72ea3f45-0738-459a-8560-5853a3c36367/test_void_extraction_tactical.png")

        # 3. Test Orbital Slingshot Mode (Angry Birds Space)
        print("\n--- Testing Orbital Slingshot Mode (Angry Birds Space) ---")
        await page.click('#sf-btn-mode-slingshot')
        await page.wait_for_timeout(600)

        sling_state = await page.evaluate('''() => {
            const overlay = document.getElementById('sf-slingshot-overlay');
            const game = window.OrbitalSlingshot;
            return {
                overlayActive: overlay ? overlay.classList.contains('active') : false,
                gameActive: game ? game.active : false,
                planetsCount: game && game.currentLevel ? game.currentLevel.planets.length : 0,
                targetsCount: game && game.currentLevel ? game.currentLevel.targets.length : 0,
                hasBird: game && !!game.currentBird,
                birdType: game && game.currentBird ? game.currentBird.type : '',
                rosterTokens: document.querySelectorAll('#sf-sling-roster-box .sf-sling-bird-token').length
            };
        }''')
        print("Slingshot mode state:", sling_state)
        assert sling_state['overlayActive'] and sling_state['gameActive']
        assert sling_state['planetsCount'] > 0 and sling_state['targetsCount'] > 0
        await page.screenshot(path="C:/Users/machine/.gemini/antigravity/brain/72ea3f45-0738-459a-8560-5853a3c36367/test_orbital_slingshot_puzzle.png")

        # 4. Test Switching back to Cruise
        print("\n--- Testing Switching back to Cruise ---")
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(400)

        cruise_state = await page.evaluate('''() => {
            const extOverlay = document.getElementById('sf-extraction-overlay');
            const slingOverlay = document.getElementById('sf-slingshot-overlay');
            const btnCruise = document.getElementById('sf-btn-mode-cruise');
            return {
                extHidden: !extOverlay.classList.contains('active'),
                slingHidden: !slingOverlay.classList.contains('active'),
                cruiseActive: btnCruise.classList.contains('active'),
                extStopped: !window.VoidExtraction.active,
                slingStopped: !window.OrbitalSlingshot.active
            };
        }''')
        print("Back to cruise state:", cruise_state)
        assert cruise_state['extHidden'] and cruise_state['slingHidden'] and cruise_state['cruiseActive']
        assert cruise_state['extStopped'] and cruise_state['slingStopped']

        print("\n--- Total Console Errors ---")
        print(f"Errors count: {len(errors)}")
        if errors:
            print("Errors:", errors)
        assert len(errors) == 0, f"Found {len(errors)} console errors!"

        print("\n🎉 ALL EXPANSION MODES (DUCKOV & ANGRY BIRDS SPACE) VERIFICATIONS PASSED 100%!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
