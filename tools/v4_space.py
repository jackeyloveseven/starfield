"""V4: make it read as a cosmos rather than a landscape.

The user's read, three times running: it does not feel like space, and the route
is a chessboard. Both trace to the same thing - deepfield() draws an opaque plane
tiled on a 900x940 grid with a road down the middle, inherited from the migration
piece where a patchwork of fields under a flock of cranes is exactly right.

So the ground goes, and the paper becomes the picture plane instead of the floor:
a star chart. In its place: a full-sky star sphere (the old field only covered the
upper hemisphere, which is why a floor was needed to fill the bottom), a Milky Way
band marking the corridor, worlds drawn as engraved discs with a terminator, and
a black hole with the general-relativistic furniture - shadow, photon ring, and an
accretion disc whose far side is lensed up over the top.

Also fixes two measured defects: the fleet being torn apart by gravity from every
scenery mass (maxRadius 3238 against a 276-unit rest radius), and the full-screen
white fill on every capture.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# ---------------------------------------------------------------- full sky ----
# Elevation was sampled uniformly in [0, 1.5] rad, so every star, bright star and
# nebula sat in the upper hemisphere; the floor existed to hide the empty half.
# Sample y uniformly instead - a uniform sphere, no pole clustering.
rep("""const stars=Array.from({length:coarse?2400:5000},(_,i)=>{
 const a=hash(i,110)*TAU,e=.03+hash(i,111)*1.46,mag=Math.pow(hash(i,114),2.6);
 return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:.34+mag*2.4,mag,phase:hash(i,113)*TAU};
});""",
    """const stars=Array.from({length:coarse?2400:5000},(_,i)=>{
 const a=hash(i,110)*TAU,y=hash(i,111)*2-1,r=Math.sqrt(Math.max(0,1-y*y)),mag=Math.pow(hash(i,114),2.6);
 return {x:Math.cos(a)*r,y,z:Math.sin(a)*r,size:.34+mag*2.4,mag,phase:hash(i,113)*TAU};
});""")

rep("""const brightStars=Array.from({length:coarse?7:12},(_,i)=>{
 const a=hash(i,310)*TAU,e=.06+hash(i,311)*1.4;
 return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:1.9+hash(i,312)*2.4,phase:hash(i,313)*TAU,warm:hash(i,314)>.55};
});""",
    """const brightStars=Array.from({length:coarse?7:12},(_,i)=>{
 const a=hash(i,310)*TAU,y=hash(i,311)*2-1,r=Math.sqrt(Math.max(0,1-y*y));
 return {x:Math.cos(a)*r,y,z:Math.sin(a)*r,size:1.9+hash(i,312)*2.4,phase:hash(i,313)*TAU,warm:hash(i,314)>.55};
});
/* The band the corridor runs inside: a great circle through the direction of
 * travel, so flying forward the Milky Way converges ahead and sweeps overhead. */
