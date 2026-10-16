"""V6b: put the disc's three images where the reference puts them.

In the Interstellar still the far side of the disc is not another flat band: it is
an ARC bent up over the top of the shadow, roughly concentric with it, joining the
direct band at the sides. And the direct band crosses in FRONT of the shadow along
its near edge only - drawing the whole ellipse again after the shadow put the far
half in front too, which is why it read as a plate rather than a ring.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

start = s.index("function drawHole(m,q,p,t,rad){")
end = s.index("function drawMass(m,p,t){")
old = s[start:end]

new = """function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1];
 // White-hot at the inner edge, amber through the body, rust at the rim.
 const white=[255,250,242],amber=[255,178,98],rust=[150,74,38];
 const a=rad*3.3,b=Math.max(1.2,a*.09),ry=rad*.20;
 glow([m.x,m.y,m.z],rad*4.0,blend(amber,[255,255,255],.34),.13,2.6);
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  ctx.save();ctx.translate(cx,cy);ctx.lineCap='round';
  // Doppler along the length, radial tone across it.
  const dop=(col,al,sx)=>{
   const lg=ctx.createLinearGradient(-sx,0,sx,0);
   lg.addColorStop(0,css(col,al*.42));lg.addColorStop(.24,css(col,al));
   lg.addColorStop(.46,css(col,al*.86));lg.addColorStop(.70,css(col,al*.42));
   lg.addColorStop(1,css(col,al*.15));return lg;
  };
  const sheet=(sx,sy,alpha)=>{
   ctx.beginPath();ctx.ellipse(0,ry,sx,sy,0,0,TAU);ctx.fillStyle=dop(amber,alpha,sx);ctx.fill();
   for(let k=0;k<4;k++){
    const f=k/3,ex=sx*(.26+.20*f),ey=Math.max(.7,sy*(.26+.20*f));
    ctx.beginPath();ctx.ellipse(0,ry,ex,ey,0,0,TAU);ctx.fillStyle=dop(white,alpha*(.54-.14*f),ex);ctx.fill();
   }
  };
  // Fibrous streaks: the disc is gas in orbit, not a ribbon of paint.
  const streaks=(alpha,sd)=>{
   for(let k=0;k<22;k++){
    const t0=hash(k+sd,801)*TAU,len=.16+hash(k+sd,802)*.52,rr=.30+.64*hash(k+sd,803);
    const d=.24+.76*(.5-.5*Math.cos(t0));
    const al=alpha*d*(.16+.48*hash(k+sd,804));
    if(al<.02)continue;
    const col=rr<.50?white:rr<.78?amber:rust;
    ctx.beginPath();
    for(let j=0;j<=5;j++){
     const th=t0+len*(j/5),px=Math.cos(th)*a*rr,py=ry+Math.sin(th)*Math.max(.6,b*rr);
     if(j)ctx.lineTo(px,py);else ctx.moveTo(px,py);
    }
    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(.5,rad*(.006+.022*hash(k+sd,805)));
    ctx.stroke();
   }
  };
  // The lensed far side: an arc bent up over the top of the shadow, concentric
  // with it, not a second flat band.
  const arcBand=(rr,ww,alpha,below)=>{
   for(let k=0;k<4;k++){
    const f=k/3;
    ctx.beginPath();
    ctx.ellipse(0,0,rad*(rr+f*.17),rad*(rr*.90+f*.17),0,below?0:Math.PI,below?Math.PI:TAU);
    ctx.strokeStyle=css(k<2?white:amber,alpha*(.55-.13*f));
    ctx.lineWidth=Math.max(1,rad*ww*(1-f*.28));ctx.stroke();
   }
  };
  arcBand(1.34,.19,.50,false);          // the far side, over the top
  arcBand(1.15,.12,.15,true);           // the secondary image, underneath
  // the disc itself, seen almost edge-on
  sheet(a,b,.90);streaks(1,40);
  // the shadow, over the middle of the disc
  const sg=ctx.createRadialGradient(0,0,rad*.80,0,0,rad*1.03);
  sg.addColorStop(0,'#04050a');sg.addColorStop(.90,'#04050a');sg.addColorStop(1,'rgba(4,5,10,0)');
  ctx.beginPath();ctx.arc(0,0,rad*1.03,0,TAU);ctx.fillStyle=sg;ctx.fill();
  // only the near half of the disc passes in front of the shadow
  ctx.save();ctx.beginPath();ctx.rect(-a*1.3,ry,a*2.6,a*1.4);ctx.clip();
  sheet(a,b,.90);streaks(1,40);
  ctx.restore();
  // the photon ring: razor thin, and the brightest thing in the frame
  ctx.beginPath();ctx.arc(0,0,rad*1.055,0,TAU);
  ctx.strokeStyle=css(blend(white,amber,.22),.95);ctx.lineWidth=Math.max(.8,rad*.020);ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,rad*1.15,0,TAU);
  ctx.strokeStyle=css(amber,.16);ctx.lineWidth=Math.max(1.4,rad*.07);ctx.stroke();
  ctx.restore();
 }});
}
"""

s = s[:start] + new + s[end:]
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V6b applied:", len(s), "bytes")
