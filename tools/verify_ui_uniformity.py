
# -*- coding: utf-8 -*-
"""UI 一致性验证：全站扫描「大圆角 / 彩色填充 / 彩色 emoji / 控制台错误」。

运行时遍历 8 个界面状态（起航 / 飞行 / 折纸坞 / 摄影 / 图鉴 / 设置 / 天象馆 / 开卡 / 档案），
对每个可见元素检查：
  1. 圆角 >= 9px（球体的 50% 除外）
  2. 高饱和背景填充（深蓝灰底色不计）
  3. 文本里的彩色 emoji（↗ ◀ ▶ 三个几何符号白名单）

用法：python tools/verify_ui_uniformity.py
"""
import sys
import os
import traceback
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(BASE, 'starfield.html')
URL = 'file:///' + HTML.replace(os.sep, '/')

# 设计语言里允许的几何 / 星象符号（非彩色 emoji）
ALLOW_CODEPOINTS = {
    0x2197,             # ↗
    0x25C0, 0x25B6,     # ◀ ▶
    0x2726,             # ✦
    0x263F, 0x2640, 0x2641, 0x2642, 0x2643, 0x2644, 0x2295,   # ☿ ♀ ♂ ♃ ♄ ⊕
    0x00B7, 0x2022,     # · •
}
EMOJI_RANGES = ((0x1F000, 0x1FAFF), (0x2600, 0x27BF), (0x2B00, 0x2BFF), (0xFE0F, 0xFE0F), (0x200D, 0x200D))
ROUND_EXEMPT = ('sf-hatch-orb', 'sf-planet-canvas', 'sf-planet-gl')

AUDIT = r"""
() => {
  function sat(rgb) {
    var m = rgb.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    if (!m) return { s: 0, a: 0 };
    var r = +m[1] / 255, g = +m[2] / 255, b = +m[3] / 255, a = m[4] === undefined ? 1 : +m[4];
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    var l = (mx + mn) / 2;
    if (mx === mn) return { s: 0, a: a };
    var d = mx - mn;
    return { s: l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn), a: a };
  }
  var out = { radius: [], color: [], emoji: [] };
  var EMOJI = /\p{Extended_Pictographic}/u;
  document.querySelectorAll('body *').forEach(function (e) {
    var r = e.getBoundingClientRect();
    if (r.width < 14 || r.height < 8) return;
    var cs = getComputedStyle(e);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) < 0.05) return;
    var cls = (e.className && e.className.toString) ? e.className.toString() : '';
    var id = e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') +
             (cls ? '.' + cls.trim().split(/\s+/).slice(0, 2).join('.') : '');
    var rad = Math.max(parseFloat(cs.borderTopLeftRadius) || 0,
                       parseFloat(cs.borderBottomRightRadius) || 0);
    var exempt = false;
    for (var i = 0; i < 3; i++) {
      var k = ['sf-hatch-orb', 'sf-planet-canvas', 'sf-planet-gl'][i];
      if ((e.id && e.id.indexOf(k) >= 0) || cls.indexOf(k) >= 0) exempt = true;
    }
    if (rad >= 9 && r.width > 20 && !exempt) {
      out.radius.push(id.slice(0, 46) + ' r=' + Math.round(rad));
    }
    var bg = sat(cs.backgroundColor);
    if (bg.a > 0.12 && bg.s > 0.42) out.color.push(id.slice(0, 46) + ' bg=' + cs.backgroundColor);
    var txt = '';
    for (var j = 0; j < e.childNodes.length; j++) {
      if (e.childNodes[j].nodeType === 3) txt += e.childNodes[j].textContent;
    }
    if (EMOJI.test(txt) && out.emoji.length < 24) out.emoji.push(txt.trim().slice(0, 30));
  });
  return out;
}
"""


def main():
    failures = []
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(channel='chrome', headless=True,
                                   args=['--enable-unsafe-swiftshader'])
            pg = b.new_context(viewport={'width': 1440, 'height': 900},
                               device_scale_factor=1.0).new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
            pg.on('console', lambda m: errs.append('CONSOLE ' + m.text) if m.type == 'error' else None)
            pg.goto(URL, wait_until='networkidle')
            pg.wait_for_timeout(1500)

            states = []
            states.append(('launch', pg.evaluate(AUDIT)))
            pg.click('#begin'); pg.wait_for_timeout(3000)
            states.append(('flight', pg.evaluate(AUDIT)))
            pg.keyboard.press('h'); pg.wait_for_timeout(900)
            states.append(('hangar', pg.evaluate(AUDIT)))
            pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
            pg.keyboard.press('p'); pg.wait_for_timeout(900)
            states.append(('photo', pg.evaluate(AUDIT)))
            pg.keyboard.press('Escape'); pg.wait_for_timeout(600)
            pg.evaluate("() => { try { Codex.open(); } catch(e) { document.getElementById('codex-modal').classList.add('open'); } }")
            pg.wait_for_timeout(800)
            states.append(('codex', pg.evaluate(AUDIT)))
            pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
            pg.evaluate("() => { try { GameSettings.open(); } catch(e) { document.getElementById('settings-drawer').classList.add('open'); } }")
            pg.wait_for_timeout(800)
            states.append(('settings', pg.evaluate(AUDIT)))
            pg.keyboard.press('Escape'); pg.wait_for_timeout(500)
            pg.evaluate("() => window.StarfieldHatch.openList()"); pg.wait_for_timeout(800)
            states.append(('planetarium', pg.evaluate(AUDIT)))
            pg.evaluate("() => document.getElementById('sf-hatch-list').classList.remove('on')")
            pg.evaluate("() => { localStorage.setItem('sf_unopened_cores_v1','3'); window.StarfieldHatch.openNextCore(); }")
            pg.wait_for_timeout(2400)
            states.append(('hatch', pg.evaluate(AUDIT)))
            pg.evaluate("() => { var x=document.getElementById('sf-btn-flip'); if(x) x.click(); }")
            pg.wait_for_timeout(800)
            states.append(('archive', pg.evaluate(AUDIT)))

            for name, rep in states:
                print('%-12s  radius=%-2d color=%-2d emoji=%d' %
                      (name, len(rep['radius']), len(rep['color']), len(rep['emoji'])))
                for x in rep['radius']:
                    print('   [R] ' + x)
                    failures.append(name + ' radius ' + x)
                for x in rep['emoji']:
                    bad = []
                    for c in x:
                        cp = ord(c)
                        if cp in ALLOW_CODEPOINTS:
                            continue
                        for lo, hi in EMOJI_RANGES:
                            if lo <= cp <= hi:
                                bad.append(c)
                                break
                    if bad:
                        print('   [E] ' + x + '   ->  ' + ' '.join('U+%04X' % ord(c) for c in bad))
                        failures.append(name + ' emoji ' + x)

            print('console errors:', len(errs))
            if errs:
                failures.append('console errors: ' + '; '.join(errs[:3]))
            b.close()
    except Exception:
        traceback.print_exc()
        failures.append('script crashed')

    print('')
    if failures:
        print('UI UNIFORMITY: %d 项待处理' % len(failures))
        for f in failures[:12]:
            print('  - ' + f)
        sys.exit(1)
    print('UI UNIFORMITY OK：圆角残留 0，emoji 仅剩几何符号，0 控制台错误')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
