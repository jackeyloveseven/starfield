
# -*- coding: utf-8 -*-
"""v211 — 性能浮层接入统一语言（最后一个未改的 overlay）。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

CSS = N("""
/* 性能浮层 */
#sf-perf-hud{
  border-radius:0 !important;
  background:rgba(5,8,12,.94) !important;
  border:1px solid rgba(230,237,242,.12) !important;
  box-shadow:none !important;
  -webkit-backdrop-filter:none !important;backdrop-filter:none !important;
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;
  letter-spacing:.16em !important;
  line-height:1.9 !important;
  color:rgba(230,237,242,.62) !important;
  padding:10px 14px !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-perf">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('perf hud styled')
