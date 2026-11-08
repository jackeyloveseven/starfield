
# -*- coding: utf-8 -*-
"""v269 - 景观分步诊断：定位为何一个都没画。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = """    draw: function (env) {
      E = env;
      if (!E || !E.started) return;"""
new = """    draw: function (env) {
      E = env;
      var D = window.__passDbg = window.__passDbg || { called:0, notStarted:0, cand:0, noQ:0, faded:0, offY:0 };
      D.called++;
      if (!E || !E.started) { D.notStarted++; return; }"""
assert html.count(old) == 1
html = html.replace(old, new)

old2 = """        var h = hash(k, 9001);
        if (h > 0.55) continue;"""
new2 = """        var h = hash(k, 9001);
        if (h > 0.55) continue;
        D.cand++;"""
assert html.count(old2) == 1
html = html.replace(old2, new2)

old3 = """        var q = project([x, y, z]);
        if (!q) continue;
        var fade = fadeAtCenter(q[0]);
        if (fade <= 0) continue;
        if (q[1] < -80 || q[1] > H + 80) continue;"""
new3 = """        var q = project([x, y, z]);
        if (!q) { D.noQ++; continue; }
        var fade = fadeAtCenter(q[0]);
        if (fade <= 0) { D.faded++; continue; }
        if (q[1] < -80 || q[1] > H + 80) { D.offY++; continue; }"""
assert html.count(old3) == 1
html = html.replace(old3, new3)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('diagnostics added')
