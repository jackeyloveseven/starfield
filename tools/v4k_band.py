"""V4k: soften the band.

Four discrete strokes left visible parallel edges, so the band read as a
searchlight rather than as a galaxy. Seven layers on a gentler ramp approximate a
gradient across the band without an offscreen canvas.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("   for(const L of [[250,.055],[160,.072],[92,.098],[42,.140]]){",
    "   for(const L of [[300,.020],[232,.025],[172,.031],[122,.038],[80,.047],[46,.058],[22,.072]]){")
rep("    ctx.strokeStyle=css(col,clamp(L[1]*bw*1.7,0,.5));ctx.lineWidth=L[0];ctx.stroke();",
    "    ctx.strokeStyle=css(col,clamp(L[1]*bw*1.6,0,.34));ctx.lineWidth=L[0];ctx.stroke();")
rep("   ctx.globalAlpha=clamp(.80*bw,0,.95)*(phase?.74:1);",
    "   ctx.globalAlpha=clamp(.62*bw,0,.80)*(phase?.74:1);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4k applied:", len(s), "bytes")
