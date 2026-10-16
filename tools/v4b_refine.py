"""V4b: proportions after looking at the first render.

Three things the screenshots showed: the world hatching was full-width and coarse
enough to read as beach-ball stripes rather than a shaded sphere; the black hole's
disc was 3.6 shadow radii across and flat-filled, so it read as a tan smear rather
than a glowing disc; and the Milky Way band was too faint to see at all.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# ------------------------------------------------------- worlds: dark side only ----
rep("""  ctx.save();ctx.beginPath();ctx.arc(cx,cy,rad*.995,0,TAU);ctx.clip();
  const step=Math.max(2.2,rad*.17);
  ctx.strokeStyle=css(p.ink,.26);ctx.lineWidth=Math.max(.5,rad*.032);
  for(let k=-rad;k<rad;k+=step){ctx.beginPath();ctx.moveTo(cx-rad,cy+k);ctx.lineTo(cx+rad,cy+k-rad*.34);ctx.stroke();}""",
    """  ctx.save();ctx.beginPath();ctx.arc(cx,cy,rad*.995,0,TAU);ctx.clip();
  // Hatched only where the light does not reach, and fine enough to read as
  // engraving: full-width coarse lines made every world a beach ball.
  const step=Math.max(1.6,rad*.085),edge=rad*.06;
  ctx.strokeStyle=css(p.ink,.30);ctx.lineWidth=Math.max(.45,rad*.022);
  for(let k=edge;k<rad;k+=step){
   const f=(k-edge)/rad;
   ctx.globalAlpha=.20+f*.52;
   ctx.beginPath();ctx.moveTo(cx-rad,cy+k);ctx.lineTo(cx+rad,cy+k-rad*.30);ctx.stroke();
  }
  ctx.globalAlpha=1;""")

# ------------------------------------------------ black hole: smaller, hotter ----
rep(" const cx=q[0],cy=q[1],hot=blend(p.sun,[255,238,206],.52),a=rad*3.6,b=Math.max(1.4,a*.20);",
    " const cx=q[0],cy=q[1],hot=blend(p.sun,[255,238,206],.52),a=rad*2.5,b=Math.max(1.2,a*.16);")

rep("""  const band=(sx,sy,ry,alpha)=>{
   const lg=ctx.createLinearGradient(-sx,0,sx,0);
   lg.addColorStop(0,css(hot,alpha*.34));lg.addColorStop(.30,css(hot,alpha));
   lg.addColorStop(.52,css(hot,alpha*.80));lg.addColorStop(1,css(hot,alpha*.26));
   ctx.beginPath();ctx.ellipse(0,ry,sx,sy,0,0,TAU);ctx.fillStyle=lg;ctx.fill();
  };
  // the far side of the disc, lensed over the top of the shadow
  ctx.save();ctx.scale(1,-1);band(a*.86,b*.78,rad*1.06,.62);ctx.restore();
  // the disc itself, then the shadow over its middle
  band(a,b,0,.92);""",
    """  // Nested ellipses rather than one flat fill: the disc is hottest at the inner
  // edge and thins outward, which a single gradient across it cannot say.
  const band=(sx,sy,ry,alpha)=>{
   for(let k=0;k<7;k++){
    const f=k/6,ex=sx*(.30+.70*f),ey=Math.max(.7,sy*(.30+.70*f)),al=alpha*Math.pow(1-f,1.8);
    if(al<.012)continue;
    const lg=ctx.createLinearGradient(-ex,0,ex,0);
    lg.addColorStop(0,css(hot,al*.28));lg.addColorStop(.28,css(hot,al));
    lg.addColorStop(.52,css(hot,al*.76));lg.addColorStop(1,css(hot,al*.20));
    ctx.beginPath();ctx.ellipse(0,ry,ex,ey,0,0,TAU);ctx.fillStyle=lg;ctx.fill();
   }
  };
  // the far side of the disc, lensed over the top of the shadow
  ctx.save();ctx.scale(1,-1);band(a*.80,b*.60,rad*1.03,.46);ctx.restore();
  // the disc itself, then the shadow over its middle
  band(a,b,0,.80);""")

# ------------------------------------------------------------ band, made legible ----
rep("const bandStars=Array.from({length:coarse?900:1900},(_,i)=>{",
    "const bandStars=Array.from({length:coarse?1200:2600},(_,i)=>{")
rep("   ctx.globalAlpha=clamp(.34*bw,0,.72)*(phase?.74:1);",
    "   ctx.globalAlpha=clamp(.58*bw,0,.88)*(phase?.74:1);")
rep("   const al=clamp(n.alpha*bw,0,.34),g2=ctx.createRadialGradient(",
    "   const al=clamp(n.alpha*bw,0,.56),g2=ctx.createRadialGradient(")

# the sky no longer has to meet a floor, so it can fall away into the ink
rep(" g.addColorStop(0,css(p.sky));g.addColorStop(.58,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.ink,.55)));",
    " g.addColorStop(0,css(p.sky));g.addColorStop(.55,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.ink,.76)));")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4b applied:", len(s), "bytes")
