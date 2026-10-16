"""V6: the disc as flowing gas, worlds with surfaces, nebulae with dust.

From the Interstellar still: the disc is NOT a smooth thin ribbon. It is a broad
turbulent sheet - fibrous streaks flowing along it, blown out to pure white at the
inner edge, amber through the middle, rust at the rim, with a razor-thin photon
ring and a distinct secondary arc. The previous version was a flat gradient fill,
which is why it read as painted rather than as gas.

From the Horsehead reference: a nebula only reads as gas when something occludes
it. The wash was pure additive glow with no dark structure at all.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# --------------------------------------------------- 1. the disc as flowing gas ----
old_hole = s[s.index("function drawHole(m,q,p,t,rad){"):s.index("function drawMass(m,p,t){")]
rep(old_hole,
    """function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1];
 // White-hot at the inner edge, amber through the body, rust at the rim.
 const white=[255,250,242],amber=[255,178,98],rust=[150,74,38];
 const a=rad*3.3,b=Math.max(1.2,a*.10);
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
  const sheet=(sx,sy,ry,alpha)=>{
   ctx.beginPath();ctx.ellipse(0,ry,sx,sy,0,0,TAU);ctx.fillStyle=dop(amber,alpha,sx);ctx.fill();
   for(let k=0;k<4;k++){
    const f=k/3,ex=sx*(.28+.18*f),ey=Math.max(.7,sy*(.28+.18*f));
    ctx.beginPath();ctx.ellipse(0,ry,ex,ey,0,0,TAU);ctx.fillStyle=dop(white,alpha*(.50-.13*f),ex);ctx.fill();
   }
  };
  // Fibrous streaks: the disc is gas in orbit, not a ribbon of paint.
  const streaks=(sx,sy,ry,alpha,sd)=>{
   for(let k=0;k<20;k++){
    const t0=hash(k+sd,801)*TAU,len=.16+hash(k+sd,802)*.52,rr=.34+.62*hash(k+sd,803);
    const d=.26+.74*(.5-.5*Math.cos(t0));
    const al=alpha*d*(.16+.46*hash(k+sd,804));
    if(al<.02)continue;
    const col=rr<.52?white:rr<.80?amber:rust;
    ctx.beginPath();
    for(let j=0;j<=5;j++){
     const th=t0+len*(j/5),px=Math.cos(th)*sx*rr,py=ry+Math.sin(th)*Math.max(.6,sy*rr);
     if(j)ctx.lineTo(px,py);else ctx.moveTo(px,py);
    }
    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(.5,rad*(.006+.020*hash(k+sd,805)));
    ctx.stroke();
   }
  };
  // the far side of the disc, bent up over the top of the shadow
  sheet(a*.90,b*1.00,-rad*1.20,.44);streaks(a*.90,b*1.00,-rad*1.20,.80,0);
  sheet(a*.74,b*.88,-rad*1.34,.20);
  // the secondary image: the underside, bent under the shadow, much fainter
  sheet(a*.70,b*.82, rad*1.06,.13);
  // the disc itself, seen almost edge-on
  sheet(a,b,0,.90);streaks(a,b,0,1,40);
  // the shadow, over the middle of the disc
  const sg=ctx.createRadialGradient(0,0,rad*.80,0,0,rad*1.03);
  sg.addColorStop(0,'#04050a');sg.addColorStop(.90,'#04050a');sg.addColorStop(1,'rgba(4,5,10,0)');
  ctx.beginPath();ctx.arc(0,0,rad*1.03,0,TAU);ctx.fillStyle=sg;ctx.fill();
  // the near side passes in front of the shadow
  sheet(a,b,0,.90);streaks(a,b,0,1,40);
  // the photon ring: razor thin, and the brightest thing in the frame
  ctx.beginPath();ctx.arc(0,0,rad*1.055,0,TAU);
  ctx.strokeStyle=css(blend(white,amber,.22),.95);ctx.lineWidth=Math.max(.8,rad*.020);ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,rad*1.15,0,TAU);
  ctx.strokeStyle=css(amber,.16);ctx.lineWidth=Math.max(1.4,rad*.07);ctx.stroke();
  ctx.restore();
 }});
}
""")

# --------------------------------------------------- 2. worlds with surfaces ----
rep("""  ctx.fillStyle=g;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  // Engraved in circles of constant angle about the light axis: those are the""",
    """  ctx.fillStyle=g;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  // Surface bands, following the sphere's own axis: the thing that says "world"
  // rather than "ball".
  const PA0=[.16,.97,.18],pan=Math.hypot(PA0[0],PA0[1],PA0[2]),pax=[PA0[0]/pan,PA0[1]/pan,PA0[2]/pan];
  const pv0=[-pax[2],0,pax[0]],pvn=Math.hypot(pv0[0],pv0[1],pv0[2])||1,PU=[pv0[0]/pvn,pv0[1]/pvn,pv0[2]/pvn];
  const PV=[pax[1]*PU[2]-pax[2]*PU[1],pax[2]*PU[0]-pax[0]*PU[2],pax[0]*PU[1]-pax[1]*PU[0]];
  for(let k=0;k<9;k++){
   const phi=-1.05+k/8*2.10,cph=Math.cos(phi),sph=Math.sin(phi);
   const tone=.64+.58*Math.abs(Math.sin(k*2.3+m.phase));
   ctx.beginPath();
   for(let j=0;j<=30;j++){
    const th=j/30*TAU,ct=Math.cos(th),st=Math.sin(th);
    const px=(sph*pax[0]+cph*(ct*PU[0]+st*PV[0]))*rad,py=(sph*pax[1]+cph*(ct*PU[1]+st*PV[1]))*rad;
    if(j)ctx.lineTo(cx+px,cy+py);else ctx.moveTo(cx+px,cy+py);
   }
   ctx.strokeStyle=css(shade(tint,tone),.16);ctx.lineWidth=Math.max(.8,rad*.07);ctx.stroke();
  }
  // Engraved in circles of constant angle about the light axis: those are the""")

# --------------------------------------------------- 3. dust in front of the gas ----
rep(""" g.globalCompositeOperation='destination-in';
 const m=g.createRadialGradient(N*.5,N*.5,0,N*.5,N*.5,N*.5);""",
    """ // Dark dust in front of the lit gas: a nebula reads as gas only when something
 // occludes it. Pure additive glow with no dark structure is just a smudge.
 g.globalCompositeOperation='destination-out';
 for(let i=0;i<8;i++){
  const x=N*.5+(r()-.5)*N*.80,y=N*.5+(r()-.5)*N*.80,rad=N*(.07+r()*.24);
  const gr=g.createRadialGradient(x,y,0,x,y,rad);
  gr.addColorStop(0,`rgba(0,0,0,${(.30+r()*.50).toFixed(3)})`);
  gr.addColorStop(1,'rgba(0,0,0,0)');
  g.fillStyle=gr;g.fillRect(0,0,N,N);
 }
 g.globalCompositeOperation='source-over';
 g.globalCompositeOperation='destination-in';
 const m=g.createRadialGradient(N*.5,N*.5,0,N*.5,N*.5,N*.5);""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V6 applied:", len(s), "bytes")
