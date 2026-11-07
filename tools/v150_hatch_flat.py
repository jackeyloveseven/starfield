
# -*- coding: utf-8 -*-
"""v150 — sf-hatch-flat: 把「开星核」从爆炸式抽卡改成极简几何 / 3D 扁平平开卡。

只换视觉与时序，保留全部 DOM 契约：
  #sf-igniter-box / #sf-shockwave / .sf-hatch-card / .sf-card-holo
  #sf-card-serial / #sf-card-tier-badge / #sf-card-orb-bezel
所以 verify_cores_and_ui.py 与 verify_all_mechanics_and_aesthetics.py 无需改动。
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / 'starfield.html'


def main():
    with open(HTML, 'r', encoding='utf-8', newline='') as f:
        src = f.read()
    nl = '\r\n' if '\r\n' in src[:6000] else '\n'

    def N(s):
        return s.replace('\r\n', '\n').replace('\n', nl)

    report = []

    def swap(tag, start_marker, end_marker, new_text, inclusive_end=False):
        nonlocal src
        start_marker = N(start_marker)
        end_marker = N(end_marker)
        s = src.find(start_marker)
        assert s >= 0, 'start not found: ' + tag
        e = src.find(end_marker, s)
        assert e >= 0, 'end not found: ' + tag
        if inclusive_end:
            e += len(end_marker)
        old = src[s:e]
        src = src[:s] + new_text + src[e:]
        report.append(tag + ': ' + str(len(old)) + ' -> ' + str(len(new_text)))

    # ---------------------------------------------------------------- 1. 仪式底座
    swap(
        'igniter',
        "    igniterBox.innerHTML = '<div class=\"sf-singularity-core\"></div>",
        "    root.appendChild(igniterBox);",
        N("""    igniterBox.innerHTML = '' +
      '<div class="sf-flat-reticle">' +
        '<span class="sf-flat-cross h"></span>' +
        '<span class="sf-flat-cross v"></span>' +
        '<span class="sf-flat-ring r1"></span>' +
        '<span class="sf-flat-ring r2"></span>' +
        '<span class="sf-flat-dot"></span>' +
      '</div>' +
      '<div class="sf-flat-label">CORE <b id="sf-flat-idx">01</b> / 03</div>' +
      '<div class="sf-igniter-prompt">轻触校准 · 打开星核</div>';
