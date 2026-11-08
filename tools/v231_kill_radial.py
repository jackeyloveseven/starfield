# -*- coding: utf-8 -*-
"""v231 — 删除弹弓辐射流光；预测弧线收敛。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
src = HTML.read_text(encoding='utf-8', newline='')
log = []


def cut(start_marker, end_marker, replacement, tag):
    global src
    i = src.find(start_marker)
    assert i >= 0, tag + ' start not found'
    j = src.find(end_marker, i)
    assert j >= 0, tag + ' end not found'
    j += len(end_marker)
    src = src[:i] + replacement + src[j:]
    log.append(tag)


def rep(old, new, tag):
    global src
    assert src.count(old) == 1, tag + ' count=%d' % src.count(old)
    src = src.replace(old, new)
    log.append(tag)


cut(
    '    // 2. Relativistic Space-Stretching Stream Glow FX',
    '      c.restore();\r\n    }',
    '    // 2. 弹弓激活时不再画辐射流光（18 条线从屏幕中心向四面八方辐射，\r\n'
    '    //    遮挡视野且无信息量）。速度感改由星尘拖尾与粒子层承担。',
    'radial-glow',
)

rep(
    "      c.strokeStyle = 'rgba(56, 189, 248, 0.72)';\r\n"
    '      c.lineWidth = 2.2;\r\n'
    '      c.setLineDash([7, 4]);\r\n'
    '      c.lineDashOffset = -(performance.now() * 0.02) % 11;\r\n'
    "      c.shadowColor = '#38bdf8';\r\n"
    '      c.shadowBlur = 12;',
    "      c.strokeStyle = 'rgba(120, 200, 245, 0.34)';\r\n"
    '      c.lineWidth = 1.1;\r\n'
    '      c.setLineDash([5, 7]);\r\n'
    '      c.lineDashOffset = -(performance.now() * 0.02) % 12;\r\n'
    "      c.shadowColor = 'rgba(56, 189, 248, 0.35)';\r\n"
    '      c.shadowBlur = 5;',
    'arc-style',
)

HTML.write_text(src, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))