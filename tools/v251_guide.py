
# -*- coding: utf-8 -*-
"""v251 - 引导文字上移，避开规格行。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """  bottom:calc(env(safe-area-inset-bottom,0px) + 96px);"""
new = """  bottom:calc(env(safe-area-inset-bottom,0px) + 128px);"""
assert html.count(old) == 1
html = html.replace(old, new)

# 加背景衬托，避免压在文字上
old2 = """  pointer-events:none;
  z-index:46;
  opacity:0;
  animation:sfGuideIn .7s var(--ui-ease,ease) .9s forwards;"""
new2 = """  pointer-events:none;
  z-index:46;
  padding:5px 12px;
  background:rgba(6,9,13,.72);
  opacity:0;
  animation:sfGuideIn .7s var(--ui-ease,ease) .9s forwards;"""
assert html.count(old2) == 1
html = html.replace(old2, new2)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('guide repositioned')
