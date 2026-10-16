"""V19: the black hole sprite has to be sampled at screen resolution.

The sprite was a fixed 512x512 drawn onto a quad 10.54*rad pixels wide. At rad=102
that is 1075 px of screen fed by 512 px of texture - a 2.1x upscale, so every
texture pixel became a 2.1 px block and the plasma read as a field of dots.

Resolution is not the whole story though. The plasma's noise is a function of the
disc radius, and `radius = length(p)` spans 0..13.75 over half the sprite, so at
512 the sampling is 256/13.75 = 18.6 px per radius unit, and 8.8 after the
upscale. That is below the noise frequency, which is what turns it into blocks
rather than a soft blur.

So the drawing buffer now follows the drawn size: S = 2*DRAW, quantised to 128 px
steps so the buffer is not reallocated every frame, capped at 1536. The final
drawImage also gets the high-quality filter, which costs nothing at this size.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:140]))
    s = s.replace(a, b, n)


rep("""  const G=holeGL,DRAW=rad*5.27;holeDraws++;holeLastRad=Math.round(rad);
  queue.push({type:4,d:q[2],alpha:1,fn:()=>{
   const g=G.gl;
   g.uniform2f(G.u.res,G.S,G.S);""",
    """  const G=holeGL,DRAW=rad*5.27;holeDraws++;holeLastRad=Math.round(rad);
  queue.push({type:4,d:q[2],alpha:1,fn:()=>{
   const g=G.gl;
   // 1:1 with the screen, in 128 px steps so the drawing buffer is not
   // reallocated every frame. Below this the plasma's noise aliases into blocks.
   const want=clamp(Math.round(DRAW*2/128)*128,256,1536);
   if(G.cv.width!==want){G.cv.width=want;G.cv.height=want;g.viewport(0,0,want,want);G.S=want;}
   g.uniform2f(G.u.res,G.S,G.S);""")

rep("   ctx.drawImage(G.cv,cx-DRAW,cy-DRAW,DRAW*2,DRAW*2);",
    "   ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';\n"
    "   ctx.drawImage(G.cv,cx-DRAW,cy-DRAW,DRAW*2,DRAW*2);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V19 applied:", len(s), "chars")
