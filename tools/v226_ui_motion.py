
# -*- coding: utf-8 -*-
"""v226 — 动效补齐：列表项 stagger 入场（恢复动画）、面板打开位移、卡片入场。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new):
    global src
    o, n = N(old), N(new)
    assert src.count(o) == 1, tag
    src = src.replace(o, n)
    log.append(tag)


# 1) 反向掉 v178 里「animation:none」这句，换成 stagger 入场
rep('row-anim',
    "  animation:none !important;\n  position:relative !important;",
    "  animation:sfRowIn .62s var(--ui-ease) both !important;\n  position:relative !important;")

CSS = N("""
/* ---------- 入场动效：全站统一的 stagger ---------- */
@keyframes sfRowIn{
  from{opacity:0;transform:translateY(10px)}
  to{opacity:1;transform:none}
}
@keyframes sfPanelIn{
  from{opacity:0;transform:translateY(12px)}
  to{opacity:1;transform:none}
}

#sf-hatch-list .sf-hl-item:nth-child(1){animation-delay:0s}
#sf-hatch-list .sf-hl-item:nth-child(2){animation-delay:.045s}
#sf-hatch-list .sf-hl-item:nth-child(3){animation-delay:.09s}
#sf-hatch-list .sf-hl-item:nth-child(4){animation-delay:.135s}
#sf-hatch-list .sf-hl-item:nth-child(5){animation-delay:.18s}
#sf-hatch-list .sf-hl-item:nth-child(6){animation-delay:.225s}
#sf-hatch-list .sf-hl-item:nth-child(7){animation-delay:.27s}
#sf-hatch-list .sf-hl-item:nth-child(8){animation-delay:.315s}
#sf-hatch-list .sf-hl-item:nth-child(n+9){animation-delay:.34s}

/* 面板本体：淡入 + 轻微上浮 */
#codex-modal .codex-container,
#hangar-modal .hangar-container{
  animation:sfPanelIn .5s var(--ui-ease) both;
}
#codex-modal:not(.open) .codex-container,
#hangar-modal:not(.open) .hangar-container{
  animation:none;
}

/* 图鉴 / 折纸坞的卡片也要 stagger */
#codex-modal .codex-card{
  animation:sfRowIn .56s var(--ui-ease) both;
}
#codex-modal .codex-card:nth-child(1){animation-delay:0s}
#codex-modal .codex-card:nth-child(2){animation-delay:.03s}
#codex-modal .codex-card:nth-child(3){animation-delay:.06s}
#codex-modal .codex-card:nth-child(4){animation-delay:.09s}
#codex-modal .codex-card:nth-child(5){animation-delay:.12s}
#codex-modal .codex-card:nth-child(6){animation-delay:.15s}
#codex-modal .codex-card:nth-child(n+7){animation-delay:.18s}

#hangar-modal .hangar-card{
  animation:sfRowIn .56s var(--ui-ease) both;
}
#hangar-modal .hangar-card:nth-child(1){animation-delay:.02s}
#hangar-modal .hangar-card:nth-child(2){animation-delay:.06s}
#hangar-modal .hangar-card:nth-child(3){animation-delay:.10s}
#hangar-modal .hangar-card:nth-child(4){animation-delay:.14s}
#hangar-modal .hangar-card:nth-child(n+5){animation-delay:.17s}

/* 设置抽屉的分节逐条浮入 */
#settings-drawer.open .settings-section{
  animation:sfRowIn .5s var(--ui-ease) both;
}
#settings-drawer.open .settings-section:nth-child(1){animation-delay:0s}
#settings-drawer.open .settings-section:nth-child(2){animation-delay:.06s}
#settings-drawer.open .settings-section:nth-child(3){animation-delay:.12s}
#settings-drawer.open .settings-section:nth-child(4){animation-delay:.18s}
#settings-drawer.open .settings-section:nth-child(n+5){animation-delay:.22s}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-motion">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log), '+ motion layer')
