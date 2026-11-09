
# -*- coding: utf-8 -*-
"""v300 - 渐进式建设：轨道设施随专注时长逐级成型。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   渐进式建设：你专注的时间，真的在建造东西。
   建设度 = 当前累计专注 - 收藏时的累计专注（focusAtBirth）。
   阶段：太阳能板 -> 环带骨架 -> 闭合环 -> 戴森云。
   ============================================================ */
(function () {
  if (window.SFBuildup) return;

  function totalFocus() {
    try { return parseInt(localStorage.getItem('sf_total_focus_v1') || '0', 10) || 0; }
    catch (e) { return 0; }
  }

  var STAGES = [
    { min: 0,   label: '\\u672a\\u5f00\\u5de5',   en: 'NOT STARTED' },
    { min: 30,  label: '\\u592a\\u9633\\u80fd\\u677f\\u9635\\u5217', en: 'SOLAR ARRAY' },
    { min: 120, label: '\\u73af\\u5e26\\u9aa8\\u67b6', en: 'RING FRAME' },
    { min: 300, label: '\\u95ed\\u5408\\u73af\\u5e26', en: 'CLOSED RING' },
    { min: 600, label: '\\u6234\\u68ee\\u4e91',     en: 'DYSON SWARM' }
  ];

  window.SFBuildup = {
    minutes: function (item) {
      if (!item || typeof item.focusAtBirth !== 'number') return 0;
      return Math.max(0, totalFocus() - item.focusAtBirth);
    },
    stage: function (item) {
      var m = this.minutes(item), s = 0;
      for (var i = 0; i < STAGES.length; i++) if (m >= STAGES[i].min) s = i;
      return s;
    },
    stageLabel: function (item) {
      var s = this.stage(item);
      return STAGES[s].label;
    },
    progress: function (item) {
      /* 到下一阶段还差多少分钟 */
      var m = this.minutes(item), s = this.stage(item);
      if (s >= STAGES.length - 1) return null;
      return Math.max(0, STAGES[s + 1].min - m);
    },

    /* 在星球周围搭建设施，挂到 group 上 */
    build: function (THREE, group, R, stage, hue) {
      if (stage <= 0) return null;
      var g = new THREE.Group();
      var mat = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.12, 0.55, 0.55),
        roughness: 0.35, metalness: 0.75,
        emissive: new THREE.Color().setHSL(0.12, 0.6, 0.12), flatShading: true
      });
      var glow = new THREE.MeshBasicMaterial({
        color: new THREE.Color().setHSL(0.55, 0.85, 0.62),
        transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending, depthWrite: false
      });
      var orbit = R * 1.5;

      if (stage === 1) {
        /* 太阳能板：轨道上若干小方块 */
        for (var i = 0; i < 6; i++) {
          var a = i / 6 * Math.PI * 2;
          var p = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.12, 1.2), mat);
          p.position.set(Math.cos(a) * orbit, 0, Math.sin(a) * orbit);
          g.add(p);
        }
      } else {
        /* 环带：阶段 2 是断弧，阶段 3 是整环，阶段 4 加云 */
        var frac = stage === 2 ? 0.55 : 1.0;
        var ring = new THREE.Mesh(
          new THREE.TorusGeometry(orbit, 0.28, 6, 96, Math.PI * 2 * frac), mat);
        ring.rotation.x = Math.PI / 2 - 0.22;
        g.add(ring);
        var rim = new THREE.Mesh(
          new THREE.TorusGeometry(orbit, 0.06, 4, 96, Math.PI * 2 * frac), glow);
        rim.rotation.x = Math.PI / 2 - 0.22;
        rim.position.y = 0.35;
        g.add(rim);

        if (stage >= 4) {
          /* 戴森云：环外散布的收集器点 */
          var pts = [];
          for (var d = 0; d < 320; d++) {
            var a2 = Math.random() * Math.PI * 2;
            var rr = orbit * (1.05 + Math.random() * 0.35);
            pts.push(Math.cos(a2) * rr, (Math.random() - 0.5) * 3.5, Math.sin(a2) * rr);
          }
          var cg = new THREE.BufferGeometry();
          cg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
          g.add(new THREE.Points(cg, new THREE.PointsMaterial({
            color: new THREE.Color().setHSL(0.55, 0.9, 0.7), size: 0.5,
            transparent: true, opacity: 0.75, blending: THREE.AdditiveBlending, depthWrite: false
          })));
        }
      }
      g.rotation.x = 0.22;
      return g;
    }
  };
})();
'''

body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-buildup">' + MODULE + '\n</script>\n' + html[body_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('buildup module added')
