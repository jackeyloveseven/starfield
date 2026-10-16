"""v27f_framing -- the black hole ENCOUNTER, reframed so the whole well is in
shot and the fleet is a small off-centre detail.

WHAT THE USER SAID. The last round made the hole bigger ("the event horizon
could be more exaggerated") and this round's build shows only a sliver of the
photon ring, cropped by every edge. They sent the Interstellar Gargantua still
and said:

  "我说的是类似这种 一窥全貌，你看这个图多震撼"   (I mean something like THIS - a
   glimpse of the WHOLE - look how stunning this image is)
  "飞船在一个角落"                                  (the ship is in a corner)

The reference is overwhelming because the hole is LARGE and COMPLETE - the
entire shadow in frame, the disc sweeping across the full width, the far side
lensed up over the shadow - with the station a tiny detail in a corner. Not
because it is cropped.

WHY IT BROKE, measured. The drawn hole is a sprite whose screen radius is
rad = m.r * q[3] (q[3] = camera.focal / depth), and the disc's light reaches
3.45 rad (9 Schwarzschild radii against a 2.608 rs shadow). The mass radius was
doubled to 2200 last round, and the free-flight camera distance is fixed by the
lens table, NOT a multiple of m.r - so in free flight the apparent size doubled
straight through: at the encounter the shadow came out ~378 px in a 900 px
frame and the disc ~163% of the frame width. During the CAPTURE the camera
distance IS a multiple of r (captureCam), so that framing is scale-free - but
the multiples themselves were sized for a hole whose disc is only ~2x the
shadow. At GRIP the camera sits 2.45 r out, which puts rad = focal/2.45 ~ 411 px
- the shadow alone is a full frame height. Both ends are simply too close.

THE FIX, three levers, none of them physics:

  1. THE MASS RADIUS GOES BACK TO 1100, and the capture factor .30 -> .60, so
     the capture distance is still exactly 660 (dist < m.r*.60). Nothing about
     the gravity changes - updateBirds uses GRAV*MASS_KIND[kind], never m.r -
     and the lens warp, the drawn shadow and the flash bloom all read m.r*q[3],
     so they shrink together and stay registered.

  2. captureCam PULLS BACK. The camera distances were 3.60 -> 2.45 r (GRIP),
     2.45 -> 2.30 (DRAWN), 2.24 (FLASH). They are 6.00 -> 5.20, 5.20 -> 4.90,
     4.70 now, which is rad ~ 190 px at the start of the grip and ~255 px at the
     flash: the shadow is 42-57% of the frame height and the disc sweeps 81-111%
     of its width - the whole well, with margin, exactly like the reference.
     The pull-back runs on its own fast ramp so it completes in the first few
     seconds of GRIP instead of over the whole thirteen, and the pose stays
     continuous at every seam: 5.20 -> 5.20 at GRIP|DRAWN, 4.70 -> 4.70 at
     DRAWN|FLASH, 4.70 -> 4.70 at FLASH|DIVE. pitch, roll and focal are
     untouched, so the entry (blend 0) and the RECOVER exit (blend -> 0) still
     cannot jump.

  3. THE ENCOUNTER SHOT. In free flight the camera watched the corridor, so the
     fleet sat on the projection centre and the well wandered past the edge. Now,
     when an ink well is close and ahead, the camera turns onto it - the aim
     swings to the well and the fleet is left small and off to one side, which is
     the reference framing ("look past the fleet at the well"). The weight eases
     to zero with distance and with how far the well is off the bow, so an
     ordinary stretch of corridor is untouched, and it is skipped entirely during
     a capture (that pose is the capture's own).

Owns: captureCam() (the pose only), the capture branch of updateDirector(), the
mass radius literal and the capture trigger factor. Does NOT touch GLSL_HOLE,
drawHole, drawMass, drawWorld, chunk()'s placement, updateCapture()'s state
machine or divePose().

Run:  python -I v27f_framing.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v27f_framing.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:200]))
    s = s.replace(a, b, n)


# ---- 1. the mass radius back to 1100; the capture factor compensates ----
# The 2200 was chosen for the size of the horizon and the camera was never moved
# with it. 1100 is the value every framing multiple in this file was written
# against, and the factor .30 -> .60 keeps the capture distance at 660.
rep(
"""   // A horizon sits well off to the side: scenery with gravity, not a roadblock.
   // On the course it swallowed the fleet every ~200 seconds. Its offset is
   // untouched. Its 1100 became 2200 (the user: "the event horizon could be more
   // exaggerated") - the drawn shadow and the lensing radius both scale with it,
   // so the lens warp stays registered with the disc. The capture factor moved
   // with it, .60 -> .30, which leaves the capture distance at exactly 660.""",
"""   // A horizon sits well off to the side: scenery with gravity, not a roadblock.
   // On the course it swallowed the fleet every ~200 seconds. Its offset is
   // untouched. Its radius went to 2200 last round and that was a mistake: the
   // free-flight camera distance comes from the lens table and is NOT a multiple
   // of m.r, so doubling the radius doubled the hole's apparent size straight
   // through and the encounter became a sliver of photon ring. It is back at
   // 1100, the value the capture multiples below were written against. The
   // drawn shadow, the lensing radius and the flash bloom all read m.r*q[3], so
   // they stay registered with each other; the capture factor goes .30 -> .60
   // with it, which leaves the capture distance at exactly 660.""")

rep(":kind===8?200+r()*280:2200;", ":kind===8?200+r()*280:1100;")

rep("   if(dist<m.r*.30){", "   if(dist<m.r*.60){")

