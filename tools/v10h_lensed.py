"""V10h: the lensed far-side arc was drawn as ten stroked ellipse arcs, and where
the ellipse runs nearly vertical consecutive radii sit closer together than the
stroke is wide, so they overlap into a comb - a zipper, not a lensed arc.

A radial gradient across the same annulus paints the identical brightness profile
with no discrete edges at all, and it is a circle rather than a flattened ellipse,
which matches the shadow (also drawn as a circle).
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = s.index("  const lensed=(alpha,below)=>{")
b = s.index("  lensed(1.0,false);")
old = s[a:b]

new = """  const lensed=(alpha,below)=>{
   const g=ctx.createRadialGradient(0,0,rad*1.00,0,0,rad*1.95);
   for(let k=0;k<=7;k++){
    const f=k/7,[col,al]=tone(RIN+(ROUT-RIN)*f*.62,alpha);
    g.addColorStop(f,css(col,al));
   }
   g.addColorStop(1,css(blackbody(TEMP*.8),0));
   ctx.beginPath();
   ctx.arc(0,0,rad*1.95,below?0:Math.PI,below?Math.PI:TAU,false);
   ctx.arc(0,0,rad*1.00,below?Math.PI:TAU,below?0:Math.PI,true);
   ctx.closePath();ctx.fillStyle=g;ctx.fill();
  };
"""

s = s[:a] + new + s[b:]

GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10h applied:", len(s), "bytes")
