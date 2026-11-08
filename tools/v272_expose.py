
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
old = "isOn: function () { return ok; }"
assert html.count(old) == 1, 'count=%d' % html.count(old)
new = ("isOn: function () { return ok; },\n"
       "    LivingPlanet: LivingPlanet, Presets: Presets, SimplexNoise: SimplexNoise, tierLook: TIER_LOOK")
html = html.replace(old, new)
HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('exposed LivingPlanet/Presets/SimplexNoise')
