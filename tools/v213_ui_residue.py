
# -*- coding: utf-8 -*-
"""v213 — 清掉弹弓提示圆角、横屏按钮胶囊、剩余 3 处 emoji。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new, optional=False):
    global src
    o, n = N(old), N(new)
    c = src.count(o)
    if c != 1:
        if optional:
            log.append(tag + ' SKIP(' + str(c) + ')')
            return
        raise AssertionError(tag + ' count=' + str(c))
    src = src.replace(o, n)
    log.append(tag)


rep('sfx', "\U0001f680 \u5f15\u64ce\u4e0e\u7a7a\u95f4\u97f3\u6548 (SFX)", "\u5f15\u64ce\u4e0e\u7a7a\u95f4\u97f3\u6548 (SFX)", optional=True)
rep('track7', "\u26a1 7. \u5f8b\u653f\u72c2\u60f3", "7. \u5f8b\u653f\u72c2\u60f3", optional=True)
rep('track8', "\U0001f338 8. \u56db\u6708\u662f\u4f60\u7684\u8c0e\u8a00", "8. \u56db\u6708\u662f\u4f60\u7684\u8c0e\u8a00", optional=True)

CSS = N("""
/* 弹弓提示：圆角去掉 */
#slingshot-toast{
  border-radius:0 !important;
  background:none !important;
  border:0 !important;
}
/* 横屏切换键：胶囊 → 细框 */
#orientation-toggle-btn{
  border-radius:0 !important;
  background:none !important;
  border:1px solid rgba(230,237,242,.18) !important;
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;
  letter-spacing:.22em !important;
  color:rgba(230,237,242,.62) !important;
}
#orientation-toggle-btn:hover{
  color:#fff !important;
  border-color:rgba(230,237,242,.55) !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-controls2">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
