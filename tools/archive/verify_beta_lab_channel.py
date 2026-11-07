# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_URL = (BASE_DIR / 'starfield.html').as_uri()

async def main():
    print(f"Testing URL: {HTML_URL}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 390, "height": 844})

        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: errors.append(str(err)))

        await page.goto(HTML_URL)
        await page.wait_for_timeout(1000)

        # 1. Verify Default Clean State (Beta Disabled by default)
        print("\n--- 1. Testing Default Clean State (Beta Disabled) ---")
        state1 = await page.evaluate('''() => {
            const modal = document.getElementById('sf-lab-modal');
            const lab = window.StarfieldBetaLab;
            return {
                hasLab: !!lab,
                isEnabled: lab ? lab.isEnabled() : false,
                noModeBar: !document.getElementById('sf-mode-bar'),
                labOpen: modal ? modal.classList.contains('open') : false,
                entryDisplay: getComputedStyle(document.getElementById('btn-open-lab')).display
            };
        }''')
        print("Default state:", state1)
        assert not state1['isEnabled'], "Beta must be disabled by default"
        assert state1['noModeBar'], "常驻模式栏必须已拆除（主航线不该是一个 tab）"
        assert not state1['labOpen'], "Lab must stay closed by default"
        assert state1['entryDisplay'] == 'none', "未加入测试时不显示实验舱入口"

        # 2. Verify Voluntary Enrollment (Clicking Join Beta)
        print("\n--- 2. Testing Voluntary Beta Channel Enrollment ---")
        await page.evaluate('''() => {
            window.StarfieldBetaLab.toggle();
        }''')
        await page.wait_for_timeout(400)

        state2 = await page.evaluate('''() => {
            const modal = document.getElementById('sf-lab-modal');
            const lab = window.StarfieldBetaLab;
            const statusTag = document.getElementById('sf-beta-channel-status');
            const toggleBtn = document.getElementById('btn-toggle-beta-channel');
            return {
                isEnabled: lab.isEnabled(),
                labOpen: modal ? modal.classList.contains('open') : false,
                entryDisplay: getComputedStyle(document.getElementById('btn-open-lab')).display,
                currentItem: document.querySelector('#sf-lab-modal .sf-lab-item.is-current')?.id,
                statusText: statusTag ? statusTag.textContent : '',
                btnText: toggleBtn ? toggleBtn.textContent : ''
            };
        }''')
        print("Enrolled state:", state2)
        assert state2['isEnabled'], "Beta should now be enabled"
        assert state2['labOpen'], "加入测试后实验舱应当自动展开"
        assert state2['entryDisplay'] == 'block', "实验舱入口应可见"
        assert state2['currentItem'] == 'sf-lab-item-cruise', "主航线仍应是当前项"
        assert '先锋测试' in state2['statusText']

        # 3. Test Mode Switching While in Beta
        print("\n--- 3. Testing Gameplay Mode Switch Under Beta ---")
        await page.evaluate("() => window.switchStarfieldMode('redalert')")
        await page.wait_for_timeout(400)
        raActive = await page.evaluate('() => window.RedAlertRTS && window.RedAlertRTS.active')
        print("Red Alert activated under Beta:", raActive)
        assert raActive, "Red Alert should activate when entered"

        # ESC 必须能从原型退回主航线（旧版主键位表在非 cruise 时整体 return，ESC 是死路）
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)
        esc_state = await page.evaluate('''() => ({
            mode: window.currentMode,
            raActive: !!(window.RedAlertRTS && window.RedAlertRTS.active),
            drawerOpen: document.getElementById('settings-drawer').classList.contains('open')
        })''')
        print("ESC exit state:", esc_state)
        assert esc_state['mode'] == 'cruise', "ESC 应退回主航线"
        assert not esc_state['raActive'], "ESC 应停止原型引擎"
        assert not esc_state['drawerOpen'], "ESC 不应同时弹出设置抽屉"

        # 再进一次，供下一步验证「退出测试自动回主航线」
        await page.evaluate("() => window.switchStarfieldMode('redalert')")
        await page.wait_for_timeout(400)

        # 4. Verify Voluntary Exit (Switching Back to Stable)
        print("\n--- 4. Testing Voluntary Exit from Beta ---")
        await page.evaluate('''() => {
            window.StarfieldBetaLab.toggle();
        }''')
        await page.wait_for_timeout(400)

        state4 = await page.evaluate('''() => {
            const modal = document.getElementById('sf-lab-modal');
            const lab = window.StarfieldBetaLab;
            const statusTag = document.getElementById('sf-beta-channel-status');
            const raActive = window.RedAlertRTS && window.RedAlertRTS.active;
            return {
                isEnabled: lab.isEnabled(),
                labOpen: modal ? modal.classList.contains('open') : false,
                entryDisplay: getComputedStyle(document.getElementById('btn-open-lab')).display,
                statusText: statusTag ? statusTag.textContent : '',
                raStopped: !raActive
            };
        }''')
        print("Exited state:", state4)
        assert not state4['isEnabled'], "Beta should now be disabled"
        assert not state4['labOpen'], "Lab must be closed on exit"
        assert state4['entryDisplay'] == 'none', "退出测试后实验舱入口应隐藏"
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
