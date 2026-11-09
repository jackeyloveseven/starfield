
# -*- coding: utf-8 -*-
"""v306 - 地表 UI 显示建设阶段。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

old = "      container.querySelector('#sf-surface-env').textContent = env.label + ' · SURFACE FLIGHT';"
new = """      var envLine = env.label + ' · SURFACE FLIGHT';
      if (env.__buildStage > 0 && window.SFBuildup) {
        envLine += ' · ' + window.SFBuildup.stageLabel(opts);
      }
      container.querySelector('#sf-surface-env').textContent = envLine;"""
assert html.count(old) == 1, 'count=%d' % html.count(old)
html = html.replace(old, new)

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('surface shows build stage')
