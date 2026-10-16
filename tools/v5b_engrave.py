"""V5b: hatch the night side only, and calm the hole's outer glow.

A family of circles about the light axis covering the whole disc reads as a
wireframe globe, not as shading - the lit side should be a clean tone with the
engraving crowding into the night. And the .15 glow at 4.6 shadow radii washed a
grey ellipse right across the frame.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("""  ctx.strokeStyle=css(p.ink,.5);
  for(let k=1;k<=11;k++){
   const phi=k/11*Math.PI*.94,cph=Math.cos(phi),sph=Math.sin(phi);
   ctx.globalAlpha=.07+Math.pow(k/11,1.7)*.44;
   ctx.lineWidth=Math.max(.4,rad*(.014+.010*k/11));""",
    """  ctx.strokeStyle=css(p.ink,.5);
  for(let k=1;k<=9;k++){
   const f=k/9,phi=(.58+.40*f)*Math.PI,cph=Math.cos(phi),sph=Math.sin(phi);
   ctx.globalAlpha=.06+Math.pow(f,1.5)*.52;
   ctx.lineWidth=Math.max(.4,rad*.016);""")

rep(" glow([m.x,m.y,m.z],rad*4.6,hot,.15,2.6);", " glow([m.x,m.y,m.z],rad*3.4,hot,.11,2.4);")
rep("  strand(a*.68,b*.86, rad*1.05,.15);", "  strand(a*.68,b*.86, rad*1.05,.11);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V5b applied:", len(s), "bytes")
