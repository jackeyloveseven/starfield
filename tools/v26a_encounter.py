"""v26a_encounter -- the black hole encounter: make the pull inescapable, and let
the sixth act be a descent that never arrives.

Two things the user asked for, verbatim:

  "怎么也飞不过去的那种窒息感直到吸入进去"
  (that suffocating feeling of never being able to fly past it, until you are
   pulled in)

  "然后第六幕借鉴那个星际穿越仓库不断往深处的那个"
  (and the sixth act should borrow from that Interstellar repo - the one that
   keeps going deeper)

WHAT WAS WRONG. The old machine was FREE -> (4 s of nothing) -> SPIRAL -> FLASH
-> RELEASE. The trigger fired when the lead crane was already 0.60 of a horizon
radius away, so by the time anything happened the fleet had already flown *into*
the well; the four seconds after the trigger did nothing at all, then the spiral
yanked the flock out to 3.2 horizon radii and drew it back in. Nothing fought,
nothing was inevitable, and the camera never once looked at the well - the
baseline capture frame is a white bloom with the horizon entirely off screen. And
the whole thing resolved by snapping the flock back to formation and forgetting.

BEAT (a), INESCAPABILITY. A new GRIP phase replaces the four dead seconds. The
well has hold: the flock is dragged bodily off the corridor onto a closing ring
while the camera leans in and shuts the distance, so the horizon swells past the
frame and can never be seen whole. Steering away from the well is read and it
slows the tide - but only slows it: the ring closes at 1/(8+5*away) per second,
so a hard fight buys five seconds and never a reprieve. GRIP ends on the ring of
no return and DRAWN picks up from exactly there (the handoff is continuous in
position, angle and formation scale - no jump).

BEAT (b), THE SIXTH ACT. The sixth score is 深空漂移 / DEEP DRIFT and it had no
beat of its own; the capture's terminal phase is now that act. After the flash
the piece does not release - it descends. DIVE is a fifteen-second fall that
chains deterministic gear changes (a surge, a hard brake, a surge - the
Interstellar-repo idea of an ever-deepening dive, borrowed as an idea only): the
frame widens so the corridor stretches away into the deep, the flock is strung
out toward the vanishing point, and the surge keeps being re-lit, so it never
arrives. RECOVER is what makes this act END DIFFERENTLY from every other beat in
the piece: the others hard-reset the flock with reseedFlock(); this one eases the
flock home on a smoothstep and lets the surge bleed away slowly, so the journey
is left further down the route than any other beat leaves it. The toast names it.

CAMERA. captureCam() is a whole pose (target, distance, pitch, roll, focal) and
updateDirector blends it in by a single 0..1 factor. The factor is 0 at the
instant of capture, so the entry cannot jump, and it is 1 - blend - 0 across
RECOVER, so the exit cannot jump either. camera.focal is scaled by the same
factor, which is the only thing here that touches the projection: it is how
"space compresses ahead" is faked without touching the raymarcher.

Owns: updateCapture(), the capture state variables, captureCam()/divePose(), and
the capture branch inside updateDirector(). Does NOT touch GLSL_HOLE, drawHole,
chunk(), drawMass, drawWorld, the trigger gate (dist < m.r*0.60 stays, so the
no-pointer case still never fires a capture) or the warp mechanic.

Run:  python -I v26a_encounter.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v26a_encounter.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:180]))
    s = s.replace(a, b, n)


# ---- 1. new state: the grip tide, the fall, the gear, and the camera pose ----
rep(
"let capturePhase=0,captureT=0,captureTotal=0,captureMass=null,captureFlash=0,captureJumped=false;",
"let capturePhase=0,captureT=0,captureTotal=0,captureMass=null,captureFlash=0,captureJumped=false,captureGrip=0,captureDive=0,captureGear=0,captureCamPose=null;")

# ---- 2. the grip reads the steering, so wind must NOT be damped during it ----
# (damped from DRAWN on, when the flock is no longer flying itself)
rep(
" if(capturePhase){wind.x=expStep(wind.x,0,3,dt);wind.y=expStep(wind.y,0,3,dt);return;}",
" if(capturePhase>1){wind.x=expStep(wind.x,0,3,dt);wind.y=expStep(wind.y,0,3,dt);return;}")

# ---- 3. the machine header, and the two new helpers ----
rep(
"""/* FREE -> DRAWN -> SPIRAL -> FLASH -> RELEASE. The lead crane is the body we
 * author; the flock follows on its own springs, which is what draws the
 * stretched paper ribbon for free. */""",
"""/* FREE -> GRIP -> DRAWN -> FLASH -> DIVE -> RECOVER. The lead crane is the body
 * we author; the flock follows on its own springs, which is what draws the
 * stretched paper ribbon for free.
 *
 * GRIP is the inescapable part: the well has hold, the flock is dragged off the
 * corridor, and steering away only slows the tide - the ring closes either way.
 * DRAWN is the last orbit. FLASH is the punch through. Then the piece does not
 * release: DIVE is the sixth act, 深空漂移 / DEEP DRIFT, a fall that keeps
 * descending, and RECOVER is the one ending in the piece that does not reset the
 * flock - it eases it home, so the journey is left deeper than it began. */
