"""v22d_dust -- make the nebula dust lanes read as DUST, not as cracks.

The v18n rebuild gave the nebulae their saturation and their structure, and it
gave them dark lanes - but the lanes print as GEOMETRIC BRANCHES: a thin,
constant-width, smooth-edged curve, every lane the same language, crossing the
gas like a scratch in glass. The reference photographs (Rosette et al) have the
opposite: dust that is irregular in width, ragged at the edge and feathered into
the gas, so it reads as something occluding the light rather than as a line laid
over it.

The cause is the primitive, not the placement. `lane()` was two strokes of the
same quadratic path - a wide faint one under a narrow opaque one - so the width
was constant end to end, the edge was a clean two-step, and the ends were blunt
caps. The placement and the curvature were fine; the stroke was not.

The fix: stamp each lane as a CHAIN of overlapping discs along the same bowed
path. Every disc is wider or narrower than its neighbours and its centre is
nudged off the spine, so the band breathes and meanders; the discs are left to
accumulate under destination-out, and the overlap does the shading for free -
the spine of the chain is cut deepest and the fringe only feathered. Width tapers
to nothing at both ends.

Each disc is drawn as a flat-toned plate - one alpha to half its radius, then a
short ragged shoulder - rather than a long gradient. That is the answer to
"flat-toned or gradient": the lane's body is a single tone (the paper showing
through the cut) with only a brief feathered edge, so it keeps the
flat-graphic-art reading instead of turning into an airbrush, while the width is
irregular and the shoulder ragged, so it is dust and not a rule.

Only the lane primitive and the three width ranges that feed it change. The
number, placement and curvature of the lanes are untouched, and the gas - blobs,
filaments, mask, two-tone colour - is untouched, so the saturation and the
structure the v18n rebuild earned are kept.

Run:  python -I v22d_dust.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v22d_dust.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- the lane primitive: a constant-width stroke -> a ragged chain of clumps
rep(""" // Dark dust in front of the lit gas: a nebula reads as gas only when something
 // occludes it. Hard edge, soft shoulder - one wide faint stroke under one
 // narrow opaque stroke - because a soft radial hole reads as a smudge and an
 // even softness all over reads as nothing at all.
 g.globalCompositeOperation='destination-out';g.lineCap='round';
 const lane=(x0,y0,mx,my,x1,y1,w,a)=>{
  g.strokeStyle=`rgba(0,0,0,${(a*.55).toFixed(3)})`;g.lineWidth=w*3.1;
  g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
  g.strokeStyle=`rgba(0,0,0,${a.toFixed(3)})`;g.lineWidth=w;
  g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
 };""",
""" // Dark dust in front of the lit gas: a nebula reads as gas only when something
 // occludes it. It must not be a stroke, though. A constant-width curve with a
 // clean edge prints as a crack - regular, thin, the same width the whole way -
 // and that is what the reference photographs do not have. So a lane is a CHAIN
 // of overlapping discs stamped along its bowed path: each disc is wider or
 // narrower than its neighbours and its centre is nudged off the spine, so the
 // band breathes and wanders, and the discs accumulate under destination-out.
 // The overlap does the shading for free - the spine of the chain is cut
 // deepest, the fringe only feathered. Each disc is a soft halo plus a small
 // FLAT disc on top, so the lane's body is one flat tone (the paper showing
 // through the cut) with a short ragged shoulder - not a gradient all the way
 // through, which would be an airbrush, and not a clean constant stroke, which
 // is the crack being removed.
 g.globalCompositeOperation='destination-out';
 const lane=(x0,y0,mx,my,x1,y1,w,a)=>{
  const K=18;
  for(let i=0;i<=K;i++){
   const t=i/K,it=1-t;
   const bx=it*it*x0+2*it*t*mx+t*t*x1;
   const by=it*it*y0+2*it*t*my+t*t*y1;
   const dx=2*it*(mx-x0)+2*t*(x1-mx),dy=2*it*(my-y0)+2*t*(y1-my);
   const nl=Math.hypot(dx,dy)||1,ox=-dy/nl,oy=dx/nl;
   // Taper to nothing at both ends and breathe in between: a lane that keeps its
   // width end to end is a rule, not dust.
   const env=.28+.72*Math.pow(Math.sin(Math.PI*t),.50);
   const rr=w*env*(.50+r()*1.35);
   const wd=(r()-.5)*w*1.05;              // the spine wanders across the path
   const px=bx+ox*wd,py=by+oy*wd,R=rr*2.0,al=a*(.24+r()*.30);
   // Flat tone to half the radius, then a short ragged shoulder: the body of the
   // lane is one tone and only its edge is a gradient, which is what keeps this
   // flat graphic art instead of an airbrush.
   const gr=g.createRadialGradient(px,py,0,px,py,R);
   gr.addColorStop(0,`rgba(0,0,0,${al.toFixed(3)})`);
   gr.addColorStop(.50,`rgba(0,0,0,${al.toFixed(3)})`);
   gr.addColorStop(.82,`rgba(0,0,0,${(al*.30).toFixed(3)})`);
   gr.addColorStop(1,'rgba(0,0,0,0)');
   g.fillStyle=gr;
   const bx0=px-R,by0=py-R;
   g.fillRect(bx0,by0,R*2,R*2);
  }
 };""")

# ---- the arcs: a little wider than the old stroke, so the band has a body
rep("  lane(x0,y0,(x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1,N*(.008+r()*.020),.40+r()*.45);",
    "  lane(x0,y0,(x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1,N*(.008+r()*.017),.40+r()*.45);")

# ---- the fingers off the gas edge
rep("  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.09,(y0+y1)*.5+(r()-.5)*N*.09,x1,y1,N*(.010+r()*.022),.50+r()*.42);",
    "  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.09,(y0+y1)*.5+(r()-.5)*N*.09,x1,y1,N*(.010+r()*.019),.50+r()*.42);")

# ---- the two lanes that cut across the body
rep("  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.22,(y0+y1)*.5+(r()-.5)*N*.22,x1,y1,N*(.010+r()*.024),.45+r()*.40);",
    "  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.22,(y0+y1)*.5+(r()-.5)*N*.22,x1,y1,N*(.009+r()*.019),.45+r()*.40);")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("v22d_dust applied:", len(s), "chars ->", out_p)
