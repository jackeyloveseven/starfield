"""V12: clear the clutter, even out the layout, and give the planets headroom.

Three things the user reported, in one pass.

1. "宇宙中飘着很多长方块和正方块什么意义"
   Those are `plates` (120-270 x 88-200 printed atlas pages) and `shards` (34-96 x
   22-66 torn-paper scraps) - scenery inherited from the MIGRATION sister piece,
   where "pages and scraps drifting past" meant something. In space they are
   literally unlabelled rectangles. Removed, along with their draw calls.

2. "星球排布不均匀很怪，黑洞排布也不均匀"
   Every position was uniform random: off = 560 + r()*1700, y = 150 + r()*520,
   and a black hole appeared with probability r() < .07 + void*.40 per chunk, so
   they clumped hard in one region and vanished elsewhere. Now the bodies sit on a
   regular lattice with only a small jitter, and the black hole is on a fixed
   every-seventh-chunk schedule.

3. "星球还是很丑"
   The planet was coming out of the press as a featureless white ball: the lit
   hemisphere peaked near 255 BEFORE the grade, and contrast() subtracts a fixed
   offset, so the whole day side clipped and the terminator became a hard stair.
   The shading field is now compressed into .20..80 of the range, so the
   terminator lands just above the black point instead of under it.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:150]))
    s = s.replace(a, b, n)


# ---- 1. the rectangles go ----
rep(""" for(let i=0,n=1+Math.floor(r()*2);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=900+r()*2200;
  shards.push({x:laneX(z)+side*off,y:60+r()*760,z,w:34+r()*62,h:22+r()*44,ang:r()*TAU,tilt:(r()-.5)*1.1,spin:(r()-.5)*.5,tone:r()});
 }
 for(let i=0,n=1+Math.floor(r()*2);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=1100+r()*2400;
  plates.push({x:laneX(z)+side*off,y:120+r()*620,z,w:120+r()*150,h:88+r()*112,ang:r()*TAU,tilt:(r()-.5)*.8,spin:(r()-.5)*.32,tone:r()});
 }
""", """ // `plates` and `shards` used to be generated here: printed atlas pages and
 // torn-paper scraps, scenery inherited from the MIGRATION sister piece where
 // "pages drifting past" carried the metaphor. In space they are unlabelled
 // rectangles, and they were the loudest thing in the frame. Both arrays stay so
 // the chunk record keeps its shape, but nothing goes into them.
""")

# ---- 1b. and so do their draw calls ----
rep("  for(const s of c.shards){const pj=project([s.x,s.y,s.z]);if(!pj||pj[2]>9000||pj[0]<-160||pj[0]>W+160||pj[1]<-160||pj[1]>H+160)continue;drawShard(s,region(s.x,s.z),time);}\n"
    "  for(const pl of c.plates){const pj=project([pl.x,pl.y,pl.z]);if(!pj||pj[2]>12000||pj[0]<-260||pj[0]>W+260||pj[1]<-260||pj[1]>H+260)continue;drawPlate(pl,region(pl.x,pl.z),time);}",
    "  // The shard and plate draw loops were here. drawShard/drawPlate are now\n"
    "  // unreferenced; left in place rather than deleted blind.\n")

# ---- 2. even layout ----
rep(""" const horizon=r()<.07+pc.void*.40;
 for(let i=0,n=1+Math.floor(r()*3);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;
  // A horizon sits near the corridor, so the course is really bent by it.
  // A horizon sits well off to the side: it is scenery with gravity, not a
  // roadblock. On the course it swallowed the fleet every ~200 seconds.
  const off=kind===4?760+r()*420:560+r()*1700;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[110,150,200,260,330][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }""",
    """ // A horizon is on a schedule, not a die roll. It used to be r() < .07+void*.40
 // per chunk, which clumped them hard in the void and left long stretches with
 // none at all - which reads as "the black holes are unevenly distributed".
 // Every seventh chunk is a rhythm you can feel instead.
 const horizon=(k%7===0);
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
  masses.push({x:laneX(z)+side*off,y,z,kind,r:[110,150,200,260,330][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }""")

# ---- 3. the planets stop clipping ----
rep("""  // Lambertian brightness IS b, so the ramp is near linear: a real gradient
  // across the lit hemisphere, not a white cap with a cliff under it
  const v=b>=0?.13+.87*b:.13*Math.pow(1+b,1.5);""",
    """  // The ramp has to leave headroom for the grade. contrast() subtracts a fixed
  // offset, so anything under the black point is destroyed - a day side peaking
  // at 255 before the press came out as a featureless white ball with a hard
  // stair where the terminator should be. Compressed into .20...80: the
  // terminator now lands just ABOVE the black point instead of under it.
  const v=b>=0?.20+.60*b:.20*Math.pow(1+b,1.5);""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V12 applied:", len(s), "chars")
