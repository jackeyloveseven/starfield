"""v22g_galaxy -- the printed galaxy plate: real dust, real structure, flat.

The brief: "drawGalaxy() currently draws a bloom core plus engraved spiral
strokes and a dust lane. Make it match the reference photographs - structured,
high contrast, with real dark lanes - while staying flat and graphic rather
than soft."

What was wrong, in the reference's terms (cosmicbroth flat graphic art +
the two Rosette plates):

  * The object was a glow. `glow(...,g.rad*.20,...,.62)` is a soft airbrushed
    blob two fifths of the galaxy's radius across, and it was the single
    loudest thing on the plate. Flat graphic art has hard boundaries and few
    tones; it has no airbrush at all.
  * The arms were hairlines. Three strands at lineWidth 1.0/0.5 and alpha
    .46/.19 on a plate hundreds of pixels wide read as faint scratches, not
    as arms. Nothing had a shape.
  * The dust lane could not occlude anything. One `line()` at alpha .40 over
    spiral strokes that run .19-.46: the lane sat in exactly the same alpha
    band as the thing it was supposed to hide, so it never won. The file
    already knew the right recipe - nebulaTex()'s `lane()`, "hard edge, soft
    shoulder - one wide faint stroke under one narrow opaque stroke" - and
    simply never used it on a galaxy.

Five changes, all inside drawGalaxy() plus the galaxy records it reads:

1. FLAT TONED DISC with a crisp edge, in the region's own palette. It hides
   the background stars, which is what makes the plate read as an object.

2. ARMS AS RIBBONS. Each arm is a tapered polygon, filled flat, not a wire:
   a wide band in the region's warm rim tone, a narrow band in its cool core
   tone, and one crisp centre line. Three tones and hard edges - the colour
   scale the Rosette plates have and the single-ink plate never did.

3. A FLAT CORE PLATE under one small tight bloom, instead of the old rad*.20
   wash. The core is the only place on the object allowed to be soft.

4. DUST LANES THAT OCCLUDE. Three lanes, each a wide faint shoulder under a
   narrow near-opaque stroke in paper colour, plus two branch stubs. They are
   built on the camera-ward half of the disc, so the depth sort really puts
   them in front of the arms - the same reason a dust lane hides stars in a
   photograph.

5. LOBES, NOT A CIRCLE. The disc radius and the arm radius carry a
   low-frequency wobble seeded per galaxy, so the boundary is torn rather
   than a mathematically perfect ellipse.

The galaxies array in chunk() is not touched: the new look needs nothing the
record does not already carry (g.tone seeds the lobes, g.arms/g.tilt/g.ang
already vary). The masses table, the horizon schedule, GLSL_HOLE and the
drawHole uniforms are all left exactly as they were.

Run:  python -I v22g_galaxy.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v22g_galaxy.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


OLD = """/* A spiral galaxy as a printed plate: a bloom for the core, engraved strokes
 * for the arms, and a dust lane laid across the disc. */
