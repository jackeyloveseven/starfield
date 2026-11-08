
# -*- coding: utf-8 -*-
"""v249 - 蓝闪去掉、震动收敛。"""
import re, sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 1. 奇异核：蓝 -> 白金
rep("background: radial-gradient(circle at 35% 35%, #fff 0%, #60a5fa 30%, #1e1b4b 70%, #000 100%);",
    "background: radial-gradient(circle at 35% 35%, #fff 0%, #e8dcc0 30%, #2a2418 70%, #000 100%);", 'coreColor')
rep("box-shadow: 0 0 45px rgba(96, 165, 250, 0.8), 0 0 100px rgba(147, 51, 234, 0.5), inset 0 0 20px #000;",
    "box-shadow: 0 0 40px rgba(232, 220, 192, 0.55), 0 0 90px rgba(180, 160, 120, 0.28), inset 0 0 20px #000;", 'coreGlow')
rep("border: 1px dotted rgba(96, 165, 250, 0.4);",
    "border: 1px dotted rgba(232, 220, 192, 0.32);", 'coreRing')

# 2. 震动：用正则整段替换
# 搜刮（高频）：删掉
pat_loot = re.compile(
    r"    if \(typeof navigator !== 'undefined' && \(navigator\.userActivation \? navigator\.userActivation\.hasBeenActive : true\) && navigator\.vibrate\) \{\n"
    r"      try \{ navigator\.vibrate\(\[40, 30, 60\]\); \} catch\(e\) \{\}\n    \}\n")
html, n1 = pat_loot.subn("    /* 搜刮是高频动作，不再震动 */\n", html)
log.append('vib-loot x%d' % n1)

# 弹弓：短促 18ms
pat_sling = re.compile(
    r"    if \(typeof navigator !== 'undefined' && \(navigator\.userActivation \? navigator\.userActivation\.hasBeenActive : true\) && navigator\.vibrate\) \{\n"
    r"      try \{ navigator\.vibrate\(\[60, 40, 100\]\); \} catch\(e\) \{\}\n    \}")
html, n2 = pat_sling.subn(
    "    if (typeof navigator !== 'undefined' && (navigator.userActivation ? navigator.userActivation.hasBeenActive : true) && navigator.vibrate) {\n"
    "      try { navigator.vibrate(18); } catch(e) {}\n    }", html)
log.append('vib-sling x%d' % n2)

# 激波：保留但收敛
pat_shock = re.compile(
    r"    if \(typeof navigator !== 'undefined' && \(navigator\.userActivation \? navigator\.userActivation\.hasBeenActive : true\) && navigator\.vibrate\) \{\n"
    r"      try \{ navigator\.vibrate\(\[80, 50, 140\]\); \} catch\(e\) \{\}\n    \}")
html, n3 = pat_shock.subn(
    "    /* 只有激波保留一次长震 */\n"
    "    if (typeof navigator !== 'undefined' && (navigator.userActivation ? navigator.userActivation.hasBeenActive : true) && navigator.vibrate) {\n"
    "      try { navigator.vibrate([45, 40, 85]); } catch(e) {}\n    }", html)
log.append('vib-shock x%d' % n3)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
