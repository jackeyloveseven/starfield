"""V5: the band back in the world, Gargantua's disc, and worlds that read as spheres.

Three complaints, all fair:

1. The band was re-anchored to the view every frame (V4j). That kept it on screen
   but made it slide when you steer, which is worse than it being absent. Fixed in
   the world instead: its plane is the VERTICAL plane containing the direction of
   travel, so the great circle passes through ahead, overhead and underfoot at
   once. A director that pitches 74 degrees down still sees it.

2. The black hole's disc was 2.5 shadow radii across and 0.16 as thick, drawn as
   seven nested ellipses - a fat ring. Gargantua is a THIN disc seen almost
   edge-on: the shadow, a razor-thin photon ring, a thin band across the front,
   and the far side of the disc bent up over the top of the shadow with a fainter
   secondary image underneath.

3. The worlds were a smooth radial highlight plus straight parallel stripes, which
   is a beach ball. An engraved sphere is hatched in curves that follow the form -
   circles of constant angle about the light axis, which project to curves, not to
   straight lines.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# ------------------------------------------------------- 1. band, fixed in world ----
rep("""/* The band the corridor runs inside. Its plane is rebuilt from the camera basis
 * every frame rather than pinned to the world horizon: the camera director spends
 * most of its time pitched ~74 degrees down at the fleet, so a horizon-locked band
 * is out of shot almost always. The plane contains the view direction - the band
 * therefore always crosses the frame - rolled .62 rad so it runs diagonally. */
function bandBasisNow(){
 const fl=Math.hypot(camera.forward[0],camera.forward[1],camera.forward[2])||1;
 const f=[camera.forward[0]/fl,camera.forward[1]/fl,camera.forward[2]/fl];
 const d=camera.up[0]*f[0]+camera.up[1]*f[1]+camera.up[2]*f[2];
 let u=[camera.up[0]-d*f[0],camera.up[1]-d*f[1],camera.up[2]-d*f[2]];
 const ul=Math.hypot(u[0],u[1],u[2])||1;u=[u[0]/ul,u[1]/ul,u[2]/ul];
 const c=[f[1]*u[2]-f[2]*u[1],f[2]*u[0]-f[0]*u[2],f[0]*u[1]-f[1]*u[0]];
 const th=.62,ct=Math.cos(th),st=Math.sin(th);
 let n=[u[0]*ct+c[0]*st,u[1]*ct+c[1]*st,u[2]*ct+c[2]*st];
 const nl=Math.hypot(n[0],n[1],n[2])||1;n=[n[0]/nl,n[1]/nl,n[2]/nl];
 const v=[n[1]*f[2]-n[2]*f[1],n[2]*f[0]-n[0]*f[2],n[0]*f[1]-n[1]*f[0]];
 return [f,v,n];
}""",
    """/* The band the corridor runs inside, fixed in the world. Its plane is the
 * VERTICAL plane containing the direction of travel, so its great circle passes
 * through ahead, overhead and underfoot at once - a director that spends most of
 * its time pitched 74 degrees down at the fleet still sees it. (An earlier version
 * re-anchored the plane to the view every frame; that kept it on screen but made
 * it slide around whenever the hand moved, which is worse than it being absent.) */
