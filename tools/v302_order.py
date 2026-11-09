
# -*- coding: utf-8 -*-
"""v302 - 建设信息改为在演化文本之后追加（否则被 = 覆盖）。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

# 1) 删掉之前放在 SFEvolution 之前的 buildup 段
old_build = """    if (evoEl && window.SFBuildup) {
      var stg = window.SFBuildup.stage(item);
      if (stg > 0) {
        var left = window.SFBuildup.progress(item);
        evoEl.textContent += ' \\u00b7 \\u8f68\\u9053\\u8bbe\\u65bd ' + window.SFBuildup.stageLabel(item)
          + (left !== null ? '\\uff08\\u8fd8\\u5dee ' + left + ' \\u5206\\u949f\\uff09' : '');
      }
    }
"""
assert html.count(old_build) == 1, 'build seg count=%d' % html.count(old_build)
html = html.replace(old_build, "")
log.append('removed misplaced')

# 2) 在 SFEvolution 赋值之后追加
old2 = """    if (evoEl && window.SFEvolution) {
      evoEl.textContent = window.SFEvolution.elapsedText(item) + ' \\u00b7 ' + window.SFEvolution.note(item);
    }"""
new2 = """    if (evoEl && window.SFEvolution) {
      evoEl.textContent = window.SFEvolution.elapsedText(item) + ' \\u00b7 ' + window.SFEvolution.note(item);
    }
    if (evoEl && window.SFBuildup) {
      var stg = window.SFBuildup.stage(item);
      if (stg > 0) {
        var left = window.SFBuildup.progress(item);
        evoEl.textContent += ' \\u00b7 \\u8f68\\u9053\\u8bbe\\u65bd ' + window.SFBuildup.stageLabel(item)
          + (left !== null ? '\\uff08\\u8fd8\\u5dee ' + left + ' \\u5206\\u949f\\uff09' : '');
      }
    }"""
assert html.count(old2) == 1, 'evo seg count=%d' % html.count(old2)
html = html.replace(old2, new2)
log.append('appended after')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