"""),
    )

    # ---------------------------------------------------------------- 2. 扁平星球
    swap(
        'planet',
        "  function drawPlanetSphere(ctx, cx, cy, r, hue, tier, rotX, rotY, cloudRot) {",
        "  ProceduralPlanet.prototype.render = function() {",
        N("""  /* 扁平几何星球：纯色面 + 硬边昼夜 + 球面椭圆斑块 + 发丝赤道。
   * 旋转不靠渐变位移，而靠斑块的经度投影收缩 —— 硬边、无光晕。 */
  function drawPlanetSphere(ctx, cx, cy, r, hue, tier, rotX, rotY, cloudRot) {
    var DEG = Math.PI / 180;
    var rank = (TIERS[tier] && typeof TIERS[tier].rank === 'number') ? TIERS[tier].rank : 0;
    var base = 'hsl(' + hue + ', 30%, 15%)';
    var land = 'hsl(' + hue + ', 42%, 30%)';
    var edge = 'hsl(' + hue + ', 58%, 62%)';

    function ringHalf(front, rad, flat, alpha) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(-22 * DEG);
      ctx.beginPath();
      ctx.ellipse(0, 0, r * rad, r * flat, 0,
        front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
      ctx.strokeStyle = edge;
      ctx.globalAlpha = alpha;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();
    }

    if (rank >= 2) ringHalf(false, 1.44, 0.30, 0.26);

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = base;
    ctx.fill();

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.clip();

    var PATCHES = [
      { lon: 18,  lat: 20,  rx: 0.46, ry: 0.34 },
      { lon: 124, lat: -22, rx: 0.40, ry: 0.26 },
      { lon: 236, lat: 32,  rx: 0.34, ry: 0.22 },
      { lon: 302, lat: -10, rx: 0.30, ry: 0.20 },
      { lon: 72,  lat: 54,  rx: 0.20, ry: 0.13 }
    ];
    var spin = rotY / DEG;
    ctx.fillStyle = land;
    for (var i = 0; i < PATCHES.length; i++) {
      var p = PATCHES[i];
      var lon = (p.lon + spin) * DEG;
      var depth = Math.cos(lon);
      if (depth <= 0.05) continue;
      var lat = (p.lat + (rotX / DEG) * 42) * DEG;
      var px = Math.sin(lon) * Math.cos(lat) * r;
      var py = -Math.sin(lat) * r;
      ctx.beginPath();
      ctx.ellipse(cx + px, cy + py, p.rx * r * depth, p.ry * r * (0.55 + 0.45 * depth),
        0, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.beginPath();
    ctx.moveTo(cx, cy - r);
    ctx.arc(cx, cy, r, -Math.PI / 2, Math.PI / 2, false);
    ctx.closePath();
    ctx.fillStyle = 'rgba(4, 6, 10, 0.74)';
    ctx.fill();

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rotX * 0.55);
    ctx.beginPath();
    ctx.ellipse(0, 0, r, r * Math.max(0.03, Math.abs(Math.sin(rotX))), 0, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255,255,255,0.10)';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    ctx.restore();

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = edge;
    ctx.globalAlpha = 0.52;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.globalAlpha = 1;

    if (rank >= 2) ringHalf(true, 1.44, 0.30, 0.72);

    ctx.save();
    ctx.translate(cx, cy);
    ctx.strokeStyle = edge;
    ctx.lineWidth = 1;
    ctx.globalAlpha = 0.50;
    if (rank >= 1) {
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.16, -0.92, 0.92);
      ctx.stroke();
    }
    if (rank >= 2) {
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.28, Math.PI - 0.74, Math.PI + 0.74);
      ctx.stroke();
    }
    if (rank >= 3) {
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.44, 0, Math.PI * 2);
      ctx.stroke();
      for (var t1 = 0; t1 < 4; t1++) {
        var a1 = t1 * Math.PI / 2 + 0.34;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a1) * r * 1.44, Math.sin(a1) * r * 1.44);
        ctx.lineTo(Math.cos(a1) * r * 1.57, Math.sin(a1) * r * 1.57);
        ctx.stroke();
      }
    }
    if (rank >= 4) {
      ctx.globalAlpha = 0.28;
      ctx.beginPath();
      ctx.arc(0, 0, r * 1.62, 0, Math.PI * 2);
      ctx.stroke();
      for (var t2 = 0; t2 < 8; t2++) {
        var a2 = t2 * Math.PI / 4;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a2) * r * 1.62, Math.sin(a2) * r * 1.62);
        ctx.lineTo(Math.cos(a2) * r * 1.70, Math.sin(a2) * r * 1.70);
        ctx.stroke();
      }
    }
    ctx.restore();

    ctx.beginPath();
    ctx.moveTo(cx + r * 1.02, cy - r * 0.42);
    ctx.lineTo(cx + r * 1.02, cy + r * 0.42);
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }

"""),
    )

    # ---------------------------------------------------------------- 3. 画布留白
    src = src.replace('var cx = w * 0.5, cy = h * 0.5, r = w * 0.42;',
                      'var cx = w * 0.5, cy = h * 0.5, r = w * 0.33;')
    src = src.replace('var cx = w * 0.5, cy = h * 0.5, r = w * 0.40;',
                      'var cx = w * 0.5, cy = h * 0.5, r = w * 0.33;')

    # ---------------------------------------------------------------- 4. 视差改写变量
    swap(
        'tilt',
        '    // 3D Tarot Parallax Tilt & Holographic Diffraction Sheen',
        '    // Loop - only runs when overlay is on to avoid background RAF burn',
        N("""    /* 视差只写 CSS 变量：卡片 tilt 交给样式表，避免内联 transform 互斥。 */
    card.addEventListener('pointermove', function (e) {
      if (card.classList.contains('flipped')) return;
      var rect = card.getBoundingClientRect();
      var nx = (e.clientX - rect.left) / rect.width - 0.5;
      var ny = (e.clientY - rect.top) / rect.height - 0.5;
      card.style.setProperty('--ry', (nx * 7).toFixed(2) + 'deg');
      card.style.setProperty('--rx', (-ny * 6).toFixed(2) + 'deg');
      card.style.setProperty('--holo-angle', (115 + nx * 46).toFixed(1) + 'deg');
    });
    card.addEventListener('pointerleave', function () {
      if (card.classList.contains('flipped')) return;
      card.style.setProperty('--ry', '0deg');
      card.style.setProperty('--rx', '0deg');
    });