const BAND_U=[.10,0,1],BAND_REF=[.62,.74,-.06];
function bandBasis(){
 const n0=Math.hypot(...BAND_U),u=BAND_U.map(v=>v/n0);
 const d=BAND_REF[0]*u[0]+BAND_REF[1]*u[1]+BAND_REF[2]*u[2];
 const t=BAND_REF.map((v,i)=>v-d*u[i]),tn=Math.hypot(...t),n=t.map(v=>v/tn);
 const v=[n[1]*u[2]-n[2]*u[1],n[2]*u[0]-n[0]*u[2],n[0]*u[1]-n[1]*u[0]];
 return [u,v,n];
}
const [BAND_U1,BAND_V,BAND_N]=bandBasis();
function bandDir(a,g){
 const x=BAND_U1[0]*Math.cos(a)+BAND_V[0]*Math.sin(a)+BAND_N[0]*g;
 const y=BAND_U1[1]*Math.cos(a)+BAND_V[1]*Math.sin(a)+BAND_N[1]*g;
 const z=BAND_U1[2]*Math.cos(a)+BAND_V[2]*Math.sin(a)+BAND_N[2]*g;
 const n=Math.hypot(x,y,z);
 return [x/n,y/n,z/n];
}
const bandStars=Array.from({length:coarse?900:1900},(_,i)=>{
 const a=hash(i,410)*TAU,g=(hash(i,411)+hash(i,412)+hash(i,413)-1.5)*.085,mag=Math.pow(hash(i,414),2.4);
 const d=bandDir(a,g);
 return {x:d[0],y:d[1],z:d[2],size:.30+mag*2.1,mag,phase:hash(i,415)*TAU};
});
const bandWash=Array.from({length:coarse?9:15},(_,i)=>{
 const a=hash(i,420)*TAU,g=(hash(i,421)-.5)*.10,d=bandDir(a,g);
 return {x:d[0],y:d[1],z:d[2],size:.30+hash(i,422)*.46,alpha:.10+hash(i,423)*.20};
});""")

rep(" const a=hash(i,210)*TAU,e=.02+hash(i,211)*1.05;",
    " const a=hash(i,210)*TAU,y=hash(i,211)*2-1,r=Math.sqrt(Math.max(0,1-y*y));")
rep(" return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:.30+hash(i,212)*.58,seed:1+Math.floor(hash(i,213)*6),rot:hash(i,214)*TAU,alpha:.17+hash(i,215)*.38};",
    " return {x:Math.cos(a)*r,y,z:Math.sin(a)*r,size:.30+hash(i,212)*.58,seed:1+Math.floor(hash(i,213)*6),rot:hash(i,214)*TAU,alpha:.17+hash(i,215)*.38};")

# ------------------------------------------------------------------ lensing ----
# The Einstein radius now scales with the hole's own projected size, so the ring
# sits just outside the shadow at any distance, and the deflection reaches six
# Einstein radii out instead of a fixed 360px.
rep("  if(q&&q[2]>40&&q[2]<14000&&q[0]>-500&&q[0]<W+500&&q[1]>-500&&q[1]<H+500)lensSources.push([q[0],q[1]]);",
    "  if(q&&q[2]>40&&q[2]<14000&&q[0]>-900&&q[0]<W+900&&q[1]>-900&&q[1]<H+900)lensSources.push([q[0],q[1],clamp(m.r*q[3],4,Math.max(W,H))]);")

rep("""function lensWarp(x,y){
 if(!lensSources.length)return [x,y];
 let dx=0,dy=0;
 for(const L of lensSources){
  const ex=x-L[0],ey=y-L[1],r2=ex*ex+ey*ey;
  if(r2>129600||r2<1)continue;
  const r=Math.sqrt(r2),pull=clamp(4200/r,0,110)*(1-smooth((r-130)/230));
  if(pull<=0)continue;
  dx+=ex/r*pull;dy+=ey/r*pull;
 }
 return [x+dx,y+dy];
}""",
    """function lensWarp(x,y){
 if(!lensSources.length)return [x,y];
 let dx=0,dy=0;
 for(const L of lensSources){
  const rE=L[2]*1.35,ex=x-L[0],ey=y-L[1],r2=ex*ex+ey*ey;
  const rmax=rE*6;
  if(r2>rmax*rmax||r2<1)continue;
  const r=Math.sqrt(r2),pull=Math.min(rE*rE/r,r*2.4);
  if(pull<=0)continue;
  dx+=ex/r*pull;dy+=ey/r*pull;
 }
 return [x+dx,y+dy];
}""")

# -------------------------------------------------------------------- worlds ----
rep("""function drawMass(m,p,t){
 if(m.kind===4){
  const pts=[];for(let i=0;i<36;i++){const a=i/36*TAU;pts.push([m.x+Math.cos(a)*m.r,m.y+Math.sin(a)*m.r,m.z]);}
  glow([m.x,m.y,m.z],m.r*1.35,blend(p.sun,p.paper,.30),.26,3.6);
  poly(pts,[7,9,13],{noFog:true,alpha:1});
  const ring=[];for(let i=0;i<=44;i++){const a=i/44*TAU,rr=m.r*(1.22+.10*Math.sin(a*3+t*.5+m.phase));ring.push([m.x+Math.cos(a)*rr,m.y+Math.sin(a)*rr,m.z]);}
  line(ring,blend(p.sun,[255,246,228],.55),.62,1.2);
  return;
 }
 const tint=m.kind===0?blend(p.sun,p.paper,.30):m.kind===1?p.sun:m.kind===2?blend(p.sun,[255,214,170],.45):blend(p.sun,[196,214,255],.5);
 glow([m.x,m.y,m.z],m.r*.55,tint,.62,3.0);
 sprite([m.x,m.y,m.z],m.r*.34,blend(tint,[255,255,255],.5),'snow',.92);
}""",
    """/* Screen-space, because a world is a sphere: a flat disc in the XY plane
 * collapsed to a sliver and popped whenever the corridor passed one edge-on. */
