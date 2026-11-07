
# -*- coding: utf-8 -*-
"""v194 — 完整度指示条去青绿，改灰阶发丝。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* 完整度条：灰阶发丝，去掉青绿渐变 */
#sf-hull .t{
  background:rgba(230,237,242,.16) !important;
  background-image:none !important;
  border-radius:0 !important;
  height:1px !important;
  align-self:center !important;
}
#sf-hull .t > *{
  background:rgba(230,237,242,.72) !important;
  background-image:none !important;
  border-radius:0 !important;
}
#sf-hull .k{
  font-family:var(--ui-mono) !important;
  letter-spacing:.20em !important;
  color:rgba(230,237,242,.40) !important;
}
#sf-hull .v{
  font-family:var(--ui-mono) !important;
  letter-spacing:.16em !important;
  color:rgba(230,237,242,.72) !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-hull">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('hull bar greyed')
