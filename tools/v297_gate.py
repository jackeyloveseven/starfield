
# -*- coding: utf-8 -*-
"""v297 - 距离门槛改用 travel/m.z（不依赖 IIFE 内的 project，避免全被挡住）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """    /* 渐进式揭示：远处掠过不算发现，屏幕上足够大（看清了）才录入 */
    var q = (typeof project === 'function') ? project([m.x, m.y, m.z]) : null;
    if (!q) return;
    if ((m.r || 300) * q[3] < 55) return;"""
new = """    /* 渐进式揭示：远处掠过不算发现，靠得足够近才录入。
       用航线距离而不是屏幕半径——project 在主 IIFE 内，这里未必拿得到；
       travel 是全局的，Codex.discover 里本来就在用。 */
    var dz = m.z - travel;
    var reach = (m.r || 300) * 16;
    if (dz > reach || dz < -reach * 0.5) return;"""
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('gate now uses travel distance')
