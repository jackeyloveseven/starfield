
# -*- coding: utf-8 -*-
"""v173 — 起航页加压暗层，保证文字在任意背景上可读。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

anchor = N("""/* ---------- 起航点：胶囊 → 下方发丝下划线 ---------- */""")
add = N("""/* ---------- 起航页压暗：UI 必须在任意随机背景上都读得清 ---------- */
#intro::after{
  content:"";position:absolute;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 68% 52% at 50% 46%,
      rgba(5,9,14,.78) 0%, rgba(5,9,14,.52) 52%, rgba(5,9,14,.16) 78%, transparent 100%),
    linear-gradient(to bottom,
      rgba(5,9,14,.70) 0%, rgba(5,9,14,.10) 26%,
      rgba(5,9,14,.10) 66%, rgba(5,9,14,.82) 100%);
}
#intro .intro-inner{position:relative;z-index:1}

/* ---------- 起航点：胶囊 → 下方发丝下划线 ---------- */""")

assert src.count(anchor) == 1
src = src.replace(anchor, add)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('scrim added')
