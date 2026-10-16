"""V10c: give the worlds weather.

V10/V10b fixed the shape and the value; what is left is that they are bare. DSP's
worlds are smooth but not featureless - they carry large, soft, irregular cloud
masses. The old three horizontal ellipses were the wrong instrument (at this size
a band reads as a ring, the same concentric mistake again); irregular blobs faded
by how much sun actually falls on them are the right one. A few darker patches go
in under them so the surface has tone as well as brightness.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = s.index("  if(rad>13){\n   const hb=(m.phase*4096)|0;")
b = s.index("  ctx.restore();\n  // The lit limb, as a CRESCENT.")
old = s[a:b]

new = """  if(rad>13){
   const hb=(m.phase*4096)|0;
   const blob=(k,col,al0)=>{
    const ang=hash(k,hb,31)*TAU,rr=Math.sqrt(hash(k,hb,32))*rad*.88;
    const bx=cx+Math.cos(ang)*rr,by=cy+Math.sin(ang)*rr;
    const dx=(bx-cx)/rad,dy=(by-cy)/rad;
    const lb=dx*l[0]+dy*l[1]+Math.sqrt(Math.max(0,1-dx*dx-dy*dy))*l[2];
    const al=al0*clamp((lb+.10)/.45);
    if(al<.02)return;
    const br=rad*(.24+.42*hash(k,hb,33));
    ctx.save();
    ctx.translate(bx,by);ctx.rotate(hash(k,hb,34)*TAU);ctx.scale(1,.44);ctx.translate(-bx,-by);
    const bg=ctx.createRadialGradient(bx,by,0,bx,by,br);
    bg.addColorStop(0,css(col,al));bg.addColorStop(1,css(col,0));
    ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=bg;ctx.fill();
    ctx.restore();
   };
   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.72),.24);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.34),.16);
  }
"""

s = s[:a] + new + s[b:]

GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10c applied:", len(s), "bytes")
