
# -*- coding: utf-8 -*-
"""v254 - 操作栏被父级 transform 影响（left:0 失效），改用 left:50%+translateX。"""
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

# 操作栏：left/right 在含 transform 的祖先里不可靠，用 50% + translateX(-50%)
rep("""#sf-hatch .sf-card-actions{
  position:fixed !important;
  left:0 !important; right:0 !important;
  bottom:0 !important;
  width:100% !important;""",
    """#sf-hatch .sf-card-actions{
  position:fixed !important;
  left:50% !important; right:auto !important;
  transform:translateX(-50%) !important;
  bottom:0 !important;
  width:100vw !important;""",
    'actionsPos')

# 引导已进信息流，去掉旧的 fixed 残留（若还有）
rep("""#sf-hatch .sf-hatch-close{
  position:fixed !important;
  left:50% !important;
  transform:translateX(-50%) !important;
  bottom:calc(env(safe-area-inset-bottom,0px) + 96px) !important;""",
    """#sf-hatch .sf-hatch-close{
  position:fixed !important;
  left:50% !important;
  transform:translateX(-50%) !important;
  bottom:calc(env(safe-area-inset-bottom,0px) + 108px) !important;""",
    'closePos')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
