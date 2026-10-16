"""v22t_trails -- star trails at speed.

The piece already has a warp state (it replaced a 2600-unit one-frame teleport
that made the scene feel jumpy: see warp / updateCapture). This makes the sky
answer it. While the fleet is warping - and, more lightly, during a slingshot -
each star is dragged into a short streak along the direction of travel instead
of sitting as a point.

Three properties the study pinned down, all honoured here:

1. THE STREAK IS DRAWN IN DIRECTION SPACE, not screen space. A star is a unit
   direction at infinity; its trail is that direction pushed a little further
   from the pole the fleet is flying toward: d' = normalize(d + eps*(d - (d.u)u)),
   with u the travel direction. Both ends then pass through skyPoint() and
   lensWarp(), so a trail near the ink well bends with the lens instead of
   sliding under it, and a trail is a big arc of the sphere rather than a 2D
   smudge.

2. THE TRAIL IS INK, NOT GLOW. Same colour the star is
   (blend(p.craft,[255,255,255],.32)), a thin butt-capped line, no gradient, no
   blur, no queue/glow (which would drag it into the depth sort). Two passes per
   magnitude tier - a long faint tail at full drag, then a short solid head - so
   it reads as a pen pulled across the paper. Twinkle is dropped while trailing:
   a streak does not flicker.

3. IT STAYS BATCHED. Today the 16000-star field is <=8 fills; the trail version
   is <=8 strokes (4 tiers x 2 passes) plus <=2 for the band. The only new cost
   is one extra normalize + skyPoint + lensWarp per star, and lensWarp returns
   immediately when there is no horizon on screen.

DETERMINISM. burst is a pure function of warp and sling, both of which seek()
already steps, so a screenshot and a live flight of the same length agree. No
new cross-frame state is introduced. When burst is 0 the field is drawn exactly
as before, byte for byte.

Reads the artwork, asserts each replaced string occurs exactly once, writes a
working copy. Two explicit paths are required: a bare run must not be able to
touch the shared original.

Run:  python -I v22t_trails.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v22t_trails.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. compute the burst once, before the bright-star loop, so both the
# bright crosses and the two batched star loops can read it. warp peaks at 28
# on a capture jump (updateCapture), sling is the decaying slingshot push.
rep(""" // Bright stars: a bloom and a cross each, so the eye has somewhere to land.
 for(const st of brightStars){""",
""" // ---- star trails ----
 // How hard the sky is being dragged. warp is the capture jump (28 at its
 // peak, decaying with a ~0.6 s half-life), sling the close-pass push; both are
 // stepped by seek(), so this is deterministic and needs no new state.
 const burst=clamp(warp/28+sling*.42,0,1);
 // eps is the drag in direction space. Low quality gets a shorter trail rather
 // than a dropped one, so the effect survives on a phone.
 const eps=burst*(lowQuality?.034:.075);
 // u is the direction the fleet is travelling: the lane tangent, flat in y.
 // Every streak fans out from the point this direction projects to.
 const hd=laneD(travel)*.68,hl=Math.hypot(hd,1),ux=hd/hl,uz=1/hl;
 // Bright stars: a bloom and a cross each, so the eye has somewhere to land.
 for(const st of brightStars){""")

# ---- 2. a bright star's cross becomes a single stroke along its own trail:
# the head of the longest few streaks. Falls back to the symmetric cross when
# there is no drag or the stretched end is off the sphere.
rep("""  ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);ctx.stroke();""",
"""  if(eps>0){
   const du=st.x*ux+st.z*uz,be=eps*5;
   const ex=st.x+be*(st.x-du*ux),ey=st.y+be*st.y,ez=st.z+be*(st.z-du*uz);
   const el=Math.hypot(ex,ey,ez)||1,q2=skyPoint([ex/el,ey/el,ez/el]);
   if(q2){const w2=lensWarp(q2[0],q2[1]);ctx.moveTo(x,y);ctx.lineTo(w2[0],w2[1]);}
   else{ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);}
  }else{ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);}
  ctx.stroke();""")

# ---- 3. the faint field: same four buckets, but each star's slot is now
# (x,y,tipX,tipY,size) and the bucket is stroked instead of filled. Twinkle is
# dropped while trailing.
rep(""" // The faint field, batched: eight fills instead of four hundred.
 const buckets=[[],[],[],[]];
 const limit=lowQuality?Math.floor(stars.length*.26):stars.length;
 for(let i=0;i<limit;i++){
  const st=stars[i],q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
  const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
  if(x<-6||x>W+6||y<-6||y>H+6)continue;
  const tier=st.mag>.70?3:st.mag>.40?2:st.mag>.16?1:0;
  buckets[tier].push(x,y,st.size,Math.sin(time*.35+st.phase)>0?1:0);
 }
 for(let t=0;t<4;t++){
  const b=buckets[t];if(!b.length)continue;
  ctx.fillStyle=css(blend(p.craft,[255,255,255],.32));
  for(let phase=0;phase<2;phase++){
   ctx.globalAlpha=clamp((.40+t*.24)*dense,0,.95)*(phase?.72:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b.length;j+=4){if(b[j+3]!==phase)continue;ctx.moveTo(b[j]+b[j+2],b[j+1]);ctx.arc(b[j],b[j+1],b[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
 }
 ctx.globalAlpha=1;""",
""" // The faint field, batched: a handful of fills (or strokes) instead of
 // thousands of individual draws. A star's slot is (x,y,size,twinkle) when the
 // sky is still, and (x,y,tipX,tipY,size) while it is being dragged - the tip
 // is the star's own direction pushed away from the travel pole and projected,
 // so it is a real arc of the sphere, not a 2D offset.
 const buckets=[[],[],[],[]];
 const limit=lowQuality?Math.floor(stars.length*.26):stars.length;
 for(let i=0;i<limit;i++){
  const st=stars[i],q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
  const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
  if(x<-6||x>W+6||y<-6||y>H+6)continue;
  const tier=st.mag>.70?3:st.mag>.40?2:st.mag>.16?1:0;
  if(eps>0){
   const du=st.x*ux+st.z*uz;
   const ex=st.x+eps*(st.x-du*ux),ey=st.y+eps*st.y,ez=st.z+eps*(st.z-du*uz);
   const el=Math.hypot(ex,ey,ez)||1,q2=skyPoint([ex/el,ey/el,ez/el]);
   if(q2){const w2=lensWarp(q2[0],q2[1]);buckets[tier].push(x,y,w2[0],w2[1],st.size);}
   else buckets[tier].push(x,y,x,y,st.size);
  }else buckets[tier].push(x,y,st.size,Math.sin(time*.35+st.phase)>0?1:0);
 }
 const ink=css(blend(p.craft,[255,255,255],.32));
 if(eps>0){
  for(let t=0;t<4;t++){
   const b=buckets[t];if(!b.length)continue;
   const a0=clamp((.40+t*.24)*dense,0,.95);
   ctx.strokeStyle=ink;
   // the long, faint tail: the ink dragged to its full length
   ctx.globalAlpha=a0*.46;ctx.lineWidth=.5+t*.20;
   ctx.beginPath();
   for(let j=0;j<b.length;j+=5){ctx.moveTo(b[j],b[j+1]);ctx.lineTo(b[j+2],b[j+3]);}
   ctx.stroke();
   // the short, solid head: the star itself, pulled a third of the way
   ctx.globalAlpha=a0;ctx.lineWidth=.7+t*.22;
   ctx.beginPath();
   for(let j=0;j<b.length;j+=5){const x=b[j],y=b[j+1];ctx.moveTo(x,y);ctx.lineTo(x+(b[j+2]-x)*.34,y+(b[j+3]-y)*.34);}
   ctx.stroke();
  }
 }else{
  for(let t=0;t<4;t++){
   const b=buckets[t];if(!b.length)continue;
   ctx.fillStyle=ink;
   for(let phase=0;phase<2;phase++){
    ctx.globalAlpha=clamp((.40+t*.24)*dense,0,.95)*(phase?.72:1);
    ctx.beginPath();let any=false;
    for(let j=0;j<b.length;j+=4){if(b[j+3]!==phase)continue;ctx.moveTo(b[j]+b[j+2],b[j+1]);ctx.arc(b[j],b[j+1],b[j+2],0,TAU);any=true;}
    if(any)ctx.fill();
   }
  }
 }
 ctx.globalAlpha=1;""")

# ---- 4. the band stars ride the same drag. They are already directions
# (bdir), so the tip is the same push; the band is where the corridor's own
# stars live, and it should answer the jump first.
rep("""  const bb=[[],[]];
  for(const st of bandStars){
   const q=skyPoint(bdir(st.ca,st.sa,st.g));if(!q)continue;
   const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
   if(x<-6||x>W+6||y<-6||y>H+6)continue;
   bb[Math.sin(time*.35+st.phase)>0?1:0].push(x,y,st.size);
  }
  ctx.fillStyle=css(blend(p.craft,[255,255,255],.34));
  for(let phase=0;phase<2;phase++){
   const b2=bb[phase];if(!b2.length)continue;
   ctx.globalAlpha=clamp(.62*bw,0,.80)*(phase?.74:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b2.length;j+=3){ctx.moveTo(b2[j]+b2[j+2],b2[j+1]);ctx.arc(b2[j],b2[j+1],b2[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
  ctx.globalAlpha=1;""",
"""  const bink=css(blend(p.craft,[255,255,255],.34));
  if(eps>0){
   const bb=[];
   for(const st of bandStars){
    const d=bdir(st.ca,st.sa,st.g),q=skyPoint(d);if(!q)continue;
    const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
    if(x<-6||x>W+6||y<-6||y>H+6)continue;
    const du=d[0]*ux+d[2]*uz;
    const ex=d[0]+eps*(d[0]-du*ux),ey=d[1]+eps*d[1],ez=d[2]+eps*(d[2]-du*uz);
    const el=Math.hypot(ex,ey,ez)||1,q2=skyPoint([ex/el,ey/el,ez/el]);
    if(!q2)continue;
    const w2=lensWarp(q2[0],q2[1]);bb.push(x,y,w2[0],w2[1]);
   }
   if(bb.length){
    const a0=clamp(.62*bw,0,.80);
    ctx.strokeStyle=bink;
    ctx.globalAlpha=a0*.48;ctx.lineWidth=.5;
    ctx.beginPath();for(let j=0;j<bb.length;j+=4){ctx.moveTo(bb[j],bb[j+1]);ctx.lineTo(bb[j+2],bb[j+3]);}ctx.stroke();
    ctx.globalAlpha=a0;ctx.lineWidth=.85;
    ctx.beginPath();for(let j=0;j<bb.length;j+=4){const x=bb[j],y=bb[j+1];ctx.moveTo(x,y);ctx.lineTo(x+(bb[j+2]-x)*.34,y+(bb[j+3]-y)*.34);}ctx.stroke();
   }
  }else{
   const bb=[[],[]];
   for(const st of bandStars){
    const q=skyPoint(bdir(st.ca,st.sa,st.g));if(!q)continue;
    const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
    if(x<-6||x>W+6||y<-6||y>H+6)continue;
    bb[Math.sin(time*.35+st.phase)>0?1:0].push(x,y,st.size);
   }
   ctx.fillStyle=bink;
   for(let phase=0;phase<2;phase++){
    const b2=bb[phase];if(!b2.length)continue;
    ctx.globalAlpha=clamp(.62*bw,0,.80)*(phase?.74:1);
    ctx.beginPath();let any=false;
    for(let j=0;j<b2.length;j+=3){ctx.moveTo(b2[j]+b2[j+2],b2[j+1]);ctx.arc(b2[j],b2[j+1],b2[j+2],0,TAU);any=true;}
    if(any)ctx.fill();
   }
  }
  ctx.globalAlpha=1;""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V22t applied:", len(s), "chars ->", out_p)