function captureCam(){
 const m=captureMass,r=(m&&m.r)||1100;
 if(capturePhase===1){
  // Lean in until the well spills past every edge. You never see it whole.
  const g=smoother(clamp(captureGrip,0,1));
  return {blend:g*.95,tx:m.x,ty:m.y,tz:m.z,distance:mix(3.60,2.45,g)*r,pitch:mix(.34,.16,g),roll:.02*g,focal:mix(1.12,1.30,g)};
 }
 if(capturePhase===2){
  const g=clamp(captureT/6.5,0,1);
  return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:mix(2.45,2.30,g)*r,pitch:mix(.16,.34,g),roll:mix(.02,.06,g),focal:mix(1.30,1.20,g)};
 }
 if(capturePhase===3)return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:2.24*r,pitch:.34,roll:.06,focal:1.20};
 if(capturePhase===4){
  // The fall: move off the well and let the corridor stretch away ahead. The
  // focal is widened so the space in front compresses - the raymarcher is not
  // touched; this is the projection doing it.
  const out=smoother(clamp(captureT/3.5,0,1)),g=smoother(clamp(captureDive,0,1)),fz=travel+520;
  return {blend:1,tx:mix(m.x,routeX(fz),out),ty:mix(m.y,courseY(fz),out),tz:mix(m.z,fz,out),
   distance:mix(2.24*r,mix(2200,4300,g),out),pitch:mix(.34,mix(.10,-.22,g),out),
   roll:mix(.06,.06+.46*g,out),focal:mix(1.20,mix(1.05,.66,g),out)};
 }
 const g=clamp(captureT/6,0,1),fz=travel+520;
 return {blend:1-g,tx:routeX(fz),ty:courseY(fz),tz:fz,distance:mix(4300,1600,g),pitch:mix(-.22,.10,g),roll:.52*(1-g),focal:mix(.66,1.12,g)};
}
/* Where the flock sits during the fall, as a pure function of the bird and of
 * how deep the dive has gone - so DIVE and RECOVER agree exactly at the seam
 * and the flock never has to be teleported. */
