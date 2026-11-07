
# -*- coding: utf-8 -*-
"""v193 — 弹弓提示去装饰符改灰阶；OTA 按钮去蓝色与星标。"""
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
    assert src.count(o) == 1, tag + ' count=' + str(src.count(o))
    src = src.replace(o, n)
    log.append(tag)


rep('toast-text',
    '<div id="slingshot-toast">\u2726 \u5f15\u529b\u5f39\u5f13\u52a0\u901f\u9501\u5b9a \u00b7 \u822a\u901f\u6fc0\u589e \u2726</div>',
    '<div id="slingshot-toast">\u5f15\u529b\u5f39\u5f13\u52a0\u901f\u9501\u5b9a \u00b7 \u822a\u901f\u6fc0\u589e</div>')

rep('ota-btn',
    '<button class="photo-btn active" id="btn-check-ota" style="padding: 2px 8px; color: #88c0d0;">\u68c0\u67e5\u66f4\u65b0 \u2726</button>',
    '<button class="photo-btn active" id="btn-check-ota" style="padding: 2px 8px;">\u68c0\u67e5\u66f4\u65b0</button>')

CSS = N("""
/* 弹弓提示：去装饰符，灰阶细字 */
#slingshot-toast{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;
  letter-spacing:.30em !important;
  font-weight:400 !important;
  color:rgba(230,237,242,.82) !important;
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
  text-shadow:0 1px 10px rgba(0,0,0,.92) !important;
  padding:0 !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-toast">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
