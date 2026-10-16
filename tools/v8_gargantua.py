"""V8: the disc, computed instead of painted.

The reference (a Schwarzschild null-geodesic renderer) exposes its whole shading
model. What matters:

  T(r)   = diskTemp * (diskIn/r)^tempExp        ~7400 K at the inner edge
  flux   = (diskIn/r)^1.55                      brightness falls fast outward
  eIn    = smoothstep(diskIn, diskIn*1.14+.06, r)
  eOut   = 1 - smoothstep(diskOut*.74, diskOut*1.04, r)
  flick  = 1 + flicker*.5*(sin(t*.42 + r*2.1) + sin(t*.23 - r*1.3))
  col    = blackbody(T * gt) * flux * dens * eIn * eOut * flick * pow(gt, beaming)

with diskIn=1, diskOut=28-34 Schwarzschild radii - so the disc is far wider than
the shadow, and its colour is a blackbody at a temperature that falls with radius.
My version had a hardcoded white/amber/rust gradient and a disc 3.3 shadow radii
across, which is why it read as painted rather than as hot gas.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

start = s.index("function drawHole(m,q,p,t,rad){")
end = s.index("function drawMass(m,p,t){")
old = s[start:end]

new = """/* Tanner Helland's blackbody approximation, the same ramp the reference uses.
 * It is what makes the inner edge read as hot rather than merely bright. */
function blackbody(kelvin){
 const T=clamp(kelvin,900,40000),t=T*.01;
 const r=T<=6600?1:clamp(Math.pow(Math.max(t-60,1e-3),-.1332047592)*1.292936186,0,1);
 const g=T<=6600?clamp((99.4708025861*Math.log(Math.max(t,1.001))-161.1195681661)/255,0,1)
                :clamp(Math.pow(Math.max(t-60,1e-3),-.0755148492)*288.1221695283/255,0,1);
 const b=T>=6600?1:T<=1900?0:clamp((138.5177312231*Math.log(Math.max(t-10,1e-3))-305.0447927307)/255,0,1);
 return [r*255,g*255,b*255];
}
function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1];
 // 1 shadow radius ~ 2.6 Schwarzschild radii, so the reference's diskIn=1 and
 // diskOut=28-34 come out at roughly 1.1 and 6.5 shadow radii.
 const RIN=rad*1.12,ROUT=rad*6.5,TEMP=7400,TEXP=.75,FLAT=.09,ry=rad*.18;
 glow([m.x,m.y,m.z],rad*4.4,blend(blackbody(TEMP*.55),[255,255,255],.2),.12,2.6);
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  ctx.save();ctx.translate(cx,cy);ctx.lineCap='round';
  const tone=(rr,alpha)=>{
   const T=TEMP*Math.pow(RIN/rr,TEXP),flux=Math.pow(RIN/rr,1.55);
   const eIn=smooth((rr-RIN)/(RIN*.16+.05)),eOut=1-smooth((rr-ROUT*.72)/(ROUT*.32));
   const flick=1+.25*.5*(Math.sin(t*.42+rr*.02)+Math.sin(t*.23-rr*.013));
   return [blackbody(T),clamp(flux*eIn*eOut*flick,0,1)*alpha];
  };
  // The disc: nested ellipses from the rim inward, each at its own blackbody
  // temperature and flux. Doppler is the horizontal ramp - the line-of-sight
  // velocity varies as the cosine of the azimuth, which is exactly what a
  // linear gradient across the disc says.
  const disc=(alpha,ryOff)=>{
   const N=26;
   for(let k=N;k>=1;k--){
    const f=k/N,rr=RIN+(ROUT-RIN)*f,[col,al]=tone(rr,alpha);
    if(al<.004)continue;
    const sx=rr,sy=Math.max(.6,rr*FLAT);
    const lg=ctx.createLinearGradient(-sx,0,sx,0);
    lg.addColorStop(0,css(col,al*.34));lg.addColorStop(.24,css(col,al));
    lg.addColorStop(.50,css(col,al*.70));lg.addColorStop(1,css(col,al*.14));
    ctx.beginPath();ctx.ellipse(0,ryOff,sx,sy,0,0,TAU);ctx.fillStyle=lg;ctx.fill();
   }
  };
  // Fibrous streaks: gas in orbit, not a ribbon of paint.
  const streaks=(alpha,sd)=>{
   for(let k=0;k<26;k++){
    const t0=hash(k+sd,801)*TAU,len=.14+hash(k+sd,802)*.5,fr=.10+.90*hash(k+sd,803);
    const rr=RIN+(ROUT-RIN)*fr;
    const d=.22+.78*(.5-.5*Math.cos(t0));
    const al=alpha*d*(.14+.42*hash(k+sd,804));
    if(al<.02)continue;
    const [col]=tone(rr,1);
    ctx.beginPath();
    for(let j=0;j<=5;j++){
     const th=t0+len*(j/5),px=Math.cos(th)*rr,py=ry+Math.sin(th)*Math.max(.6,rr*FLAT);
     if(j)ctx.lineTo(px,py);else ctx.moveTo(px,py);
    }
    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(.5,rad*(.006+.022*hash(k+sd,805)));
    ctx.stroke();
   }
  };
  // The far side of the disc, lensed into a compressed arc over the top of the
  // shadow, and the secondary image of it underneath.
  const lensed=(alpha,below)=>{
   const N=10;
   for(let k=N;k>=1;k--){
    const f=k/N,rr=rad*(1.10+.78*f),[col,al]=tone(RIN+(ROUT-RIN)*f*.62,alpha);
    if(al<.006)continue;
    ctx.beginPath();
    ctx.ellipse(0,0,rr,rr*.90,0,below?0:Math.PI,below?Math.PI:TAU);
    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(1.2,rad*.10);ctx.stroke();
   }
  };
  lensed(1.0,false);
  lensed(.20,true);
  disc(1,ry);
  // the shadow, over the middle of the disc
  const sg=ctx.createRadialGradient(0,0,rad*.80,0,0,rad*1.03);
  sg.addColorStop(0,'#04050a');sg.addColorStop(.90,'#04050a');sg.addColorStop(1,'rgba(4,5,10,0)');
  ctx.beginPath();ctx.arc(0,0,rad*1.03,0,TAU);ctx.fillStyle=sg;ctx.fill();
  // only the near half of the disc passes in front of the shadow
  ctx.save();ctx.beginPath();ctx.rect(-ROUT*1.2,ry,ROUT*2.4,ROUT*1.4);ctx.clip();
  disc(1,ry);streaks(1,40);
  ctx.restore();
  streaks(.85,40);
  // the photon ring: razor thin, and the brightest thing in the frame
  ctx.beginPath();ctx.arc(0,0,rad*1.055,0,TAU);
  ctx.strokeStyle=css(blend(blackbody(TEMP*1.5),[255,255,255],.5),.95);
  ctx.lineWidth=Math.max(.8,rad*.020);ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,rad*1.15,0,TAU);
  ctx.strokeStyle=css(blackbody(TEMP*.8),.16);ctx.lineWidth=Math.max(1.4,rad*.07);ctx.stroke();
  ctx.restore();
 }});
}
"""

s = s[:start] + new + s[end:]
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V8 applied:", len(s), "bytes")
