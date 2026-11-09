
# -*- coding: utf-8 -*-
"""v285 - 星球演化（一）：时间戳 + SFEvolution + 卡面时间显示。"""
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

# 1) 收藏写入毫秒时间戳（at 只有日期，无法支撑小时级演化）
rep("at: new Date().toISOString().slice(0, 10),",
    "at: new Date().toISOString().slice(0, 10), ts: Date.now(),",
    'ts')

MODULE = r'''
/* ============================================================
   星球演化：它在你离开时也一直在运转。
   时间因子来自收藏时刻（item.ts，老数据退回 item.at），
   所有变化都是时间的确定函数 —— 同一时刻打开，看到的就是同一副样子。
   ============================================================ */
(function () {
  if (window.SFEvolution) return;

  function hours(item) {
    if (!item) return 0;
    var t = item.ts;
    if (typeof t !== 'number' || !isFinite(t)) {
      t = item.at ? Date.parse(item.at + 'T00:00:00Z') : NaN;
    }
    if (!isFinite(t)) return 0;
    return Math.max(0, (Date.now() - t) / 3600000);
  }

  window.SFEvolution = {
    hours: hours,
    days: function (item) { return hours(item) / 24; },

    /* 自转相位：每小时转过一定角度，回来时已不是你离开时的那一面 */
    spinPhase: function (item) { return hours(item) * 0.16; },

    /* 卫星/彗星相位：比自转快，位置变化更明显 */
    orbitPhase: function (item) { return hours(item) * 0.55; },

    /* 文明成长：城市光点随天数增加，有上限，不会无限膨胀 */
    cityGrowth: function (item, base) {
      var d = this.days(item);
      var extra = Math.floor(Math.min(d * 26, 900));
      return base + extra;
    },

    /* 一句话说明隔了多久 */
    elapsedText: function (item) {
      var h = hours(item);
      if (h < 1 / 60) return '\\u521a\\u521a\\u70b9\\u4eae';
      if (h < 1) return Math.max(1, Math.round(h * 60)) + ' \\u5206\\u949f\\u524d\\u70b9\\u4eae';
      if (h < 48) return Math.round(h) + ' \\u5c0f\\u65f6\\u524d\\u70b9\\u4eae';
      var d = Math.floor(h / 24);
      return d + ' \\u5929\\u524d\\u70b9\\u4eae';
    },

    /* 演化注记：让「等你回来」被看见，而不是只变几个像素 */
    note: function (item) {
      var d = this.days(item);
      if (d < 1 / 24) return '\\u5b83\\u4ecd\\u5728\\u7f13\\u6162\\u81ea\\u8f6c';
      if (d < 2) return '\\u536b\\u661f\\u5df2\\u79fb\\u52a8\\u5230\\u65b0\\u7684\\u4f4d\\u7f6e';
      if (d < 7) return '\\u591c\\u9762\\u7684\\u5149\\u70b9\\u6bd4\\u4e0a\\u6b21\\u591a\\u4e86\\u4e00\\u4e9b';
      return '\\u57ce\\u5e02\\u5728\\u4f60\\u79bb\\u5f00\\u65f6\\u4ecd\\u7ee7\\u7eed\\u751f\\u957f';
    }
  };
})();
'''

body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-evolution">' + MODULE + '\n</script>\n' + html[body_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log), '+ SFEvolution')
