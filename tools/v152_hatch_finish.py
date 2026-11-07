
# -*- coding: utf-8 -*-
"""v152 — sf-hatch-flat 收口：填满版面、压暗光带、清掉彩色 emoji、直角化背面控件。"""
import sys
from pathlib import Path

BT = chr(96)
DOL = chr(36)

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new, count=1):
    global src
    o, n = N(old), N(new)
    c = src.count(o)
    assert c == count, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag + ' x' + str(c))


rep('card-ratio',
    "#sf-hatch .sf-hatch-card{\n  width:min(312px,80vw);aspect-ratio:9/14.4;",
    "#sf-hatch .sf-hatch-card{\n  width:min(312px,80vw);aspect-ratio:9/13.6;")

rep('shock-ratio',
    "#sf-hatch #sf-shockwave{\n  width:min(312px,80vw);aspect-ratio:9/14.4;",
    "#sf-hatch #sf-shockwave{\n  width:min(312px,80vw);aspect-ratio:9/13.6;")

rep('orb-size',
    "#sf-hatch .sf-hatch-orb{\n  width:min(178px,52vw);aspect-ratio:1;box-shadow:none;cursor:grab;\n}",
    "#sf-hatch .sf-hatch-orb{\n  width:min(202px,56vw);aspect-ratio:1;box-shadow:none;cursor:grab;\n}")

rep('orb-stage',
    "#sf-hatch .sf-card-orb-stage{\n  flex:0 0 auto;height:258px;min-height:0;max-height:none;\n  margin:0;padding:58px 0 0 0;\n}",
    "#sf-hatch .sf-card-orb-stage{\n  flex:0 0 auto;height:298px;min-height:0;max-height:none;\n  margin:0;padding:64px 0 0 0;\n}")

rep('info-pad',
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 66px 20px;z-index:6}",
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 58px 20px;z-index:6}")

rep('holo',
    "    transparent 46.5%,rgba(255,255,255,.045) 50%,transparent 53.5%);",
    "    transparent 47%,rgba(255,255,255,.030) 50%,transparent 53%);")

rep('back-btn',
    "#sf-hatch .sf-hb-quote-box{",
    """#sf-hatch .sf-hb-name-btn{
  border-radius:0!important;background:none!important;
  border:1px solid rgba(255,255,255,.24)!important;
  color:rgba(255,255,255,.72)!important;
  font-family:"SFMono-Regular",Consolas,monospace!important;
  font-size:8.5px!important;letter-spacing:.26em!important;font-weight:600!important;
  padding:8px 16px!important;
}
#sf-hatch .sf-hb-name-btn:hover{border-color:rgba(255,255,255,.5)!important;color:#fff!important}
#sf-hatch .sf-hb-name-input{
  border-radius:0!important;background:rgba(255,255,255,.04)!important;
  border:1px solid rgba(255,255,255,.18)!important;
  font-family:"SFMono-Regular",Consolas,monospace!important;
  letter-spacing:.18em!important;color:#fff!important;
}
#sf-hatch .sf-hb-quote-box{""")

rep('btn-escort-html', '<button class="sf-card-act-btn primary" id="sf-btn-escort">\u2728 \u7f16\u5165\u62a4\u822a</button>',
    '<button class="sf-card-act-btn primary" id="sf-btn-escort">\u7f16\u5165\u62a4\u822a</button>')
rep('btn-flip-html', '<button class="sf-card-act-btn" id="sf-btn-flip">\u2726 \u5929\u6587\u6863\u6848</button>',
    '<button class="sf-card-act-btn" id="sf-btn-flip">\u5929\u6587\u6863\u6848</button>')
rep('btn-next-html', '<button class="sf-card-act-btn" id="sf-btn-next-core">\u2726 \u5f00\u542f\u4e0b\u4e00\u9897</button>',
    '<button class="sf-card-act-btn" id="sf-btn-next-core">\u5f00\u542f\u4e0b\u4e00\u9897</button>')
rep('escort-text', "escortBtn.textContent = escorted ? '\u2713 \u6b63\u5728\u968f\u884c\u62a4\u822a' : '\u2728 \u7f16\u5165\u62a4\u822a';",
    "escortBtn.textContent = escorted ? '\u968f\u884c\u62a4\u822a\u4e2d' : '\u7f16\u5165\u62a4\u822a';")
rep('flip-text', "this.textContent = isFlipped ? '\u2726 \u8fd4\u56de\u5361\u9762' : '\u2726 \u5929\u6587\u6863\u6848';",
    "this.textContent = isFlipped ? '\u8fd4\u56de\u5361\u9762' : '\u5929\u6587\u6863\u6848';")
rep('next-text', "nextBtn.textContent = " + BT + "\u2726 \u5f00\u542f\u4e0b\u4e00\u9897 (" + DOL + "{coresLeft})" + BT + ";",
    "nextBtn.textContent = '\u5f00\u542f\u4e0b\u4e00\u9897 \u00b7 ' + coresLeft;")
rep('next-empty', "nextBtn.textContent = '\u2726 \u661f\u6838\u5df2\u7528\u5c3d (0)';",
    "nextBtn.textContent = '\u661f\u6838\u5df2\u7528\u5c3d';")
rep('close-text', "el('button', 'sf-hatch-close', '\u2715 \u6536\u5165\u5929\u8c61\u9986')",
    "el('button', 'sf-hatch-close', '\u6536\u5165\u5929\u8c61\u9986')")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
