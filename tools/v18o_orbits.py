"""v18o_orbits -- what bodies EXIST, where, how big, and whether they MOVE.

Answers two complaints, verbatim:

  "星球有恒星，中子星红矮星等等，你这所有星球样貌差不多，位置差不多大小差不多，
   还不公转是不是太奇怪"
  (planets should include stars, neutron stars, red dwarfs etc; right now every
   planet looks the same, is about the same size, sits about the same way, and
   none of them orbit)

Four changes:

1. STAR SYSTEMS. One chunk in three (and never a horizon chunk, so the ink well
   keeps its every-seventh rhythm) now holds a primary - a sun (kind 5), a red
   dwarf (kind 6) or a neutron star (kind 7) - with two to five worlds orbiting
   it at different radii, plane tilts and angular speeds. The other chunks keep
   the v12 lattice, so the sky is not all systems.

2. ORBITS ARE A PURE FUNCTION of the body's own phase and the world clock
   (stepOrbits, called at the head of updateGravity). Nothing integrates, so a
   seek lands on the same sky a flight of the same length would have made, and a
   chunk that scrolls out and is rebuilt puts its family back where it belongs.
   The system is placed as far off the lane as its widest orbit needs, so no
   world ever swings across the corridor.

3. SIZES VARY HARD. The old r was one number per kind out of a five-entry table:
   [110,150,200,260,1100]. Now a rock is 55..270, a gas giant 380..1000, a
   neutron star 14..24 - so a 14-unit neutron star next to a 900-unit gas giant
   is an ordinary sight. The black hole keeps its tuned 1100 and its offset.

4. GRAVITY. MASS_KIND was five entries long, so the new kinds read undefined and
   would have made the fleet's force NaN the moment a star was allowed to pull.
   Extended with large factors for the primaries, and the ship-gravity filter in
   updateBirds now lets the stars bend the flock, not just the ink well.

Reads the artwork, asserts each replaced string occurs exactly once, writes a
working copy. Two explicit paths are required: a bare run must not be able to
touch the shared original.

Run:  python -I v18o_orbits.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v18o_orbits.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. MASS_KIND grows four entries: sun, red dwarf, neutron star, ringed giant
# Indices 0-4 are untouched. 5..8 were undefined; gravity reads MASS_KIND[kind],
# so a star that pulled on the fleet would have produced NaN.
rep("const GRAV=1.6e7,MASS_KIND=[.35,.7,1,1.6,2.4],LEAD=2;",
    "const GRAV=1.6e7,MASS_KIND=[.35,.7,1,1.6,2.4,12,5,22,1.2],LEAD=2;")

# ---- 2. the sky: systems, and sizes that are actually far apart
rep(""" const horizon=(k%7===0);
 // Bodies sit on a regular lattice with a small jitter rather than anywhere in
 // the chunk: three distance bands and three height bands, walked in step with
 // the index, so consecutive bodies never pile up or all vanish off the same way.
 const n=2+(k&1);
 for(let i=0;i<n;i++){
  const z=z0+CHUNK*((i+.5)/n)+(r()-.5)*CHUNK*.20;
  const side=((k+i)&1)?1:-1;
  const roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;
  // A horizon sits well off to the side: scenery with gravity, not a roadblock.
  // On the course it swallowed the fleet every ~200 seconds.
  const band=(i+(k%3))%3;
  const off=kind===4?760+band*150+r()*90:620+band*430+r()*150;
  const y=150+((i+(k%2))%3)*180+r()*80;
  masses.push({x:laneX(z)+side*off,y,z,kind,r:[110,150,200,260,1100][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }""",
""" const horizon=(k%7===0);
 // One chunk in three carries a system: a primary with a family on real orbits.
 // That is the whole complaint answered at once - a hierarchy of sizes, bodies
 // that do not all sit the same distance off the lane, and motion you can watch.
 // A horizon chunk is never a system, so the ink well keeps its every-seventh
 // rhythm and its offset.
 const system=!horizon&&(k%3===1);
 if(system){
  const sr=r();
  const skind=sr<.62?5:sr<.88?6:7;              // sun / red dwarf / neutron star
  const srad=skind===5?320+r()*380:skind===6?110+r()*130:14+r()*10;
  const dwarf=skind>=6;                         // a small star can hold a giant
  const spin=r()>.5?1:-1;                       // the family's common direction
  const fam=[];let a=srad+240;
  for(let i=0,n=2+Math.floor(r()*4);i<n;i++){   // two to five worlds
   const kid=r();
   const kind=kid<.20?0:kid<.38?1:kid<.60?2:kid<.74?3:kid<.86?8:kid<.96?1:0;
   const rad=kind===2?(dwarf?380+r()*520:150+r()*190)
            :kind===8?(dwarf?420+r()*480:200+r()*220)
            :kind===1?95+r()*r()*265
            :kind===0?55+r()*r()*215
            :48+r()*r()*185;
   a+=rad*.8+110+r()*160;                       // each orbit clears the last
   fam.push({kind,rad,a,b:a*(.76+.24*r()),inc:(r()-.5)*.7,nod:r()*TAU,ph:r()*TAU,
             spd:spin*(.05+.22*Math.pow(700/a,.9))});
  }
  // The system is set as far off the lane as its widest orbit needs, so no world
  // ever swings across the corridor and pops when the camera enters its sphere.
  // The bound is the orbit's own x-extent: |x| <= hypot(a, b*sin inc), since
  // x = a cosT cosN + b sinT sin(inc) sinN. Using a+b here (the first cut) set
  // every system twice as far off the lane as it needed to be, and a sun that
  // never comes closer than 8000 units is a speck.
  const aMax=fam.reduce((m,f)=>Math.max(m,Math.hypot(f.a,f.b*Math.sin(f.inc))),0);
  const radMax=fam.reduce((m,f)=>Math.max(m,f.rad),0);
  const z=z0+CHUNK*.5+(r()-.5)*CHUNK*.25;
  const off=aMax+radMax+520+Math.floor(r()*3)*380+r()*160;
  const y=150+Math.floor(r()*3)*180+r()*80;
  const side=(k&1)?1:-1,sx=laneX(z)+side*off;
  masses.push({x:sx,y,z,kind:skind,r:srad,axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
  for(const f of fam)masses.push({x:sx+f.a,y,z,kind:f.kind,r:f.rad,
   axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU,
   orb:{cx:sx,cy:y,cz:z,a:f.a,b:f.b,inc:f.inc,nod:f.nod,spd:f.spd,ph:f.ph}});
 }else{
  // Bodies sit on a regular lattice with a small jitter rather than anywhere in
  // the chunk: three distance bands and three height bands, walked in step with
  // the index, so consecutive bodies never pile up or all vanish off the same way.
  const n=2+(k&1);
  for(let i=0;i<n;i++){
   const z=z0+CHUNK*((i+.5)/n)+(r()-.5)*CHUNK*.20;
   const side=((k+i)&1)?1:-1;
   const roll=r();
   let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
   if(horizon&&i===0)kind=4;
   // One radius per kind out of a five-entry table was the "all the same size"
   // complaint: a rock and a gas giant differed by a factor of two. They differ
   // by a factor of twenty now, and a small world can be a speck.
   const rad=kind===0?55+r()*r()*215:kind===1?95+r()*r()*265
            :kind===2?380+r()*620:kind===3?48+r()*r()*185:1100;
   // A horizon sits well off to the side: scenery with gravity, not a roadblock.
   // On the course it swallowed the fleet every ~200 seconds. Its 1100 and its
   // offset are untouched: the capture radius was tuned against them.
   const band=(i+(k%3))%3;
   const off=kind===4?760+band*150+r()*90:Math.max(620+band*430,rad+700)+r()*150;
   const y=150+((i+(k%2))%3)*180+r()*80;
   masses.push({x:laneX(z)+side*off,y,z,kind,r:rad,axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
  }
 }""")

# ---- 3. the course bends around a star, and stops wobbling around an orbit
rep("""  if(m.kind<2)continue;
  const dz=z-m.z,rr=m.kind===4?900:700,amp=m.kind===4?90:120;""",
"""  if(m.kind<2||m.orb)continue;
  // A star bends the lane wide, the ink well bends it hard. A body on an orbit
  // is left out: it can cross the lane line, and the sign of the bend would flip
  // with it - a 240-unit lurch of the whole corridor, once per orbit.
  const dz=z-m.z,rr=m.kind===4?900:m.kind>=5?1500:700,amp=m.kind===4?90:m.kind>=5?150:120;""")

# ---- 4. the orbits themselves
rep("""function updateGravity(){
 activeMasses.length=0;""",
"""/* Orbits. A body's place is a pure function of its own orbit and the world
 * clock - never of the last frame - so a seek lands on the same sky a flight of
 * the same length would have made, and a chunk that scrolls out and is rebuilt
 * puts its family back exactly where it belongs. updateGravity() steps them
 * before anything reads m.x/m.z, so the course bend, the ship gravity, the
 * capture test and the draw all see the same positions. */
function stepOrbits(){
 const t=time;
 for(const c of chunks.values())for(const m of c.masses){
  if(!m.orb)continue;
  const o=m.orb,th=o.ph+o.spd*t,x=Math.cos(th)*o.a,y=Math.sin(th)*o.b;
  const ci=Math.cos(o.inc),si=Math.sin(o.inc),cn=Math.cos(o.nod),sn=Math.sin(o.nod);
  const y1=y*ci,z1=y*si;
  m.x=o.cx+x*cn+z1*sn;m.y=o.cy+y1;m.z=o.cz-x*sn+z1*cn;
 }
}
function updateGravity(){
 activeMasses.length=0;
 stepOrbits();""")

# ---- 5. the stars bend the fleet, not just the ink well
rep("if(m.kind!==4)continue;   // worlds are scenery; only the ink well pulls a ship",
    "if(m.kind!==4&&!(m.kind>=5&&m.kind<=7))continue;   // worlds are scenery; the ink well and the stars pull a ship")

# ---- 6. a star is the light, not a lit ball
rep(""" const tint=massTint(m,p);
 if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);""",
""" const tint=massTint(m,p);
 // A star is not a lit ball: it is the light. Colour from the blackbody ramp
 // the horizon already uses, not from the region's palette - a sun that turns
 // from gold to blue-grey when the sky changes is not a sun - and drawn here
 // rather than through drawWorld: a world's ramp is built to sit under the
 // grade as a lit body, so a sun at that brightness comes out the same grey as
 // a moon. A radial falloff is the right shape for a source (it is only wrong
 // on a planet, where concentric rings read as a specular highlight).
 if(m.kind>=5&&m.kind<=7){
  const cx=q[0],cy=q[1];
  const lit=m.kind===7?blackbody(14000):m.kind===6?blackbody(3000):blackbody(4800);
  // A neutron star is twenty units of matter carrying the light of a sun: its
  // bloom is deliberately far larger than its disc, which is the only thing that
  // makes a 3-pixel object read as a neutron star rather than as a dust speck.
  const halo=m.kind===7?11:m.kind===6?2.6:2.0;
  queue.push({type:4,d:q[2],alpha:1,fn:()=>{
   const R=Math.max(m.kind===7?2.4:1.6,rad),g=ctx.createRadialGradient(cx,cy,0,cx,cy,R*1.06);
   g.addColorStop(0,css(blend(lit,[255,255,255],.70),.98));
   g.addColorStop(.52,css(lit,.96));
   g.addColorStop(.86,css(blend(lit,[255,255,255],.16),.70));
   g.addColorStop(1,css(lit,0));
   ctx.beginPath();ctx.arc(cx,cy,R*1.06,0,TAU);ctx.fillStyle=g;ctx.fill();
  }});
  glow([m.x,m.y,m.z],m.r*halo,lit,m.kind===7?.46:.24,2.2);
  glow([m.x,m.y,m.z],m.r*halo*.36,blend(lit,[255,255,255],.55),m.kind===7?.85:.52,2.4);
  return;
 }
 if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V18o applied:", len(s), "chars ->", out_p)