"""),
    )

    # ---------------------------------------------------------------- 5. 低音垫音色
    swap(
        'drone',
        '  function playDrone() {',
        '  function playSupernovaChime(tier) {',
        N("""  /* 正弦双音 + 低通上扫：玻璃感，不用锯齿（原方案太脏）。 */
  function playDrone() {
    var ctx = getAudio(); if (!ctx) return;
    try {
      var t0 = ctx.currentTime;
      var g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.050, t0 + 0.55);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.55);
      var lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(340, t0);
      lp.frequency.exponentialRampToValueAtTime(1500, t0 + 1.25);
      var tones = [220, 329.63];
      for (var i = 0; i < tones.length; i++) {
        var osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(tones[i], t0);
        osc.detune.setValueAtTime(i ? 6 : -6, t0);
        osc.connect(lp);
        osc.start(t0);
        osc.stop(t0 + 1.6);
      }
      lp.connect(g);
      g.connect(ctx.destination);
    } catch (e) {}
  }

"""),
    )

    # ---------------------------------------------------------------- 6. 开卡时序
    swap(
        'openFor-ceremony',
        '    if (isNewHatch) {',
        '    } else {\n      // Direct Inspection',
        N("""    if (isNewHatch) {
      /* 校准 → 光栅 → 分层显影。全程无爆炸、无全屏闪白。 */
      card.classList.remove('revealed', 'flipped', 'sf-in');
      card.style.opacity = '0';
      card.style.display = 'flex';

      igniterBox.classList.remove('sf-collapse');
      igniterBox.style.display = 'flex';
      igniterBox.style.opacity = '1';
      igniterBox.style.transform = 'translate(-50%, -50%) scale(1)';
      igniterBox.style.pointerEvents = 'auto';

      var idxEl = igniterBox.querySelector('#sf-flat-idx');
      if (idxEl) {
        var left = 0;
        try { left = window.StarfieldHatch.getUnopenedCores(); } catch (e) { left = 0; }
        idxEl.textContent = String(Math.max(1, left)).padStart(2, '0');
      }

      particleSystem.startSingularity();
      playDrone();

      var triggered = false;
      var triggerIgnition = function () {
        if (triggered) return;
        triggered = true;
        igniterBox.style.pointerEvents = 'none';
        igniterBox.classList.add('sf-collapse');

        setTimeout(function () {
          igniterBox.style.display = 'none';
          shockwave.classList.remove('boom');
          void shockwave.offsetWidth;
          shockwave.classList.add('boom');
          particleSystem.explode(item.tier);
          playSupernovaChime(item.tier);
        }, 400);

        setTimeout(function () {
          card.classList.remove('sf-in');
          void card.offsetWidth;
          card.style.opacity = '1';
          card.classList.add('revealed');
          card.classList.add('sf-in');
        }, 560);
      };

      igniterBox.onclick = triggerIgnition;
      setTimeout(function () {
        if (!triggered && root.classList.contains('on')) triggerIgnition();
      }, 1800);
"""),
    )

    # ---------------------------------------------------------------- 7. 直检分支
    swap(
        'openFor-direct',
        "      // Direct Inspection\n      igniterBox.style.display = 'none';",
        "  function hide(){",
        N("""      // Direct Inspection
      igniterBox.style.display = 'none';
      card.style.display = 'flex';
      card.classList.remove('flipped', 'sf-in');
      card.style.opacity = '1';
      void card.offsetWidth;
      card.classList.add('revealed', 'sf-in');
    }
  }

"""),
    )

    # ---------------------------------------------------------------- 8. 关闭时复位
    src = src.replace(
        N("  function hide(){ if(root) root.classList.remove('on'); }"),
        N("""  function hide(){
    if (root) {
      root.classList.remove('on');
      if (card) card.classList.remove('sf-in', 'revealed', 'flipped');
    }
  }"""),
    )

    # ---------------------------------------------------------------- 9. 追加样式
    CSS = N("""<style id="sf-hatch-flat-css">
/* ============================================================
   sf-hatch-flat · 极简几何 / 3D 扁平平开卡
   纯色面 + 1px 发丝线 + 真实透视 + 慢缓动分层入场。
   颜色克制：tier 色只出现在顶线、标签、星球几何、底部主键。
   ============================================================ */
