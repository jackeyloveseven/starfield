
# -*- coding: utf-8 -*-
"""v197 — 照片模式接入统一语言：白底/蓝底按钮改下划线，去圆角底色，红点改方点。"""
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


rep('export-emoji',
    '\U0001f4f7 \u5bfc\u51fa\u9ad8\u6e05\u58c1\u7eb8 (PNG)',
    '\u5bfc\u51fa\u9ad8\u6e05\u58c1\u7eb8 PNG',
    optional=True)

CSS = N("""
/* ============================================================
   深空摄影工坊（photo mode）
   ============================================================ */
#photo-ui .photo-title{
  font-family:var(--ui-mono) !important;
  font-size:9px !important;letter-spacing:.30em !important;
  color:rgba(230,237,242,.70) !important;
}
#photo-ui .photo-topbar i{
  width:5px !important;height:5px !important;
  border-radius:1px !important;
  background:rgba(230,237,242,.78) !important;
  box-shadow:none !important;
}
#photo-ui .photo-label{
  font-family:var(--ui-mono) !important;
  font-size:8.5px !important;letter-spacing:.24em !important;
  color:rgba(230,237,242,.34) !important;
}
#photo-ui .photo-stamp{
  font-family:var(--ui-mono) !important;
  font-size:8px !important;letter-spacing:.26em !important;
  color:rgba(230,237,242,.30) !important;
}
#photo-ui .photo-group{
  background:none !important;
  border:0 !important;
  border-left:1px solid rgba(230,237,242,.10) !important;
  border-radius:0 !important;
  padding:2px 0 2px 18px !important;
  box-shadow:none !important;
}
#photo-ui .photo-btn{
  background:none !important;
  border:0 !important;
  border-bottom:1px solid rgba(230,237,242,.13) !important;
  border-radius:0 !important;
  box-shadow:none !important;
  color:rgba(230,237,242,.52) !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;
  letter-spacing:.18em !important;
  padding:8px 12px !important;
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
#photo-ui .photo-btn:hover{
  color:rgba(230,237,242,.92) !important;
  border-bottom-color:rgba(230,237,242,.40) !important;
}
#photo-ui .photo-btn.active{
  background:none !important;
  color:#fff !important;
  border-bottom-color:rgba(230,237,242,.88) !important;
}
#photo-ui .photo-btn.primary{
  background:none !important;
  color:rgba(230,237,242,.92) !important;
  border-bottom-color:rgba(230,237,242,.55) !important;
}
#photo-ui .photo-btn.primary:hover{
  color:#fff !important;
  border-bottom-color:#fff !important;
}
#photo-ui .photo-frame-guide{
  border-color:rgba(230,237,242,.14) !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-photo">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
