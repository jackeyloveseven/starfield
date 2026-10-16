"""v21w_worlds -- finish the v18v "every kind has its own appearance" merge onto
the orbits code that landed on top of it.

v18v_worlds.py gave each body kind its own look (rock maria and craters, ocean
clouds, gas-giant belts, ice cracks, ringed-giant rings, an emitter path for the
stars) but was never applied: v18o_orbits.py then rewrote the same two places it
anchored on - the body roll / radius table inside chunk(), and drawMass() - and
the two hard-collided. This patch does that reconciliation on the live file and
extends the orbits code rather than duplicating it.

What is kept from v18v:
  - massTint: each kind's own colour, absolute with a little palette mixed in, so
    a rock world is rust and an ocean world is blue wherever you meet them.
  - AIR: the atmosphere is the kind's air, not one blue halo for everybody.
  - kindSurface: the structure that NAMES the kind - belts, maria and craters,
    cloud swirls, pressure cracks - drawn after the shading pass.
  - ringHalf / drawRinged: the ring system of a ringed giant, split into the half
    behind the planet and the half in front of it.

What is reconciled with orbits (NOT duplicated):
  - chunk(): orbits already gives sizes that "read differently" (rock 55..270,
    gas giant 380..1000, neutron star 14..24), so v18v's fixed radius table is
    dropped and the roll only gains kind 8 (ringed giant) - the reference's
    Saturn - with a radius branch to match.
  - drawMass(): orbits already routes kinds 5..7 to a star path. That path is
    left exactly as it is; only kind 8 is routed to drawRinged. v18v's own
    drawLuminary is not added, because it would duplicate the star path.

What is added for the reference's FLAT-TONED look (the user has complained about
softness twice): worldShade() bakes the Lambert sprite with a flat day tone and a
crisp terminator instead of a smooth gradient, kindSurface draws flat shapes with
hard edges instead of airbrushed radial gradients, and the atmosphere halo is
thinned by a global factor.

Reads <in.html>, asserts every replaced string occurs exactly once, writes
<out.html>. Two explicit paths are required - a bare run must not touch anything.

  python -I v21w_worlds.py work-worldsmerge.html work-worldsmerge-out.html
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v21w_worlds.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. the tint is the body's own colour, not the region's ----
rep("""function massTint(m,p){
 return m.kind===0?blend(p.sun,p.paper,.30):m.kind===1?p.sun:m.kind===2?blend(p.sun,[255,214,170],.45):blend(p.sun,[196,214,255],.5);
}""",
"""function massTint(m,p){
 // The tint has to survive the palette shift. A region's sun runs from a cold
 // blue-white to amber, and every tint used to be built mostly from it, so in any
 // one region every world came out the same colour. These are absolute with a
 // little of the palette mixed in, so a rock world is rust and an ocean world is
 // blue wherever you meet them.
 switch(m.kind){
  case 0:return blend([178,132,102],p.sun,.22);  // rock world: rust brown
  case 1:return blend([56,116,186],p.sun,.20);   // ocean world: deep blue
  case 2:return blend([214,180,132],p.sun,.22);  // gas giant: warm tan
  case 3:return blend([186,220,226],p.sun,.22);  // ice world: pale teal
  case 5:return blackbody(5200);                 // a sun is its own light
  case 6:return [255,104,72];                    // red dwarf: deep red
  case 7:return [214,234,255];                   // neutron star: blue-white
  case 8:return blend([206,176,140],p.sun,.22);  // ringed giant
 }
 return blend([196,214,255],p.sun,.25);
}
/* The air, per kind: [colour, mix, strength]. The same blue halo on every body
 * was half of "they all look the same" - a rock world wears a thin dusty haze,
 * an ocean world the strongest blue, a gas giant a broad warm one. */
