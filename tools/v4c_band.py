"""V4c: the sky itself.

The vertical gradient was inherited from a piece that had a horizon to meet, so
it was pale at the bottom and swallowed the faint stars - which is why the lower
half of every frame read as empty wash. And the band was laid exactly along the
direction of travel, so it converged at the vanishing point instead of crossing
the frame.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# Deep space, not sky-over-fog: everything falls toward the ink.
rep(" g.addColorStop(0,css(p.sky));g.addColorStop(.55,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.ink,.76)));",
    " g.addColorStop(0,css(blend(p.sky,p.ink,.36)));g.addColorStop(.55,css(blend(p.horizon,p.ink,.54)));g.addColorStop(1,css(blend(p.fog,p.ink,.86)));")

# The band runs diagonally across the view instead of dead ahead.
rep("const BAND_U=[.10,0,1],BAND_REF=[.62,.74,-.06];",
    "const BAND_U=[.26,.44,1],BAND_REF=[.70,.50,-.14];")

# More of it, and brighter: it is the only thing marking the route now.
rep("const bandStars=Array.from({length:coarse?1200:2600},(_,i)=>{",
    "const bandStars=Array.from({length:coarse?1700:3400},(_,i)=>{")
rep("   ctx.globalAlpha=clamp(.58*bw,0,.88)*(phase?.74:1);",
    "   ctx.globalAlpha=clamp(.72*bw,0,.95)*(phase?.74:1);")
rep("   const al=clamp(n.alpha*bw,0,.56),g2=ctx.createRadialGradient(",
    "   const al=clamp(n.alpha*bw,0,.70),g2=ctx.createRadialGradient(")
rep(" return {x:d[0],y:d[1],z:d[2],size:.30+hash(i,422)*.46,alpha:.10+hash(i,423)*.20};",
    " return {x:d[0],y:d[1],z:d[2],size:.34+hash(i,422)*.52,alpha:.14+hash(i,423)*.24};")
# and let the faint field read against a darker ground
rep("  ctx.fillStyle=css(blend(p.craft,[255,255,255],.25));\n  for(let phase=0;phase<2;phase++){\n   ctx.globalAlpha=clamp((.30+t*.22)*dense,0,.92)*(phase?.72:1);",
    "  ctx.fillStyle=css(blend(p.craft,[255,255,255],.32));\n  for(let phase=0;phase<2;phase++){\n   ctx.globalAlpha=clamp((.40+t*.24)*dense,0,.95)*(phase?.72:1);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4c applied:", len(s), "bytes")
