"""P3: gravity, slingshot, and being taken by a horizon.

Two layers, one mass list:
  - the course bends, as a pure function of z (a Lorentzian bulge toward each
    heavy body), so the camera, the flock, the chart and the audio all follow
    without a single call site changing
  - every crane feels the pull inside the existing sub-step integrator, which
    is what stretches the flock into a ribbon near a horizon
Gravity goes in as one more force term; no new integrator.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit(f"expected 1, found {s.count(old)}:\n{old[:150]}")
    s = s.replace(old, new, 1)


# ------------------------------------------------------------- state ------
rep("let lookTarget=[0,224,travel];",
    "let lookTarget=[0,224,travel];\n"
    "let activeMasses=[],sling=0,slingPrev=1e9,slingHold=0;\n"
    "let capturePhase=0,captureT=0,captureMass=null,captureFlash=0,captureJumped=false;\n"
    "const GRAV=1.35e8,MASS_KIND=[.35,.7,1,1.6,2.4],LEAD=2;")

# -------------------------------------------- the course bends (pure in z) --
rep("const routeX=z=>laneX(z)*.68-120+55*Math.sin(z*.00086+1);",
    "const routeX=z=>laneX(z)*.68-120+55*Math.sin(z*.00086+1)+courseBend(z);")

rep("function local(h,a,y,b){return [h.x+h.u[0]*a+h.v[0]*b,y,h.z+h.u[1]*a+h.v[1]*b];}",
    """/* Massive bodies bend the course. A pure function of z, so every consumer of
 * the corridor follows for free and the world stays revisitable. */
function courseBend(z){
 let sum=0;
 const k0=Math.floor(z/CHUNK);
 for(let k=k0-1;k<=k0+1;k++)for(const m of chunk(k).masses){
  if(m.kind<2)continue;
  const dz=z-m.z,rr=m.kind===4?900:700,amp=(m.kind===4?260:150)*(m.kind===4?1.5:.8);
  sum+=(m.x>=laneX(m.z)?1:-1)*amp*rr*rr/(dz*dz+rr*rr);
 }
 return sum;
}
function local(h,a,y,b){return [h.x+h.u[0]*a+h.v[0]*b,y,h.z+h.u[1]*a+h.v[1]*b];}""")

# ------------------------------------- a horizon sits close to the corridor --
rep("""  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=560+r()*1700,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[110,150,200,260,330][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});""",
    """  const z=z0+r()*CHUNK,side=r()>.5?1:-1,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;
  // A horizon sits near the corridor, so the course is really bent by it.
  const off=kind===4?140+r()*520:560+r()*1700;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[110,150,200,260,330][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});""")

# -------------------------------------------------- gravity + capture ------
rep("function birdWorld(b){return [routeX(travel)+b.x,courseY(travel)+b.y,travel+b.z];}",
    """function birdWorld(b){return [routeX(travel)+b.x,courseY(travel)+b.y,travel+b.z];}
function updateGravity(){
 activeMasses.length=0;
 const k0=Math.floor(travel/CHUNK);
 for(let k=k0-2;k<=k0+2;k++)for(const m of chunk(k).masses){
  if(Math.abs(m.z-travel)>7200)continue;
  activeMasses.push(m);
 }
}
function flockCentre(){
 let x=0,y=0,z=0;for(const b of birds){x+=b.x;y+=b.y;z+=b.z;}
 const n=birds.length;
 return [routeX(travel)+x/n,courseY(travel)+y/n,travel+z/n];
}
/* The corridor damps every step, so an honest slingshot could never come out
 * faster. Make the boost a narrative beat instead, decided by impact
 * parameter: steering away from a horizon is rewarded with distance. */
function updateSling(dt){
 const c=flockCentre();let near=1e9;
 for(const m of activeMasses){const d=Math.hypot(c[0]-m.x,c[1]-m.y,c[2]-m.z);if(d<near)near=d;}
 if(near>slingPrev&&slingPrev<1900&&slingHold<=0&&capturePhase===0)slingHold=2.4;
 slingPrev=near;
 if(slingHold>0){slingHold-=dt;sling=Math.sin(Math.PI*clamp(1-slingHold/2.4,0,1))*(1-clamp(slingPrev/1900,0,1));}
 else sling=0;
}
function reseedFlock(){
 const ga=Math.PI*(3-Math.sqrt(5));
 for(let i=0;i<birds.length;i++){
  const b=birds[i],a=i*ga,rad=Math.sqrt((i+.5)/birds.length);
  b.bx=Math.cos(a)*rad*276;b.bz=Math.sin(a)*rad*218;b.by=(i%4-1.5)*18;
  b.x=b.bx;b.y=b.by;b.z=b.bz;b.vx=b.vy=b.vz=0;
 }
}
/* FREE -> DRAWN -> SPIRAL -> FLASH -> RELEASE. The lead crane is the body we
 * author; the flock follows on its own springs, which is what draws the
 * stretched paper ribbon for free. */