function divePose(b,dd){
 const k=(b.bold*.37)%1,edge=1-dd*.55;
 return [b.bx*edge*(.55+.9*k),b.by*edge*.75,mix(700,1900,dd)*(.35+.65*k)];
}""")

# ---- 4. the trigger seeds the new state ----
rep(
"     capturePhase=1;captureT=0;captureTotal=0;captureMass=m;toast('引力捕获 · GRAVITY CAPTURE',6);break;",
"     capturePhase=1;captureT=0;captureTotal=0;captureGrip=0;captureDive=0;captureGear=0;captureMass=m;toast('引力捕获 · GRAVITY CAPTURE',6);break;")

# ---- 5. the interlude is now long by design; the trap-guard moves out with it ----
rep(
" if(captureTotal>26){capturePhase=0;captureFlash=0;captureMass=null;captureTotal=0;reseedFlock();return;}",
""" if(captureTotal>50){capturePhase=0;captureFlash=0;captureMass=null;captureTotal=0;captureGrip=0;captureDive=0;captureGear=0;captureCamPose=null;reseedFlock();return;}
 const m=captureMass;""")

# ---- 6. GRIP and DRAWN. GRIP ends exactly where DRAWN begins: same ring radius,
#         same angle, same formation scale, so the handoff is continuous. ----
rep(
""" if(capturePhase===1){if(captureT>4){capturePhase=2;captureT=0;}}
 else if(capturePhase===2){
  const m=captureMass,r=m.r*3.2*Math.exp(-captureT/2.0),th=captureT*3.0;
  const lx=m.x+Math.cos(th)*r,ly=m.y+Math.sin(th)*r*.62,lz=m.z+Math.sin(th*.5)*r*.5;
  const ox=routeX(travel),oy=courseY(travel),k=r/(m.r*3.2),stretch=1.1+1.7*(1-k);
  for(const b of fleet){
   b.x=lx-ox+b.bx*stretch*.62;b.y=ly-oy+b.by*.55;b.z=lz-travel+b.bz*stretch*.62;
   b.vx=b.vy=b.vz=0;
  }
  if(captureT>6.5){capturePhase=3;captureT=0;captureJumped=false;}
 }""",
""" if(capturePhase===1){
  // GRIP. The well has hold. Steering away from it is read and it stretches the
  // tide from eight seconds toward thirteen - a fight that always loses. The
  // ring closes from 0.60 to 0.22 horizon radii; the camera closes with it.
  const lw=craftWorld(fleet[LEAD]);
  const dx=m.x-lw[0],dz=m.z-lw[2];
  const away=clamp(-Math.sign(dx*camera.right[0]+dz*camera.right[2]||1)*wind.x,0,1);
  captureGrip=clamp(captureGrip+dt/(8+5*away),0,1);
  const g=smoother(captureGrip),rad=mix(m.r*.60,m.r*.22,g);
  for(const b of fleet){
   const wx=routeX(travel)+b.x,wy=courseY(travel)+b.y,wz=travel+b.z;
   b.x=mix(wx,m.x+rad+b.bx*.68,g)-routeX(travel);
   b.y=mix(wy,m.y+b.by*.55,g)-courseY(travel);
   b.z=mix(wz,m.z+b.bz*.68,g)-travel;
   b.vx*=.34;b.vy*=.34;b.vz*=.34;
  }
  if(captureGrip>=1||captureT>14){capturePhase=2;captureT=0;}
 }
 else if(capturePhase===2){
  // The last orbit: the ring closes from the point of no return, and the flock
  // is spread wider as it tightens, so it goes down around the shadow rather
  // than into a point.
  const k=clamp(captureT/6.5,0,1),r=m.r*mix(.22,.045,k),th=captureT*3.0;
  const lx=m.x+Math.cos(th)*r,ly=m.y+Math.sin(th)*r*.62,lz=m.z+Math.sin(th*.5)*r*.5;
  const ox=routeX(travel),oy=courseY(travel),stretch=1.1+1.7*k;
  for(const b of fleet){
   b.x=lx-ox+b.bx*stretch*.62;b.y=ly-oy+b.by*.55;b.z=lz-travel+b.bz*stretch*.62;
   b.vx=b.vy=b.vz=0;
  }
  if(captureT>6.5){capturePhase=3;captureT=0;captureJumped=false;}
 }""")

# ---- 7. the flash now opens the sixth act ----
rep(
""" else if(capturePhase===3){
  captureFlash=Math.sin(Math.PI*clamp(captureT/1.4,0,1));
  if(captureT>.7&&!captureJumped){
   captureJumped=true;warp=28;reseedFlock();
  }
  if(captureT>1.4){capturePhase=4;captureT=0;}
 }""",
""" else if(capturePhase===3){
  captureFlash=Math.sin(Math.PI*clamp(captureT/1.4,0,1));
  if(captureT>.7&&!captureJumped){
   captureJumped=true;warp=28;reseedFlock();
  }
  if(captureT>1.4){capturePhase=4;captureT=0;captureDive=0;captureGear=0;toast('第六幕 · 深空漂移 / ACT VI · DEEP DRIFT',7);}
 }""")

# ---- 8. DIVE and RECOVER replace the old one-and-a-half-second RELEASE ----
rep(
""" else{
  captureFlash=Math.max(0,captureFlash-dt*1.5);
  if(captureT>1.5){capturePhase=0;captureFlash=0;captureMass=null;slingPrev=1e9;}
 }
}""",
""" else if(capturePhase===4){
  // DIVE - the sixth act. A surge, a hard brake, a surge: the gear is chained
  // deterministically (a hash of the segment, never Math.random, because seek()
  // has to replay), so the fall keeps being re-lit and never arrives.
  captureDive=clamp(captureDive+dt/15,0,1);
  const gh=hash(Math.floor(captureT/2.4)*13+7),surge=gh<.58;
  captureGear=expStep(captureGear,surge?5+gh*11:.35,surge?1.6:5.2,dt);
  warp=captureGear;
  const dd=smoother(captureDive);
  for(const b of fleet){
   const p=divePose(b,dd);
   b.x=p[0];b.y=p[1];b.z=p[2];b.vx=b.vy=b.vz=0;
  }
  if(captureDive>=1){capturePhase=5;captureT=0;}
 }
 else{
  // RECOVER - the ending that is different. No reseedFlock(): the flock is eased
  // home on a smoothstep and the surge bleeds away over six seconds, so the
  // corridor resumes from deeper than it left and the fall is never undone.
  captureFlash=Math.max(0,captureFlash-dt*1.2);
  captureGear=expStep(captureGear,0,1.1,dt);warp=captureGear;
  captureDive=clamp(captureDive-dt/6,0,1);
  const back=smoother(clamp(captureT/6,0,1));
  for(const b of fleet){
   const p=divePose(b,1);
   b.x=mix(p[0],b.bx,back);b.y=mix(p[1],b.by,back);b.z=mix(p[2],b.bz,back);
   b.vx*=.86;b.vy*=.86;b.vz*=.86;
  }
  if(captureT>6){capturePhase=0;captureFlash=0;captureMass=null;captureGrip=0;captureDive=0;captureGear=0;captureCamPose=null;slingPrev=1e9;}
 }
}""")

# ---- 9. the director blends the encounter pose in, by one factor ----
rep(
" else{goal.distance+=observation.distance;goal.pitch=clamp(goal.pitch+observation.pitch,-.16,1.48);}",
""" else{goal.distance+=observation.distance;goal.pitch=clamp(goal.pitch+observation.pitch,-.16,1.48);}
 captureCamPose=capturePhase&&captureMass?captureCam():null;
 if(captureCamPose){const c=captureCamPose;goal.distance=mix(goal.distance,c.distance,c.blend);goal.pitch=mix(goal.pitch,c.pitch,c.blend);goal.roll=mix(goal.roll||0,c.roll,c.blend);}""")

rep(
" lookTarget=[routeX(travel),courseY(travel)+camera.aimY,travel];",
""" lookTarget=[routeX(travel),courseY(travel)+camera.aimY,travel];
 if(captureCamPose){const c=captureCamPose;lookTarget=[mix(lookTarget[0],c.tx,c.blend),mix(lookTarget[1],c.ty,c.blend),mix(lookTarget[2],c.tz,c.blend)];}""")

rep(
" camera.forward=f;camera.right=r;camera.up=u;camera.cx=W*.385;camera.cy=H*.465;camera.focal=H*1.12;",
" camera.forward=f;camera.right=r;camera.up=u;camera.cx=W*.385;camera.cy=H*.465;camera.focal=H*1.12*(captureCamPose?mix(1,captureCamPose.focal,captureCamPose.blend):1);")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("v26a_encounter: wrote %s (%d chars)" % (out_p, len(s)))
