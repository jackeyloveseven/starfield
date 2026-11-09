
# -*- coding: utf-8 -*-
"""v301 - 建设设施接入渲染与卡面。"""
import sys
from pathlib import Path
HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# 1) buildFor：生成轨道设施
rep("    startT = performance.now();\n    curKey = tier + '|' + hue;",
    """    /* 轨道设施：建设阶段也参与 curKey，阶段变了要重建 */
    var buildupStage = window.SFBuildup ? window.SFBuildup.stage(item) : 0;
    if (window.SFBuildup && buildupStage > 0) {
      var fac = window.SFBuildup.build(THREE, scene, 36, buildupStage, hue);
      if (fac) { scene.add(fac); facilityGroup = fac; }
    }

    startT = performance.now();
    curKey = tier + '|' + hue + '|' + buildupStage;""",
    'facility')

# 2) 声明 facilityGroup
rep("      outlineMesh = null, manifExtra = null,",
    "      outlineMesh = null, manifExtra = null, facilityGroup = null,",
    'decl')

# 3) 帧循环里让设施缓慢转动
rep("      if (manifExtra && manifExtra.updaters) {",
    "      if (facilityGroup) facilityGroup.rotation.y = t * 0.05;\n      if (manifExtra && manifExtra.updaters) {",
    'rotate')

# 4) 卡面：显示建设阶段
rep("    if (evoEl && window.SFEvolution) {",
    """    if (evoEl && window.SFBuildup) {
      var stg = window.SFBuildup.stage(item);
      if (stg > 0) {
        var left = window.SFBuildup.progress(item);
        evoEl.textContent += ' \\u00b7 \\u8f68\\u9053\\u8bbe\\u65bd ' + window.SFBuildup.stageLabel(item)
          + (left !== null ? '\\uff08\\u8fd8\\u5dee ' + left + ' \\u5206\\u949f\\uff09' : '');
      }
    }
    if (evoEl && window.SFEvolution) {""",
    'cardBuild')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
