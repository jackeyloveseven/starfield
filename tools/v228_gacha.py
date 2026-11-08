
# -*- coding: utf-8 -*-
"""v228 — 开卡演出按二次元抽卡重做：恢复粒子 + 闪白 + 光柱 + 光环扩散 + 卡片过冲。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def rep(tag, old, new):
    global src
    o, n = N(old), N(new)
    assert src.count(o) == 1, tag + ' count=%d' % src.count(o)
    src = src.replace(o, n)
    log.append(tag)


rep('particles-in',
    """  CeremonyParticles.prototype.startSingularity = function() {
    /* v151: 粒子层停用。极简版本只用发丝线与色块，不做散点。 */
    this.phase = 'IDLE';
    this.particles = [];
  };""",
    """  CeremonyParticles.prototype.startSingularity = function() {
    /* 星尘收拢：粒子从四周螺旋向中心汇聚 */
    this.phase = 'SINGULARITY';
    this.particles = [];
    var cx = this.canvas.width * 0.5, cy = this.canvas.height * 0.5;
    var R = Math.min(this.canvas.width, this.canvas.height) * 0.5;
    for (var i = 0; i < 260; i++) {
      var angle = Math.random() * Math.PI * 2;
      var dist = R * (0.55 + Math.random() * 1.15);
      this.particles.push({
        x: cx + Math.cos(angle) * dist,
        y: cy + Math.sin(angle) * dist,
        angle: angle, dist: dist,
        speed: 1.6 + Math.random() * 4.4,
        size: 0.8 + Math.random() * 2.6,
        alpha: 0.25 + Math.random() * 0.75
      });
    }
  };""")

rep('particles-out',
    """  CeremonyParticles.prototype.explode = function() {
    this.phase = 'IDLE';
    this.particles = [];
  };""",
    """  CeremonyParticles.prototype.explode = function(tier) {
    /* 稀有度爆发：火花四散，颜色跟 tier 走 */
    this.phase = 'SHOCKWAVE';
    this.particles = [];
    var cx = this.canvas.width * 0.5, cy = this.canvas.height * 0.5;
    var t = (this.tiers && this.tiers[tier]) || { color: '#f4d06f' };
    var R = Math.min(this.canvas.width, this.canvas.height) * 0.5;
    var n = tier === 'myth' ? 320 : (tier === 'legend' ? 260 : 200);
    for (var i = 0; i < n; i++) {
      var angle = Math.random() * Math.PI * 2;
      var speed = (2 + Math.random() * 13) * (R / 380);
      this.particles.push({
        x: cx, y: cy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        size: 1.2 + Math.random() * 3.2,
        alpha: 1,
        decay: 0.010 + Math.random() * 0.022,
        color: t.color || '#f4d06f'
      });
    }
  };""")

rep('ignition',
    """        setTimeout(function () {
          igniterBox.style.display = 'none';
          shockwave.classList.remove('boom');
          void shockwave.offsetWidth;
          shockwave.classList.add('boom');
          particleSystem.explode(item.tier);
          playSupernovaChime(item.tier);
        }, 380);""",
    """        setTimeout(function () {
          igniterBox.style.display = 'none';
          /* 中心闪白 + 光柱 */
          root.classList.remove('sf-flash', 'sf-glow');
          void root.offsetWidth;
          root.classList.add('sf-flash', 'sf-glow');
          /* 光环扩散 */
          shockwave.classList.remove('boom');
          void shockwave.offsetWidth;
          shockwave.classList.add('boom');
          particleSystem.explode(item.tier);
          playSupernovaChime(item.tier);
          setTimeout(function () {
            root.classList.remove('sf-flash', 'sf-glow');
          }, 1700);
        }, 380);""")

rep('beam-dom',
    "    root.appendChild(shockwave);",
    """    root.appendChild(shockwave);

    var beam = el('div', 'sf-beam');
    root.appendChild(beam);""")

rep('card-pop',
    """          card.classList.remove('sf-in');
          void card.offsetWidth;
          card.style.opacity = '1';
          card.classList.add('revealed');
          card.classList.add('sf-in');""",
    """          card.classList.remove('sf-in', 'sf-pop');
          void card.offsetWidth;
          card.style.opacity = '1';
          card.classList.add('revealed', 'sf-pop');
          card.classList.add('sf-in');""")

CSS = N("""
/* ============================================================
   开卡演出 · 二次元抽卡
   ============================================================ */
#sf-hatch::after{
  content:"";position:absolute;inset:0;pointer-events:none;z-index:26;
  background:radial-gradient(circle at 50% 44%,
    #ffffff 0%, rgba(255,255,255,.92) 12%,
    rgba(255,255,255,.45) 26%, transparent 58%);
  opacity:0;transform:scale(.35);
}
#sf-hatch.sf-flash::after{
  animation:sfFlash .62s cubic-bezier(.15,.75,.2,1) forwards;
}
@keyframes sfFlash{
  0%{opacity:0;transform:scale(.3)}
  16%{opacity:1;transform:scale(1)}
  100%{opacity:0;transform:scale(1.9)}
}

#sf-hatch .sf-beam{
  position:absolute;left:50%;top:44%;z-index:24;
  width:min(46vw,380px);height:150vh;
  transform:translate(-50%,-50%);
  background:linear-gradient(to bottom,
    transparent 0%, rgba(255,238,190,0) 18%,
    rgba(255,238,190,.34) 50%, rgba(255,238,190,0) 82%, transparent 100%);
  filter:blur(14px);
  opacity:0;pointer-events:none;
  mix-blend-mode:screen;
}
#sf-hatch.sf-glow .sf-beam{
  animation:sfBeam 1.5s cubic-bezier(.2,.75,.2,1) forwards;
}
@keyframes sfBeam{
  0%{opacity:0;transform:translate(-50%,-50%) scaleY(.12) scaleX(.4)}
  22%{opacity:1;transform:translate(-50%,-50%) scaleY(1) scaleX(1)}
  100%{opacity:0;transform:translate(-50%,-50%) scaleY(1.15) scaleX(1.7)}
}

#sf-hatch #sf-shockwave.boom{
  animation:none !important;
  border:0 !important;
  background:none !important;
}
#sf-hatch #sf-shockwave.boom::before,
#sf-hatch #sf-shockwave.boom::after{
  content:"";position:absolute;inset:0;border-radius:50%;
  border:2px solid var(--tier,#f4d06f);
  opacity:0;
}
#sf-hatch #sf-shockwave.boom::before{animation:sfRing 1.1s cubic-bezier(.1,.8,.2,1) .02s forwards}
#sf-hatch #sf-shockwave.boom::after{animation:sfRing 1.25s cubic-bezier(.1,.8,.2,1) .18s forwards}
@keyframes sfRing{
  0%{opacity:0;transform:scale(.05)}
  12%{opacity:.95}
  100%{opacity:0;transform:scale(6.5)}
}

#sf-hatch .sf-hatch-card.sf-pop{
  animation:sfCardPop .78s cubic-bezier(.18,1.35,.4,1) both;
}
@keyframes sfCardPop{
  0%{opacity:0;transform:scale(.55)}
  55%{opacity:1;transform:scale(1.045)}
  100%{opacity:1;transform:scale(1)}
}
""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + N('<style id="sf-ui-gacha">') + CSS + N('</style>\n\n') + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
