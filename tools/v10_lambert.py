"""V10: stop painting a glossy ball. Paint the Lambertian field instead.

Diagnosis of the "plastic" complaint. The old drawWorld painted a RADIAL GRADIENT
centred on the sub-solar point. The iso-brightness curves of a radial gradient are
concentric circles - which is the visual signature of a glossy sphere with a
specular highlight, i.e. a billiard ball. On top of that it stroked a ring clipped
between .84 and 1.02 rad (a machined band around the ball) and a thin ink outline
(a hard circular edge). Three concentric-circle cues stacked.

A Lambertian sphere lit from L is bright by

    b = x*lx + y*ly + z*lz,   z = sqrt(1 - r^2)

and the curves of constant b are ELLIPSES, not circles: centre pushed along the
light by b*sin(theta), semi-axes (cos(theta), 1)*sqrt(1-b^2). Painting that field
is what makes a disc read as a lit world rather than as a shiny ball.

Cost: the light never moves and the field is scale-invariant, so the whole field is
baked once into an offscreen sprite. Per world it is one drawImage plus one
multiply pass to tint it - independent of how fine the field is.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

start = s.index("/* A world, kept smooth and clean.")
end = s.index("/* Tanner Helland's blackbody approximation")
old = s[start:end]

new = """/* The shading field of a Lambertian sphere, baked once into an offscreen sprite.
 *
 * A world used to be a radial gradient centred on the sub-solar point, and that
 * is exactly why it read as plastic: a radial gradient's iso-brightness curves are
 * concentric circles, which is the signature of a glossy ball with a specular
 * highlight, not of a lit sphere. The ring clipped between .84 and 1.02 rad and
 * the thin ink outline made it worse - a machined band around a ball.
 *
 * A sphere lit from L is bright by b = x*lx + y*ly + z*lz with z = sqrt(1-r^2),
 * and the curves of constant b are ellipses, not circles. The light never moves
 * and the field is scale invariant, so baking it once costs nothing per frame:
 * every world is one drawImage of the same sprite, tinted by a multiply pass. */
let worldLit=null;
function worldShade(){
 if(worldLit)return worldLit;
 const S=320,cv=document.createElement('canvas');cv.width=cv.height=S;
 const ic=cv.getContext('2d'),img=ic.createImageData(S,S),px=img.data;
 const L=[-.40,-.50,.77],ln=Math.hypot(L[0],L[1],L[2]);
 const lx=L[0]/ln,ly=L[1]/ln,lz=L[2]/ln;
 for(let j=0;j<S;j++)for(let i=0;i<S;i++){
  const x=(i+.5)/S*2-1,y=(j+.5)/S*2-1,r2=x*x+y*y,o=(j*S+i)*4;
  if(r2>1)continue;
  const b=x*lx+y*ly+Math.sqrt(Math.max(0,1-r2))*lz;
  // a broad, even day side; a night side that is nearly black; no hotspot
  const v=b>=0?.16+.84*Math.pow(b,.50):.16*Math.pow(1+b,2.0);
  const g=(clamp(v)*255)|0;
  px[o]=px[o+1]=px[o+2]=g;px[o+3]=255;
 }
 ic.putImageData(img,0,0);
 return worldLit=cv;
}
/* A world: a lit sphere with weather on it. No hotspot, no ring, no outline. */
function drawWorld(m,q,p,t,rad,tint){
 const cx=q[0],cy=q[1];
 const L=[-.40,-.50,.77],ln=Math.hypot(L[0],L[1],L[2]),l=[L[0]/ln,L[1]/ln,L[2]/ln];
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  if(rad<2.4){ctx.beginPath();ctx.arc(cx,cy,Math.max(.6,rad),0,TAU);ctx.fillStyle=css(tint,.85);ctx.fill();return;}
  const sp=Math.hypot(l[0],l[1]);
  const ux=sp>1e-3?l[0]/sp:1,uy=sp>1e-3?l[1]/sp:0;
  // A world does not end in a line, it dissolves. The haze sits behind the disc,
  // offset toward the sun so the lit limb is the brighter one.
  const ax=cx+ux*rad*.30,ay=cy+uy*rad*.30;
  const ag=ctx.createRadialGradient(ax,ay,rad*.92,ax,ay,rad*1.55);
  ag.addColorStop(0,css(blend(tint,[255,255,255],.50),.22));
  ag.addColorStop(.42,css(blend(tint,[255,255,255],.42),.09));
  ag.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(cx,cy,rad*1.55,0,TAU);ctx.fillStyle=ag;ctx.fill();
  ctx.save();
  ctx.beginPath();ctx.arc(cx,cy,rad,0,TAU);ctx.clip();
  ctx.drawImage(worldShade(),cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='multiply';
  ctx.fillStyle=css(blend(tint,[255,255,255],.62));
  ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='source-over';
  // Weather. Only where there are pixels to spend on it, and only where the sun
  // actually falls - a cloud on the night side is a bug, not a cloud. Irregular
  // blobs, not bands: bands at this size read as rings, which is the same
  // concentric-circle mistake in a different costume.
  if(rad>13){
   const hb=(m.phase*4096)|0;
   for(let k=0;k<5;k++){
    const a=hash(k,hb,31)*TAU,rr=Math.sqrt(hash(k,hb,32))*rad*.86;
    const bx=cx+Math.cos(a)*rr,by=cy+Math.sin(a)*rr;
    const dx=(bx-cx)/rad,dy=(by-cy)/rad;
    const lb=dx*l[0]+dy*l[1]+Math.sqrt(Math.max(0,1-dx*dx-dy*dy))*l[2];
    const al=.20*clamp((lb+.10)/.45);
    if(al<.02)continue;
    const br=rad*(.26+.38*hash(k,hb,33));
    ctx.save();
    ctx.translate(bx,by);ctx.rotate(hash(k,hb,34)*TAU);ctx.scale(1,.46);ctx.translate(-bx,-by);
    const bg=ctx.createRadialGradient(bx,by,0,bx,by,br);
    bg.addColorStop(0,css(blend(tint,[255,255,255],.70),al));
    bg.addColorStop(1,'rgba(255,255,255,0)');
    ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=bg;ctx.fill();
    ctx.restore();
   }
  }
  ctx.restore();
  // The lit limb, as a CRESCENT. A full ring around the edge is what made the old
  // version read as a machined band; the light only grazes one side.
  const a0=Math.atan2(uy,ux);
  ctx.save();ctx.lineCap='round';
  for(let k=0;k<3;k++){
   ctx.beginPath();ctx.arc(cx,cy,rad*(1+k*.026),a0-1.25,a0+1.25);
   ctx.strokeStyle=css(blend(tint,[255,255,255],.58),.24-k*.075);
   ctx.lineWidth=Math.max(.9,rad*(.05+k*.055));
   ctx.stroke();
  }
  ctx.restore();
 }});
}
"""

s = s[:start] + new + s[end:]

GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(P, 'w', encoding='utf-8', newline='').write(s)
print("V10 applied:", len(s), "bytes")
