"""Diagnostic only: neutralise one surface-texture source at a time in GLSL_HOLE,
so a render can say which one actually puts the stipple on the disc.

  python -I diag_surf.py <in.html> <out.html> silk|warp|both|none
"""
import sys

if len(sys.argv) != 4:
    sys.exit("usage: python -I diag_surf.py <in.html> <out.html> silk|warp|both|none")
src_p, out_p, mode = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


if mode in ("silk", "both"):
    rep(" col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));",
        " col*=1.0; // DIAG: silk off")

if mode in ("warp", "both"):
    rep(" float rw=r+(warp-0.5)*0.22;",
        " float rw=r; // DIAG: warp off")

if mode == "flat":
    rep(" fragColor=vec4(outc*alpha,alpha);",
        " fragColor=vec4(vec3(0.50,0.50,0.52),1.0); // DIAG: flat sprite")

if mode == "silkflat":
    rep(" col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));",
        " col*=1.0; // DIAG: silk removed")

if mode == "silkdrift":
    rep(""" float s3=silk*3.0,qf=floor(s3);
 float silkQ=(qf+smoothstep(0.35,0.65,s3-qf))/3.0;
 col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));""",
        """ float drift=noiseP(vec2(radius*1.4,az*4.0-uTime/8.0*1.2),4.0);
 col*=1.0+0.10*(drift-0.5); // DIAG: smooth low-freq drift""")

if mode == "grain":
    rep(" ctx.save();ctx.globalAlpha=.40;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1;",
        " ctx.save();ctx.globalAlpha=0.0;ctx.fillStyle=grainPattern;ctx.fillRect(0,0,W,H);ctx.globalAlpha=1; // DIAG: grain off")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("diag %s applied -> %s" % (mode, out_p))
