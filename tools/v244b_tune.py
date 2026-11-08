
# -*- coding: utf-8 -*-
"""v244b - 用正则改 TIER_LOOK 的 light；同时降曝光。"""
import re, sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

# light 全档下调
def fix_light(m):
    tier = m.group(1)
    val = {'common':0.95,'rare':1.0,'epic':1.06,'legend':0.98,'myth':0.94}[tier]
    return m.group(0).replace('light: ' + m.group(2), 'light: %s' % val)

html, n = re.subn(r"(common|rare|epic|legend|myth):\s*\{[^}]*?light:\s*([0-9.]+)", fix_light, html)
log.append('light x%d' % n)

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

rep("      envIntensity: 0.42 + L.rim * 0.30,",
    "      envIntensity: (0.26 + L.rim * 0.12) * (tier === 'myth' ? 0.60 : tier === 'legend' ? 0.72 : 1.0),",
    'envInt')
rep("    sun.intensity = L.light * 0.92;",
    "    sun.intensity = L.light * 0.78;", 'sunI')
rep("    amb.intensity = 0.40 + L.rim * 0.10;",
    "    amb.intensity = (0.26 + L.rim * 0.08) * (tier === 'myth' ? 0.72 : 1.0);", 'ambI')
rep("    rimLight.intensity = 0.30 + L.rim * 0.42;",
    "    rimLight.intensity = 0.18 + L.rim * 0.24;", 'rimI')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
