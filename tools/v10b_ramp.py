"""V10b: the shape is right, the tonality is not. V10 fixed the geometry - the
terminator is a real ellipse, the machined ring and the outline are gone - but it
came out as a glowing white egg.

Three causes, all value rather than shape:

  * the ramp exponent .50 put most of the lit hemisphere at ~95%, so there was no
    gradient across the day side at all, just white then a cliff. Lambertian
    brightness IS b, so a near-linear ramp is both more correct and more readable.
  * the multiply tint at 62% toward white pushed the peak to near-white.
  * the atmosphere haze was wide (.22 alpha out to 1.55 rad) and read as a glow
    sticker behind a light bulb.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:120]))
    s = s.replace(a, b, n)


# 1. a real gradient across the lit hemisphere instead of a white cap
rep("  // a broad, even day side; a night side that is nearly black; no hotspot\n"
    "  const v=b>=0?.16+.84*Math.pow(b,.50):.16*Math.pow(1+b,2.0);",
    "  // Lambertian brightness IS b, so the ramp is near linear: a real gradient\n"
    "  // across the lit hemisphere, not a white cap with a cliff under it\n"
    "  const v=b>=0?.13+.87*b:.13*Math.pow(1+b,1.5);")

# 2. stop blowing the highlight out
rep("  ctx.fillStyle=css(blend(tint,[255,255,255],.62));\n"
    "  ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);",
    "  ctx.fillStyle=css(blend(tint,[255,255,255],.40));\n"
    "  ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);")

# 3. a tighter, fainter haze - it was reading as a glow sticker
rep("  const ax=cx+ux*rad*.30,ay=cy+uy*rad*.30;\n"
    "  const ag=ctx.createRadialGradient(ax,ay,rad*.92,ax,ay,rad*1.55);\n"
    "  ag.addColorStop(0,css(blend(tint,[255,255,255],.50),.22));\n"
    "  ag.addColorStop(.42,css(blend(tint,[255,255,255],.42),.09));\n"
    "  ag.addColorStop(1,'rgba(255,255,255,0)');\n"
    "  ctx.beginPath();ctx.arc(cx,cy,rad*1.55,0,TAU);ctx.fillStyle=ag;ctx.fill();",
    "  const ax=cx+ux*rad*.26,ay=cy+uy*rad*.26;\n"
    "  const ag=ctx.createRadialGradient(ax,ay,rad*.95,ax,ay,rad*1.34);\n"
    "  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.13));\n"
    "  ag.addColorStop(.45,css(blend(tint,[255,255,255],.40),.05));\n"
    "  ag.addColorStop(1,'rgba(255,255,255,0)');\n"
    "  ctx.beginPath();ctx.arc(cx,cy,rad*1.34,0,TAU);ctx.fillStyle=ag;ctx.fill();")

# 4. the lit limb, quieter
rep("   ctx.strokeStyle=css(blend(tint,[255,255,255],.58),.24-k*.075);\n"
    "   ctx.lineWidth=Math.max(.9,rad*(.05+k*.055));",
    "   ctx.strokeStyle=css(blend(tint,[255,255,255],.52),.15-k*.05);\n"
    "   ctx.lineWidth=Math.max(.8,rad*(.035+k*.045));")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10b applied:", len(s), "bytes")
