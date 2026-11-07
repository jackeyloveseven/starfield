
# -*- coding: utf-8 -*-
"""v154 — 收紧仪式节奏，保证自动触发后 1.92s 内完成显影。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

pairs = [
    ('        }, 400);', '        }, 380);'),
    ('        }, 560);', '        }, 520);'),
    ('      }, 1800);', '      }, 1400);'),
]
for o, n in pairs:
    o2, n2 = N(o), N(n)
    assert src.count(o2) == 1, o
    src = src.replace(o2, n2)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('DONE 1400 / 380 / 520')