function drawGalaxy(g,p,t){
 const q=project([g.x,g.y,g.z]);if(!q)return;
 if(g.rad*q[3]<10)return;
 glow([g.x,g.y,g.z],g.rad*.20,blend(p.sun,[255,255,255],.42),.62,2.2);
 glow([g.x,g.y,g.z],g.rad*.055,blend(p.sun,[255,255,255],.85),.85,1.6);
 const u=[Math.cos(g.ang),0,Math.sin(g.ang)],ct=Math.cos(g.tilt),st=Math.sin(g.tilt);
 const v=[-Math.sin(g.ang)*ct,st,Math.cos(g.ang)*ct];
 const at=(a,b)=>[g.x+u[0]*a+v[0]*b,g.y+u[1]*a+v[1]*b,g.z+u[2]*a+v[2]*b];
 const ink=blend(p.craft,p.tree,.42),dim=blend(p.tree,p.paper,.35);
 // Three parallel strands per arm, offset across the arm: an engraver's band
 // of hatchings rather than a single wire.
 for(let k=0;k<g.arms;k++){
  const off0=k/g.arms*TAU+g.tone*2;
  for(let pass=0;pass<3;pass++){
   const w=(pass-1)*.038*g.rad,al=pass===1?.46:.19,lw=pass===1?1.0:.5,pts=[];
   for(let i=0;i<=18;i++){
    const f=i/18,th=off0+f*2.9,r=g.rad*(.10+.90*f);
    pts.push(at(Math.cos(th)*r-w*Math.sin(th),Math.sin(th)*r+w*Math.cos(th)));
   }
   line(pts,ink,al,lw);
  }
 }
 // the dust lane, laid across the near side of the disc
 const dust=[];
 for(let i=0;i<=12;i++){const a=(i/12-.5)*2.2,r=g.rad*.86;dust.push(at(Math.cos(a)*r,Math.sin(a)*r*.30));}
 line(dust,shade(p.treeDark,.82),.40,2.6);
 // a few cross strokes, the way an engraver would close the hatchings
 for(let i=0;i<7;i++){
  const a=(i/7-.5)*2.4,r=g.rad*(.30+.55*((i*37)%7)/7);
  line([at(Math.cos(a)*r*.82,Math.sin(a)*r*.82),at(Math.cos(a)*r*1.12,Math.sin(a)*r*1.12)],dim,.13,.5);
 }
}
"""

NEW = """/* A spiral galaxy as a printed plate: a flat toned disc with a crisp edge,
 * arms built as tapered ribbons rather than wires, and dust lanes that actually
 * occlude - a narrow near-opaque band over a wide faint shoulder, the recipe the
 * nebulae already use. Flat tones and hard edges; the only soft thing on the
 * object is the core bloom. */
