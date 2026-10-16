"""V9: flat and clean, the way the reference actually is.

Studied Dyson Sphere Program's own screenshots. Its worlds are smooth pale spheres:
a bright sub-solar point, a WIDE soft terminator falling to black, a bright rim on
the lit limb, and almost no surface detail at all. Its nebulae are clean soft wisps
on deep navy with high contrast.

Mine had engraved hatching, latitude bands, and a hard-ish edge - which at the
size a world actually appears on screen is noise, not detail. That is why three
rounds of adding more surface structure never made them look better. This removes
all of it and commits to a smooth, flat, bright sphere.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

start = s.index("function drawWorld(m,q,p,t,rad,tint){")
end = s.index("/* Tanner Helland's blackbody approximation")
old = s[start:end]

new = """/* A world, kept smooth and clean. The engraved hatching, the latitude bands and
 * the hard edge that used to be here are all gone: at the size a world actually
 * appears on screen they read as noise. What sells a planet at this scale is the
 * shape of the light - a bright sub-solar point, a wide soft terminator falling
 * to black, and a rim where the light grazes the limb. */
function drawWorld(m,q,p,t,rad,tint){
 const cx=q[0],cy=q[1];
 const L=[-.40,-.50,.77],ln=Math.hypot(L[0],L[1],L[2]),l=[L[0]/ln,L[1]/ln,L[2]/ln];
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  if(rad<2.4){ctx.beginPath();ctx.arc(cx,cy,Math.max(.6,rad),0,TAU);ctx.fillStyle=css(tint,.85);ctx.fill();return;}
  // the atmosphere, behind the disc
  const ax=cx+l[0]*rad*.5,ay=cy+l[1]*rad*.5;
  const ag=ctx.createRadialGradient(ax,ay,rad*.70,ax,ay,rad*1.46);
  ag.addColorStop(0,css(blend(tint,[255,255,255],.55),.36));
  ag.addColorStop(.55,css(blend(tint,[255,255,255],.5),.12));
  ag.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(cx,cy,rad*1.20,0,TAU);ctx.fillStyle=ag;ctx.fill();
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,rad,0,TAU);ctx.clip();
  // the disc: bright at the sub-solar point, falling away to black
  const g=ctx.createRadialGradient(cx+l[0]*rad*.92,cy+l[1]*rad*.92,rad*.02,cx,cy,rad*1.46);
  g.addColorStop(0,css(blend(tint,[255,255,255],.66)));
  g.addColorStop(.24,css(tint));
  g.addColorStop(.48,css(shade(tint,.62)));
  g.addColorStop(.70,css(shade(tint,.28)));
  g.addColorStop(1,css(shade(tint,.05)));
  ctx.fillStyle=g;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  // three soft cloud bands, low contrast
  for(let k=0;k<3;k++){
   const off=(-.36+k*.36)*rad;
   const bg=ctx.createLinearGradient(0,cy+off-rad*.18,0,cy+off+rad*.18);
   bg.addColorStop(0,'rgba(255,255,255,0)');
   bg.addColorStop(.5,css(blend(tint,[255,255,255],.55),.12));
   bg.addColorStop(1,'rgba(255,255,255,0)');
   ctx.beginPath();ctx.ellipse(cx,cy+off,rad*1.02,rad*.17,0,0,TAU);ctx.fillStyle=bg;ctx.fill();
  }
  ctx.restore();
  // the rim: light grazing the limb is brighter than the middle of the disc
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,rad*1.02,0,TAU);ctx.arc(cx,cy,rad*.84,0,TAU,true);ctx.clip();
  const rg=ctx.createRadialGradient(ax,ay,rad*.44,ax,ay,rad*1.56);
  rg.addColorStop(0,css(blend(tint,[255,255,255],.74),.60));
  rg.addColorStop(.55,css(blend(tint,[255,255,255],.5),.18));
  rg.addColorStop(1,'rgba(255,255,255,0)');
  ctx.fillStyle=rg;ctx.fillRect(cx-rad*1.1,cy-rad*1.1,rad*2.2,rad*2.2);
  ctx.restore();
  ctx.beginPath();ctx.arc(cx,cy,rad*.995,0,TAU);
  ctx.strokeStyle=css(p.ink,.26);ctx.lineWidth=Math.max(.5,rad*.016);ctx.stroke();
 }});
}
"""

s = s[:start] + new + s[end:]

# the disc ran too orange: the reference's visible disc is white through cream
s = s.replace("const RIN=rad*1.12,ROUT=rad*6.5,TEMP=7400,TEXP=.75,FLAT=.09,ry=rad*.18;",
              "const RIN=rad*1.12,ROUT=rad*6.0,TEMP=9600,TEXP=.82,FLAT=.09,ry=rad*.18;", 1)
s = s.replace("const T=TEMP*Math.pow(RIN/rr,TEXP),flux=Math.pow(RIN/rr,1.55);",
              "const T=TEMP*Math.pow(RIN/rr,TEXP),flux=Math.pow(RIN/rr,1.95);", 1)


GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V9 applied:", len(s), "bytes")