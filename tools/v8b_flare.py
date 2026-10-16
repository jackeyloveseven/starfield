"""V8b: flare the disc and commit to the Doppler.

Rendered the reference (headless, SwiftShader, 800x450) and put it beside mine.
Two differences that matter: the disc is FLARED - it thickens with radius, so the
outer edge is a broad soft sweep rather than a flat ribbon - and the Doppler is
far more committed, with the approaching side several times brighter than the
receding one rather than a gentle ramp.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("""    const sx=rr,sy=Math.max(.6,rr*FLAT);
    const lg=ctx.createLinearGradient(-sx,0,sx,0);
    lg.addColorStop(0,css(col,al*.34));lg.addColorStop(.24,css(col,al));
    lg.addColorStop(.50,css(col,al*.70));lg.addColorStop(1,css(col,al*.14));""",
    """    // flared: the disc thickens with radius, so the rim is a broad soft sweep
    const sx=rr,sy=Math.max(.6,rr*FLAT*(1+1.25*f));
    const lg=ctx.createLinearGradient(-sx,0,sx,0);
    lg.addColorStop(0,css(col,al*.10));lg.addColorStop(.20,css(col,al));
    lg.addColorStop(.46,css(col,al*.52));lg.addColorStop(.72,css(col,al*.20));
    lg.addColorStop(1,css(col,al*.06));""")

rep("     const th=t0+len*(j/5),px=Math.cos(th)*rr,py=ry+Math.sin(th)*Math.max(.6,rr*FLAT);",
    "     const th=t0+len*(j/5),px=Math.cos(th)*rr,py=ry+Math.sin(th)*Math.max(.6,rr*FLAT*(1+1.25*fr));")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V8b applied:", len(s), "bytes")
