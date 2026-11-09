
# -*- coding: utf-8 -*-
"""v288 - 演化注记时序修正。"""
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

rep("""    /* 演化注记：让它"等你回来"被看见 */
    if (infoBox && window.SFEvolution && cur) {
      var evo = el('div', 'sf-card-evolution');
      evo.textContent = window.SFEvolution.elapsedText(cur) + ' \\u00b7 ' + window.SFEvolution.note(cur);
      infoBox.appendChild(evo);
    }""",
    """    /* 演化注记：build() 先于 cur=item 执行，文本在 openFor 里填 */
    if (infoBox) {
      evoEl = el('div', 'sf-card-evolution');
      infoBox.appendChild(evoEl);
    }""",
    'buildEmpty')

rep("    nameEl.textContent = item.name;",
    """    if (evoEl && window.SFEvolution) {
      evoEl.textContent = window.SFEvolution.elapsedText(item) + ' \\u00b7 ' + window.SFEvolution.note(item);
    }
    nameEl.textContent = item.name;""",
    'fill')

rep("var root=null, card=null, orb=null, nameEl=null, metaEl=null, specsEl=null, serialEl=null, tierBadgeEl=null;",
    "var root=null, card=null, orb=null, nameEl=null, metaEl=null, specsEl=null, serialEl=null, tierBadgeEl=null, evoEl=null;",
    'decl')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
