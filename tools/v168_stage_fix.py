
# -*- coding: utf-8 -*-
"""v168 — 重写全屏舞台：用直接子选择器压过入场规则，重排四角。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

start = src.find(N('<style id="sf-hatch-stage-css">'))
end = src.find(N('</style>'), start)
assert start > 0 and end > start

CSS = N("""
/* ============================================================
   全屏舞台：没有卡片，画面本身就是卡（v168）
   ============================================================ */
#sf-hatch{perspective:none}

#sf-hatch .sf-hatch-card{
  width:100%;height:100%;max-width:none;aspect-ratio:auto;
  background:none;border:0;border-radius:0;box-shadow:none;
  padding:0;overflow:visible;transform:none!important;
  transform-style:flat;
}
#sf-hatch .sf-hatch-card:active{transform:none!important}
#sf-hatch .sf-hatch-card::before,
#sf-hatch .sf-hatch-card::after{content:none!important}
#sf-hatch .sf-hatch-card .sf-card-holo,
#sf-hatch .sf-hatch-card .sf-hatch-back{display:none!important}

/* 顶部：编号 / 星历 / 品阶 */
#sf-hatch .sf-hatch-card > .sf-card-header{
  position:fixed;top:calc(env(safe-area-inset-top,0px) + 40px);
  left:40px;right:40px;height:auto;padding:0;
  display:flex;align-items:baseline;justify-content:space-between;
  transform:none!important;
}
#sf-hatch .sf-hatch-card > .sf-card-serial,
#sf-hatch .sf-card-header .sf-card-serial{
  font-size:9px;line-height:1;letter-spacing:.32em;color:rgba(255,255,255,.28);
}
#sf-hatch .sf-card-header .sf-card-tier-badge{
  font-size:9px;line-height:1;letter-spacing:.32em;
  color:var(--tier,#fff)!important;
}
#sf-hatch .sf-hatch-card > .sf-card-coords{
  position:fixed;top:calc(env(safe-area-inset-top,0px) + 66px);
  left:0;right:0;font-size:8px;line-height:1;letter-spacing:.30em;
  color:rgba(255,255,255,.18);transform:none!important;
}

/* 星球：屏幕正中偏上 */
#sf-hatch .sf-hatch-card > .sf-card-orb-stage{
  position:fixed;left:50%;top:43%;
  width:min(58vh,42vw);height:min(58vh,42vw);
  min-height:0;max-height:none;margin:0;padding:0;flex:none;
  transform:translate(-50%,-50%)!important;
}
#sf-hatch .sf-hatch-orb{width:100%;height:100%}

/* 名字块：球下 */
#sf-hatch .sf-hatch-card > .sf-card-info{
  position:fixed;left:0;right:0;
  bottom:calc(env(safe-area-inset-bottom,0px) + 112px);
  padding:0 28px;gap:10px;transform:none!important;
}
#sf-hatch .sf-hatch-name{
  font-size:36px;letter-spacing:.20em;line-height:1.12;
}
#sf-hatch .sf-hatch-meta{font-size:9px;letter-spacing:.32em}
#sf-hatch .sf-card-specs{font-size:8px;letter-spacing:.28em;margin-top:9px}
#sf-hatch .sf-hatch-hint{margin-top:12px;letter-spacing:.34em;font-size:8px}

/* 动作：底部一条细线 */
#sf-hatch .sf-hatch-card > .sf-card-actions{
  position:fixed;left:50%;
  bottom:calc(env(safe-area-inset-bottom,0px) + 46px);
  width:min(430px,88vw);height:36px;
  border-top:1px solid rgba(255,255,255,.10);
  transform:translateX(-50%)!important;
}
#sf-hatch .sf-card-act-btn{font-size:9px;letter-spacing:.26em;font-weight:500}

/* 关闭：最底一行细字，不与动作抢位 */
#sf-hatch .sf-hatch-close{
  position:fixed;left:50%;transform:translateX(-50%);
  bottom:calc(env(safe-area-inset-bottom,0px) + 12px);
  top:auto;right:auto;
  border:0;background:none;padding:6px 0;
  font-size:8px;letter-spacing:.30em;color:rgba(255,255,255,.34);
}
#sf-hatch .sf-hatch-close:hover{color:rgba(255,255,255,.75)}

/* 入场：只做显影，不做位移（位移会打架） */
#sf-hatch .sf-hatch-card > .sf-card-header,
#sf-hatch .sf-hatch-card > .sf-card-coords,
#sf-hatch .sf-hatch-card > .sf-card-orb-stage,
#sf-hatch .sf-hatch-card > .sf-card-info,
#sf-hatch .sf-hatch-card > .sf-card-actions{
  opacity:0;filter:blur(6px);
}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-header,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-coords,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-orb-stage,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-info,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-actions{
  opacity:1;filter:blur(0);
  transition:opacity .9s cubic-bezier(.16,1,.3,1),filter .9s cubic-bezier(.16,1,.3,1);
}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-header{transition-delay:0s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-coords{transition-delay:.08s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-orb-stage{transition-delay:.16s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-info{transition-delay:.30s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-actions{transition-delay:.42s}

@media (max-width:520px){
  #sf-hatch .sf-hatch-card > .sf-card-header{
    left:24px;right:24px;top:calc(env(safe-area-inset-top,0px) + 30px);
  }
  #sf-hatch .sf-hatch-card > .sf-card-coords{
    top:calc(env(safe-area-inset-top,0px) + 52px);
    font-size:7.5px;letter-spacing:.22em;
  }
  #sf-hatch .sf-hatch-card > .sf-card-orb-stage{
    width:min(44vh,74vw);height:min(44vh,74vw);top:41%;
  }
  #sf-hatch .sf-hatch-card > .sf-card-info{
    bottom:calc(env(safe-area-inset-bottom,0px) + 104px);padding:0 22px;
  }
  #sf-hatch .sf-hatch-name{font-size:26px;letter-spacing:.16em}
  #sf-hatch .sf-hatch-meta{font-size:8px;letter-spacing:.24em}
  #sf-hatch .sf-card-specs{font-size:7.5px;letter-spacing:.20em}
  #sf-hatch .sf-hatch-card > .sf-card-actions{width:92vw;height:34px;
    bottom:calc(env(safe-area-inset-bottom,0px) + 44px)}
  #sf-hatch .sf-card-act-btn{font-size:8.5px;letter-spacing:.18em}
}
""")

src = src[:start] + N('<style id="sf-hatch-stage-css">') + CSS + N('</style>') + src[end + len(N('</style>')):]
with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('stage css rewritten', len(CSS))
