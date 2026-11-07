
# -*- coding: utf-8 -*-
"""v219 — 起航页压暗层从 #intro::after 移到 #intro::before（z-index:-1）。
   ::after 设了 z-index:0，叠在 .intro-inner 之上；Chromium 里 pointer-events:none
   正常所以不挡触摸，iOS Safari 上伪元素的 pointer-events 偶发失效 -> 起航键点不到。
   移到 ::before 后与内容层无关，任何浏览器都不会遮挡。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

# 1) 删掉 ::after 整块（含 masthead 的 z-index 保留）
old_after = N("""#intro::after{
  content:"";position:absolute;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 68% 52% at 50% 46%,
      rgba(5,9,14,.78) 0%, rgba(5,9,14,.52) 52%, rgba(5,9,14,.16) 78%, transparent 100%),
    linear-gradient(to bottom,
      rgba(5,9,14,.34) 0%, rgba(5,9,14,.06) 22%,
      rgba(5,9,14,.06) 64%, rgba(5,9,14,.84) 100%);
}
#masthead{position:relative;z-index:6}""")
new_after = N("""#masthead{position:relative;z-index:6}

/* 起航页压暗：并入原有的 ::before（z-index:-1，永远在内容之下，不会遮挡触摸） */
#intro::before{
  background:
    radial-gradient(ellipse 68% 52% at 50% 46%,
      rgba(5,9,14,.78) 0%, rgba(5,9,14,.52) 52%, rgba(5,9,14,.16) 78%, transparent 100%),
    linear-gradient(to bottom,
      rgba(5,9,14,.34) 0%, rgba(5,9,14,.06) 22%,
      rgba(5,9,14,.06) 64%, rgba(5,9,14,.84) 100%),
    linear-gradient(90deg, transparent 36%, var(--soft) 80%) !important;
}""")
assert src.count(old_after) == 1, 'after block count=%d' % src.count(old_after)
src = src.replace(old_after, new_after)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('scrim moved: #intro::after -> #intro::before')
