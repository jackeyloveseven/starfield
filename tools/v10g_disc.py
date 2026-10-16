"""V10g: two more disc artifacts, both bounded changes.

The disc is nested translucent ellipses, so their edges accumulate into visible
horizontal bands - the step between ring k and ring k+1 is a_k*(1-accumulated),
which does not shrink just because the profile is smooth. More rings pushes the
accumulation to saturation sooner, so the bands move out to the faint rim where
they cannot be seen.

The lensed far-side arcs are stroked at ten radii with lineWidth rad*.10; where
the ellipse runs nearly vertical, consecutive radii are closer together than the
stroke is wide, so they overlap into a comb. Fewer and wider merges them.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("  const disc=(alpha,ryOff)=>{\n   const N=26;", "  const disc=(alpha,ryOff)=>{\n   const N=44;")
rep("  const lensed=(alpha,below)=>{\n   const N=10;", "  const lensed=(alpha,below)=>{\n   const N=7;")
rep("    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(1.2,rad*.10);ctx.stroke();",
    "    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(1.6,rad*.155);ctx.stroke();")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10g applied:", len(s), "bytes")
