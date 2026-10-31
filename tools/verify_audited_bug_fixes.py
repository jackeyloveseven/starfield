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
        await page.wait_for_timeout(1000)

        # 1. Test Drawer Version Tag Fallback
        print("\n--- 1. Testing Drawer Version Tag Fallback ---")
        vtagText = await page.evaluate('''() => {
            const vtag = document.getElementById('sf-version-tag');
            return vtag ? vtag.textContent : '';
        }''')
        print("Version tag text:", vtagText)
        assert 'v1.18.0' in vtagText and '150' in vtagText, f"Expected v1.18.0 (Build 150), got {vtagText}"

        # Enable Beta Lab
        await page.evaluate("() => window.StarfieldBetaLab && window.StarfieldBetaLab.setEnabled(true)")
        await page.wait_for_timeout(300)

        # 2. Test Red Alert Harvester Proportional Pay & Depletion Idle
        print("\n--- 2. Testing Red Alert Harvester Proportional Pay & Depletion Idle ---")
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(500)

        harvTest = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            const h = game.harvesters[0];
            
            // Set cargo to 50%
            h.cargo = 500;
            h.maxCargo = 1000;
            h.state = 'unloading';
            h.unloadTimer = 0.01;
            const creditsBefore = game.credits;
            
            // Deplete all ore fields to test idle state transition
            game.oreFields.forEach(f => f.ore = 0);
            
            // Step game simulation by 0.05s
            game.update(0.05);
            
            return {
                creditsBefore,
                creditsAfter: game.credits,
                creditsGained: game.credits - creditsBefore,
                harvesterState: h.state,
                harvesterCargo: h.cargo
            };
        }''')
        print("Harvester test result:", harvTest)
        assert harvTest['creditsGained'] == 250, f"Expected 50% cargo = 250 credits, got {harvTest['creditsGained']}"
        assert harvTest['harvesterState'] == 'idle', f"Expected idle state when all fields depleted, got {harvTest['harvesterState']}"

        # 3. Test Harvester Prerequisite (Require Refinery)
        print("\n--- 3. Testing Harvester Refinery Prerequisite ---")
        prereqTest = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            // Remove refinery
            game.buildings = game.buildings.filter(b => b.type !== 'refinery');
            const harvCountBefore = game.harvesters.length;
            game.credits = 3000;
            game.produceUnit('harvester', 1400);
            return {
                harvCountBefore,
                harvCountAfter: game.harvesters.length
            };
        }''')
        print("Prerequisite test:", prereqTest)
        assert prereqTest['harvCountBefore'] == prereqTest['harvCountAfter'], "Harvester should not be built without Refinery"

        # 4. Test Red Alert Wave Progression
        print("\n--- 4. Testing Red Alert Wave Progression On Enemy Clear ---")
        waveTest = await page.evaluate('''() => {
            const game = window.RedAlertRTS;
            // Kill all enemies
            game.enemies.forEach(e => e.hp = 0);
            const creditsBefore = game.credits;
            game.update(0.05);
            return {
                creditsBefore,
                creditsAfter: game.credits,
                creditsGained: game.credits - creditsBefore,
                wave: game.wave,
                isSpawningWave: game.isSpawningWave
            };
        }''')
        print("Wave progression test:", waveTest)
        assert waveTest['creditsGained'] >= 800, f"Expected at least 800 wave reward, got {waveTest['creditsGained']}"
        assert waveTest['wave'] == 2, f"Expected wave 2, got {waveTest['wave']}"
        assert waveTest['isSpawningWave'], "Expected isSpawningWave to be true"

        # 5. Test Dyson Sphere Shell Tech Locking
        print("\n--- 5. Testing Dyson Sphere Shell Tech Button Locking ---")
        await page.click('#sf-btn-mode-dyson')
        await page.wait_for_timeout(500)

        techTest = await page.evaluate('''() => {
            const game = window.DysonSphereProgram;
            game.universeMatrix = 1000;
            game.toggleTechModal(true);
            game.upgradeTech('shell', 500);
            const btn = document.getElementById('sf-dsp-btn-upgrade-shell');
            return {
                matrixLeft: game.universeMatrix,
                shellLevel: game.techLevels.shell,
                btnDisabled: btn ? btn.disabled : false,
                btnText: btn ? btn.textContent : ''
            };
        }''')
        print("Tech lock test:", techTest)
        assert techTest['matrixLeft'] == 500, f"Expected 500 matrix left, got {techTest['matrixLeft']}"
        assert techTest['shellLevel'] == 1, "Shell level should be 1"
        assert techTest['btnDisabled'], "Shell button must be disabled after research"
        assert '已达上限' in techTest['btnText'], f"Button text should indicate MAX, got {techTest['btnText']}"

        # 6. Test Modal Cleanup on Mode Stop
        print("\n--- 6. Testing Modal Cleanup on Mode Stop ---")
        await page.click('#sf-btn-mode-cruise')
        await page.wait_for_timeout(400)
        dspModalOpen = await page.evaluate('() => document.getElementById("sf-dsp-tech-modal").classList.contains("active")')
        print("DSP tech modal closed on exit:", not dspModalOpen)
        assert not dspModalOpen, "Tech modal should be closed when leaving Dyson mode"

        print("\n--- Total Console Errors ---")
        print("Errors count:", len(errors))
        if errors:
            print("Errors:", errors)
        assert len(errors) == 0, "No console errors allowed"

        print("\n🎉 ALL AUDITED BUG FIXES VERIFIED 100% SUCCESSFULLY!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