# ---- 2. captureCam pulls back far enough to hold the whole well ----
# The disc reaches 3.45 shadow radii, so the old 2.45 r GRIP (rad = focal/2.45)
# put the shadow alone at a full frame height. Every distance is roughly doubled
# and the pull-back is driven by its own fast ramp (e), so the reveal is done in
# the first few seconds of the grip rather than over all thirteen.
rep(
""" if(capturePhase===1){
  // Lean in until the well spills past every edge. You never see it whole.
  const g=smoother(clamp(captureGrip,0,1));
  return {blend:g*.95,tx:m.x,ty:m.y,tz:m.z,distance:mix(3.60,2.45,g)*r,pitch:mix(.34,.16,g),roll:.02*g,focal:mix(1.12,1.30,g)};
 }
 if(capturePhase===2){
  const g=clamp(captureT/6.5,0,1);
  return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:mix(2.45,2.30,g)*r,pitch:mix(.16,.34,g),roll:mix(.02,.06,g),focal:mix(1.30,1.20,g)};
 }
 if(capturePhase===3)return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:2.24*r,pitch:.34,roll:.06,focal:1.20};""",
""" if(capturePhase===1){
  // GRIP holds the whole well in shot: the camera pulls back off the fleet and
  // the horizon is small and complete instead of spilling past every edge. e is
  // the pull-back, fast; g is the slow lean that turns the view over onto the
  // disc as the ring closes.
  const g=smoother(clamp(captureGrip,0,1)),e=smoother(clamp(captureGrip*2.6,0,1));
  return {blend:e*.95,tx:m.x,ty:m.y,tz:m.z,distance:mix(6.00,5.20,e)*r,pitch:mix(.34,.16,g),roll:.02*g,focal:mix(1.12,1.30,g)};
 }
 if(capturePhase===2){
  // The last orbit, still whole: the ring closes, the frame does not.
  const g=clamp(captureT/6.5,0,1);
  return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:mix(5.20,4.90,g)*r,pitch:mix(.16,.34,g),roll:mix(.02,.06,g),focal:mix(1.30,1.20,g)};
 }
 if(capturePhase===3)return {blend:1,tx:m.x,ty:m.y,tz:m.z,distance:4.70*r,pitch:.34,roll:.06,focal:1.20};""")

rep(
"   distance:mix(2.24*r,mix(2200,4300,g),out),pitch:mix(.34,mix(.10,-.22,g),out),",
"   distance:mix(4.70*r,mix(2200,4300,g),out),pitch:mix(.34,mix(.10,-.22,g),out),")

# ---- 3. the encounter shot: slide the camera off the fleet when a well is near ----
# NOTE the anchor is the lookTarget assignment, NOT the captureCamPose line above
# it: the truck rewrites lookTarget, and that assignment would wipe it out if the
# block sat before it (which is exactly how the first attempt of this patch
# failed - the eye came out bit-identical to the unpatched build).
rep(
""" lookTarget=[routeX(travel),courseY(travel)+camera.aimY,travel];
 if(captureCamPose){const c=captureCamPose;lookTarget=[mix(lookTarget[0],c.tx,c.blend),mix(lookTarget[1],c.ty,c.blend),mix(lookTarget[2],c.tz,c.blend)];}""",
""" lookTarget=[routeX(travel),courseY(travel)+camera.aimY,travel];
 if(captureCamPose){const c=captureCamPose;lookTarget=[mix(lookTarget[0],c.tx,c.blend),mix(lookTarget[1],c.ty,c.blend),mix(lookTarget[2],c.tz,c.blend)];}
 // The encounter shot. An ink well is scenery with gravity, not a roadblock, so
 // when one is close and ahead the camera slides sideways off the fleet: the aim
 // - and with it the eye - trucks perpendicular to the view, which moves the
 // fleet further than the well (the fleet is nearer, so its screen scale is
 // larger) and pushes it out of the middle of the frame while the well is left
 // whole and to one side. The truck is perpendicular only, so the depth to the
 // well never changes and the well's size is untouched - this can only move the
 // well across the frame, never lose it. The weight eases to zero with distance
 // and with how far the well is off the bow, so an ordinary stretch of corridor
 // is untouched, and a capture is skipped: that pose is the capture's own.
 if(started&&autoCamera&&!captureCamPose){
  const lw=craftWorld(fleet[LEAD]);
  let well=null,wd=1e9;
  for(const m of activeMasses){
   if(m.kind!==4)continue;
   const d=Math.hypot(m.x-lw[0],m.y-lw[1],m.z-lw[2]);
   if(d<wd){wd=d;well=m;}
  }
  if(well){
   const dx=well.x-lw[0],dy=well.y-lw[1],dz=well.z-lw[2];
   const fwd=dx*camera.forward[0]+dy*camera.forward[1]+dz*camera.forward[2];
   const w=smoother(clamp((2400-wd)/1400,0,1))*smoother(clamp(fwd/900,0,1));
   if(w>.002){
    const lat=dx*camera.right[0]+dz*camera.right[2];
    const hi=dx*camera.up[0]+dy*camera.up[1]+dz*camera.up[2];
    // Sized in SCREEN px, not world units: the fleet sits at the aim, so its
    // slide is truck*k and k = focal/distance - measure it and ask for the slide
    // directly, so the framing does not change with the lens distance.
    const kf=camera.focal/Math.max(1,camera.distance);
    const off=Math.sign(lat||1)*Math.min(520/kf,1800)*w;
    const offv=Math.sign(hi||1)*Math.min(210/kf,750)*w;
    lookTarget=[lookTarget[0]+camera.right[0]*off+camera.up[0]*offv,
                lookTarget[1]+camera.up[1]*offv,
                lookTarget[2]+camera.right[2]*off+camera.up[2]*offv];
   }
  }
 }""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("v27f_framing: wrote %s (%d chars)" % (out_p, len(s)))