#sf-hatch{
  background:#07080b;
  -webkit-backdrop-filter:none;backdrop-filter:none;
  perspective:1400px;perspective-origin:50% 46%;
}
#sf-hatch.on{animation:sfFlatVeil .42s ease both}
@keyframes sfFlatVeil{from{opacity:0}to{opacity:1}}

/* 3D 地板网格：画面里唯一的空间参照 */
#sf-hatch::before{
  content:"";position:absolute;inset:-20%;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
  background-size:58px 58px;
  transform:perspective(620px) rotateX(66deg) translateZ(-60px);
  transform-origin:50% 72%;
  -webkit-mask-image:radial-gradient(ellipse 55% 46% at 50% 60%,#000 0%,transparent 74%);
  mask-image:radial-gradient(ellipse 55% 46% at 50% 60%,#000 0%,transparent 74%);
  animation:sfFlatDrift 26s linear infinite;
}
@keyframes sfFlatDrift{
  from{background-position:0 0,0 0}
  to{background-position:0 58px,58px 0}
}

/* ---------------- 校准仪式 ---------------- */
.sf-igniter-box{gap:0;transition:opacity .42s ease,transform .42s cubic-bezier(.16,1,.3,1)}
.sf-flat-reticle{position:relative;width:186px;height:186px;display:flex;align-items:center;justify-content:center}
.sf-flat-ring{position:absolute;inset:0;border-radius:50%;border:1px solid rgba(255,255,255,.14);pointer-events:none}
.sf-flat-ring.r1{border-top-color:rgba(255,255,255,.55);animation:sfFlatSpin 7.5s linear infinite}
.sf-flat-ring.r2{inset:30px;border-style:dashed;border-color:rgba(255,255,255,.11);animation:sfFlatSpin 13s linear infinite reverse}
.sf-flat-cross{position:absolute;background:rgba(255,255,255,.13);pointer-events:none}
.sf-flat-cross.h{width:252px;height:1px}
.sf-flat-cross.v{width:1px;height:252px}
.sf-flat-dot{position:absolute;width:5px;height:5px;border-radius:50%;background:#fff;
  box-shadow:0 0 0 5px rgba(255,255,255,.09);animation:sfFlatBeat 2.8s ease-in-out infinite}
@keyframes sfFlatSpin{to{transform:rotate(360deg)}}
@keyframes sfFlatBeat{0%,100%{transform:scale(1);opacity:.85}50%{transform:scale(1.35);opacity:1}}
@keyframes sfFlatCollapse{0%{transform:scale(1);opacity:1}100%{transform:scale(.02);opacity:0}}
.sf-igniter-box.sf-collapse .sf-flat-reticle{animation:sfFlatCollapse .46s cubic-bezier(.7,0,.84,0) forwards}
.sf-igniter-box.sf-collapse .sf-flat-cross,
.sf-igniter-box.sf-collapse .sf-flat-label,
.sf-igniter-box.sf-collapse .sf-igniter-prompt{opacity:0;transition:opacity .2s ease}
.sf-flat-label{
  margin-top:30px;
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
  font-size:9.5px;line-height:1;font-weight:600;letter-spacing:.34em;
  color:rgba(255,255,255,.40);
}
.sf-flat-label b{color:#fff;font-weight:600}
.sf-igniter-prompt{
  margin-top:12px;font-size:10px;letter-spacing:.30em;font-weight:500;
  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
  color:rgba(255,255,255,.55);text-shadow:none;animation:none;opacity:1;
}
.sf-singularity-core{display:none!important}

/* ---------------- 矩形光栅 ---------------- */
#sf-hatch #sf-shockwave{
  width:min(312px,80vw);aspect-ratio:9/14.4;border-radius:6px;
  border:1px solid var(--tier,#fff);box-shadow:none;
  transform:translate(-50%,-50%) scale(.62);opacity:0;
  transition:none;will-change:transform,opacity;
}
#sf-hatch #sf-shockwave.boom{animation:sfFlatRaster .8s cubic-bezier(.16,1,.3,1) forwards}
@keyframes sfFlatRaster{
  0%{transform:translate(-50%,-50%) scale(.60);opacity:0}
  18%{opacity:.9}
  100%{transform:translate(-50%,-50%) scale(1.22);opacity:0}
}

/* ---------------- 卡片本体 ---------------- */
#sf-hatch .sf-hatch-card{
  width:min(312px,80vw);aspect-ratio:9/14.4;
  border-radius:6px;padding:0;
  background:#0b0d11;
  border:1px solid rgba(255,255,255,.11);
  border-top-color:var(--tier,#fff);
  box-shadow:
    0 1px 0 rgba(255,255,255,.05),
    0 2px 0 #07080b,
    0 3px 0 rgba(255,255,255,.03),
    0 4px 0 #060709,
    0 46px 90px -30px rgba(0,0,0,.96);
  transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg));
  transform-style:preserve-3d;
  transition:transform .9s cubic-bezier(.16,1,.3,1),opacity .5s ease;
  opacity:0;
}
#sf-hatch .sf-hatch-card.revealed{opacity:1;filter:none}
#sf-hatch .sf-hatch-card:active{transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) scale(.985)}
#sf-hatch .sf-hatch-card::before,
#sf-hatch .sf-hatch-card::after{content:none!important}

