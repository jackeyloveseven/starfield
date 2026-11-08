
# -*- coding: utf-8 -*-
"""v262 - 接线：形态独立于品阶，buildFor 调用 sfManifFor + sfBuildManif。"""
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

# 1) buildFor 开头：解析形态，预设由形态决定（品阶只影响光效）
rep("""  function buildFor(item) {
    disposePlanet();
    var tier = item.tier || 'common';
    var L = TIER_LOOK[tier] || TIER_LOOK.common;
    var hue = item.hue || 200;

    var basePreset = Presets[L.preset] || Presets.archipelago;""",
    """  function buildFor(item) {
    disposePlanet();
    var tier = item.tier || 'common';
    var L = TIER_LOOK[tier] || TIER_LOOK.common;
    var hue = item.hue || 200;

    /* 形态独立于品阶：manif 决定"这是什么星球"，tier 只管光效 */
    var manif = sfManifFor(item);
    var basePreset = Presets[manif.preset] || Presets[L.preset] || Presets.archipelago;""",
    'manifResolve')

# 2) cfg.preset 跟随形态
rep("      preset: L.preset,", "      preset: manif.preset,", 'cfgPreset')

# 3) 在 planet.build() 之后挂形态几何
rep("""    planet = new LivingPlanet(scene, cfg);
    planet.build();""",
    """    planet = new LivingPlanet(scene, cfg);
    planet.build();

    /* 形态专属几何：水晶簇 / 菌毯囊肿 / 裂壳电弧 / 雷暴带 / 霓虹网格 / 幽冥壳 */
    manifExtra = sfBuildManif(THREE, planet, manif.id, hue, (function () {
      var s = (hue * 131 + 7) >>> 0;
      return function () { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
    })());""",
    'buildManif')

# 4) 声明 manifExtra
rep("      outlineMesh = null,", "      outlineMesh = null, manifExtra = null,", 'decl')

# 5) 帧循环里驱动形态动画
rep("      planet.update(t, 1 / 60);",
    """      if (manifExtra && manifExtra.updaters) {
        for (var ui = 0; ui < manifExtra.updaters.length; ui++) manifExtra.updaters[ui](t);
      }
      planet.update(t, 1 / 60);""",
    'tick')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
