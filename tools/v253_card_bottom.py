
# -*- coding: utf-8 -*-
"""v253 - 重构卡面底部：引导挪进卡面信息区、关闭键挪到操作栏之上、
   操作栏改成无边框的通栏三段。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

CSS = """
/* ============================================================
   卡面底部重构
   原问题：
     1) 引导文字 fixed bottom+128px，正好压在 sf-card-info 的规格行上
     2) sf-hatch-close fixed bottom+12px，被 58px 高的操作栏切开一半
     3) 操作栏带上下边框 + 半透明底，像一块贴在画面上的板子
   ============================================================ */

/* --- 1. 操作栏：去掉板子感，改成贴着画面底部的三段文字 --- */
#sf-hatch .sf-card-actions{
  position:fixed !important;
  left:0 !important; right:0 !important;
  bottom:0 !important;
  width:100% !important;
  max-width:none !important;
  height:auto !important;
  min-height:0 !important;
  display:flex !important;
  gap:0 !important;
  transform:none !important;
  border:0 !important;
  background:linear-gradient(to top,
    rgba(5,8,12,.96) 0%, rgba(5,8,12,.88) 55%, rgba(5,8,12,0) 100%) !important;
  padding:22px 0 calc(env(safe-area-inset-bottom,0px) + 26px) !important;
  box-sizing:border-box !important;
  z-index:46 !important;
}
#sf-hatch .sf-card-act-btn{
  flex:1 1 0 !important;
  height:auto !important;
  min-height:0 !important;
  padding:14px 6px !important;
  font-size:12px !important;
  letter-spacing:.10em !important;
  font-weight:500 !important;
  color:rgba(236,242,248,.72) !important;
  background:none !important;
  border:0 !important;
  border-radius:0 !important;
  display:flex !important;
  align-items:center !important;
  justify-content:center !important;
  line-height:1.2 !important;
  transition:color .2s ease !important;
  -webkit-tap-highlight-color:transparent !important;
}
#sf-hatch .sf-card-act-btn:active{
  color:#fff !important;
  background:none !important;
}
#sf-hatch .sf-card-act-btn.primary{
  color:var(--tier,#f4d06f) !important;
  font-weight:600 !important;
}
#sf-hatch .sf-card-act-btn.primary::before{
  content:"";
  width:4px;height:4px;border-radius:50%;
  background:currentColor;
  margin-right:7px;
  flex:none;
  animation:sfDotPulse 1.9s ease-in-out infinite;
}
/* 三段之间的发丝分隔 */
#sf-hatch .sf-card-act-btn + .sf-card-act-btn{
  box-shadow:inset 1px 0 0 rgba(230,237,242,.10) !important;
}

/* --- 2. 引导：从 fixed 挪进卡面信息流，紧跟规格行之后 --- */
#sf-hatch .sf-card-guide{
  position:static !important;
  left:auto !important; bottom:auto !important;
  transform:none !important;
  margin:14px auto 0 auto !important;
  padding:0 !important;
  background:none !important;
  font-family:var(--ui-mono,monospace) !important;
  font-size:8.5px !important;
  letter-spacing:.24em !important;
  line-height:1.6 !important;
  color:rgba(230,237,242,.38) !important;
  white-space:normal !important;
  text-align:center !important;
  max-width:78vw !important;
  pointer-events:none !important;
  opacity:0;
  animation:sfGuideIn .7s var(--ui-ease,ease) 1.05s forwards !important;
}
#sf-hatch .sf-card-guide b{
  color:rgba(240,245,250,.80) !important;
  font-weight:500 !important;
}
@keyframes sfGuideIn{
  from{opacity:0}
  to{opacity:1}
}

/* --- 3. 关闭键：挪到操作栏正上方，不再被切 --- */
#sf-hatch .sf-hatch-close{
  position:fixed !important;
  left:50% !important;
  transform:translateX(-50%) !important;
  bottom:calc(env(safe-area-inset-bottom,0px) + 96px) !important;
  top:auto !important; right:auto !important;
  border:0 !important;
  background:none !important;
  padding:6px 0 !important;
  font-family:var(--ui-mono,monospace) !important;
  font-size:8px !important;
  letter-spacing:.30em !important;
  color:rgba(230,237,242,.30) !important;
  z-index:47 !important;
  transition:color .2s ease !important;
}
#sf-hatch .sf-hatch-close:hover{ color:rgba(230,237,242,.72) !important; }

/* --- 4. 卡面信息区：给底部操作栏让出空间 --- */
#sf-hatch .sf-card-info{
  bottom:calc(env(safe-area-inset-bottom,0px) + 132px) !important;
  padding:0 26px !important;
  gap:8px !important;
}

@media (max-width:420px){
  #sf-hatch .sf-card-act-btn{
    font-size:11px !important;
    letter-spacing:.06em !important;
    padding:13px 4px !important;
  }
  #sf-hatch .sf-card-guide{ font-size:8px !important; letter-spacing:.18em !important; }
  #sf-hatch .sf-card-info{ bottom:calc(env(safe-area-inset-bottom,0px) + 126px) !important; }
}
"""

head_end = html.find('</head>')
assert head_end > 0
html = html[:head_end] + '\n<style id="sf-ui-card-bottom">' + CSS + '</style>\n' + html[head_end:]

# 引导 DOM：从 root 挪到 card-info 里
old = """    var guide = el('div', 'sf-card-guide');
    guide.innerHTML = '\\u70b9\\u51fb\\u5361\\u9762\\u7ffb\\u9762 \\u00b7 \\u6216\\u7528\\u4e0b\\u65b9 <b>\\u4e09\\u4e2a\\u6309\\u94ae</b>';
    root.appendChild(guide);

    orb = card.querySelector('.sf-hatch-orb');"""
new = """    orb = card.querySelector('.sf-hatch-orb');"""
assert html.count(old) == 1, 'guide remove count=%d' % html.count(old)
html = html.replace(old, new)

# 在 card-info 之后插入引导
old2 = """    nameEl = card.querySelector('.sf-hatch-name');"""
new2 = """    var infoBox = card.querySelector('.sf-card-info');
    if (infoBox) {
      var guide = el('div', 'sf-card-guide');
      guide.innerHTML = '\\u70b9\\u51fb\\u5361\\u9762\\u7ffb\\u9762\\u67e5\\u770b\\u5929\\u6587\\u6863\\u6848 \\u00b7 \\u4e0b\\u65b9\\u4e09\\u4e2a\\u6309\\u94ae\\u76f4\\u63a5\\u64cd\\u4f5c';
      infoBox.appendChild(guide);
    }

    nameEl = card.querySelector('.sf-hatch-name');"""
assert html.count(old2) == 1, 'info anchor count=%d' % html.count(old2)
html = html.replace(old2, new2)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('card bottom restructured')