#sf-hatch .sf-card-header{
  position:absolute;top:0;left:0;right:0;height:32px;
  padding:0 18px;margin:0;border:0;
  display:flex;align-items:center;justify-content:space-between;z-index:6;
}
#sf-hatch .sf-card-serial{
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.28em;font-weight:600;
  color:rgba(255,255,255,.34);text-transform:uppercase;
}
#sf-hatch .sf-card-tier-badge{
  padding:0!important;border:0!important;border-radius:0!important;background:none!important;
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.28em;font-weight:600;
  color:var(--tier,#fff)!important;
}
#sf-hatch .sf-card-coords{
  margin:0;padding:0 18px;position:absolute;top:34px;left:0;right:0;
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:7.5px;line-height:1;letter-spacing:.26em;
  color:rgba(255,255,255,.24);text-align:center;
}
#sf-hatch .sf-card-orb-stage{
  flex:1 1 0;min-height:150px;max-height:230px;
  margin:0;padding:56px 0 0 0;
}
#sf-hatch .sf-hatch-orb{
  width:min(178px,52vw);aspect-ratio:1;box-shadow:none;cursor:grab;
}
#sf-hatch .sf-hatch-orb::before,
#sf-hatch .sf-hatch-orb::after{content:none!important}
#sf-hatch canvas.sf-planet-canvas{filter:none}

#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 74px 20px;z-index:6}
#sf-hatch .sf-hatch-name{
  font-family:"Songti SC","Noto Serif SC","Source Han Serif SC",Georgia,"Times New Roman",serif;
  font-size:23px;font-weight:400;line-height:1.24;letter-spacing:.16em;
  color:#fff;text-shadow:none;
}
#sf-hatch .sf-hatch-meta{
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.26em;font-weight:600;
  color:var(--tier,#fff);opacity:.85;
}
#sf-hatch .sf-card-specs{
  margin:6px 0 0 0;
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:7.5px;line-height:1;letter-spacing:.22em;
  color:rgba(255,255,255,.30);
}
#sf-hatch .sf-hatch-hint{
  margin-top:10px;
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8px;line-height:1;letter-spacing:.30em;
  color:rgba(255,255,255,.45);
}

/* 扫描光带（保留 .sf-card-holo 元素契约，去掉彩虹叠加） */
#sf-hatch .sf-card-holo{
  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 42%,rgba(255,255,255,.09) 50%,transparent 58%);
  mix-blend-mode:normal;
  opacity:0;transition:opacity .8s ease .3s;
  z-index:5;border-radius:6px;
}
#sf-hatch .sf-hatch-card.revealed .sf-card-holo{opacity:1}
#sf-hatch .sf-card-corner-tl,
#sf-hatch .sf-card-corner-tr,
#sf-hatch .sf-card-corner-bl,
#sf-hatch .sf-card-corner-br,
#sf-hatch .sf-foil-rim{display:none!important}

