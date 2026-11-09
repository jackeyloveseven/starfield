
# -*- coding: utf-8 -*-
"""v296 - 渐进式揭示：距离门槛。锚点只用函数名行。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "checkCelestialEncounter(m) {"
new = """checkCelestialEncounter(m) {
    /* 渐进式揭示：远处掠过不算发现，屏幕上足够大（看清了）才录入 */
    var q = (typeof project === 'function') ? project([m.x, m.y, m.z]) : null;
    if (!q) return;
    if ((m.r || 300) * q[3] < 55) return;"""
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new, 1)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('proximity gate added')
