"""V10d: two artifacts visible at 3x zoom.

1. The clouds were DARKER than the day side they sit on. The day side peaks at
   blend(tint,white,.40) after the multiply, and the clouds were painted at
   blend(tint,white,.72) - i.e. below it. So the "clouds" composited as grey
   smudges, which is exactly what a stain looks like, not what a cloud looks
   like. Clouds have to be brighter than what is under them.

2. The lit limb was drawn as three stroked arcs, and at 3x it reads as a thin arc
   floating just off the disc with a gap under it - a sticker. DSP has no rim
   light on the disc at all: the limb is sold by the WIDE soft haze outside it,
   which is already drawn behind. So the crescent goes, and the haze carries it.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# 1. clouds brighter than the surface under them; softer edges on both layers
rep("""    const bg=ctx.createRadialGradient(bx,by,0,bx,by,br);
    bg.addColorStop(0,css(col,al));bg.addColorStop(1,css(col,0));
    ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=bg;ctx.fill();
    ctx.restore();
   };
   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.72),.24);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.34),.16);""",
    """    const bg=ctx.createRadialGradient(bx,by,0,bx,by,br);
    bg.addColorStop(0,css(col,al));bg.addColorStop(.45,css(col,al*.62));
    bg.addColorStop(1,css(col,0));
    ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=bg;ctx.fill();
    ctx.restore();
   };
   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.86),.22);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.42),.11);""")

# 2. the haze carries the limb, so it can be a little stronger
rep("  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.13));\n"
    "  ag.addColorStop(.45,css(blend(tint,[255,255,255],.40),.05));",
    "  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.16));\n"
    "  ag.addColorStop(.30,css(blend(tint,[255,255,255],.42),.08));\n"
    "  ag.addColorStop(.62,css(blend(tint,[255,255,255],.38),.03));")

# 3. drop the crescent entirely
a = s.index("  // The lit limb, as a CRESCENT.")
b = s.index(" }});\n}\n/* Tanner Helland's blackbody approximation")
s = s[:a] + s[b:]

GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10d applied:", len(s), "bytes")
