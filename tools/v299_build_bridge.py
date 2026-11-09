
# -*- coding: utf-8 -*-
"""v299 - 渐进式建设（一）：桥接累计专注分钟 + 收藏时记录出生点。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 1) completeMission 里把累计值写到独立 key，供任何模块读取
rep("this.stats.totalFocusMinutes += focusedMinutes;",
    """this.stats.totalFocusMinutes += focusedMinutes;
    /* 桥接到独立 key：收藏与渲染都要读它来算"建设度" */
    try { localStorage.setItem('sf_total_focus_v1', String(this.stats.totalFocusMinutes)); } catch (e) {}""",
    'bridge')

# 2) 收藏时记录"出生时的累计专注"
rep("at: new Date().toISOString().slice(0, 10), ts: Date.now(),",
    """at: new Date().toISOString().slice(0, 10), ts: Date.now(),
    focusAtBirth: (function(){ try { return parseInt(localStorage.getItem('sf_total_focus_v1')||'0',10)||0; } catch(e){ return 0; } })(),""",
    'birth')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
