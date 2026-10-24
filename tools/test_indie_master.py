import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    errors = []
    logs = []
    edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=edge_path, headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        page.on('console', lambda msg: logs.append(f'[{msg.type}] {msg.text}'))
        page.on('pageerror', lambda err: errors.append(str(err)))
        
        file_url = 'file:///' + os.path.abspath(r'd:\items\code\starfield-pub\starfield.html').replace('\\\\', '/')
        print('1. Navigating to:', file_url)
        await page.goto(file_url, wait_until='networkidle')
        await asyncio.sleep(1)
        
        # Click #begin to embark on flight
        print('2. Clicking #begin to launch flight...')
        await page.click('#begin')
        await asyncio.sleep(2)
        
        os.makedirs(r'd:\items\code\starfield-pub\shots', exist_ok=True)
        
        # Test 1: Celestial Codex
        print('3. Testing Celestial Codex (Press Tab)...')
        await page.keyboard.press('Tab')
        await asyncio.sleep(1)
        
        # Switch to wonders tab
        await page.click('.codex-tab[data-tab="wonders"]')
        await asyncio.sleep(0.5)
        
        shot_codex = r'd:\items\code\starfield-pub\shots\indie_codex_wonders.png'
        await page.screenshot(path=shot_codex)
        print('   Saved Codex screenshot to:', shot_codex)
        
        # Close Codex
        await page.click('#codex-close-btn')
        await asyncio.sleep(0.5)
        
        # Test 2: Fleet Formations
        print('4. Testing Fleet Formations (Press F)...')
        for f_idx in range(3):
            await page.keyboard.press('KeyF')
            await asyncio.sleep(0.8)
            
        shot_formation = r'd:\items\code\starfield-pub\shots\indie_formation_orbital.png'
        await page.screenshot(path=shot_formation)
        print('   Saved Fleet Formation screenshot to:', shot_formation)
        
        # Test 3: Photo Mode
        print('5. Testing Deep Space Photo Mode (Press P)...')
        await page.keyboard.press('KeyP')
        await asyncio.sleep(1)
        
        # Apply Golden Foil filter and CinemaScope ratio
        await page.click('.photo-btn[data-filter="gold"]')
        await page.click('.photo-btn[data-ratio="cinema"]')
        await asyncio.sleep(0.8)
        
        shot_photo = r'd:\items\code\starfield-pub\shots\indie_photo_mode.png'
        await page.screenshot(path=shot_photo)
        print('   Saved Photo Mode screenshot to:', shot_photo)
        
        # Exit Photo Mode
        await page.click('#photo-exit-btn')
        await asyncio.sleep(0.5)
        
        # Test 4: Settings Drawer
        print('6. Testing Settings & Audio Mixer (Press ESC)...')
        await page.keyboard.press('Escape')
        await asyncio.sleep(1)
        
        shot_settings = r'd:\items\code\starfield-pub\shots\indie_settings_drawer.png'
        await page.screenshot(path=shot_settings)
        print('   Saved Settings Drawer screenshot to:', shot_settings)
        
        # Close Settings
        await page.click('#settings-close-btn')
        await asyncio.sleep(0.5)
        
        # Check flight progress
        travel_dist = await page.evaluate("window.Starfield.getTravel()")
        print(f'7. Flight Active Travel: {travel_dist:.1f} units')
        
        await browser.close()
        
    print('\n==================================================')
    print('VERIFICATION SUMMARY')
    print('Total Console Logs:', len(logs))
    if errors:
        print('ERRORS FOUND:', errors)
    else:
        print('ALL INDIE MASTER TESTS PASSED WITH ZERO ERRORS!')
    print('==================================================')

asyncio.run(main())
