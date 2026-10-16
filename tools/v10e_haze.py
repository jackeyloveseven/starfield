"""V10e: the haze read as a defined grey pad rather than a glow. Fade it further
out at lower alpha so it dissolves instead of ending.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = "  const ag=ctx.createRadialGradient(ax,ay,rad*.95,ax,ay,rad*1.34);\n"
a += "  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.16));\n"
a += "  ag.addColorStop(.30,css(blend(tint,[255,255,255],.42),.08));\n"
a += "  ag.addColorStop(.62,css(blend(tint,[255,255,255],.38),.03));\n"
a += "  ag.addColorStop(1,'rgba(255,255,255,0)');\n"
a += "  ctx.beginPath();ctx.arc(cx,cy,rad*1.34,0,TAU);ctx.fillStyle=ag;ctx.fill();"

b = "  const ag=ctx.createRadialGradient(ax,ay,rad*.94,ax,ay,rad*1.72);\n"
b += "  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.15));\n"
b += "  ag.addColorStop(.16,css(blend(tint,[255,255,255],.42),.075));\n"
b += "  ag.addColorStop(.42,css(blend(tint,[255,255,255],.38),.026));\n"
b += "  ag.addColorStop(1,'rgba(255,255,255,0)');\n"
b += "  ctx.beginPath();ctx.arc(cx,cy,rad*1.72,0,TAU);ctx.fillStyle=ag;ctx.fill();"

if s.count(a) != 1:
    sys.exit("count=%d: haze block not found" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10e applied:", len(s), "bytes")