const BAND_U=[.10,.20,1],BAND_UP=[0,1,0];
const BAND_BASIS=(()=>{
 const un=Math.hypot(BAND_U[0],BAND_U[1],BAND_U[2]),u=[BAND_U[0]/un,BAND_U[1]/un,BAND_U[2]/un];
 const d=BAND_UP[0]*u[0]+BAND_UP[1]*u[1]+BAND_UP[2]*u[2];
 let v=[BAND_UP[0]-d*u[0],BAND_UP[1]-d*u[1],BAND_UP[2]-d*u[2]];
 const vl=Math.hypot(v[0],v[1],v[2])||1;v=[v[0]/vl,v[1]/vl,v[2]/vl];
 const n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
 return [u,v,n];
})();""")
rep("  const [BU,BV,BN]=bandBasisNow();", "  const [BU,BV,BN]=BAND_BASIS;")

# ------------------------------------------------------------- 2. Gargantua ----
rep("""function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1],hot=blend(p.sun,[255,238,206],.52),a=rad*2.5,b=Math.max(1.2,a*.16);
 glow([m.x,m.y,m.z],rad*4.2,hot,.20,2.4);   // queued now; fn() runs during flush()
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  ctx.save();ctx.translate(cx,cy);
  // Nested ellipses rather than one flat fill: the disc is hottest at the inner
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
  band(a,b,0,.80);
  const sg=ctx.createRadialGradient(0,0,rad*.72,0,0,rad*1.04);
  sg.addColorStop(0,'#05060a');sg.addColorStop(.86,'#05060a');sg.addColorStop(1,'rgba(5,6,10,0)');
  ctx.beginPath();ctx.arc(0,0,rad*1.04,0,TAU);ctx.fillStyle=sg;ctx.fill();
  // the near side passes in front of the shadow
  band(a,b,0,.92);
  // photon ring
  ctx.beginPath();ctx.arc(0,0,rad*1.06,0,TAU);
  ctx.strokeStyle=css(blend(hot,[255,255,255],.45),.92);ctx.lineWidth=Math.max(.7,rad*.035);ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,rad*1.20,0,TAU);
  ctx.strokeStyle=css(hot,.22);ctx.lineWidth=Math.max(1.2,rad*.10);ctx.stroke();
  ctx.restore();
 }});
}""",
    """function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1],hot=blend(p.sun,[255,240,214],.55);
 // The disc is thin and seen almost edge-on, so b is a small fraction of a -
 // at .16 of it the whole thing read as a fat ring rather than a disc.
 const a=rad*3.1,b=Math.max(1.0,a*.05);
 glow([m.x,m.y,m.z],rad*4.6,hot,.15,2.6);
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  ctx.save();ctx.translate(cx,cy);ctx.lineCap='round';
  // One strand: a thin ellipse, Doppler-brightened on the side coming toward us.
  const strand=(sx,sy,ry,alpha)=>{
   const lg=ctx.createLinearGradient(-sx,0,sx,0);
   lg.addColorStop(0,css(hot,alpha*.34));
   lg.addColorStop(.26,css(hot,alpha));
   lg.addColorStop(.48,css(hot,alpha*.84));
   lg.addColorStop(.72,css(hot,alpha*.40));
   lg.addColorStop(1,css(hot,alpha*.15));
   ctx.beginPath();ctx.ellipse(0,ry,sx,sy,0,0,TAU);ctx.fillStyle=lg;ctx.fill();
  };
  // the far side of the disc, bent up over the top of the shadow
  strand(a*.88,b*1.05,-rad*1.19,.40);
  strand(a*.72,b*.92,-rad*1.33,.20);
  // the secondary image: the underside, bent under the shadow, much fainter
  strand(a*.68,b*.86, rad*1.05,.15);
  // the disc itself, seen almost edge-on
  strand(a,b,0,.88);
  // the shadow, over the middle of the disc
  const sg=ctx.createRadialGradient(0,0,rad*.80,0,0,rad*1.03);
  sg.addColorStop(0,'#04050a');sg.addColorStop(.90,'#04050a');sg.addColorStop(1,'rgba(4,5,10,0)');
  ctx.beginPath();ctx.arc(0,0,rad*1.03,0,TAU);ctx.fillStyle=sg;ctx.fill();
  // the near side passes in front of the shadow
  strand(a,b,0,.88);
  // the photon ring: razor thin, and the brightest thing in the frame
  ctx.beginPath();ctx.arc(0,0,rad*1.055,0,TAU);
  ctx.strokeStyle=css(blend(hot,[255,255,255],.62),.95);ctx.lineWidth=Math.max(.8,rad*.022);ctx.stroke();
  ctx.beginPath();ctx.arc(0,0,rad*1.15,0,TAU);
  ctx.strokeStyle=css(hot,.18);ctx.lineWidth=Math.max(1.4,rad*.07);ctx.stroke();
  ctx.restore();
 }});
}""")

# --------------------------------------------------------- 3. engraved worlds ----
rep("""function drawWorld(m,q,p,t,rad,tint){
 const cx=q[0],cy=q[1],lx=-.46,ly=-.58;
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  if(rad<2.4){ctx.beginPath();ctx.arc(cx,cy,Math.max(.6,rad),0,TAU);ctx.fillStyle=css(tint,.85);ctx.fill();return;}
  const g=ctx.createRadialGradient(cx+lx*rad*.58,cy+ly*rad*.58,rad*.05,cx,cy,rad*1.06);
  g.addColorStop(0,css(blend(tint,[255,255,255],.50)));
  g.addColorStop(.40,css(tint));
  g.addColorStop(.74,css(shade(tint,.40)));
  g.addColorStop(1,css(shade(tint,.13)));
  ctx.beginPath();ctx.arc(cx,cy,rad,0,TAU);ctx.fillStyle=g;ctx.fill();
  // the night side, hatched the way an engraver would
  ctx.save();ctx.beginPath();ctx.arc(cx,cy,rad*.995,0,TAU);ctx.clip();
  // Hatched only where the light does not reach, and fine enough to read as
  // engraving: full-width coarse lines made every world a beach ball.
  const step=Math.max(1.6,rad*.085),edge=rad*.06;
  ctx.strokeStyle=css(p.ink,.30);ctx.lineWidth=Math.max(.45,rad*.022);
  for(let k=edge;k<rad;k+=step){
   const f=(k-edge)/rad;
   ctx.globalAlpha=.20+f*.52;
   ctx.beginPath();ctx.moveTo(cx-rad,cy+k);ctx.lineTo(cx+rad,cy+k-rad*.30);ctx.stroke();
  }
  ctx.globalAlpha=1;
  const tg=ctx.createRadialGradient(cx+lx*rad*.62,cy+ly*rad*.62,rad*.26,cx+lx*rad*.52,cy+ly*rad*.52,rad*1.30);
  tg.addColorStop(0,'rgba(0,0,0,0)');tg.addColorStop(.52,'rgba(0,0,0,0)');tg.addColorStop(1,css(p.ink,.90));
  ctx.fillStyle=tg;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.restore();
  ctx.beginPath();ctx.arc(cx,cy,rad*.99,0,TAU);ctx.strokeStyle=css(p.ink,.46);ctx.lineWidth=Math.max(.5,rad*.028);ctx.stroke();
 }});
}""",
    """function drawWorld(m,q,p,t,rad,tint){
 const cx=q[0],cy=q[1];
 // The light sits a little out of the view plane. With it exactly in the plane the
 // hatch lines project to straight parallels - which is what made every world look
 // like a beach ball. Tilted, they curve with the form.
 const L=[-.44,-.56,.44],ln=Math.hypot(L[0],L[1],L[2]),l=[L[0]/ln,L[1]/ln,L[2]/ln];
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  if(rad<2.4){ctx.beginPath();ctx.arc(cx,cy,Math.max(.6,rad),0,TAU);ctx.fillStyle=css(tint,.85);ctx.fill();return;}
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,rad,0,TAU);ctx.clip();
  const g=ctx.createRadialGradient(cx+l[0]*rad,cy+l[1]*rad,rad*.05,cx,cy,rad*1.34);
  g.addColorStop(0,css(blend(tint,[255,255,255],.54)));
  g.addColorStop(.30,css(tint));
  g.addColorStop(.58,css(shade(tint,.58)));
  g.addColorStop(.80,css(shade(tint,.20)));
  g.addColorStop(1,css(shade(tint,.06)));
  ctx.fillStyle=g;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  // Engraved in circles of constant angle about the light axis: those are the
  // curves that follow a sphere's form, and they crowd together into the night.
  const u0=[-l[1],l[0],0],un=Math.hypot(u0[0],u0[1],u0[2])||1,U=[u0[0]/un,u0[1]/un,u0[2]/un];
  const V=[l[1]*U[2]-l[2]*U[1],l[2]*U[0]-l[0]*U[2],l[0]*U[1]-l[1]*U[0]];
  ctx.strokeStyle=css(p.ink,.5);
  for(let k=1;k<=11;k++){
   const phi=k/11*Math.PI*.94,cph=Math.cos(phi),sph=Math.sin(phi);
   ctx.globalAlpha=.07+Math.pow(k/11,1.7)*.44;
   ctx.lineWidth=Math.max(.4,rad*(.014+.010*k/11));
   ctx.beginPath();
   for(let j=0;j<=30;j++){
    const th=j/30*TAU,ct=Math.cos(th),st=Math.sin(th);
    const px=(cph*l[0]+sph*(ct*U[0]+st*V[0]))*rad,py=(cph*l[1]+sph*(ct*U[1]+st*V[1]))*rad;
    if(j)ctx.lineTo(cx+px,cy+py);else ctx.moveTo(cx+px,cy+py);
   }
   ctx.stroke();
  }
  ctx.globalAlpha=1;
  // the lit limb is brighter than the middle of the disc
  const lb=ctx.createRadialGradient(cx,cy,rad*.78,cx,cy,rad);
  lb.addColorStop(0,'rgba(0,0,0,0)');lb.addColorStop(1,css(blend(tint,[255,255,255],.36),.50));
  ctx.fillStyle=lb;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.restore();
  ctx.beginPath();ctx.arc(cx,cy,rad*.995,0,TAU);ctx.strokeStyle=css(p.ink,.40);ctx.lineWidth=Math.max(.5,rad*.022);ctx.stroke();
 }});
}""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V5 applied:", len(s), "bytes")
