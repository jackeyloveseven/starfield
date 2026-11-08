
# -*- coding: utf-8 -*-
"""v268 - 给景观加绘制计数，便于验证确实画出来了。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """        var seed = hash(k, 9007);
        if (type === 0) comet(x, y, z, side, seed, fade);
        else if (type === 1) darkNebula(x, y, z, seed, fade);
        else planetaryNebula(x, y, z, seed, fade);"""
new = """        var seed = hash(k, 9007);
        window.__passDrawn = (window.__passDrawn || 0) + 1;
        if (type === 0) { window.__passComet = (window.__passComet||0)+1; comet(x, y, z, side, seed, fade); }
        else if (type === 1) { window.__passDark = (window.__passDark||0)+1; darkNebula(x, y, z, seed, fade); }
        else { window.__passPlan = (window.__passPlan||0)+1; planetaryNebula(x, y, z, seed, fade); }"""
assert html.count(old) == 1
html = html.replace(old, new)
HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('counters added')