const AIR={0:[[198,182,166],.50,.55],1:[[140,190,255],.55,1.0],2:[[255,226,190],.50,1.10],3:[[212,232,255],.55,.80],8:[[255,222,186],.50,1.0]};""")

# ---- 2. the atmosphere is the kind's air, thinned toward a hard edge ----
# The reference is flat graphic art: a world is a cut-out with a crisp boundary,
# not a soft halo. The band stays (it is what makes a disc read as a world) but a
# global factor folds into `ak` so every halo is roughly half as heavy, and the
# per-kind AIR strength rides on top of it.
rep("  const atmo=blend(tint,[168,206,255],.44);",
    "  const air=AIR[m.kind],atmo=air?blend(tint,air[0],air[1]):blend(tint,[168,206,255],.44),ak=(air?air[2]:1)*.50;")

rep("""  bg2.addColorStop(.31,css(atmo,.26));
  bg2.addColorStop(.55,css(atmo,.10));
  bg2.addColorStop(.78,css(atmo,.045));""",
"""  bg2.addColorStop(.31,css(atmo,.26*ak));
  bg2.addColorStop(.55,css(atmo,.10*ak));
  bg2.addColorStop(.78,css(atmo,.045*ak));""")

rep("""  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.13));
  ag.addColorStop(.16,css(blend(tint,[255,255,255],.42),.065));
  ag.addColorStop(.42,css(blend(tint,[255,255,255],.38),.022));""",
"""  ag.addColorStop(0,css(blend(tint,[255,255,255],.46),.13*ak));
  ag.addColorStop(.16,css(blend(tint,[255,255,255],.42),.065*ak));
  ag.addColorStop(.42,css(blend(tint,[255,255,255],.38),.022*ak));""")

# ---- 3. the Lambert sprite is baked flat: few tones, a crisp terminator ----
# A printed world is a handful of spot colours, not a smooth Lambert gradient.
# The day side is held at one value and the terminator falls off over a narrow
# band, so a world reads as a flat disc of colour with its structure drawn on top
# (kindSurface) - which is exactly how the reference draws its planets. Night
# keeps a little light so the unlit half is a second, darker tone, not a hole.
rep("  const v=b>=0?.16+.30*b:.16*Math.pow(1+b,1.5);",
    """  // Flat tones: night, a crisp terminator, and one flat day value.
  const v=b<=0?.16*Math.pow(1+b,1.5):(.24+.24*clamp(b/.20));""")

# ---- 4. kindSurface names the kind, flat, in place of the soft weather blobs ----
# The old block drew six white and four dark airbrushed radial blobs over every
# world. That is the softness the reference does not have, and it smeared over the
# belts a gas giant needs. It is replaced by one call that draws the kind's own
# structure with hard edges.
rep("""  if(rad>13){
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
    bg.addColorStop(0,css(col,al));bg.addColorStop(.45,css(col,al*.62));
    bg.addColorStop(1,css(col,0));
    ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=bg;ctx.fill();
    ctx.restore();
   };
   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.86),.22);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.42),.11);
  }
  ctx.restore();""",
"""  if(rad>13){
   const hb=(m.phase*4096)|0;
   // The structure that names the kind, drawn flat over the flat day tone.
   kindSurface(m,cx,cy,rad,l,hb,tint);
  }
  ctx.restore();""")

# ---- 5. the structure of each kind, and the ring system ----
NEW = r""" }});
}
/* The structure that names the kind, drawn inside the disc after the shading
 * pass. Everything here is FLAT: fill shapes with hard edges, not radial
 * gradients - a printed world is spot colours, and an airbrushed patch on a flat
 * day tone is the one thing that reads as a rendering rather than as a drawing.
 * Anything that catches light is modulated by `lit`, so nothing lands on the
 * night side - a band or a crater on the unlit half is a bug, not a feature. */
