
# -*- coding: utf-8 -*-
"""v287 - 卡面显示演化注记：N 小时前点亮 · 它仍在自转。"""
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

rep("""    var infoBox = card.querySelector('.sf-card-info');
    if (infoBox) {""",
    """    var infoBox = card.querySelector('.sf-card-info');
    /* 演化注记：让它"等你回来"被看见 */
    if (infoBox && window.SFEvolution && cur) {
      var evo = el('div', 'sf-card-evolution');
      evo.textContent = window.SFEvolution.elapsedText(cur) + ' \\u00b7 ' + window.SFEvolution.note(cur);
      infoBox.appendChild(evo);
    }
    if (infoBox) {""",
    'evo')

CSS = """
/* 演化注记：比规格行更淡，但是时间维度唯一的出口 */
#sf-hatch .sf-card-evolution{
  margin-top:9px;
  font-family:var(--ui-mono,monospace);
  font-size:8.5px;
  letter-spacing:.22em;
  line-height:1.6;
  color:rgba(200,214,228,.42);
  text-align:center;
  opacity:0;
  animation:sfGuideIn .8s var(--ui-ease,ease) .75s forwards;
}
#sf-hatch .sf-card-evolution::before{
  content:"";
  display:inline-block;
  width:4px;height:4px;border-radius:50%;
  background:rgba(200,214,228,.5);
  margin-right:7px;
  vertical-align:middle;
}
"""

head_end = html.find('</head>')
assert head_end > 0
html = html[:head_end] + '\n<style id="sf-ui-evolution">' + CSS + '</style>\n' + html[head_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