function drawGalaxy(g,p,t){
 const q=project([g.x,g.y,g.z]);if(!q)return;
 const R=g.rad*q[3];if(R<10)return;
 const u=[Math.cos(g.ang),0,Math.sin(g.ang)],ct=Math.cos(g.tilt),st=Math.sin(g.tilt);
 const v=[-Math.sin(g.ang)*ct,st,Math.cos(g.ang)*ct];
 const at=(a,b)=>[g.x+u[0]*a+v[0]*b,g.y+u[1]*a+v[1]*b,g.z+u[2]*a+v[2]*b];
 // Where the camera lies, in the disc's own coordinates. The dust lanes have to
 // be built on the near half of the plate, or the depth sort can put them behind
 // the arms they are meant to hide.
 const dx=camera.eye[0]-g.x,dy=camera.eye[1]-g.y,dz=camera.eye[2]-g.z;
 const ca=dx*u[0]+dy*u[1]+dz*u[2],cb=dx*v[0]+dy*v[1]+dz*v[2];
 const cl=Math.hypot(ca,cb)||1,near=Math.atan2(cb/cl,ca/cl);
 // The region's nebula pair tints the plate - a warm rim outside a cool core,
 // the way the reference photographs run - but mixed most of the way back to
 // the region's own ink, because this universe is still printed on navy paper.
 const pal=NEB_PAL[p.index]||NEB_PAL[0];
 const rim=blend(p.ink,pal[0],.30),inner=blend(p.ink,pal[1],.42);
 const plate=blend(p.tree,p.paper,.34),dust=blend(p.paper,p.treeDark,.28);
 const white=blend(p.craft,[255,255,255],.30);
 // The plate is not a circle. A wobble, seeded per galaxy, tears the boundary
 // into lobes instead of closing it into a perfect ellipse; the arms get a much
 // gentler one, or the wobble reads as a kink in the ribbon.
 const lobeD=a=>1+.11*Math.sin(a*4.3+g.tone*TAU*3)+.05*Math.sin(a*7.1+g.tone*TAU*5);
 const lobeA=(a,k)=>1+.045*Math.sin(a*3.1+k*1.7+g.tone*TAU*2);
 // A path in disc coordinates, drawn as a flat ribbon with the width tapering to
 // a point at each end - the difference between an arm and a wire. `off` slides
 // the ribbon sideways, so a bright band can sit on the arm's inner edge instead
 // of down its middle, which is what stops the arm reading as a tube.
 const ribbon=(mid,w0,alpha,c,off=0)=>{
  const N=mid.length-1,A=[],B=[];
  for(let i=0;i<=N;i++){
   const j=Math.min(N,i+1),h=Math.max(0,i-1);
   let tx=mid[j][0]-mid[h][0],ty=mid[j][1]-mid[h][1];const L=Math.hypot(tx,ty)||1;tx/=L;ty/=L;
   const f=i/N,w=w0*Math.pow(Math.sin(Math.PI*Math.min(1,f*.94+.03)),.62);
   A.push(at(mid[i][0]-ty*(off-w),mid[i][1]+tx*(off-w)));
   B.push(at(mid[i][0]-ty*(off+w),mid[i][1]+tx*(off+w)));
  }
  poly(A.concat(B.reverse()),c,{alpha});
 };
 // The disc the arms are printed on: one flat tone and a hard edge, closed by a
 // crisp rim line. It hides the stars behind it, which is what makes the plate
 // read as an object rather than as a glow.
 const disc=[];
 for(let i=0;i<=72;i++){const a=i/72*TAU,r=g.rad*.94*lobeD(a);disc.push(at(Math.cos(a)*r,Math.sin(a)*r*.985));}
 poly(disc,plate,{alpha:.52});
 line(disc,blend(plate,p.ink,.34),.24,.6);
 // Arms as ribbons: a wide band in the warm tone, a narrow band in the cool one,
 // then a crisp centre line. Three tones, hard edges, and a band that tapers to
 // a point at the tip the way an arm does. Each arm gets its own span, start
 // radius and width, or four identical arms read as a pinwheel logo.
 for(let k=0;k<g.arms;k++){
  const off0=k/g.arms*TAU+g.tone*2,N=34,mid=[];
  const span=2.75+.45*Math.sin(k*2.3+g.tone*TAU*2),r0=.10+.05*Math.abs(Math.sin(k*1.7+g.tone*TAU));
  const wv=.82+.36*Math.abs(Math.sin(k*1.1+g.tone*TAU*3));
  for(let i=0;i<=N;i++){
   const f=i/N,th=off0+f*span,rr=g.rad*(r0+(.90-r0)*f)*lobeA(th,k);
   mid.push([Math.cos(th)*rr,Math.sin(th)*rr]);
  }
  ribbon(mid,g.rad*.062*wv,.28,rim);
  ribbon(mid,g.rad*.022*wv,.42,inner,-g.rad*.030);
  line(mid.map(m=>at(m[0],m[1])),white,.54,.9);
 }
 // The core: a flat bright plate with a hard edge under one small tight bloom.
 const cr=g.rad*.070,core=[];
 for(let i=0;i<=28;i++){const a=i/28*TAU;core.push(at(Math.cos(a)*cr*1.5,Math.sin(a)*cr*.9));}
 poly(core,blend(inner,[255,255,255],.45),{alpha:.78});
 glow([g.x,g.y,g.z],g.rad*.075,blend(inner,[255,255,255],.5),.55,1.9);
 // Dust lanes. Two tapered ribbons on the NEAR half, running along the inside of
 // an arm the way a real lane does, over a wider faint shoulder. The lane is
 // paper colour at .80 and the arms run .24-.34: that gap is the whole point - a
 // lane that cannot out-dark the thing it covers is not a lane. Built on the
 // near half so the depth sort really puts it in front.
 for(let i=0;i<2;i++){
  const off0=near+(i?1.75:-1.75)+g.tone*.9,N=16,mid=[];
  for(let j=0;j<=N;j++){
   const f=j/N,th=off0+f*1.65,rr=g.rad*(.36+.48*f)*lobeA(th,i+1);
   mid.push([Math.cos(th)*rr,Math.sin(th)*rr]);
  }
  ribbon(mid,g.rad*.072,.22,dust);
  ribbon(mid,g.rad*.030,.82,dust);
 }
 // One branch stub, a short tongue hanging off a lane.
 const bs=near+1.9+g.tone*1.3,bsm=[];
 for(let j=0;j<=8;j++){const f=j/8,th=bs+f*.42,rr=g.rad*(.42+.46*f);bsm.push([Math.cos(th)*rr,Math.sin(th)*rr]);}
 ribbon(bsm,g.rad*.020,.62,dust);
}
"""

rep(OLD, NEW)
open(out_p, "w", encoding="utf-8", newline="").write(s)
print("v22g applied:", len(s), "chars ->", out_p)
