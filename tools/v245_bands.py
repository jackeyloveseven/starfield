
# -*- coding: utf-8 -*-
"""v245 - 压低雪线/云层。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

rep("        } else if (landElev < 0.88) {\n          col.copy(cRock); // High rocky mountain",
    "        } else if (landElev < 0.95) {\n          col.copy(cRock); // High rocky mountain",
    'snowline')
rep("        } else if (landElev < 0.65) {\n          col.copy(cForest); // Upland forest",
    "        } else if (landElev < 0.74) {\n          col.copy(cForest); // Upland forest",
    'forestBand')
rep("        } else if (landElev < 0.35) {\n          col.copy(cGrass); // Lowland grass",
    "        } else if (landElev < 0.44) {\n          col.copy(cGrass); // Lowland grass",
    'grassBand')
rep("      opacity: this.cfg.cloudCoverage * 0.75,", "      opacity: this.cfg.cloudCoverage * 0.40,", 'cloudOp')
rep("      envIntensity: (0.26 + L.rim * 0.12) * (tier === 'myth' ? 0.60 : tier === 'legend' ? 0.72 : 1.0),",
    "      envIntensity: (0.16 + L.rim * 0.09) * (tier === 'myth' ? 0.55 : tier === 'legend' ? 0.58 : 1.0),",
    'envInt')
rep("      clearcoat: tier === 'myth' ? 1.0 : tier === 'legend' ? 0.75 : tier === 'epic' ? 0.42 : 0.16,",
    "      clearcoat: tier === 'myth' ? 0.62 : tier === 'legend' ? 0.34 : tier === 'epic' ? 0.20 : 0.08,",
    'clearcoat')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
