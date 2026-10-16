"""V5c: atmosphere, and engraving fine enough to read as tone.

A perfectly smooth sphere with a hard edge is the other half of what makes a
painted planet look fake: a thin rim of scattered light at the limb, brightest
where the light strikes, is the cue that says "this has air around it".
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("""  g.addColorStop(0,css(blend(tint,[255,255,255],.54)));
  g.addColorStop(.30,css(tint));
  g.addColorStop(.58,css(shade(tint,.58)));
  g.addColorStop(.80,css(shade(tint,.20)));
  g.addColorStop(1,css(shade(tint,.06)));""",
    """  g.addColorStop(0,css(blend(tint,[255,255,255],.56)));
  g.addColorStop(.28,css(tint));
  g.addColorStop(.55,css(shade(tint,.50)));
  g.addColorStop(.78,css(shade(tint,.15)));
  g.addColorStop(1,css(shade(tint,.04)));""")

rep("""  for(let k=1;k<=9;k++){
   const f=k/9,phi=(.58+.40*f)*Math.PI,cph=Math.cos(phi),sph=Math.sin(phi);
   ctx.globalAlpha=.06+Math.pow(f,1.5)*.52;
   ctx.lineWidth=Math.max(.4,rad*.016);""",
    """  for(let k=1;k<=13;k++){
   const f=k/13,phi=(.55+.43*f)*Math.PI,cph=Math.cos(phi),sph=Math.sin(phi);
   ctx.globalAlpha=.05+Math.pow(f,1.5)*.46;
   ctx.lineWidth=Math.max(.35,rad*.011);""")

rep("""  ctx.globalAlpha=1;
  // the lit limb is brighter than the middle of the disc
  const lb=ctx.createRadialGradient(cx,cy,rad*.78,cx,cy,rad);
  lb.addColorStop(0,'rgba(0,0,0,0)');lb.addColorStop(1,css(blend(tint,[255,255,255],.36),.50));
  ctx.fillStyle=lb;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.restore();""",
    """  ctx.globalAlpha=1;
  // the lit limb is brighter than the middle of the disc
  const lb=ctx.createRadialGradient(cx,cy,rad*.78,cx,cy,rad);
  lb.addColorStop(0,'rgba(0,0,0,0)');lb.addColorStop(1,css(blend(tint,[255,255,255],.36),.50));
  ctx.fillStyle=lb;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.restore();
  // Air: a thin ring of scattered light just outside the limb, brightest where
  // the light lands. A bare disc with a hard edge is the other half of "fake".
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,rad*1.13,0,TAU);ctx.arc(cx,cy,rad*.965,0,TAU,true);ctx.clip();
  const ax=cx+l[0]*rad*.42,ay=cy+l[1]*rad*.42;
  const ag=ctx.createRadialGradient(ax,ay,rad*.5,ax,ay,rad*1.85);
  ag.addColorStop(0,css(blend(tint,[255,255,255],.55),.40));
  ag.addColorStop(.55,css(blend(tint,[255,255,255],.40),.15));
  ag.addColorStop(1,css(blend(tint,[255,255,255],.40),0));
  ctx.fillStyle=ag;ctx.fillRect(cx-rad*1.2,cy-rad*1.2,rad*2.4,rad*2.4);
  ctx.restore();""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V5c applied:", len(s), "bytes")