function massTint(m,p){
 return m.kind===0?blend(p.sun,p.paper,.30):m.kind===1?p.sun:m.kind===2?blend(p.sun,[255,214,170],.45):blend(p.sun,[196,214,255],.5);
}
function drawWorld(m,q,p,t,rad,tint){
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
  const step=Math.max(2.2,rad*.17);
  ctx.strokeStyle=css(p.ink,.26);ctx.lineWidth=Math.max(.5,rad*.032);
  for(let k=-rad;k<rad;k+=step){ctx.beginPath();ctx.moveTo(cx-rad,cy+k);ctx.lineTo(cx+rad,cy+k-rad*.34);ctx.stroke();}
  const tg=ctx.createRadialGradient(cx+lx*rad*.62,cy+ly*rad*.62,rad*.26,cx+lx*rad*.52,cy+ly*rad*.52,rad*1.30);
  tg.addColorStop(0,'rgba(0,0,0,0)');tg.addColorStop(.52,'rgba(0,0,0,0)');tg.addColorStop(1,css(p.ink,.90));
  ctx.fillStyle=tg;ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.restore();
  ctx.beginPath();ctx.arc(cx,cy,rad*.99,0,TAU);ctx.strokeStyle=css(p.ink,.46);ctx.lineWidth=Math.max(.5,rad*.028);ctx.stroke();
 }});
}
/* The general-relativistic furniture: the shadow, the photon ring just outside
 * it, and an accretion disc seen nearly edge-on whose far side is bent up and
 * over the top of the shadow. Drawn in screen space, so it is stable at any
 * angle, and Doppler-brightened on one side. */