/* 底部三键：无边框、发丝分隔 */
#sf-hatch .sf-card-actions{
  bottom:0;left:0;right:0;height:44px;gap:0;
  border-top:1px solid rgba(255,255,255,.08);z-index:30;
}
#sf-hatch .sf-card-act-btn{
  border:0!important;border-radius:0!important;
  background:none!important;box-shadow:none!important;
  -webkit-backdrop-filter:none;backdrop-filter:none;
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.22em;font-weight:600;
  color:rgba(255,255,255,.48)!important;
  transition:color .28s ease,background .28s ease;
}
#sf-hatch .sf-card-act-btn+.sf-card-act-btn{border-left:1px solid rgba(255,255,255,.07)!important}
#sf-hatch .sf-card-act-btn:hover{background:rgba(255,255,255,.04)!important;color:#fff!important}
#sf-hatch .sf-card-act-btn.primary{color:var(--tier,#fff)!important}
#sf-hatch .sf-card-act-btn:disabled{opacity:.3!important;color:rgba(255,255,255,.3)!important;filter:none}

#sf-hatch .sf-hatch-close{
  top:calc(env(safe-area-inset-top,0px) + 18px);right:20px;
  border:1px solid rgba(255,255,255,.16);border-radius:0;background:none;
  color:rgba(255,255,255,.55);
  font-family:"SFMono-Regular",Consolas,monospace;
  font-size:8.5px;line-height:1;letter-spacing:.26em;padding:9px 14px;
  transition:color .25s ease,border-color .25s ease;
}
#sf-hatch .sf-hatch-close:hover{color:#fff;border-color:rgba(255,255,255,.4)}

/* 背面档案 */
#sf-hatch .sf-hatch-back{
  border-radius:6px!important;background:#0b0d11!important;
  border:1px solid rgba(255,255,255,.11)!important;box-shadow:none!important;
  padding:22px 18px 62px 18px!important;
}
#sf-hatch .sf-foil{
  font-family:"SFMono-Regular",Consolas,monospace!important;
  font-size:8px!important;letter-spacing:.26em!important;font-weight:600!important;
  color:rgba(255,255,255,.34)!important;text-shadow:none!important;opacity:1!important;
  left:18px!important;top:16px!important;
}
#sf-hatch .sf-hb-card-title,
#sf-hatch .sf-hb-card-sub,
#sf-hatch .sf-hb-astrolabe-icon{
  font-family:"SFMono-Regular",Consolas,monospace!important;letter-spacing:.24em!important;
}
#sf-hatch .sf-hb-row{
  border-radius:0!important;background:none!important;
  border:0!important;border-bottom:1px solid rgba(255,255,255,.06)!important;padding:7px 0!important;
}
#sf-hatch .sf-hb-quote-box{
  border-radius:0!important;background:none!important;
  border-left:1px solid var(--tier)!important;padding:0 0 0 10px!important;
}

/* ---------------- 分层入场 ---------------- */
#sf-hatch .sf-hatch-card > .sf-card-header,
#sf-hatch .sf-hatch-card > .sf-card-coords,
#sf-hatch .sf-hatch-card > .sf-card-orb-stage,
#sf-hatch .sf-hatch-card > .sf-card-info,
#sf-hatch .sf-hatch-card > .sf-card-actions{opacity:0;transform:translateY(10px)}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-header,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-coords,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-orb-stage,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-info,
#sf-hatch .sf-hatch-card.sf-in > .sf-card-actions{
  opacity:1;transform:none;
  transition:opacity .68s cubic-bezier(.16,1,.3,1),transform .68s cubic-bezier(.16,1,.3,1);
}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-header{transition-delay:.00s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-coords{transition-delay:.07s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-orb-stage{transition-delay:.14s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-info{transition-delay:.22s}
#sf-hatch .sf-hatch-card.sf-in > .sf-card-actions{transition-delay:.30s}

@media (prefers-reduced-motion:reduce){
  #sf-hatch::before{animation:none}
  .sf-flat-ring,.sf-flat-dot{animation:none}
  #sf-hatch .sf-hatch-card,
  #sf-hatch .sf-hatch-card.sf-in > *{transition-duration:.01s!important;transition-delay:0s!important}
}
</style>

""")
    assert src.count('</body>') >= 1, 'no body close'
    i = src.rfind('</body>')
    src = src[:i] + CSS + src[i:]
    report.append('css: appended ' + str(len(CSS)) + ' chars')

    with open(HTML, 'w', encoding='utf-8', newline='') as f:
        f.write(src)

    for r in report:
        print('  ' + r)
    print('DONE, bytes=' + str(len(src.encode('utf-8'))))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