function updateCapture(dt){
 if(capturePhase===0){
  if(!started||!activeMasses.length)return;
  const lw=birdWorld(birds[LEAD]);
  for(const m of activeMasses){
   if(m.kind!==4||m.z<travel-500)continue;
   if(Math.hypot(lw[0]-m.x,lw[1]-m.y,lw[2]-m.z)<m.r*2.4){
    capturePhase=1;captureT=0;captureMass=m;toast('引力捕获 · GRAVITY CAPTURE',6);break;
   }
  }
  return;
 }
 captureT+=dt;
 if(capturePhase===1){if(captureT>4){capturePhase=2;captureT=0;}}
 else if(capturePhase===2){
  const m=captureMass,r=m.r*3.2*Math.exp(-captureT/2.0),th=captureT*3.0;
  const lx=m.x+Math.cos(th)*r,ly=m.y+Math.sin(th)*r*.62,lz=m.z+Math.sin(th*.5)*r*.5;
  const ox=routeX(travel),oy=courseY(travel),k=r/(m.r*3.2);
  for(const b of birds){
   b.x=lx-ox+b.bx*k*1.5;b.y=ly-oy+b.by*k*1.5;b.z=lz-travel+b.bz*k*1.5;
   b.vx=b.vy=b.vz=0;
  }
  if(captureT>6.5){capturePhase=3;captureT=0;captureJumped=false;}
 }
 else if(capturePhase===3){
  captureFlash=Math.sin(Math.PI*clamp(captureT/1.4,0,1));
  if(captureT>.7&&!captureJumped){
   captureJumped=true;travel+=2600;reseedFlock();
  }
  if(captureT>1.4){capturePhase=4;captureT=0;}
 }
 else{
  captureFlash=Math.max(0,captureFlash-dt*1.5);
  if(captureT>1.5){capturePhase=0;captureFlash=0;captureMass=null;slingPrev=1e9;}
 }
}""")

# --------------------------------------- one more force, inside the sub-step --
rep("""   const screen=project(birdWorld(b)),lo=W*(.045+.013*Math.sin(time*.34+b.phase)),hi=W*(.572+.017*Math.sin(time*.31+b.phase));""",
    """   const wp=birdWorld(b),screen=project(wp),lo=W*(.045+.013*Math.sin(time*.34+b.phase)),hi=W*(.572+.017*Math.sin(time*.31+b.phase));""")

rep("""   b.fx=(tx-b.x)*b.k;b.fy=(ty-b.y)*(b.k*.78);b.fz=(tz-b.z)*(b.k*.83);
   const p=screen;""",
    """   b.fx=(tx-b.x)*b.k;b.fy=(ty-b.y)*(b.k*.78);b.fz=(tz-b.z)*(b.k*.83);
   for(const m of activeMasses){
    const gx=wp[0]-m.x,gy=wp[1]-m.y,gz=wp[2]-m.z;
    const r2=gx*gx+gy*gy+gz*gz+57600,f=GRAV*MASS_KIND[m.kind]/(r2*Math.sqrt(r2));
    b.fx-=f*gx;b.fy-=f*gy;b.fz-=f*gz;
   }
   const p=screen;""")

# --------------------------------------------- your hand lets go when taken --
rep(" const targetX=input((wind.filteredX-.42)/.55)*energy,targetY=input((wind.filteredY-.5)/.5)*energy;",
    " if(capturePhase){wind.x=expStep(wind.x,0,3,dt);wind.y=expStep(wind.y,0,3,dt);return;}\n"
    " const targetX=input((wind.filteredX-.42)/.55)*energy,targetY=input((wind.filteredY-.5)/.5)*energy;")

# ------------------------------------------------------------- the loop ----
rep("if(dt){time+=dt;if(started){travel+=SPEED*dt;flightTime+=dt;}else{previewTime+=dt;travel+=SPEED*.15*dt;}}",
    "if(dt){time+=dt;if(started){travel+=SPEED*dt*(1+1.1*sling);flightTime+=dt;}else{previewTime+=dt;travel+=SPEED*.15*dt;}}")
rep("if(dt){updateWind(dt);updateBirds(dt);updateParticles(dt);updatePoem(dt);}",
    "if(dt){updateWind(dt);updateGravity();updateBirds(dt);updateCapture(dt);updateSling(dt);updateParticles(dt);updatePoem(dt);}")
rep("   updateDirector(step);updateWind(step);updateBirds(step);updateParticles(step);updatePoem(step);",
    "   updateDirector(step);updateWind(step);updateGravity();updateBirds(step);updateCapture(step);updateSling(step);updateParticles(step);updatePoem(step);")

# ------------------------------------------------------------ the flash ----
rep("""function paperFinish(){
 ctx.save();ctx.globalAlpha=.40;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;""",
    """function paperFinish(){
 ctx.save();ctx.globalAlpha=.40;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;
 if(captureFlash>.002){
  ctx.save();ctx.fillStyle=css(currentPalette.bird,captureFlash*.94);ctx.fillRect(0,0,W,H);
  const fg=ctx.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,Math.hypot(W,H)*.62);
  fg.addColorStop(0,css(currentPalette.sun,captureFlash*.5));fg.addColorStop(1,css(currentPalette.sun,0));
  ctx.fillStyle=fg;ctx.fillRect(0,0,W,H);ctx.restore();
 }""")

# --------------------------------------------------------- diagnostics -----
rep("regionMix:currentPalette.t,travel,flightTime,",
    "regionMix:currentPalette.t,travel,flightTime,capture:capturePhase,sling:Math.round(sling*100)/100,masses:activeMasses.length,")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("p3 applied")
