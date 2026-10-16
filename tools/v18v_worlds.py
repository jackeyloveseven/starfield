"""V18v WORLDS -- give each kind of body its own appearance, and its own size.

The user, twice: "星球有恒星，中子星红矮星等等，你这所有星球样貌差不多，位置差不多
大小差不多" and "星球还是很丑". The second one is not a shading bug: the shading is
a correct Lambert field now (v10), the tint is a palette hue shift, and there is
exactly ONE drawing path for every body. So a rock world, an ocean world, a gas
giant and an ice world are the same grey ball at four hues - which is what the
frame shows. Measured on shots/w-base.png: four bodies, four pale grey spheres.

This patch keeps the machinery that eleven rounds built (the baked 320x320
Lambert sprite, the multiply tint, the illumination-faded cloud blobs) for the
LIT kinds, and adds what actually names each kind:

  kind 0  rock world      dark maria over a rust ground, then craters whose rim
                          catches the sun on one side only
  kind 1  ocean world     deep blue, cloud swirls, and a specular glint at the
                          sub-solar point - the one kind where a sheen is right
  kind 2  gas giant       latitude belts, spaced by sin(phi) so they close up
                          toward the poles, plus one storm oval
  kind 3  ice world       pressure cracks and a frost cap under the sun
  kind 5  star            a NEW path: self-luminous, not lit. Limb-darkened disc
                          (brightest at the centre), a wide corona, and the bloom
                          pass makes the white core
  kind 6  red dwarf       the same emitter path, deep red, small, tight corona
  kind 7  neutron star    a few pixels of blue-white with two polar beams
  kind 8  ringed giant    belts, plus a tilted ring system split into the half
                          behind the planet and the half in front of it

Also fixed: the atmosphere was blend(tint,[168,206,255],.44) for every body, so
even a rust world wore the same blue halo. It is now per kind (AIR).

Sizes read differently too, because the user said "大小差不多": the radius table
gains the four new kinds and the lit four are spread out (rock 104, ice 132,
ocean 152, gas 228, ringed 248, red dwarf 84, star 360, neutron star 9 - a few
pixels, as asked). MASS_KIND is extended so kind 5..8 do not run off the end;
index 4 is untouched because that is the horizon's gravity, which is tuned.

Reads <in.html>, asserts every replaced string occurs exactly once, writes
<out.html>. Never writes its input in place unless the caller asks it to:

  python -I v18v_worlds.py work-worlds.html work-worlds-v18v.html

COLLISION NOTE. Another agent's copy (work-orbits.html) rewrites the same two
places: the body roll / radius table inside chunk(), and drawMass() (it inserts
a sun path for kinds 5..7). Everything else here - massTint, AIR, the atmosphere,
kindSurface, ringHalf, drawRinged, drawLuminary - is untouched by that patch and
applies in either order. MASS_KIND is deliberately NOT replaced (a guarded push
next to it composes with theirs). If v18v is applied first, the orbits patch only
has to rebase its chunk() block onto the roll and radius lines below.
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:120]))
    s = s.replace(a, b, n)


# ---- 1. the kind vocabulary is nine wide, and so is the gravity table ----
# Anchored on the comment BELOW the constant, not on the constant itself: the
# agent who owns the lattice also extends MASS_KIND, and replacing that line
# would make their patch fail for no reason. A guarded push composes with any
# version of the line - if they already made it nine long, this does nothing.
rep("/* Six beats, sixteen lenses. The next variation exists before the preceding",
    "// Indexed by kind. Only kind 4 is read by updateGravity (the horizon), and\n"
    "// index 4 is the tuned value - do not move it. 5..8 exist so the luminous\n"
    "// kinds and the ringed giant do not run off the end of the table.\n"
    "if(MASS_KIND.length<9)MASS_KIND.push(3.2,1.1,1.6,1.9);\n"
    "/* Six beats, sixteen lenses. The next variation exists before the preceding")

# ---- 2. the roll covers the whole vocabulary ----
rep("""  const roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(horizon&&i===0)kind=4;""",
    """  // The roll now reaches the luminous kinds as well. A star is an event in the
  // sky, not the fourth thing you pass, so they stay rare: sun 6%, red dwarf 9%,
  // neutron star 3%, ringed giant 5%.
  const roll=r();
  let kind=roll<.26?0:roll<.44?1:roll<.60?2:roll<.72?3
          :roll<.78?5:roll<.87?6:roll<.90?7:roll<.95?8:4;
  if(horizon&&i===0)kind=4;""")

# ---- 3. and the radius table says how big each one reads ----
rep("  masses.push({x:laneX(z)+side*off,y,z,kind,r:[110,150,200,260,1100][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});",
    "  // Radius by kind: rock 104, ocean 152, gas giant 228, ice 132, horizon 1100,\n"
    "  // sun 360, red dwarf 84, neutron star 9, ringed giant 248. The neutron star\n"
    "  // is a few pixels and the sun is large, which is the whole point of the\n"
    "  // table - the four lit kinds used to sit within 110..260 of each other.\n"
    "  masses.push({x:laneX(z)+side*off,y,z,kind,r:[104,152,228,132,1100,360,84,9,248][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});")

# ---- 4. the tint is the body's own colour, not the region's ----
rep("""function massTint(m,p){
 return m.kind===0?blend(p.sun,p.paper,.30):m.kind===1?p.sun:m.kind===2?blend(p.sun,[255,214,170],.45):blend(p.sun,[196,214,255],.5);
}""",
    """function massTint(m,p){
 // The tint has to survive the palette shift. A region's sun runs from a cold
 // blue-white (FOIL) to amber (CORE), and every tint used to be built mostly
 // from it, so in any one region every world came out the same colour. These are
 // absolute with a little of the palette mixed in, so a rock world is rust and
 // an ocean world is blue wherever you meet them.
 switch(m.kind){
  case 0:return blend([178,132,102],p.sun,.22);  // rock world: rust brown
  case 1:return blend([56,116,186],p.sun,.20);   // ocean world: deep blue
  case 2:return blend([214,180,132],p.sun,.22);  // gas giant: warm tan
  case 3:return blend([204,222,242],p.sun,.22);  // ice world: pale blue-white
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

# ---- 5. the atmosphere is the kind's air, not one blue for everybody ----
rep("  const atmo=blend(tint,[168,206,255],.44);",
    "  const air=AIR[m.kind],atmo=air?blend(tint,air[0],air[1]):blend(tint,[168,206,255],.44),ak=air?air[2]:1;")

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

# ---- 6. and the surface that names the kind, inside the disc, after the shading ----
rep("""   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.86),.22);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.42),.11);
  }
  ctx.restore();""",
    """   for(let k=0;k<6;k++)blob(k,blend(tint,[255,255,255],.86),.22);
   for(let k=0;k<4;k++)blob(k+16,shade(tint,.42),.11);
   // and the structure that actually names the kind
   kindSurface(m,cx,cy,rad,l,hb,tint);
  }
  ctx.restore();""")

# ---- 7. the dispatch, the emitter path, the rings ----
rep("""function drawMass(m,p,t){
 const q=project([m.x,m.y,m.z]);
 if(!q||q[2]<=30)return;
 const rad=m.r*q[3];
 if(m.kind===4){if(rad<1)return;drawHole(m,q,p,t,rad);return;}
 const tint=massTint(m,p);
 if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);
 if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);
 drawWorld(m,q,p,t,rad,tint);
}""",
    """function drawMass(m,p,t){
 const q=project([m.x,m.y,m.z]);
 if(!q||q[2]<=30)return;
 const rad=m.r*q[3];
 if(m.kind===4){if(rad<1)return;drawHole(m,q,p,t,rad);return;}
 // A ringed giant is a lit world with rings around it, so it wraps drawWorld
 // rather than replacing it. Kinds 5..8 are emitters and do not use the Lambert
 // sprite at all: a star is not lit by anything.
 if(m.kind===8){drawRinged(m,q,p,t,rad,massTint(m,p));return;}
 if(m.kind>=5){drawLuminary(m,q,p,t,rad);return;}
 const tint=massTint(m,p);
 if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);
 if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);
 drawWorld(m,q,p,t,rad,tint);
}""")

NEW = r""" }});
}
/* The structure that names the kind, drawn inside the disc after the shading
 * pass. Anything multiplied in is modulated by the Lambert field, and anything
 * drawn over it is faded by the local illumination, so nothing ever lands on the
 * night side - a band or a cloud on the unlit half is a bug, not a feature. */
function kindSurface(m,cx,cy,rad,l,hb,tint){
 const k=m.kind;
 const lit=(x,y)=>{const dx=(x-cx)/rad,dy=(y-cy)/rad;
  return clamp((dx*l[0]+dy*l[1]+Math.sqrt(Math.max(0,1-dx*dx-dy*dy))*l[2]+.10)/.45);};
 if(k===2||k===8){
  // A gas giant IS its belts. Latitude circles on a sphere, so the spacing
  // closes up toward the poles - horizontal strips, not concentric rings. The
  // distinction matters: rings are the plastic-ball signature (v10).
  ctx.globalCompositeOperation='multiply';
  for(let j=0;j<10;j++){
   const y0=cy+Math.sin(-Math.PI/2+Math.PI*j/10)*rad;
   const y1=cy+Math.sin(-Math.PI/2+Math.PI*(j+1)/10)*rad;
   const v=.70+.28*hash(hb,20+j,41);
   ctx.fillStyle=css([v*255,v*255,v*255]);
   ctx.fillRect(cx-rad,y0,rad*2,y1-y0+1);
  }
  ctx.globalCompositeOperation='source-over';
  // one long-lived storm, on the lit side
  const sx=cx+l[0]*rad*.34, sy=cy-l[1]*rad*.34, sl=lit(sx,sy);
  if(sl>.30){
   ctx.save();ctx.translate(sx,sy);ctx.rotate((hash(hb,3,51)-.5)*.7);ctx.scale(1,.55);
   const st=shade(blend(tint,[255,196,146],.55),.92);
   const g=ctx.createRadialGradient(0,0,0,0,0,rad*.26);
   g.addColorStop(0,css(st,.34*sl));
   g.addColorStop(.60,css(st,.15*sl));
   g.addColorStop(1,'rgba(0,0,0,0)');
   ctx.beginPath();ctx.arc(0,0,rad*.26,0,TAU);ctx.fillStyle=g;ctx.fill();ctx.restore();
  }
  return;
 }
 if(k===0){
  // A rock world: dark maria over the rust ground, then craters with a rim that
  // catches the sun on one side only - which is what a crater looks like.
  for(let j=0;j<6;j++){
   const a=hash(hb,40+j,71)*TAU, rr=Math.sqrt(hash(hb,40+j,72))*rad*.70;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.30+.36*hash(hb,40+j,73));
   const al=lit(bx,by); if(al<.06)continue;
   const g=ctx.createRadialGradient(bx,by,0,bx,by,br);
   g.addColorStop(0,css(shade(tint,.52),.46*al));
   g.addColorStop(.62,css(shade(tint,.68),.24*al));
   g.addColorStop(1,'rgba(0,0,0,0)');
   ctx.fillStyle=g;ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fill();
  }
  for(let j=0;j<7;j++){
   const a=hash(hb,50+j,81)*TAU, rr=Math.sqrt(hash(hb,50+j,82))*rad*.66;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.035+.065*hash(hb,50+j,83));
   const al=lit(bx,by); if(al<.10)continue;
   // A crater is not a circle: the inner wall facing the sun is in shadow and
   // the wall away from it is lit. Two crescents, and the eye reads a pit.
   const la=Math.atan2(-l[1],l[0]);
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(shade(tint,.40),al*.40);ctx.fill();
   ctx.beginPath();ctx.arc(bx,by,br,la-Math.PI*.62,la+Math.PI*.62);
   ctx.strokeStyle=css(shade(tint,.26),al*.55);
   ctx.lineWidth=Math.max(.5,br*.32);ctx.stroke();
   ctx.beginPath();ctx.arc(bx,by,br,la+Math.PI*.38,la+Math.PI*1.62);
   ctx.strokeStyle=css(blend(tint,[255,255,255],.50),al*.34);
   ctx.lineWidth=Math.max(.5,br*.32);ctx.stroke();
  }
  return;
 }
 if(k===1){
  // An ocean world: deep water, cloud swirls, and the glint of a smooth surface
  // exactly where the sun stands. This is the one kind for which a specular
  // sheen is correct rather than the glossy-ball mistake.
  // The shared multiply pass pulls the tint 40% toward white, so the blue is put
  // back first - without this the "deep blue" arrives as pale grey-blue.
  ctx.globalCompositeOperation='multiply';
  ctx.fillStyle=css([156,192,252]);
  ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='source-over';
  for(let j=0;j<5;j++){
   const a=hash(hb,60+j,91)*TAU, rr=Math.sqrt(hash(hb,60+j,92))*rad*.84;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.22+.40*hash(hb,60+j,93));
   const al=lit(bx,by); if(al<.05)continue;
   ctx.save();ctx.translate(bx,by);ctx.rotate(hash(hb,60+j,94)*TAU);ctx.scale(1,.34);ctx.translate(-bx,-by);
   const g=ctx.createRadialGradient(bx,by,0,bx,by,br);
   g.addColorStop(0,css(blend(tint,[255,255,255],.86),.26*al));
   g.addColorStop(.50,css(blend(tint,[255,255,255],.72),.12*al));
   g.addColorStop(1,'rgba(255,255,255,0)');
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=g;ctx.fill();ctx.restore();
  }
  const gx=cx+l[0]*rad*.80, gy=cy-l[1]*rad*.80, gr=rad*.28;
  const g=ctx.createRadialGradient(gx,gy,0,gx,gy,gr);
  g.addColorStop(0,css([255,255,255],.34));
  g.addColorStop(.34,css([238,248,255],.15));
  g.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(gx,gy,gr,0,TAU);ctx.fillStyle=g;ctx.fill();
  return;
 }
 if(k===3){
  // An ice world: pressure cracks, and a frost cap under the sun.
  ctx.globalCompositeOperation='multiply';
  ctx.fillStyle=css([214,230,252]);
  ctx.fillRect(cx-rad,cy-rad,rad*2,rad*2);
  ctx.globalCompositeOperation='source-over';
  for(let j=0;j<9;j++){
   const a=hash(hb,70+j,101)*TAU, rr=Math.sqrt(hash(hb,70+j,102))*rad*.74;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.34+.48*hash(hb,70+j,103));
   const al=lit(bx,by); if(al<.07)continue;
   const ang=hash(hb,70+j,104)*TAU, cs=Math.cos(ang), sn=Math.sin(ang);
   ctx.beginPath();
   for(let i=0;i<=6;i++){
    const u=(i/6-.5)*2, px=bx+cs*u*br, py=by+sn*u*br*.55+Math.sin(u*3+hb*.001)*rad*.045;
    if(i)ctx.lineTo(px,py);else ctx.moveTo(px,py);
   }
   // The lineae of a real ice moon are dark, not bright - the crack is a seam
   // in the surface, so it takes the shadow rather than catching the light.
   ctx.strokeStyle=css(blend(tint,[28,66,116],.78),.40*al);
   ctx.lineWidth=Math.max(.5,rad*.016);ctx.stroke();
  }
  const gx=cx+l[0]*rad*.60, gy=cy-l[1]*rad*.60;
  const g=ctx.createRadialGradient(gx,gy,0,gx,gy,rad*.72);
  g.addColorStop(0,css([255,255,255],.17));g.addColorStop(1,'rgba(255,255,255,0)');
  ctx.beginPath();ctx.arc(gx,gy,rad*.72,0,TAU);ctx.fillStyle=g;ctx.fill();
 }
}
/* The ring system of a ringed giant, split into the half behind the planet and
 * the half in front of it so the planet really does sit inside its rings. The
 * two halves are separate depth-sorted draws at q[2]+/-1, so the sort puts the
 * far half down first, the planet over it, and the near half on top. */
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
/* A self-luminous body. A lit world is a Lambert field times a tint; a star is
 * the opposite - brightest at the centre of the disc and dimmer at the limb,
 * because a line of sight at the limb leaves the photosphere sooner. So this
 * path uses a radial gradient on purpose: on a lit sphere that is the plastic
 * ball (v10), on an emitter it is the correct limb darkening. */
function drawLuminary(m,q,p,t,rad){
 const cx=q[0],cy=q[1],kind=m.kind;
 if(kind===7){
  // A neutron star: a few pixels of blue-white with two polar beams.
  const R=Math.max(rad,1.2),col=[214,234,255];
  queue.push({type:4,d:q[2],alpha:1,fn:()=>{
   const a=m.phase*TAU+t*.22, len=Math.max(R*19,34), wid=Math.max(R*1.5,2.4);
   ctx.save();ctx.translate(cx,cy);ctx.rotate(a);
   for(const sgn of [1,-1]){
    ctx.beginPath();ctx.moveTo(0,-wid*.30);ctx.lineTo(sgn*len,-wid);ctx.lineTo(sgn*len,wid);ctx.lineTo(0,wid*.30);ctx.closePath();
    const g=ctx.createLinearGradient(0,0,sgn*len,0);
    g.addColorStop(0,css(col,.50));g.addColorStop(.30,css(col,.22));g.addColorStop(1,css(col,0));
    ctx.fillStyle=g;ctx.fill();
   }
   ctx.restore();
   const hg=ctx.createRadialGradient(cx,cy,0,cx,cy,R*7);
   hg.addColorStop(0,css(col,.55));hg.addColorStop(.20,css(col,.24));hg.addColorStop(1,css(col,0));
   ctx.beginPath();ctx.arc(cx,cy,R*7,0,TAU);ctx.fillStyle=hg;ctx.fill();
   ctx.beginPath();ctx.arc(cx,cy,R,0,TAU);ctx.fillStyle='rgba(245,250,255,.98)';ctx.fill();
  }});
  return;
 }
 const warm=kind===5, col=warm?blackbody(5200):[255,104,72];
 const R=Math.max(rad,1.6), hb=(m.phase*4096)|0;
 const core=warm?.74:.82, mid=warm?.66:.62, limb=warm?.46:.34, reach=warm?3.0:2.6;
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  const cg=ctx.createRadialGradient(cx,cy,R*.55,cx,cy,R*reach);
  cg.addColorStop(0,css(col,warm?.28:.26));
  cg.addColorStop(.20,css(col,warm?.15:.14));
  cg.addColorStop(.50,css(col,.045));
  cg.addColorStop(1,css(col,0));
  ctx.beginPath();ctx.arc(cx,cy,R*reach,0,TAU);ctx.fillStyle=cg;ctx.fill();
  // Kept under ~200 before the grade. The grade clips above that, and a clipped
  // disc loses its own colour to the bloom - the bloom is what makes the white
  // core, so the disc only has to hand it a warm, bright, unclipped field.
  const pg=ctx.createRadialGradient(cx,cy,0,cx,cy,R);
  pg.addColorStop(0,css(shade(col,core)));
  pg.addColorStop(.60,css(shade(col,mid)));
  pg.addColorStop(.90,css(shade(col,limb*1.15)));
  pg.addColorStop(1,css(shade(col,limb)));
  ctx.beginPath();ctx.arc(cx,cy,R,0,TAU);ctx.fillStyle=pg;ctx.fill();
  // a few darker mottles so the disc is not one flat gradient
  if(R>18)for(let j=0;j<5;j++){
   const a=hash(hb,j,111)*TAU, rr=Math.sqrt(hash(hb,j,112))*R*.66;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=R*(.10+.18*hash(hb,j,113));
   const g=ctx.createRadialGradient(bx,by,0,bx,by,br);
   g.addColorStop(0,css(shade(col,limb*.9),.20));g.addColorStop(1,'rgba(0,0,0,0)');
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);ctx.fillStyle=g;ctx.fill();
  }
 }});
}
/* Tanner Helland's blackbody approximation, the same ramp the reference uses."""

rep(""" }});
}
/* Tanner Helland's blackbody approximation, the same ramp the reference uses.""", NEW)

# ---- 8. a diagnostic so a probe can prove the new kinds are actually out there ----
rep("masses:activeMasses.length,",
    "masses:activeMasses.length,kinds:activeMasses.map(m=>m.kind).sort().join(''),")

GUARD = '}};\n}'
if GUARD in s:
    sys.exit("unbalanced push callback: found }}; where }}); belongs")
open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V18v worlds applied:", len(s), "chars ->", out_p)
