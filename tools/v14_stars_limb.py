"""V14: more stars, and an atmosphere that actually peaks at the limb.

1. Stars. The reference photographs carry an order of magnitude more stars than
   this piece does, and the user's own reason for wanting them is exact: the
   lensing distortion is only visible if there is a dense field behind it to
   distort. 5000 -> 16000, bright stars 12 -> 22.

2. The limb. Measured on a scanline through a world: 6 px went from 72 to 177, a
   105-count cliff, and the value AT the limb (177) was lower than the disc's own
   peak - i.e. the edge was a cut-out, not an atmosphere. The old haze was a
   colourless radial puff centred on an offset point BEHIND the disc, so nothing
   in the frame peaked at the edge at all.

   A real atmosphere is brightest exactly where the line of sight grazes the most
   air, which is the limb, and it carries colour. So: a saturated band centred on
   the disc whose peak sits on rad and which continues inward over the lit edge,
   with the old offset haze kept on top for the lit-side bias.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:150]))
    s = s.replace(a, b, n)


# ---- 1. a denser field ----
rep("const stars=Array.from({length:coarse?2400:5000},(_,i)=>{",
    "const stars=Array.from({length:coarse?6500:16000},(_,i)=>{")
rep("const brightStars=Array.from({length:coarse?7:12},(_,i)=>{",
    "const brightStars=Array.from({length:coarse?12:22},(_,i)=>{")

# ---- 2. the atmosphere peaks at the limb ----
rep("""  // A world does not end in a line, it dissolves. The haze sits behind the disc,
  // offset toward the sun so the lit limb is the brighter one.
  const ax=cx+ux*rad*.26,ay=cy+uy*rad*.26;
  const ag=ctx.createRadialGradient(ax,ay,rad*.94,ax,ay,rad*1.72);
  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.15));
  ag.addColorStop(.16,css(blend(tint,[255,255,255],.42),.075));
  ag.addColorStop(.42,css(blend(tint,[255,255,255],.38),.026));
  ag.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(cx,cy,rad*1.72,0,TAU);ctx.fillStyle=ag;ctx.fill();""",
    """  // The atmosphere, and it PEAKS ON THE LIMB. A line of sight grazes the most
  // air exactly where it is tangent to the surface, so that is where a real
  // atmosphere is brightest - and that is the transition that makes a disc read
  // as a world rather than as a cut-out. The old version was a colourless puff
  // centred on a point behind the disc, so nothing in the frame peaked at the
  // edge and the rim stayed a 105-count cliff. This band is centred on the disc,
  // it carries colour, and it continues INWARD over the lit edge too.
  // The gradient runs .74..1.58 rad, so the limb sits at offset .31 of it.
  const atmo=blend(tint,[168,206,255],.44);
  const bg2=ctx.createRadialGradient(cx,cy,rad*.74,cx,cy,rad*1.58);
  bg2.addColorStop(0,css(atmo,0));
  bg2.addColorStop(.31,css(atmo,.34));
  bg2.addColorStop(.55,css(atmo,.13));
  bg2.addColorStop(.78,css(atmo,.045));
  bg2.addColorStop(1,css(atmo,0));
  ctx.beginPath();ctx.arc(cx,cy,rad*1.58,0,TAU);ctx.fillStyle=bg2;ctx.fill();
  // the lit-side bias, layered on the symmetric band
  const ax=cx+ux*rad*.26,ay=cy+uy*rad*.26;
  const ag=ctx.createRadialGradient(ax,ay,rad*.94,ax,ay,rad*1.72);
  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.13));
  ag.addColorStop(.16,css(blend(tint,[255,255,255],.42),.065));
  ag.addColorStop(.42,css(blend(tint,[255,255,255],.38),.022));
  ag.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(cx,cy,rad*1.72,0,TAU);ctx.fillStyle=ag;ctx.fill();""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V14 applied:", len(s), "chars")
