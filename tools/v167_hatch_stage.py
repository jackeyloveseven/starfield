
# -*- coding: utf-8 -*-
"""v167 — 开卡改为全屏舞台：取消了卡片容器（背景/边框/阴影/圆角），
   星球居中、文字散布在屏幕边缘，动作变成底部一条细线。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* ============================================================
   全屏舞台：取消卡片容器。画面本身就是卡（v167）
   ============================================================ */
#sf-hatch .sf-hatch-card{
  width:100%;height:100%;
  max-width:none;aspect-ratio:auto;
  background:none;border:0;border-radius:0;box-shadow:none;
  padding:0;overflow:visible;
  transform:none;
}
#sf-hatch .sf-hatch-card:active{transform:none}
#sf-hatch .sf-hatch-card::before,
#sf-hatch .sf-hatch-card::after{content:none!important}
#sf-hatch .sf-hatch-card .sf-card-holo,
#sf-hatch .sf-hatch-card .sf-hatch-back{display:none!important}

#sf-hatch .sf-card-header{
  position:fixed;top:calc(env(safe-area-inset-top,0px) + 38px);
  left:38px;right:38px;height:auto;padding:0;
  display:flex;align-items:baseline;justify-content:space-between;
}
#sf-hatch .sf-card-serial{font-size:9px;letter-spacing:.30em;color:rgba(255,255,255,.30)}
#sf-hatch .sf-card-tier-badge{font-size:9px;letter-spacing:.30em;color:var(--tier,#fff)!important}
#sf-hatch .sf-card-coords{
  position:fixed;top:calc(env(safe-area-inset-top,0px) + 60px);
  left:0;right:0;font-size:8px;letter-spacing:.30em;
  color:rgba(255,255,255,.20);
}

#sf-hatch .sf-card-orb-stage{
  position:fixed;left:50%;top:44%;
  transform:translate(-50%,-50%);
  width:min(64vh,78vw);height:min(64vh,78vw);
  min-height:0;max-height:none;margin:0;padding:0;flex:none;
}
#sf-hatch .sf-hatch-orb{width:100%;height:100%}

#sf-hatch .sf-card-info{
  position:fixed;left:0;right:0;
  bottom:calc(env(safe-area-inset-bottom,0px) + 104px);
  padding:0 28px;gap:10px;
}
#sf-hatch .sf-hatch-name{font-size:34px;letter-spacing:.18em;line-height:1.16}
#sf-hatch .sf-hatch-meta{font-size:9px;letter-spacing:.30em}
#sf-hatch .sf-card-specs{font-size:8px;letter-spacing:.26em;margin-top:8px}
#sf-hatch .sf-hatch-hint{margin-top:12px;letter-spacing:.34em;font-size:8px}

#sf-hatch .sf-card-actions{
  position:fixed;left:50%;
  bottom:calc(env(safe-area-inset-bottom,0px) + 34px);
  transform:translateX(-50%);
  width:min(430px,88vw);height:38px;
  border-top:1px solid rgba(255,255,255,.10);
}
#sf-hatch .sf-card-act-btn{
  font-size:9px;letter-spacing:.26em;font-weight:500;
}
#sf-hatch .sf-hatch-close{
  top:calc(env(safe-area-inset-top,0px) + 32px);right:38px;
  font-size:8px;letter-spacing:.28em;padding:10px 0;
  border:0;border-bottom:1px solid rgba(255,255,255,.16);background:none;
}
#sf-hatch .sf-hatch-close:hover{border-bottom-color:rgba(255,255,255,.45)}

@media (max-width:520px){
  #sf-hatch .sf-card-header{left:24px;right:24px}
  #sf-hatch .sf-card-coords{font-size:7.5px;letter-spacing:.24em}
  #sf-hatch .sf-hatch-name{font-size:27px}
  #sf-hatch .sf-card-orb-stage{width:min(52vh,74vw);height:min(52vh,74vw);top:42%}
  #sf-hatch .sf-card-info{bottom:calc(env(safe-area-inset-bottom,0px) + 92px)}
  #sf-hatch .sf-card-actions{width:92vw}
  #sf-hatch .sf-hatch-close{right:24px}
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N("<style id=\"sf-hatch-stage-css\">") + CSS + N("</style>\n\n") + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('stage css injected', len(CSS))
