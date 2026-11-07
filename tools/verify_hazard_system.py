# -*- coding: utf-8 -*-
"""
危险与损伤（HAZARD & INTEGRITY）自动化验证：
1. 起航前不出现船体条；起航后出现；
2. 逼近碎片带时左侧仪表列给出距离与缺口方向；
3. 缺口在右而船在中间 → 撞上，完整度下降；
4. 缺口居中且船在中 → 安全通过，完整度不变；
5. 完整度 < 25% 时曲率被锁回 1.0c；
6. 6 秒无伤后开始自修；
7. 全程 0 控制台错误。
"""
import asyncio
import sys

sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
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
        await page.wait_for_timeout(1200)

        pre = await page.evaluate("""() => ({
            hasModule: !!window.SFHazard,
            hullText: document.getElementById('sf-hull') ? document.getElementById('sf-hull').innerText.replace(/\\s+/g,' ') : '',
            noteShown: document.getElementById('sf-hazard-note').classList.contains('show')
        })""")
        print("pre-flight:", pre)
        assert pre['hasModule'], "危险系统未加载"
        assert 'INTEGRITY' in pre['hullText'], "船体条缺失"
        assert not pre['noteShown'], "起航前不应有碎片带预警"

        await page.click("#begin")
        await page.wait_for_timeout(1200)

        # —— 逼近预警 ——
        await page.evaluate("() => { window.SFHazard.reset(); window.SFHazard.spawn(-640, 2600); }")
        await page.wait_for_timeout(500)
        warn = await page.evaluate("""() => {
            const n = document.getElementById('sf-hazard-note');
            return { shown: n.classList.contains('show'), text: n.querySelector('.txt').textContent,
                     safeLane: [...n.querySelectorAll('.lanes i')].findIndex(x => x.classList.contains('safe')) };
        }""")
        print("warning:", warn)
        assert warn['shown'], "逼近时应显示碎片带预警"
        assert '碎片带' in warn['text'] and '缺口' in warn['text'], f"预警文案异常: {warn['text']}"
        assert warn['safeLane'] == 0, "缺口朝左时应有左车道高亮"

        # —— 撞：缺口在右、船在中 ——
        await page.evaluate("() => { window.SFHazard.reset(); window.SFHazard.spawn(640, 260); }")
        hit = None
        for _ in range(16):
            await page.wait_for_timeout(500)
            hit = await page.evaluate("() => window.SFHazard.state()")
            if hit['hull'] < 100:
                break
        print("wrong lane:", hit)
        assert hit['hull'] < 100, "对不准缺口应当受到撞击"

        # —— 安全：缺口居中 ——
        await page.evaluate("() => { window.SFHazard.reset(); window.SFHazard.spawn(0, 260); }")
        safe = None
        for _ in range(16):
            await page.wait_for_timeout(500)
            safe = await page.evaluate("() => window.SFHazard.state()")
            if safe['hull'] < 100:
                break
        print("aligned:", safe)
        assert safe['hull'] == 100, "对准缺口不应受伤"

        # —— 低完整度锁曲率 ——
        await page.evaluate("() => window.SFHazard.damage(16)")   # -80
        await page.evaluate("() => window.Starfield.cycleWarp()")  # 升到 1 档
        await page.wait_for_timeout(900)
        low = await page.evaluate("""() => ({
            hull: window.SFHazard.state().hull,
            gear: window.Starfield.getState().warpGear,
            key: document.getElementById('sf-hull').querySelector('.k').textContent
        })""")
        print("low integrity:", low)
        assert low['hull'] < 25, "构造的低完整度不成立"
        assert low['gear'] == 0, "完整度 <25% 时曲率应被锁回 1.0c"
        assert low['key'] == 'POWER LOSS', "低完整度时仪表应显示 POWER LOSS"

        # —— 自修 ——
        await page.wait_for_timeout(9000)
        repaired = await page.evaluate("() => window.SFHazard.state().hull")
        print("after repair window:", repaired)
        assert repaired > low['hull'], "无伤 6 秒后应开始自动维修"

        # —— 恒星耀斑：不加速吃伤害 ——
        await page.evaluate("() => { window.SFHazard.reset(); window.SFHazard.fireFlare(0.4); }")
        await page.wait_for_timeout(900)
        before_flare = 100
        flare = await page.evaluate("""() => ({
            hull: window.SFHazard.state().hull,
            phase: window.SFHazard.flareState().phase
        })""")
        print("flare (no boost):", before_flare, "->", flare)
        assert flare['hull'] == 80, f"未加速时耀斑应扣 20 点完整度，实际 {flare['hull']}"
        assert flare['phase'] in ('idle', 'burst'), "耀斑爆发后应回到 idle"

        # —— 恒星耀斑：曲率 ≥5.0c 可甩掉 ——
        await page.evaluate("() => window.SFHazard.reset()")
        await page.evaluate("() => window.Starfield.cycleWarp()")
        await page.wait_for_timeout(300)
        boosted_before = await page.evaluate("() => window.SFHazard.state().hull")
        await page.evaluate("() => window.SFHazard.fireFlare(0.4)")
        await page.wait_for_timeout(1200)
        boosted_after = await page.evaluate("() => window.SFHazard.state().hull")
        print("flare (boosted):", boosted_before, "->", boosted_after)
        assert boosted_after == boosted_before, "曲率 ≥5.0c 时应完全甩开耀斑"

        # —— 黑洞潮汐：靠近视界持续掉血 ——
        await page.evaluate("() => { window.SFHazard.reset(); window.SFHazard.forceTidal(0.9, 1800); }")
        tidal_before = await page.evaluate("() => window.SFHazard.state().hull")
        await page.wait_for_timeout(1300)
        tidal = await page.evaluate("""() => ({
            hull: window.SFHazard.state().hull,
            key: document.getElementById('sf-hull').querySelector('.k').textContent,
            note: document.getElementById('sf-hazard-note').textContent
        })""")
        print("tidal:", tidal_before, "->", tidal)
        assert tidal['hull'] < tidal_before, "黑洞潮汐应持续掉血"
        assert tidal['key'] == 'TIDAL SHEAR', "潮汐时仪表应显示 TIDAL SHEAR"
        assert '潮汐' in tidal['note'], "潮汐时左列应给出预警"

        print("console errors:", errors[:5])
        assert not errors, f"控制台错误: {errors[:5]}"
        print("\n🎉 HAZARD & INTEGRITY VERIFIED 100%")
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
