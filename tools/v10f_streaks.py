"""V10f: the disc's fibres were coming out as long bright horizontal bars.

streaks() draws an arc of length len*tAU at radius rr, and with len up to .64 and
rr up to ROUT = 6 shadow radii, a single "fibre" is up to 3.8 rad long - at
rad=100 that is a 380 px bar. Drawn with round caps, at alpha up to .56, and
twenty-six of them, they read as UI scan lines lying across the disc, not as gas.

Gas in orbit is filamentary, so the shape is right; the scale is wrong by an order
of magnitude. Many more, much shorter, much fainter, much thinner.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("   for(let k=0;k<26;k++){\n"
    "    const t0=hash(k+sd,801)*TAU,len=.14+hash(k+sd,802)*.5,fr=.10+.90*hash(k+sd,803);",
    "   for(let k=0;k<54;k++){\n"
    "    const t0=hash(k+sd,801)*TAU,len=.05+hash(k+sd,802)*.22,fr=.10+.90*hash(k+sd,803);")

rep("    const al=alpha*d*(.14+.42*hash(k+sd,804));\n    if(al<.02)continue;",
    "    const al=alpha*d*(.05+.16*hash(k+sd,804));\n    if(al<.015)continue;")

rep("    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(.5,rad*(.006+.022*hash(k+sd,805)));",
    "    ctx.strokeStyle=css(col,al);ctx.lineWidth=Math.max(.4,rad*(.004+.010*hash(k+sd,805)));")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10f applied:", len(s), "bytes")
