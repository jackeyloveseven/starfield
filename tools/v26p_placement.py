"""v26p_placement -- the world placement, measured and re-laid-out.

The measurement (measure.py, 3000 frames / 6000 s, seed 1a2b) says the layout is
not random, it is structured the wrong way:

  * the frame is empty at the bottom and packed at the top: 41.6% of on-screen
    bodies sit in the top 20% of the frame, 2.7% in the bottom 30%;
  * 72.1% of on-screen bodies sit in the outer 25% band of the frame and 12.3%
    are clipped by the frame edge, because the lateral offset is three FIXED
    world bands (620 / 1050 / 1480) that do not scale with the depth they are
    seen at;
  * systems are pushed two to three times further out than a lone world
    (avg |x-laneX| 3557 vs 1568) and 59.4% of their bodies render as sub-40px
    specks, so a "watchable family" is not watchable;
  * orbit members swing +/-3000 in world y (o.b ~= a and cos(inc) ~= 0.94, so
    the orbit plane is nearly VERTICAL) and spend most of the time above or
    below the frame;
  * 23.1% of adjacent bodies along z are less than 400u apart - the members of
    a system all share their system's z.

Everything fixed here lives in the masses-generation block of chunk(). Nothing
outside it is touched: drawWorld, drawMass, the per-kind drawing, GLSL_HOLE,
drawHole and postPass are all left exactly as they are, and the horizon's own
schedule (k%19), radius (1100), offset ladder (760 + band*150 + r()*90) and
height ladder (150 + ((i+(k%2))%3)*180 + r()*80) are kept byte-for-byte so the
capture tuning is untouched.

What changes, and why:

 1. HEIGHTS. courseY(z) is ~196 and the three old bands all sit at 150..590, i.e.
    on or above the corridor plane - the camera looks down the corridor at ~74
    degrees, so the bottom of the frame is the world BELOW that plane and there
    was nothing there. The bands are now centred on courseY and reach both ways.
 2. LATERAL OFFSET. One continuous, heavily right-skewed offset replaces the
    three fixed bands: most worlds sit just clear of the corridor, a few sit far
    out. The floor is still rad+520 (the fleet flies a 276-unit formation and
    must never pass through a world), but the distribution above it is no longer
    three discrete steps.
 3. SYSTEM REACH. The orbit radius used to grow without bound (a reached ~3800)
    and the system was then set off the lane by aMax+radMax+520 - hence 3557.
    a is capped, and the system offset is capped too, so a family lands at
    roughly 1.3x a lone world instead of 2-3x, at a size you can actually watch.
 4. ORBIT PLANE. inc was +/-0.35 rad, so cos(inc) ~= 0.94 and the vertical swing
    was the full semi-major axis. inc is now near +/-pi/2, i.e. the family orbits
    in a plane roughly parallel to the corridor - members stay at the family's
    height and gain real z spread for free, which is also what un-clumps z.
 5. DENSITY. Three to four worlds per open chunk instead of two to three, so a
    frame is less often empty, and the z jitter inside a chunk is tightened so
    two worlds in the same chunk can never land on top of each other.
 6. DEPTH INSIDE A SYSTEM. Each world of a family gets its own cz, so the family
    is a three-dimensional cluster rather than a row of points pinned at one
    depth; the system's own z jitter is tightened to keep the family inside its
    chunk instead of spilling into the next one's worlds.

Reads <in.html>, asserts every replaced string occurs exactly once, writes
<out.html>. Two explicit paths are required - a bare run must not touch anything.

  python -I v26p_placement.py work-placement.html work-placement-out.html
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v26p_placement.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. the family orbits a plane, not a fountain ----
# o.b was a*(.76+.24r) ~= a and inc was +-0.35 rad, so cos(inc) ~= 0.94: the
# member's y swing was essentially the full semi-major axis (measured range
# -3247..3673 against the lattice's -4..590). inc near pi/2 puts the orbit plane
# roughly parallel to the corridor: members stay at the family's height, and the
# z1 term they pick up spreads them along z instead. a is capped so a family
# cannot grow an orbit wider than the system can be placed at.
rep("""   a+=rad*.8+110+r()*160;                       // each orbit clears the last
   fam.push({kind,rad,a,b:a*(.76+.24*r()),inc:(r()-.5)*.7,nod:r()*TAU,ph:r()*TAU,""",
    """   a=Math.min(a+rad*.8+110+r()*160,950);        // each orbit clears the last, then stops
   // inc near +-pi/2: the family orbits in a plane roughly parallel to the
   // corridor, so a member stays near the family's height instead of swinging a
   // full semi-major axis above and below the frame. b still squashes the ellipse.
   fam.push({kind,rad,a,b:a*(.76+.24*r()),inc:(r()>.5?1:-1)*(Math.PI/2-(r()-.5)*.55),nod:r()*TAU,ph:r()*TAU,""")

# ---- 2. a system lands where you can watch it ----
# aMax is now ~a and radMax <= 900, so aMax+radMax+420 is the clearance the
# corridor needs; capping it at 2100 keeps the family at a readable size instead
# of a 3557-unit speck. The height band is centred on the corridor.
rep("""  const z=z0+CHUNK*.5+(r()-.5)*CHUNK*.25;
  const off=aMax+radMax+520+Math.floor(r()*3)*380+r()*160;
  const y=150+Math.floor(r()*3)*180+r()*80;""",
    """  // A family now spans about +/-1500 along z on its own (see the per-world cz
  // below), so the system itself only needs a small jitter: a wide one pushed
  // members past the chunk edge and into the next chunk's worlds, which is a
  // short z gap of exactly the kind this is meant to remove.
  const z=z0+CHUNK*.5+(r()-.5)*CHUNK*.18;
  // aMax+radMax+420 is what the widest orbit plus the biggest world needs to stay
  // clear of the corridor; the clamp keeps a family at a size you can watch.
  const off=clamp(aMax+radMax+420,900,2100)+r()*180;
  const y=courseY(z)+(Math.floor(r()*3)-1)*420+(r()-.5)*180;""")

# ---- 3. three to four worlds per open chunk, so a frame is less often empty ----
rep("""  const n=2+(k&1);
  for(let i=0;i<n;i++){
   const z=z0+CHUNK*((i+.5)/n)+(r()-.5)*CHUNK*.20;""",
    """  const n=3+(k&1);
  for(let i=0;i<n;i++){
   // The jitter stays inside half a slot, so three or four worlds in a chunk are
   // never closer along z than half their own spacing; .20 of a whole chunk could
   // put two of them on top of each other.
   const z=z0+CHUNK*((i+.5)/n)+(r()-.5)*CHUNK*.10;""")

# ---- 4. one continuous, skewed offset and a height band on both sides ----
# The three fixed bands (620/1050/1480) were the whole of the edge pile-up: the
# screen x of a world is off*focal/depth, and depth runs from 18 to 18000, so a
# fixed off cannot cover the middle of the frame. The new offset is continuous
# and right-skewed - most worlds just clear the corridor, a few are far out - so
# the frame fills from the centre outward. The floor stays rad+520: the fleet
# flies a 276-unit formation and must never pass through a world.
#
# The block's own header comment described the lattice it used to have, so it is
# brought in line with what the block now does.
rep("""  // Bodies sit on a regular lattice with a small jitter rather than anywhere in
  // the chunk: three distance bands and three height bands, walked in step with
  // the index, so consecutive bodies never pile up or all vanish off the same way.""",
    """  // Bodies sit on a regular lattice along z with a small jitter rather than
  // anywhere in the chunk, so consecutive bodies never pile up. The lateral
  // offset and the height are walked in step with the index (see below): the
  // offset is continuous and skewed, the height runs over five bands centred on
  // the corridor.""")

#
# The horizon (kind 4) keeps its own offset formula AND its own height formula
# exactly as they were - both the 760/910/1060 offset ladder and the
# 150 + ((i+(k%2))%3)*180 + r()*80 height are what the capture test was tuned
# against, so the ink well is left byte-for-byte. i is always 0 for a horizon
# (it is only ever assigned at i===0), so the height ladder reduces to the same
# 150..230 / 330..410 alternation it always had.
rep("""   const band=(i+(k%3))%3;
   const off=kind===4?760+band*150+r()*90:Math.max(620+band*430,rad+700)+r()*150;
   const y=150+((i+(k%2))%3)*180+r()*80;""",
    """   const band=(i+(k%3))%3;
   const off=kind===4?760+band*150+r()*90:Math.max(rad+520,620+Math.pow(r(),1.6)*1800);
   // Five height bands centred on the corridor plane, not three bands sitting on
   // top of it: the camera looks down at the corridor, so the frame's lower half
   // is the world below courseY and there has to be something there. Biased a
   // little below the plane, because the top of the frame was the crowded half.
   // mod() and not %: k is negative for the first chunks of the run.
   const hb=mod(i*2+mod(k,5),5);
   const y=kind===4?150+((i+(k%2))%3)*180+r()*80:courseY(z)+(hb-2)*600-200+(r()-.5)*180;""")

# ---- 5. each world in a family gets its own depth ----
# The orbit plane alone spreads a family over only +/-a along z (the z semi-axis
# of the ellipse), which is narrower than the 400u "same depth" threshold for
# most families - that is the measured 23.1% of adjacent z gaps under 400u. A
# per-world cz on top of the orbit makes the family read as a three-dimensional
# cluster rather than a row of points pinned at one depth.
rep("""  for(const f of fam)masses.push({x:sx+f.a,y,z,kind:f.kind,r:f.rad,
   axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU,
   orb:{cx:sx,cy:y,cz:z,a:f.a,b:f.b,inc:f.inc,nod:f.nod,spd:f.spd,ph:f.ph}});""",
    """  for(const f of fam){const mz=z+(r()-.5)*1400;masses.push({x:sx+f.a,y,z:mz,kind:f.kind,r:f.rad,
   axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU,
   orb:{cx:sx,cy:y,cz:mz,a:f.a,b:f.b,inc:f.inc,nod:f.nod,spd:f.spd,ph:f.ph}});}""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V26p placement applied:", len(s), "chars ->", out_p)
