
# -*- coding: utf-8 -*-
"""v257 - 「收入天象馆」下移，与引导拉开；引导上提一点。"""
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

# 关闭键再往下（贴近操作栏），引导往上
rep("  bottom:calc(env(safe-area-inset-bottom,0px) + 102px) !important;",
    "  bottom:calc(env(safe-area-inset-bottom,0px) + 92px) !important;",
    'closePos')
rep("  margin:16px auto 0 auto !important;",
    "  margin:13px auto 0 auto !important;",
    'guideMargin')
# 信息区整体上提，给关闭键留位置
rep("""#sf-hatch .sf-card-info{
  bottom:calc(env(safe-area-inset-bottom,0px) + 132px) !important;
  padding:0 26px !important;
  gap:8px !important;
}""",
    """#sf-hatch .sf-card-info{
  bottom:calc(env(safe-area-inset-bottom,0px) + 138px) !important;
  padding:0 26px !important;
  gap:7px !important;
}""",
    'infoBox')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
