
# -*- coding: utf-8 -*-
"""v305 - 地表随时间生长：老星球/高建设度的地表建筑更多。"""
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

# 1) 卡面「前往此星」带上时间信息
rep("var opts = { manif: manifId || 'earth_egg', hue: cur.hue || 200, name: cur.name || '未命名星体' };",
    "var opts = { manif: manifId || 'earth_egg', hue: cur.hue || 200, name: cur.name || '未命名星体', ts: cur.ts, at: cur.at, focusAtBirth: cur.focusAtBirth };",
    'visitOpts')

# 2) 地表 enter：按演化与建设调整植被和建筑数量
rep("      var manif = opts.manif || 'earth_egg';\n      var env = ENVS[manif] || DEFAULT_ENV;",
    """      var manif = opts.manif || 'earth_egg';
      var env = ENVS[manif] || DEFAULT_ENV;

      /* 地表也随时间生长：老星球更茂密，高建设度的星球更繁华。
         这条把「演化」和「建设」从卡片延伸到实景。 */
      env = Object.assign({}, env);
      if (opts.ts && window.SFEvolution) {
        var days = window.SFEvolution.days(opts);
        env.trees = Math.round(env.trees * (1 + Math.min(days * 0.04, 0.6)));
      }
      if (opts.focusAtBirth !== undefined && window.SFBuildup) {
        var stg = window.SFBuildup.stage(opts);
        env.buildings = Math.round(env.buildings + stg * 22);
        env.__buildStage = stg;
      }""",
    'envGrowth')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
