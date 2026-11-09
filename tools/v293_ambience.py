
# -*- coding: utf-8 -*-
"""v293 - 声音签名：每颗星球自己的底噪，Web Audio 合成，不加载音频文件。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')

MODULE = r'''
/* ============================================================
   声音签名（Ambience）
   每种形态一种底噪：水世界是流动、都市是嗡鸣、水晶是泛音、
   菌毯是呼吸、虚空近乎静音。全部 Web Audio 合成，零音频文件。
   音量刻意压低 —— 它是氛围，不是主角。
   ============================================================ */
(function () {
  if (window.SFAmbience) return;

  var ctx = null, master = null, nodes = [], curId = null;

  function ac() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
    return ctx;
  }

  /* 两秒循环噪声，给海浪/风声用 */
  function noiseBuffer(c) {
    var len = c.sampleRate * 2;
    var buf = c.createBuffer(1, len, c.sampleRate);
    var d = buf.getChannelData(0), last = 0;
    for (var i = 0; i < len; i++) {
      var w = Math.random() * 2 - 1;
      last = (last + 0.02 * w) / 1.02;   /* 棕噪声，比白噪声柔和 */
      d[i] = last * 3.2;
    }
    return buf;
  }

  function stopAll() {
    for (var i = 0; i < nodes.length; i++) {
      try { nodes[i].stop ? nodes[i].stop() : nodes[i].disconnect(); } catch (e) {}
    }
    nodes = [];
    if (master) { try { master.disconnect(); } catch (e) {} master = null; }
  }

  var VOICES = {
    skimming_water:   { kind: 'wave',  gain: 0.085, freq: 420,  lfo: 0.16 },
    dune_arrakis:     { kind: 'wave',  gain: 0.060, freq: 900,  lfo: 0.07 },
    cyber_metropolis: { kind: 'hum',   gain: 0.055, freq: 62,   trem: 0.25 },
    mothership_fleet: { kind: 'hum',   gain: 0.050, freq: 78,   trem: 0.18 },
    protoss_crystal:  { kind: 'chime', gain: 0.030, freq: 1174 },
    shattered_cataclysm:{ kind: 'hum', gain: 0.050, freq: 46,   trem: 0.5 },
    super_storm:      { kind: 'wave',  gain: 0.075, freq: 300,  lfo: 0.30 },
    zerg_biomorphic:  { kind: 'pulse', gain: 0.070, freq: 52,   rate: 0.55 },
    dark_void:        { kind: 'void',  gain: 0.010 },
    earth_egg:        { kind: 'wave',  gain: 0.055, freq: 520,  lfo: 0.12 }
  };
  var FALLBACK = { kind: 'hum', gain: 0.035, freq: 88, trem: 0.12 };

  function start(manifId) {
    if (curId === manifId) return;
    stopAll();
    curId = manifId;
    var c = ac();
    if (!c) return;
    var v = VOICES[manifId] || FALLBACK;
    var t = c.currentTime;

    master = c.createGain();
    master.gain.setValueAtTime(0.0001, t);
    master.gain.exponentialRampToValueAtTime(v.gain, t + 2.2);  /* 淡入，别突兀 */
    master.connect(c.destination);

    if (v.kind === 'wave') {
      var src = c.createBufferSource();
      src.buffer = noiseBuffer(c); src.loop = true;
      var lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = v.freq;
      var lfo = c.createOscillator(); lfo.frequency.value = v.lfo;
      var lfoG = c.createGain(); lfoG.gain.value = v.freq * 0.45;
      lfo.connect(lfoG); lfoG.connect(lp.frequency);
      src.connect(lp); lp.connect(master);
      src.start(); lfo.start();
      nodes.push(src, lfo, lp, lfoG);
    }
    else if (v.kind === 'hum') {
      var o = c.createOscillator(); o.type = 'sine'; o.frequency.value = v.freq;
      var o2 = c.createOscillator(); o2.type = 'sine'; o2.frequency.value = v.freq * 1.5;
      var g2 = c.createGain(); g2.gain.value = 0.25;
      var tr = c.createOscillator(); tr.frequency.value = v.trem;
      var trG = c.createGain(); trG.gain.value = v.gain * 0.35;
      tr.connect(trG); trG.connect(master.gain);
      o.connect(master); o2.connect(g2); g2.connect(master);
      o.start(); o2.start(); tr.start();
      nodes.push(o, o2, tr, g2, trG);
    }
    else if (v.kind === 'chime') {
      /* 水晶：几个泛音，缓慢错拍，像远处共鸣 */
      [1, 1.5, 2.0].forEach(function (mul, i) {
        var o = c.createOscillator(); o.type = 'sine'; o.frequency.value = v.freq * mul;
        var g = c.createGain(); g.gain.value = 0.5 / (i + 1);
        var trem = c.createOscillator(); trem.frequency.value = 0.1 + i * 0.07;
        var tg = c.createGain(); tg.gain.value = 0.3 / (i + 1);
        trem.connect(tg); tg.connect(g.gain);
        o.connect(g); g.connect(master);
        o.start(); trem.start();
        nodes.push(o, trem, g, tg);
      });
    }
    else if (v.kind === 'pulse') {
      /* 菌毯：像呼吸一样起伏 */
      var o = c.createOscillator(); o.type = 'sine'; o.frequency.value = v.freq;
      var lfo = c.createOscillator(); lfo.frequency.value = v.rate;
      var lg = c.createGain(); lg.gain.value = v.gain * 0.8;
      lfo.connect(lg); lg.connect(master.gain);
      o.connect(master);
      o.start(); lfo.start();
      nodes.push(o, lfo, lg);
    }
    else if (v.kind === 'void') {
      var src = c.createBufferSource(); src.buffer = noiseBuffer(c); src.loop = true;
      var lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 120;
      src.connect(lp); lp.connect(master); src.start();
      nodes.push(src, lp);
    }
  }

  window.SFAmbience = {
    start: start,
    stop: function () { curId = null; stopAll(); },
    current: function () { return curId; }
  };
})();
'''

body_end = html.rfind('</body>')
assert body_end > 0
html = html[:body_end] + '\n<script id="sf-ambience">' + MODULE + '\n</script>\n' + html[body_end:]

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('ambience module added')
