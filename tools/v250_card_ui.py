
# -*- coding: utf-8 -*-
"""v250 - 卡面按钮放大 + 引导提示。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

CSS = """
/* ============================================================
   卡面操作区：放大到可点，并给出明确引导
   ============================================================ */
#sf-hatch .sf-card-actions{
  position:fixed !important;
  left:50% !important;
  bottom:calc(env(safe-area-inset-bottom,0px) + 30px) !important;
  width:min(430px,90vw) !important;
  height:auto !important;
  min-height:56px !important;
  display:flex !important;
  gap:0 !important;
  transform:translateX(-50%) !important;
  border-top:1px solid rgba(230,237,242,.14) !important;
  border-bottom:1px solid rgba(230,237,242,.06) !important;
  background:rgba(6,9,13,.94) !important;
  z-index:46 !important;
}
#sf-hatch .sf-card-act-btn{
  flex:1 !important;
  height:56px !important;
  min-height:56px !important;
  font-size:11px !important;
  letter-spacing:.20em !important;
  font-weight:500 !important;
  color:rgba(240,245,250,.78) !important;
  background:none !important;
  border:0 !important;
  border-radius:0 !important;
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  transition:background .2s ease, color .2s ease !important;
}
#sf-hatch .sf-card-act-btn:active{
  background:rgba(255,255,255,.10) !important;
  color:#fff !important;
}
#sf-hatch .sf-card-act-btn.primary{
  color:var(--tier,#f4d06f) !important;
  font-weight:600 !important;
}
#sf-hatch .sf-card-act-btn.primary::before{
  content:"";
  width:5px;height:5px;border-radius:50%;
  background:currentColor;
  margin-right:8px;
  animation:sfDotPulse 1.9s ease-in-out infinite;
}
@keyframes sfDotPulse{
  0%,100%{opacity:.45;transform:scale(.8)}
  50%{opacity:1;transform:scale(1.25)}
}

/* 引导提示：按钮上方一行，淡入后停留 */
#sf-hatch .sf-card-guide{
  position:fixed;
  left:50%;
  bottom:calc(env(safe-area-inset-bottom,0px) + 96px);
  transform:translateX(-50%);
  font-family:var(--ui-mono,monospace);
  font-size:9px;
  letter-spacing:.26em;
  color:rgba(230,237,242,.46);
  white-space:nowrap;
  pointer-events:none;
  z-index:46;
  opacity:0;
  animation:sfGuideIn .7s var(--ui-ease,ease) .9s forwards;
}
#sf-hatch .sf-card-guide b{
  color:rgba(240,245,250,.86);
  font-weight:500;
}
@keyframes sfGuideIn{
  from{opacity:0;transform:translate(-50%,8px)}
  to{opacity:1;transform:translate(-50%,0)}
}

@media (max-width:420px){
  #sf-hatch .sf-card-actions{ width:94vw !important; }
  #sf-hatch .sf-card-act-btn{ font-size:10px !important; letter-spacing:.14em !important; }
  #sf-hatch .sf-card-guide{ font-size:8px; letter-spacing:.18em; }
}
"""

head_end = html.find('</head>')
assert head_end > 0
html = html[:head_end] + '\n<style id="sf-ui-card-actions">' + CSS + '</style>\n' + html[head_end:]

# 插入引导 DOM
old = """    orb = card.querySelector('.sf-hatch-orb');"""
new = """    var guide = el('div', 'sf-card-guide');
    guide.innerHTML = '\\u70b9\\u51fb\\u5361\\u9762\\u7ffb\\u9762 \\u00b7 \\u6216\\u7528\\u4e0b\\u65b9 <b>\\u4e09\\u4e2a\\u6309\\u94ae</b>';
    root.appendChild(guide);

    orb = card.querySelector('.sf-hatch-orb');"""
assert html.count(old) == 1, 'guide anchor count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('card actions enlarged + guide added')