function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1],hot=blend(p.sun,[255,238,206],.52),a=rad*3.6,b=Math.max(1.4,a*.20);
 glow([m.x,m.y,m.z],rad*4.2,hot,.20,2.4);   // queued now; fn() runs during flush()
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  ctx.save();ctx.translate(cx,cy);
  const band=(sx,sy,ry,alpha)=>{
   const lg=ctx.createLinearGradient(-sx,0,sx,0);
   lg.addColorStop(0,css(hot,alpha*.34));lg.addColorStop(.30,css(hot,alpha));
   lg.addColorStop(.52,css(hot,alpha*.80));lg.addColorStop(1,css(hot,alpha*.26));
   ctx.beginPath();ctx.ellipse(0,ry,sx,sy,0,0,TAU);ctx.fillStyle=lg;ctx.fill();
  };
  // the far side of the disc, lensed over the top of the shadow
  ctx.save();ctx.scale(1,-1);band(a*.86,b*.78,rad*1.06,.62);ctx.restore();
  // the disc itself, then the shadow over its middle
  band(a,b,0,.92);
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
}
function drawMass(m,p,t){
 const q=project([m.x,m.y,m.z]);
 if(!q||q[2]<=30)return;
 const rad=m.r*q[3];
 if(m.kind===4){if(rad<1)return;drawHole(m,q,p,t,rad);return;}
 const tint=massTint(m,p);
 if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);
 drawWorld(m,q,p,t,rad,tint);
}""")

# type 4: a screen-space composite that still takes part in the depth sort
rep("  else if(o.type===3){const g=ctx.createRadialGradient(o.p[0],o.p[1],0,o.p[0],o.p[1],o.s*o.spread);",
    "  else if(o.type===4){o.fn();}\n  else if(o.type===3){const g=ctx.createRadialGradient(o.p[0],o.p[1],0,o.p[0],o.p[1],o.s*o.spread);")

# ------------------------------------------------------------------ the band ----
rep(" const intensity=p.front*.22+p.shimmer*.12+(1-p.void)*.035;",
    """ // The Milky Way: the corridor's own band of stars and wash, so the route is
 // legible without a road drawn on the ground.
 const bw=.30+p.wash*.85+p.core*.40;
 if(bw>.08){
  for(const n of bandWash){
   const q=skyPoint([n.x,n.y,n.z]);if(!q)continue;
   const rad=n.size*camera.focal*.75,pad=rad*.55;
   if(q[0]<-pad||q[0]>W+pad||q[1]<-pad||q[1]>H+pad)continue;
   const w=lensWarp(q[0],q[1]);
   const al=clamp(n.alpha*bw,0,.34),g2=ctx.createRadialGradient(w[0],w[1],0,w[0],w[1],rad);
   g2.addColorStop(0,css(blend(p.sun,p.paper,.30),al));g2.addColorStop(.45,css(blend(p.sun,p.paper,.30),al*.32));g2.addColorStop(1,css(blend(p.sun,p.paper,.30),0));
   ctx.fillStyle=g2;ctx.fillRect(w[0]-rad,w[1]-rad,rad*2,rad*2);
   fillPx+=rad*rad*4;
  }
  const bb=[[],[]];
  for(const st of bandStars){
   const q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
   const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
   if(x<-6||x>W+6||y<-6||y>H+6)continue;
   bb[Math.sin(time*.35+st.phase)>0?1:0].push(x,y,st.size);
  }
  ctx.fillStyle=css(blend(p.craft,[255,255,255],.34));
  for(let phase=0;phase<2;phase++){
   const b2=bb[phase];if(!b2.length)continue;
   ctx.globalAlpha=clamp(.34*bw,0,.72)*(phase?.74:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b2.length;j+=3){ctx.moveTo(b2[j]+b2[j+2],b2[j+1]);ctx.arc(b2[j],b2[j+1],b2[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
  ctx.globalAlpha=1;
 }
 const intensity=p.front*.22+p.shimmer*.12+(1-p.void)*.035;""")

# sky gradient no longer needs to meet a floor
rep(" g.addColorStop(0,css(p.sky));g.addColorStop(.68,css(p.horizon));g.addColorStop(1,css(p.fog));",
    " g.addColorStop(0,css(p.sky));g.addColorStop(.58,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.ink,.55)));")

rep("""function flatQuad(x0,z0,x1,z1,y=0){return [[x0,y,z0],[x1,y,z0],[x1,y,z1],[x0,y,z1]];}
/* The sheet of paper the cosmos is printed on, a faint lattice of printed
 * hatching, and the dust lane the cranes follow. The sheet carries its own
 * compositing passes and fades as the camera tilts up, so looking into deep
 * space never puts an opaque floor in front of the stars. */
function hatchCorner(ix,iz){return [ix*900+58*Math.sin(iz*.33+ix*.21),iz*940+44*Math.sin(ix*.36+iz*.17)];}
function lanePoint(z,offset,y=.6){const d=laneD(z),n=1/Math.hypot(1,d);return [laneX(z)+offset*n,y,z-offset*d*n];}
function deepfield(){""",
    """/* The wide bloom the corridor runs through. The tiled floor, the printed
 * lattice and the dust lane that used to live here are gone: they put a horizon
 * across every frame and read as a chessboard. What marks the route now is the
 * Milky Way band, drawn with the rest of the sky. */
function deepfield(){""")

# ------------------------------------------------------------------ no ground ----
rep(""" // Opaque: looking up simply carries the horizon off the bottom of the
 // screen. A pitch-driven alpha here made the whole lower half pop between
 // paper and stars within a few degrees of pitch.
 fillPx+=W*H;poly(flatQuad(camera.eye[0]-100000,camera.eye[2]-100000,camera.eye[0]+100000,camera.eye[2]+100000,-2),currentPalette.fog,{noFog:true});
 flush();""",
    """ // No ground: the paper is the picture plane, not a floor. A tiled plane here
 // put a horizon across every frame and read as a chessboard.""")
rep(""" const ix0=Math.floor(camera.eye[0]/900),iz0=Math.floor(camera.eye[2]/940),range=lowQuality?9:12;
 for(let iz=iz0-range;iz<=iz0+range;iz++)for(let ix=ix0-range;ix<=ix0+range;ix++){
  const x=ix*900+450,z=iz*940+470,pj=project([x,0,z]);
  if(!pj||pj[2]>12000||pj[0]<-800||pj[0]>W+800||pj[1]<-700||pj[1]>H+700)continue;
  const p=region(x,z),id=Math.floor(hash(ix,iz,21)*6),c=p.fields[id];
  const corners=[[ix,iz],[ix+1,iz],[ix+1,iz+1],[ix,iz+1]].map(v=>hatchCorner(...v));
  const v=corners.map(a=>[a[0],0,a[1]]);
  poly(v,c,{palette:p,alpha:.30+p.core*.34});
  if(pj[2]<6000&&hash(ix,iz,23)>.42){
   const count=hash(ix,iz,24)>.48?7:4;
   for(let n=1;n<count;n++){
    const f=n/count,g=f+.018,across=hash(ix,iz,25)>.5;
    const a=across?[v[0],v[3]]:[v[0],v[1]],b=across?[v[1],v[2]]:[v[3],v[2]];
    const lerp3=(aa,bb,t)=>aa.map((q,i)=>mix(q,bb[i],t));
    poly([lerp3(a[0],a[1],f),lerp3(b[0],b[1],f),lerp3(b[0],b[1],g),lerp3(a[0],a[1],g)],shade(c,1.14),{palette:p,alpha:.34});
   }
  }
  if(pj[2]<5600&&hash(ix,iz,31)>.86)line([v[0].map((a,i)=>i===1?1:a),v[1].map((a,i)=>i===1?1:a)],p.treeDark,.14,.6);
 }
 flush();
 const zmin=Math.floor((camera.eye[2]-14000)/170)*170,zmax=camera.eye[2]+14000;
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),w0=laneW(z),w1=laneW(z+170);
  poly([lanePoint(z,-w0-26,.2),lanePoint(z,w0+26,.2),lanePoint(z+170,w1+26,.2),lanePoint(z+170,-w1-26,.2)],p.bank,{palette:p,alpha:.62});
 }
 flush();
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),w0=laneW(z)*.72,w1=laneW(z+170)*.72;
  poly([lanePoint(z,-w0,.6),lanePoint(z,w0,.6),lanePoint(z+170,w1,.6),lanePoint(z+170,-w1,.6)],p.water,{palette:p,alpha:.72});
 }
 flush();
 // Young stars still embedded in the lane, drawn as short printed strokes.
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),pj=project([laneX(z),0,z]);if(!pj||pj[2]>7000||pj[0]<-300||pj[0]>W+300||pj[1]<-200||pj[1]>H+200)continue;
  const w=laneW(z);
  for(let n=0;n<3;n++){
   const k=Math.floor(z/170),offset=(hash(k,n,61)-.5)*w*1.5+Math.sin(time*.2+k)*8;
   const st=z+hash(k,n,63)*85+mod(time*3+hash(k,n,64)*23,28),length=22+hash(k,n,65)*68;
   line([lanePoint(st,offset,1),lanePoint(st+length,offset+5,1)],blend(p.water,p.paper,.62),(.18+.13*Math.sin(time*.31+n+k)**2)*(.35+p.shimmer*.65),clamp(pj[3]*1.6,.45,1.5));
  }
 }
 flush();""",
    """""")

# ------------------------------------------------------------------- gravity ----
# Every scenery mass pulled every ship: at 600 units a mid-size star applied ~300
# units/s^2 against a formation spring of 75-180, so the stars out-pulled the
# formation (measured maxRadius 3238 against a 276-unit rest radius).
rep("const GRAV=1.35e8,MASS_KIND=[.35,.7,1,1.6,2.4],LEAD=2;",
    "const GRAV=1.6e7,MASS_KIND=[.35,.7,1,1.6,2.4],LEAD=2;")
rep("""   for(const m of activeMasses){
    const gx=wp[0]-m.x,gy=wp[1]-m.y,gz=wp[2]-m.z;""",
    """   for(const m of activeMasses){
    if(m.kind!==4)continue;   // worlds are scenery; only the ink well pulls a ship
    const gx=wp[0]-m.x,gy=wp[1]-m.y,gz=wp[2]-m.z;""")

# --------------------------------------------------------------- capture flash ----
rep(""" if(captureFlash>.002){
  ctx.save();ctx.fillStyle=css(currentPalette.craft,captureFlash*.62);ctx.fillRect(0,0,W,H);
  const fg=ctx.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,Math.hypot(W,H)*.62);
  fg.addColorStop(0,css(currentPalette.sun,captureFlash*.34));fg.addColorStop(1,css(currentPalette.sun,0));
  ctx.fillStyle=fg;ctx.fillRect(0,0,W,H);ctx.restore();
 }""",
    """ if(captureFlash>.002&&captureMass){
  // A bloom around the ink well, not a full-screen fill: the old one painted the
  // whole frame white at .62 alpha on every capture.
  const q=project([captureMass.x,captureMass.y,captureMass.z]);
  if(q){
   const r=clamp(captureMass.r*q[3]*7,90,Math.hypot(W,H)*.92);
   const fg=ctx.createRadialGradient(q[0],q[1],0,q[0],q[1],r);
   fg.addColorStop(0,css(currentPalette.sun,captureFlash*.52));
   fg.addColorStop(.30,css(currentPalette.sun,captureFlash*.20));
   fg.addColorStop(1,css(currentPalette.sun,0));
   ctx.fillStyle=fg;ctx.fillRect(0,0,W,H);
  }
 }""")

# the corridor's drawn width died with the road it measured
rep("const laneW=z=>139+27*Math.sin(z*.00072+.8)+11*Math.sin(z*.0021);\n", "")

# ----------------------------------------------------------------------- HUD ----
rep(" $('flight-stats').textContent=`ALT ${Math.round(courseY(travel))} M  /  ${FLEET_COUNT} CRAFT`;",
    " $('flight-stats').textContent=`${(travel/1000).toFixed(1)} KLY  /  ${FLEET_COUNT} CRAFT`;")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4 applied:", len(s), "bytes")
