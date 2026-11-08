
# -*- coding: utf-8 -*-
"""v274 - 地表相机改为看向前方地表，而不是水平线（否则上 2/3 屏幕是空的）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """    var alt = 7.5;
    var th = t * 0.055, ph = 1.12;

    /* 相机贴球面低空前进，up 取球面法线 —— 地形在下方掠过 */
    var pos = sph(th, ph, R + alt);
    var ahead = sph(th + 0.06, ph, R + alt);
    camera.position.copy(pos);
    camera.up.copy(pos).normalize();
    camera.lookAt(ahead);"""
new = """    var alt = 9.0;
    var th = t * 0.055, ph = 1.12;

    /* 相机贴球面低空前进，up 取球面法线。
       视线指向「前方的地表」而不是同高度的水平线，
       否则上 2/3 屏幕是空的，地形全挤在底部一条。 */
    var pos = sph(th, ph, R + alt);
    var ahead = sph(th + 0.16, ph, R * 0.985);
    camera.position.copy(pos);
    camera.up.copy(pos).normalize();
    camera.lookAt(ahead);"""
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('camera now looks at surface')
