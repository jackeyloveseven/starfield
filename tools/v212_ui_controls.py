
# -*- coding: utf-8 -*-
"""v212 — 桌面右侧控件列去胶囊；清掉四处 emoji。"""
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
    if c == 0 and optional:
        log.append(tag + ' SKIP')
        return
    assert c == 1, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


# --- emoji ---
rep('voice', "\U0001f399\ufe0f \u9886\u822a\u5458\u8bed\u97f3 (Voice)", "\u9886\u822a\u5458\u8bed\u97f3 (Voice)")
rep('ost',   "\U0001f3b5 \u539f\u521b\u661f\u6d77\u914d\u4e50 (Original OST)", "\u539f\u521b\u661f\u6d77\u914d\u4e50 (Original OST)")
rep('jukebox', "\U0001f3bc \u5019\u9e1f\u661f\u6d77 \u00b7 8\u9996\u5178\u85cf\u914d\u4e50 // SOUNDTRACK", "\u5019\u9e1f\u661f\u6d77 \u00b7 8\u9996\u5178\u85cf\u914d\u4e50", optional=True)
rep('planet-link', "\U0001f30d 3D\u751f\u6001\u661f\u7403\u68c0\u89c6 \u2197", "3D \u751f\u6001\u661f\u7403\u68c0\u89c6 \u2197", optional=True)

CSS = N("""
/* 桌面右侧控件列：胶囊 → 发丝 */
.control{
  border:0 !important;
  border-radius:0 !important;
  background:none !important;
  border-bottom:1px solid rgba(230,237,242,.14) !important;
  height:32px !important;
  padding:0 12px !important;
  font-family:var(--ui-mono) !important;
  font-size:9px !important;
  letter-spacing:.20em !important;
  color:rgba(230,237,242,.55) !important;
  opacity:1 !important;
  transition:color var(--ui-fast) var(--ui-ease),
             border-color var(--ui-fast) var(--ui-ease) !important;
}
.control:hover{
  color:#fff !important;
  border-bottom-color:rgba(230,237,242,.55) !important;
}
.control.active,
.control.on,
.control.is-on{
  color:#fff !important;
  border-bottom-color:rgba(230,237,242,.85) !important;
}
/* 纯图标键：细方框 */
#sound-toggle, #codex-toggle, #photo-toggle{
  border:1px solid rgba(230,237,242,.16) !important;
  border-bottom:1px solid rgba(230,237,242,.16) !important;
  width:34px !important;
  min-width:34px !important;
  height:34px !important;
  padding:0 !important;
}
#sound-toggle:hover, #codex-toggle:hover, #photo-toggle:hover{
  border-color:rgba(230,237,242,.5) !important;
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-controls">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
