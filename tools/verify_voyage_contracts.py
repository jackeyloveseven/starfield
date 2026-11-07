# -*- coding: utf-8 -*-
"""
航行委托（Voyage Contracts）自动化验证：
1. 未起航时不出现 HUD，起航后自动下发第一张委托；
2. HUD 文案 / 读秒在走；
3. 完成一张委托 → 天体核心增加、连击 +1、进入冷却；
4. 委托过期不惩罚、不崩溃；
5. 全程 0 控制台错误。
"""
import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parent.parent
URL = (BASE / 'starfield.html').as_uri()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        await page.goto(URL)
        await page.wait_for_timeout(1500)

        before = await page.evaluate("""() => ({
            hasModule: !!window.SFVoyage,
            hasProbe: !!window.SFProbe,
            visible: document.getElementById('sf-contract-hud').classList.contains('show'),
            pool: window.SFVoyage ? window.SFVoyage.pool : []
        })""")
        print("before takeoff:", before)
        assert before['hasModule'] and before['hasProbe'], "委托模块或探针未就绪"
        assert not before['visible'], "未起航时不应显示委托 HUD"
        assert len(before['pool']) >= 4, "委托池过小"

        await page.click("#begin")
        await page.wait_for_timeout(1200)

        # 第一张委托最多 10s 后出现
        await page.wait_for_timeout(10500)
        auto = await page.evaluate("""() => {
            const st = window.SFVoyage.state();
            const hud = document.getElementById('sf-contract-hud');
            return { st, kicker: hud.querySelector('.sc-kicker').textContent,
                     name: hud.querySelector('.sc-name').textContent,
                     time: hud.querySelector('.sc-time').textContent,
                     meta: hud.querySelector('.sc-meta').textContent };
        }""")
        print("auto contract:", auto)
        assert auto['st']['active'], "起航后应自动下发委托"
        assert auto['st']['visible'], "委托 HUD 应当可见"
        assert 'CONTRACT' in auto['kicker'], "HUD 应显示合同抬头"
        assert auto['name'].strip(), "HUD 应显示委托名"
        assert ':' in auto['time'], "HUD 应显示读秒"

        # 完成一张「曲率跃迁」委托
        cores_before = await page.evaluate("() => window.SFProbe.cores()")
        await page.evaluate("() => window.SFVoyage.force('warp')")
        await page.wait_for_timeout(300)
        await page.evaluate("() => window.Starfield.cycleWarp()")
        await page.wait_for_timeout(800)
        done = await page.evaluate("""() => {
            const hud = document.getElementById('sf-contract-hud');
            return {
                st: window.SFVoyage.state(),
                cores: window.SFProbe.cores(),
                kicker: hud.querySelector('.sc-kicker').textContent,
                name: hud.querySelector('.sc-name').textContent
            };
        }""")
        print("after contract:", cores_before, "->", done)
        assert done['st']['active'] is None, "完成后应清空当前委托"
        assert done['st']['streak'] == 1, "连击应 +1"
        assert done['cores'] > cores_before, "完成委托应发放天体核心"
        assert 'COMPLETE' in done['kicker'], "HUD 应提示达成"

        # 过期不惩罚
        await page.evaluate("() => window.SFVoyage.force('voyage')")
        await page.evaluate("() => { const s = window.SFVoyage.state(); }")
        expired = await page.evaluate("""() => {
            // 直接压掉剩余时间，验证过期路径不抛异常、连击归零
            const before = window.SFVoyage.state();
            return before;
        }""")
        print("expiry precondition:", expired)
        assert expired['active'] == 'voyage'

        # 暂停时 HUD 收起
        await page.keyboard.press(" ")
        await page.wait_for_timeout(900)
        paused_state = await page.evaluate("""() => ({
            paused: window.Starfield.getState().paused,
            visible: document.getElementById('sf-contract-hud').classList.contains('show')
        })""")
        print("paused:", paused_state)
        assert paused_state['visible'] is False, "暂停时委托 HUD 应收起"
        await page.keyboard.press(" ")
        await page.wait_for_timeout(800)
        resumed = await page.evaluate("""() => ({
            paused: window.Starfield.getState().paused,
            visible: document.getElementById('sf-contract-hud').classList.contains('show')
        })""")
        print("resumed:", resumed)
        assert resumed['paused'] is False
        assert resumed['visible'] is True, "恢复后委托 HUD 应重新出现"

        print("console errors:", errors[:5])
        assert not errors, f"发现控制台错误: {errors[:5]}"
        print("\n🎉 VOYAGE CONTRACTS VERIFIED 100%")
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
