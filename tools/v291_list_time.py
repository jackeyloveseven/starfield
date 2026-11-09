
# -*- coding: utf-8 -*-
"""v291 - 天象馆相对时间 + 植被生长。"""
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

rep("    /* 演化注记：让「等你回来」被看见，而不是只变几个像素 */",
    """    /* 列表用的短形式 */
    shortText: function (item) {
      var h = hours(item);
      if (h < 1) return Math.max(1, Math.round(h * 60)) + ' \\u5206\\u949f\\u524d';
      if (h < 48) return Math.round(h) + ' \\u5c0f\\u65f6\\u524d';
      return Math.floor(h / 24) + ' \\u5929\\u524d';
    },

    /* 植被随时间缓慢恢复/扩张，有上限 */
    treeGrowth: function (item, base) {
      var d = this.days(item);
      return Math.round(base + Math.min(d * 12, base * 0.6));
    },

    /* 演化注记：让「等你回来」被看见，而不是只变几个像素 */""",
    'evoFns')

OLD = '<div class="sf-hl-date">$' + "{it.at || ''}</div>"
NEW = '<div class="sf-hl-date">$' + "{window.SFEvolution ? window.SFEvolution.shortText(it) : (it.at || '')}</div>"
rep(OLD, NEW, 'listDate')

rep("      treeCount: L.trees,",
    "      treeCount: (window.SFEvolution ? window.SFEvolution.treeGrowth(item, L.trees) : L.trees),",
    'treeGrowth')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
