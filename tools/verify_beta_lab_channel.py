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

        # 1. Verify Default Clean State (Beta Disabled by default)
        print("\n--- 1. Testing Default Clean State (Beta Disabled) ---")
        state1 = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const lab = window.StarfieldBetaLab;
            return {
                hasLab: !!lab,
                isEnabled: lab ? lab.isEnabled() : false,
                barDisplay: bar ? getComputedStyle(bar).display : 'none',
                barVisible: bar ? (getComputedStyle(bar).display !== 'none') : false
            };
        }''')
        print("Default state:", state1)
        assert not state1['isEnabled'], "Beta must be disabled by default"
        assert not state1['barVisible'], "Mode bar must be hidden by default"

        # 2. Verify Voluntary Enrollment (Clicking Join Beta)
        print("\n--- 2. Testing Voluntary Beta Channel Enrollment ---")
        await page.evaluate('''() => {
            window.StarfieldBetaLab.toggle();
        }''')
        await page.wait_for_timeout(400)

        state2 = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const lab = window.StarfieldBetaLab;
            const statusTag = document.getElementById('sf-beta-channel-status');
            const toggleBtn = document.getElementById('btn-toggle-beta-channel');
            return {
                isEnabled: lab.isEnabled(),
                barDisplay: getComputedStyle(bar).display,
                statusText: statusTag ? statusTag.textContent : '',
                btnText: toggleBtn ? toggleBtn.textContent : ''
            };
        }''')
        print("Enrolled state:", state2)
        assert state2['isEnabled'], "Beta should now be enabled"
        assert state2['barDisplay'] == 'flex', "Mode bar should be visible"
        assert '先锋测试' in state2['statusText']

        # 3. Test Mode Switching While in Beta
        print("\n--- 3. Testing Gameplay Mode Switch Under Beta ---")
        await page.click('#sf-btn-mode-redalert')
        await page.wait_for_timeout(400)
        raActive = await page.evaluate('() => window.RedAlertRTS && window.RedAlertRTS.active')
        print("Red Alert activated under Beta:", raActive)
        assert raActive, "Red Alert should activate when clicked"

        # 4. Verify Voluntary Exit (Switching Back to Stable)
        print("\n--- 4. Testing Voluntary Exit from Beta ---")
        await page.evaluate('''() => {
            window.StarfieldBetaLab.toggle();
        }''')
        await page.wait_for_timeout(400)

        state4 = await page.evaluate('''() => {
            const bar = document.getElementById('sf-mode-bar');
            const lab = window.StarfieldBetaLab;
            const statusTag = document.getElementById('sf-beta-channel-status');
            const raActive = window.RedAlertRTS && window.RedAlertRTS.active;
            return {
                isEnabled: lab.isEnabled(),
                barDisplay: getComputedStyle(bar).display,
                statusText: statusTag ? statusTag.textContent : '',
                raStopped: !raActive
            };
        }''')
        print("Exited state:", state4)
        assert not state4['isEnabled'], "Beta should now be disabled"
        assert state4['barDisplay'] == 'none', "Mode bar must be hidden again"
        assert state4['raStopped'], "Red Alert should automatically stop on exit"
        assert '稳定正式版' in state4['statusText']

        # 5. Testing OTA Banner for Beta Update
        print("\n--- 5. Testing OTA Banner Voluntary Notification ---")
        await page.evaluate('''() => {
            window.onStarfieldOtaNotify('OTA_READY', {
                version: '1.18.0',
                build: 150,
                is_beta: true,
                title: '先锋实验版上线：包含4大太空新玩法',
                changelog: '全新上线先锋实验室，包含 4 大太空玩法！默认保持纯净漫游，您可自愿选择是否体验。'
            });
        }''')
        await page.wait_for_timeout(400)

        otaState = await page.evaluate('''() => {
            const banner = document.getElementById('sf-ota-banner');
            const applyBtn = document.getElementById('sf-ota-apply-btn');
            const keepBtn = document.getElementById('sf-ota-keep-btn');
            const titleEl = banner ? banner.querySelector('.sf-ota-title') : null;
            return {
                hasBanner: !!banner,
                title: titleEl ? titleEl.textContent : '',
                applyText: applyBtn ? applyBtn.textContent : '',
                hasKeepBtn: !!keepBtn,
                keepText: keepBtn ? keepBtn.textContent : ''
            };
        }''')
        print("OTA Banner State:", otaState)
        assert otaState['hasBanner'], "OTA Banner should display"
        assert '先锋实验版' in otaState['title']
        assert '立即体验 Beta' in otaState['applyText']
        assert otaState['hasKeepBtn'], "Keep stable button must exist"

        # Click keep stable button to dismiss safely
        await page.click('#sf-ota-keep-btn')
        await page.wait_for_timeout(500)
        bannerDismissed = await page.evaluate('() => !document.getElementById("sf-ota-banner")')
        print("Banner dismissed gracefully:", bannerDismissed)
        assert bannerDismissed, "Banner should be removed when keep stable is clicked"

        print("\n--- Total Console Errors ---")
        print("Errors count:", len(errors))
        if errors:
            print("Errors:", errors)
        assert len(errors) == 0, "No console errors allowed"

        print("\n🎉 ALL BETA LAB VOLUNTARY CHANNEL CHECKS PASSED 100%!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
