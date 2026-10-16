"""V4f: make the band read as a band.

Denser stars alone read as "more stars here". It is the luminous wash that makes
a Milky Way legible, so weight the wash over the star count.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:120]))
    s = s.replace(a, b, n)


rep(" return {x:d[0],y:d[1],z:d[2],size:.34+hash(i,422)*.52,alpha:.14+hash(i,423)*.24};",
    " return {x:d[0],y:d[1],z:d[2],size:.46+hash(i,422)*.66,alpha:.20+hash(i,423)*.30};")
rep("   const al=clamp(n.alpha*bw,0,.70),g2=ctx.createRadialGradient(",
    "   const al=clamp(n.alpha*bw*1.6,0,.86),g2=ctx.createRadialGradient(")
rep(" return {x:d[0],y:d[1],z:d[2],size:.30+mag*2.1,mag,phase:hash(i,415)*TAU};",
    " return {x:d[0],y:d[1],z:d[2],size:.34+mag*2.4,mag,phase:hash(i,415)*TAU};")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4f applied:", len(s), "bytes")