function kindSurface(m,cx,cy,rad,l,hb,tint){
 const k=m.kind;
 // 0 at the terminator, 1 in full sun, over a narrow band - a hard day/night edge
 // to match the crisp terminator the sprite is baked with.
 const lit=(x,y)=>{const dx=(x-cx)/rad,dy=(y-cy)/rad;
  return clamp((dx*l[0]+dy*l[1]+Math.sqrt(Math.max(0,1-dx*dx-dy*dy))*l[2]+.06)/.26);};
 if(k===2||k===8){
  // A gas giant IS its belts. Latitude circles on a sphere, so the spacing closes
  // up toward the poles - horizontal strips, not concentric rings, which is the
  // plastic-ball signature. Flat tones, hard edges, nine bands.
  ctx.globalCompositeOperation='multiply';
  for(let j=0;j<9;j++){
   const y0=cy+Math.sin(-Math.PI/2+Math.PI*j/9)*rad;
   const y1=cy+Math.sin(-Math.PI/2+Math.PI*(j+1)/9)*rad;
   const v=.58+.40*hash(hb,20+j,41);
   ctx.fillStyle=css([v*255,v*255,v*255]);
   ctx.fillRect(cx-rad,y0,rad*2,y1-y0+1);
  }
  ctx.globalCompositeOperation='source-over';
  // one long-lived storm, on the lit side: a flat patch with a hard edge
  const sx=cx+l[0]*rad*.34, sy=cy-l[1]*rad*.34, sl=lit(sx,sy);
  if(sl>.35){
   ctx.save();ctx.translate(sx,sy);ctx.rotate((hash(hb,3,51)-.5)*.7);ctx.scale(1,.55);
   ctx.beginPath();ctx.arc(0,0,rad*.24,0,TAU);
   ctx.fillStyle=css(shade(blend(tint,[255,196,146],.55),.94),.55*sl);ctx.fill();ctx.restore();
  }
  return;
 }
 if(k===0){
  // A rock world: flat dark maria over the rust ground, then craters whose rim
  // catches the sun on one side only - which is what a crater looks like.
  for(let j=0;j<6;j++){
   const a=hash(hb,40+j,71)*TAU, rr=Math.sqrt(hash(hb,40+j,72))*rad*.70;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.30+.36*hash(hb,40+j,73));
   const al=lit(bx,by); if(al<.10)continue;
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(shade(tint,.56),.50*al);ctx.fill();
  }
  for(let j=0;j<8;j++){
   const a=hash(hb,50+j,81)*TAU, rr=Math.sqrt(hash(hb,50+j,82))*rad*.66;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.035+.065*hash(hb,50+j,83));
   const al=lit(bx,by); if(al<.12)continue;
   // A crater is not a circle: the inner wall facing the sun is in shadow and the
   // wall away from it is lit. Two crescents, and the eye reads a pit.
   const la=Math.atan2(-l[1],l[0]);
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(shade(tint,.42),al*.45);ctx.fill();
   ctx.beginPath();ctx.arc(bx,by,br,la-Math.PI*.62,la+Math.PI*.62);
   ctx.strokeStyle=css(shade(tint,.26),al*.60);ctx.lineWidth=Math.max(.5,br*.34);ctx.stroke();
   ctx.beginPath();ctx.arc(bx,by,br,la+Math.PI*.38,la+Math.PI*1.62);
   ctx.strokeStyle=css(blend(tint,[255,255,255],.52),al*.40);ctx.lineWidth=Math.max(.5,br*.34);ctx.stroke();
  }
  return;
 }
 if(k===1){
  // An ocean world: deep flat blue put back under the shared multiply (which pulls
  // every tint 40% toward white), then flat white cloud patches on the lit side.
  ctx.globalCompositeOperation='multiply';
  ctx.fillStyle=css([150,188,250]);ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='source-over';
  for(let j=0;j<6;j++){
   const a=hash(hb,60+j,91)*TAU, rr=Math.sqrt(hash(hb,60+j,92))*rad*.80;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.16+.30*hash(hb,60+j,93));
   const al=lit(bx,by); if(al<.15)continue;
   ctx.save();ctx.translate(bx,by);ctx.rotate(hash(hb,60+j,94)*TAU);ctx.scale(1,.42);ctx.translate(-bx,-by);
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(blend(tint,[255,255,255],.90),.52*al);ctx.fill();ctx.restore();
  }
  return;
 }
 if(k===3){
  // An ice world: flat pressure cracks and a flat frost cap under the sun. The
  // lineae of a real ice moon are dark, not bright - the crack is a seam in the
  // surface, so it takes the shadow rather than catching the light.
  ctx.globalCompositeOperation='multiply';
  ctx.fillStyle=css([210,228,250]);ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='source-over';
  for(let j=0;j<9;j++){
   const a=hash(hb,70+j,101)*TAU, rr=Math.sqrt(hash(hb,70+j,102))*rad*.74;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.34+.48*hash(hb,70+j,103));
   const al=lit(bx,by); if(al<.10)continue;
   const ang=hash(hb,70+j,104)*TAU, cs=Math.cos(ang), sn=Math.sin(ang);
   ctx.beginPath();
   for(let i=0;i<=6;i++){
    const u=(i/6-.5)*2, px=bx+cs*u*br, py=by+sn*u*br*.55+Math.sin(u*3+hb*.001)*rad*.045;
    if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py);
   }
   ctx.strokeStyle=css(blend(tint,[28,66,116],.80),.42*al);
   ctx.lineWidth=Math.max(.5,rad*.017);ctx.stroke();
  }
 }
}
/* The ring system of a ringed giant, split into the half behind the planet and
 * the half in front of it so the planet really does sit inside its rings. The two
 * halves are separate depth-sorted draws at q[2]+/-1, so the sort puts the far
 * half down first, the planet over it, and the near half on top. */
