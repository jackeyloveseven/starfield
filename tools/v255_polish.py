
# -*- coding: utf-8 -*-
"""v255 - 分隔线缩短；关闭键与引导拉开距离。"""
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

# 分隔线：从「贯穿整栏」改成「居中 22px 短线」
rep("""#sf-hatch .sf-card-act-btn + .sf-card-act-btn{
  box-shadow:inset 1px 0 0 rgba(230,237,242,.10) !important;
}""",
    """#sf-hatch .sf-card-act-btn + .sf-card-act-btn{
  position:relative !important;
}
#sf-hatch .sf-card-act-btn + .sf-card-act-btn::before{
  content:"";
  position:absolute;
  left:0; top:50%;
  transform:translateY(-50%);
  width:1px; height:18px;
  background:rgba(230,237,242,.12);
  pointer-events:none;
}""",
    'divider')

# 关闭键下移到操作栏上方，与引导拉开
rep("  bottom:calc(env(safe-area-inset-bottom,0px) + 108px) !important;",
    "  bottom:calc(env(safe-area-inset-bottom,0px) + 102px) !important;",
    'closePos')

# 引导与信息区之间加间距
rep("""  margin:14px auto 0 auto !important;""",
    """  margin:16px auto 0 auto !important;""",
    'guideMargin')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
