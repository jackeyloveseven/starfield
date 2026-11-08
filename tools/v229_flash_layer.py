
# -*- coding: utf-8 -*-
"""v229 — 闪白改用独立层（#sf-hatch::after 被旧规则占用，伪元素方案失效）。"""
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
    assert src.count(o) == 1, tag + ' count=%d' % src.count(o)
    src = src.replace(o, n)
    log.append(tag)


rep('css',
    """#sf-hatch::after{
  content:"";position:absolute;inset:0;pointer-events:none;z-index:26;
  background:radial-gradient(circle at 50% 44%,
    #ffffff 0%, rgba(255,255,255,.92) 12%,
    rgba(255,255,255,.45) 26%, transparent 58%);
  opacity:0;transform:scale(.35);
}
#sf-hatch.sf-flash::after{
  animation:sfFlash .62s cubic-bezier(.15,.75,.2,1) forwards;
}""",
    """#sf-hatch .sf-flash-layer{
  position:absolute;inset:0;pointer-events:none;z-index:28;
  background:radial-gradient(circle at 50% 44%,
    #ffffff 0%, rgba(255,255,255,.94) 11%,
    rgba(255,251,235,.62) 24%, rgba(255,240,200,.22) 42%, transparent 62%);
  opacity:0;transform:scale(.35);
  mix-blend-mode:screen;
}
#sf-hatch.sf-flash .sf-flash-layer{
  animation:sfFlash .68s cubic-bezier(.15,.75,.2,1) forwards;
}""")

rep('dom',
    """    var beam = el('div', 'sf-beam');
    root.appendChild(beam);""",
    """    var beam = el('div', 'sf-beam');
    root.appendChild(beam);

    var flashLayer = el('div', 'sf-flash-layer');
    root.appendChild(flashLayer);""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