function ringHalf(m,q,rad,back){
 const hb=(m.phase*4096)|0, squash=.20+.30*hash(hb,7,61), roll=(hash(hb,8,62)-.5)*.7;
 const col=blend(massTint(m,currentPalette),[232,220,202],.30);
 const bands=[[1.10,1.32,.24],[1.44,1.96,.18]];
 queue.push({type:4,d:q[2]+(back?1:-1),alpha:1,fn:()=>{
  ctx.save();ctx.translate(q[0],q[1]);ctx.rotate(roll);ctx.scale(1,squash);
  const a0=back?Math.PI:0, a1=back?TAU:Math.PI;
  for(const b of bands){
   ctx.beginPath();
   ctx.arc(0,0,rad*b[1],a0,a1,false);
   ctx.arc(0,0,rad*b[0],a1,a0,true);
   ctx.closePath();
   ctx.fillStyle=css(col,b[2]);
   ctx.fill();
  }
  ctx.restore();
 }});
}
function drawRinged(m,q,p,t,rad,tint){
 if(rad>9)ringHalf(m,q,rad,true);
 drawWorld(m,q,p,t,rad,tint);
 if(rad>9)ringHalf(m,q,rad,false);
}
"""
rep(""" }});
}
/* Tanner Helland's blackbody approximation, the same ramp the reference uses.""",
    NEW + """/* Tanner Helland's blackbody approximation, the same ramp the reference uses.""")

# ---- 6. drawMass routes the ringed giant to drawRinged ----
# The star path for kinds 5..7 above this line is orbits' own and is left exactly
# as it is; only kind 8 is added, so nothing is duplicated.
rep(""" if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);
 if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);
 drawWorld(m,q,p,t,rad,tint);
}""",
""" // A ringed giant is a lit world with rings around it, so it wraps drawWorld
 // rather than replacing it - the same lit path, with the rings depth-sorted in
 // front of and behind the disc.
 if(m.kind===8){drawRinged(m,q,p,t,rad,tint);return;}
 if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);
 if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);
 drawWorld(m,q,p,t,rad,tint);
}""")

# ---- 7. the lattice roll reaches the ringed giant ----
# Orbits already answers "大小差不多" with hard per-kind size variation, so v18v's
# fixed radius table is dropped. The luminous kinds live in systems now; only the
# ringed giant - the reference's Saturn - is added to the open lattice, with a
# radius branch so it does not fall through to the black hole's 1100.
rep("""   let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
   if(horizon&&i===0)kind=4;""",
"""   let kind=roll<.30?0:roll<.55?1:roll<.76?2:roll<.88?3:roll<.95?8:4;
   if(horizon&&i===0)kind=4;""")

rep("""   const rad=kind===0?55+r()*r()*215:kind===1?95+r()*r()*265
            :kind===2?380+r()*620:kind===3?48+r()*r()*185:1100;""",
"""   const rad=kind===0?55+r()*r()*215:kind===1?95+r()*r()*265
            :kind===2?380+r()*620:kind===3?48+r()*r()*185
            :kind===8?200+r()*280:1100;""")

# ---- 8. a diagnostic so a probe can prove the kinds are actually out there ----
rep("masses:activeMasses.length,",
    "masses:activeMasses.length,kinds:activeMasses.map(m=>m.kind).sort().join(''),")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V21w worlds merge applied:", len(s), "chars ->", out_p)
