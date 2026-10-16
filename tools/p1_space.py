"""P1: turn the paper world into a paper cosmos.

Structure preserved, subject replaced:
  terrain()  -> deepfield()   sheet of paper + printed hatch + dust lane
  chunk()    -> masses, shards, atlas plates
  structures -> bodies()      + drawMass / drawShard / drawPlate
  climate()  -> region()      weather weights -> astronomy weights
The corridor keeps routeX's exact formula so its seven consumers stay valid;
only the lane (was: river) and the vertical course change.

Run once, on starfield.html. Every replacement asserts it matched exactly once.
"""
import sys, os

PATH = r"C:\Users\machine\Downloads\starfield.html"
s = open(PATH, encoding='utf-8').read()
before = len(s)


def rep(old, new, n=1):
    global s
    if s.count(old) != n:
        sys.exit(f"expected {n} occurrence(s), found {s.count(old)}:\n{old[:160]}")
    s = s.replace(old, new, 1)


def cut(start, end, new):
    """Replace everything from `start` up to (not including) `end`."""
    global s
    i, j = s.find(start), s.find(end)
    if i < 0 or j < 0 or j < i:
        sys.exit(f"cut markers not found/in order:\n{start[:80]}\n{end[:80]}")
    s = s[:i] + new + s[j:]


# ---------------------------------------------------------------- corridor --
rep('const flightY=z=>224+26*Math.sin(z*.00043+phase)+12*Math.sin(z*.0011);',
    'const courseY=z=>196+58*Math.sin(z*.00031+phase)+20*Math.sin(z*.00097);')

# ---------------------------------------------------------------- palettes --
cut("const rawStyles=[", "const colorKeys=[", """const rawStyles=[
 {name:'素纸',en:'PAPER',caption:'宇宙从一张还没写字的纸开始',sky:'#1c2b3c',horizon:'#33485e',fog:'#26384b',ground:'#1b2836',fields:['#1e2c3b','#22303f','#1a2735','#243342','#1c2a38','#213040'],water:'#3d5872',bank:'#2b3e52',roof:'#32475e',wall:'#4c6278',tree:'#2f4b62',treeDark:'#20344a',bird:'#f5f9fc',birdShade:'#a8bccd',ink:'#e6eff7',paper:'#111b27',sun:'#d8e8f4'},
 {name:'墨海',en:'INKWASH',caption:'墨滴进水，长出一片星云',sky:'#141a2e',horizon:'#2b2a4e',fog:'#1d2340',ground:'#151a2b',fields:['#171d33','#1b2139','#141a2c','#1e2440','#161c30','#1a2036'],water:'#3b3f72',bank:'#262c50',roof:'#2c2f56',wall:'#474a78',tree:'#463a72',treeDark:'#2a2450',bird:'#f0ecfa',birdShade:'#9c92b8',ink:'#e6e2f6',paper:'#0d1020',sun:'#d9c2f0'},
 {name:'箔野',en:'FOIL',caption:'有人把碎金，撒在了夜里',sky:'#0e1822',horizon:'#23445c',fog:'#16293a',ground:'#0f1b26',fields:['#111d28','#15222e','#0e1a24','#182631','#101c26','#14202b'],water:'#2e5674',bank:'#1b3448',roof:'#1f3a50',wall:'#3a5c74',tree:'#1f4258',treeDark:'#142c3e',bird:'#ffffff',birdShade:'#9fc0d6',ink:'#f0f7fb',paper:'#08111a',sun:'#eaf6ff'},
 {name:'星核',en:'CORE',caption:'越靠近中心，光越密',sky:'#1a1626',horizon:'#453a54',fog:'#241f36',ground:'#191627',fields:['#1c1929','#201c2e','#191624','#231f33','#1b1828','#1f1b2c'],water:'#55486a',bank:'#332b48',roof:'#3b3050',wall:'#5c4c6e',tree:'#57466e',treeDark:'#35294a',bird:'#fff6e4',birdShade:'#c0a892',ink:'#f5ecda',paper:'#131020',sun:'#ffd79a'},
 {name:'深渊',en:'ABYSS',caption:'有些地方，连光都要绕道走',sky:'#04070c',horizon:'#0a121c',fog:'#070c13',ground:'#05090f',fields:['#06090f','#080c13','#05080d','#0a0e16','#070a11','#090d14'],water:'#0e1a26',bank:'#0a121b',roof:'#0c141d',wall:'#16222e',tree:'#0b1520',treeDark:'#060c14',bird:'#dce8f4',birdShade:'#7d93a8',ink:'#cfdae6',paper:'#03060a',sun:'#ffb27a'}
];
""")

# ------------------------------------------------------- region + weights --
cut("const pureStyles=", "let W=0,H=0,DPR=1,rotated=false;", """const pureStyles=styles.map((p,i)=>({...p,a:mod(i-1,5),b:i,t:1,index:i,void:i===4?1:0,core:i===3?1:0,shimmer:i===2?1:0,wash:i===1?1:0,front:0}));
function region(x,z){
 // An irregular, 3700-unit front between two regions; crossing it is never a palette cut.
 const warped=z+430*Math.sin(x*.0027+Math.sin(z*.00014)*1.4)+185*Math.sin(x*.0084+z*.00027);
 const boundary=Math.floor((warped+1850)/SEGMENT), a=mod(boundary-1,5), b=mod(boundary,5);
 const t=smoother((warped-boundary*SEGMENT+1850)/3700);if(t===0)return pureStyles[a];if(t===1)return pureStyles[b];const A=styles[a],B=styles[b];
 const p={a,b,t,index:t<.5?a:b,void:(a===4?1-t:0)+(b===4?t:0),core:(a===3?1-t:0)+(b===3?t:0),shimmer:(a===2?1-t:0)+(b===2?t:0),wash:(a===1?1-t:0)+(b===1?t:0)};
 for(const k of colorKeys)p[k]=blend(A[k],B[k],t);
 p.fields=A.fields.map((v,i)=>blend(v,B.fields[i],t));
 p.front=Math.sin(Math.PI*t)*((a===4||b===4)?1:.38);
 return p;
}
""")

# ---------------------------------------------------- haze + a bloom sprite --
rep('function haze(c,d,p=currentPalette){const h=smooth((d-1050)/(p.mist>0?6200:9100))*(.79+p.mist*.15);return blend(c,p.fog,h);}',
    'function haze(c,d,p=currentPalette){const h=smooth((d-2000)/(p.wash>0?9000:15000))*(.70+p.wash*.24);return blend(c,p.fog,h);}')

rep('   else{ctx.beginPath();ctx.ellipse(x,y,s,o.kind===\'smoke\'?s*.75:s,0,0,TAU);ctx.fill();}\n  }\n }',
    '   else{ctx.beginPath();ctx.ellipse(x,y,s,o.kind===\'smoke\'?s*.75:s,0,0,TAU);ctx.fill();}\n  }\n'
    '  else if(o.type===3){const g=ctx.createRadialGradient(o.p[0],o.p[1],0,o.p[0],o.p[1],o.s*o.spread);'
    'g.addColorStop(0,css(o.c,.95));g.addColorStop(.28,css(o.c,.40));g.addColorStop(.62,css(o.c,.11));g.addColorStop(1,css(o.c,0));'
    'ctx.fillStyle=g;ctx.fillRect(o.p[0]-o.s*o.spread,o.p[1]-o.s*o.spread,o.s*o.spread*2,o.s*o.spread*2);}\n }')
rep("  else{\n   const [x,y]=o.p,s=o.s;", "  else if(o.type===2){\n   const [x,y]=o.p,s=o.s;")
rep("function sprite(world,size,c,kind,alpha=1,rotation=0){",
    "/* A soft radial bloom that takes part in the depth sort, so a glow can sit\n"
    " * behind the nearer shards instead of over everything. No 60px sprite clamp. */\n"
    "function glow(world,size,c,alpha=1,spread=3){const p=project(world);if(!p)return;queue.push({type:3,p,d:p[2],s:clamp(size*p[3],1,Math.max(W,H)*.7),c,alpha,spread});}\n"
    "function sprite(world,size,c,kind,alpha=1,rotation=0){")

# ------------------------------------------------- field() replaces terrain --
cut("function groundEllipse(", "const chunks=new Map(),CHUNK=1040;", """/* The sheet of paper the cosmos is printed on, a faint lattice of printed
 * hatching, and the dust lane the cranes follow. The sheet carries its own
 * compositing passes and fades as the camera tilts up, so looking into deep
 * space never puts an opaque floor in front of the stars. */
function hatchCorner(ix,iz){return [ix*900+58*Math.sin(iz*.33+ix*.21),iz*940+44*Math.sin(ix*.36+iz*.17)];}
function lanePoint(z,offset,y=.6){const d=laneD(z),n=1/Math.hypot(1,d);return [laneX(z)+offset*n,y,z-offset*d*n];}
function deepfield(){
 const sheet=smooth(clamp(-camera.forward[1]*6));
 if(sheet>.004)poly(flatQuad(camera.eye[0]-100000,camera.eye[2]-100000,camera.eye[0]+100000,camera.eye[2]+100000,-2),currentPalette.fog,{noFog:true,alpha:sheet});
 flush();
 const ix0=Math.floor(camera.eye[0]/900),iz0=Math.floor(camera.eye[2]/940),range=lowQuality?9:12;
 for(let iz=iz0-range;iz<=iz0+range;iz++)for(let ix=ix0-range;ix<=ix0+range;ix++){
  const x=ix*900+450,z=iz*940+470,pj=project([x,0,z]);
  if(!pj||pj[2]>12000||pj[0]<-800||pj[0]>W+800||pj[1]<-700||pj[1]>H+700)continue;
  const p=region(x,z),id=Math.floor(hash(ix,iz,21)*6),c=p.fields[id];
  const corners=[[ix,iz],[ix+1,iz],[ix+1,iz+1],[ix,iz+1]].map(v=>hatchCorner(...v));
  const v=corners.map(a=>[a[0],0,a[1]]);
  poly(v,c,{palette:p,alpha:sheet*(.30+p.core*.34)});
  if(pj[2]<6000&&hash(ix,iz,23)>.42){
   const count=hash(ix,iz,24)>.48?7:4;
   for(let n=1;n<count;n++){
    const f=n/count,g=f+.018,across=hash(ix,iz,25)>.5;
    const a=across?[v[0],v[3]]:[v[0],v[1]],b=across?[v[1],v[2]]:[v[3],v[2]];
    const lerp3=(aa,bb,t)=>aa.map((q,i)=>mix(q,bb[i],t));
    poly([lerp3(a[0],a[1],f),lerp3(b[0],b[1],f),lerp3(b[0],b[1],g),lerp3(a[0],a[1],g)],shade(c,1.14),{palette:p,alpha:sheet*.34});
   }
  }
  if(pj[2]<5600&&hash(ix,iz,31)>.86)line([v[0].map((a,i)=>i===1?1:a),v[1].map((a,i)=>i===1?1:a)],p.treeDark,.14,.6);
 }
 flush();
 const zmin=Math.floor((camera.eye[2]-14000)/170)*170,zmax=camera.eye[2]+14000;
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),w0=laneW(z),w1=laneW(z+170);
  poly([lanePoint(z,-w0-26,.2),lanePoint(z,w0+26,.2),lanePoint(z+170,w1+26,.2),lanePoint(z+170,-w1-26,.2)],p.bank,{palette:p,alpha:.62});
 }
 flush();
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),w0=laneW(z)*.72,w1=laneW(z+170)*.72;
  poly([lanePoint(z,-w0,.6),lanePoint(z,w0,.6),lanePoint(z+170,w1,.6),lanePoint(z+170,-w1,.6)],p.water,{palette:p,alpha:.72});
 }
 flush();
 // Young stars still embedded in the lane, drawn as short printed strokes.
 for(let z=zmin;z<zmax;z+=170){
  const p=region(laneX(z),z),pj=project([laneX(z),0,z]);if(!pj||pj[2]>7000||pj[0]<-300||pj[0]>W+300||pj[1]<-200||pj[1]>H+200)continue;
  const w=laneW(z);
  for(let n=0;n<3;n++){
   const k=Math.floor(z/170),offset=(hash(k,n,61)-.5)*w*1.5+Math.sin(time*.2+k)*8;
   const st=z+hash(k,n,63)*85+mod(time*3+hash(k,n,64)*23,28),length=22+hash(k,n,65)*68;
   line([lanePoint(st,offset,1),lanePoint(st+length,offset+5,1)],blend(p.water,p.paper,.62),(.18+.13*Math.sin(time*.31+n+k)**2)*(.35+p.shimmer*.65),clamp(pj[3]*1.6,.45,1.5));
  }
 }
 flush();
 // A broad bloom where the lane runs brightest, never a drawn disk.
 const light=currentPalette.front*.15+currentPalette.shimmer*.075;
 if(light>.005){
  const center=project([laneX(travel+1500)+750,1,travel+1500]);
  if(center){const pts=[];for(let i=0;i<28;i++){const a=i/28*TAU;pts.push([laneX(travel+1500)+750+Math.cos(a)*1200,1,travel+1500+Math.sin(a)*1200]);}const mask=clipped(pts);if(mask){ctx.save();ctx.beginPath();mask.p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.clip();const r=clamp(1100*center[3],40,W),g=ctx.createRadialGradient(center[0],center[1],0,center[0],center[1],r);g.addColorStop(0,css(currentPalette.sun,light));g.addColorStop(1,css(currentPalette.sun,0));ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.restore();}}
 }
}
""")

# ----------------------------------------------------- chunk(): the bodies --
cut("const chunks=new Map(),CHUNK=1040;", "function local(h,a,y,b){", """const chunks=new Map(),CHUNK=3200;
/* Space is sparse and large: one chunk of sky holds a few masses, a scatter of
 * torn paper, and a couple of pages from a printed atlas. */
function chunk(k){
 if(chunks.has(k))return chunks.get(k);
 const r=rng((hash(k,71)*4294967295)>>>0),z0=k*CHUNK,masses=[],shards=[],plates=[];
 const zc=z0+CHUNK*.5,pc=region(laneX(zc),zc);
 for(let i=0,n=1+Math.floor(r()*3);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=560+r()*1700,roll=r();
  let kind=roll<.34?0:roll<.62?1:roll<.84?2:roll<.95?3:4;
  if(r()<.05+pc.void*.42)kind=4;
  masses.push({x:laneX(z)+side*off,y:150+r()*520,z,kind,r:[150,205,270,340,420][kind],axis:[r()-.5,r()-.5,r()-.5],phase:r()*TAU});
 }
 for(let i=0,n=7+Math.floor(r()*8);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=180+r()*1500;
  shards.push({x:laneX(z)+side*off,y:60+r()*760,z,w:34+r()*62,h:22+r()*44,ang:r()*TAU,tilt:(r()-.5)*1.1,spin:(r()-.5)*.5,tone:r()});
 }
 for(let i=0,n=2+Math.floor(r()*4);i<n;i++){
  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=420+r()*1900;
  plates.push({x:laneX(z)+side*off,y:120+r()*620,z,w:150+r()*190,h:110+r()*140,ang:r()*TAU,tilt:(r()-.5)*.8,spin:(r()-.5)*.32,tone:r()});
 }
 const c={masses,shards,plates,k};chunks.set(k,c);return c;
}
""")

# ------------------------------------ bodies() replaces houses/trees/bridges --
cut("function drawHouse(", "function structures(){", """/* A torn shard: two facets of the same scrap of paper, tumbling. */
function shardShape(s,t,out){
 const a=s.ang+t*s.spin,cs=Math.cos(a),sn=Math.sin(a),ct=Math.cos(s.tilt),st=Math.sin(s.tilt);
 const u=[cs,0,sn],v=[-sn*st,ct,cs*st],rad=[1,.58,.92,.66];
 for(let i=0;i<4;i++){const ang=i/4*TAU+s.tone*2.6,r0=rad[i];
  out[i]=[s.x+(u[0]*Math.cos(ang)+v[0]*Math.sin(ang))*s.w*r0,
          s.y+(u[1]*Math.cos(ang)+v[1]*Math.sin(ang))*s.h*r0,
          s.z+(u[2]*Math.cos(ang)+v[2]*Math.sin(ang))*s.w*r0];}
}
function drawShard(s,p,t){
 const q=[null,null,null,null];shardShape(s,t,q);
 poly(q,blend(p.wall,p.paper,.12),{palette:p,alpha:.94});
 const mid=q.map((v,i)=>v.map((c,j)=>(c+q[(i+2)%4][j])*.5));
 poly([q[0],q[1],mid[1],mid[0]],shade(blend(p.roof,p.paper,.1),.92),{palette:p,alpha:.9});
 line([q[0],q[2]],shade(p.roof,.78),.5,.55);
}
/* A page from a printed atlas, adrift: a flat plate with paper thickness. */
function drawPlate(pl,p,t){
 const a=pl.ang+t*pl.spin,cs=Math.cos(a),sn=Math.sin(a),ct=Math.cos(pl.tilt),st=Math.sin(pl.tilt);
 const u=[cs,0,sn],v=[-sn*st,ct,cs*st];
 const o=[pl.x,pl.y,pl.z],at=(da,db,dy)=>[o[0]+u[0]*da+v[0]*db,o[1]+u[1]*da+v[1]*db+dy,o[2]+u[2]*da+v[2]*db];
 poly([at(-pl.w*.5,-pl.h*.5,0),at(pl.w*.5,-pl.h*.5,0),at(pl.w*.5,pl.h*.5,0),at(-pl.w*.5,pl.h*.5,0)],blend(p.paper,p.wall,.18),{palette:p,alpha:.9});
 poly([at(-pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,-3),at(pl.w*.5,-pl.h*.5,0),at(-pl.w*.5,-pl.h*.5,0)],shade(p.wall,.8),{palette:p,alpha:.85});
 // The engraved lines that make it a plate rather than a billboard.
 for(let i=1;i<6;i++){
  const f=-pl.h*.5+pl.h*i/6;
  line([at(-pl.w*.44,f,0),at(pl.w*(.10+.30*hash(Math.round(pl.x),i,77)),f,0)],shade(p.treeDark,.9),.24,.5);
 }
}
/* A mass: a dead star drawn as a printed asterisk inside a bloom, or the ink
 * well itself — an opaque disc that takes part in the depth sort. */
function drawMass(m,p,t){
 if(m.kind===4){
  const pts=[];for(let i=0;i<36;i++){const a=i/36*TAU;pts.push([m.x+Math.cos(a)*m.r,m.y+Math.sin(a)*m.r,m.z]);}
  glow([m.x,m.y,m.z],m.r*1.35,blend(p.sun,p.paper,.30),.26,3.6);
  poly(pts,[7,9,13],{noFog:true,alpha:1});
  const ring=[];for(let i=0;i<=44;i++){const a=i/44*TAU,rr=m.r*(1.22+.10*Math.sin(a*3+t*.5+m.phase));ring.push([m.x+Math.cos(a)*rr,m.y+Math.sin(a)*rr,m.z]);}
  line(ring,blend(p.sun,[255,246,228],.55),.62,1.2);
  return;
 }
 const tint=m.kind===0?blend(p.sun,p.paper,.30):m.kind===1?p.sun:m.kind===2?blend(p.sun,[255,214,170],.45):blend(p.sun,[196,214,255],.5);
 glow([m.x,m.y,m.z],m.r*.55,tint,.62,3.0);
 sprite([m.x,m.y,m.z],m.r*.34,blend(tint,[255,255,255],.5),'snow',.92);
}
function bodies(){
 const k0=Math.floor(camera.eye[2]/CHUNK),radius=lowQuality?7:9,active=[];
 for(let k=k0-radius;k<=k0+radius;k++)active.push(chunk(k));
 for(const [k] of chunks)if(Math.abs(k-k0)>radius+2)chunks.delete(k);
 for(const c of active){
  for(const s of c.shards){const pj=project([s.x,s.y,s.z]);if(!pj||pj[2]>9000||pj[0]<-160||pj[0]>W+160||pj[1]<-160||pj[1]>H+160)continue;drawShard(s,region(s.x,s.z),time);}
  for(const pl of c.plates){const pj=project([pl.x,pl.y,pl.z]);if(!pj||pj[2]>12000||pj[0]<-260||pj[0]>W+260||pj[1]<-260||pj[1]>H+260)continue;drawPlate(pl,region(pl.x,pl.z),time);}
  for(const m of c.masses){const pj=project([m.x,m.y,m.z]);if(!pj||pj[2]>18000)continue;drawMass(m,region(m.x,m.z),time);}
 }
 flush();
}
""")

cut("function structures(){", "/* Every bird owns its spring", "")

# ------------------------------------------- particles, sky, paper, shadows --
rep("p.x+=(p.drift+wind.x*29+Math.sin(time*.4+p.phase)*5)*dt;p.z+=Math.cos(p.phase)*7*dt;p.y-=(3+pal.snow*15)*dt;}",
    "p.x+=(p.drift+wind.x*29+Math.sin(time*.4+p.phase)*5)*dt;p.z+=Math.cos(p.phase)*7*dt;p.y-=(3+pal.wash*15)*dt;}")

rep("const pal=climate(p.x,p.z),alpha=smooth(p.life/3)*smooth((p.ttl-p.life)/5),q=[p.x+Math.sin(time*.8+p.phase)*6,p.y*(1-pal.night*.68),p.z];\n"
    "  const snow=pal.snow,petal=pal.dusk,fire=pal.night,dust=clamp(1-snow-petal-fire);\n"
    "  if(dust>.02)sprite(q,p.size*.54,blend(pal.paper,pal.sun,.16),'dust',alpha*dust*.47);\n"
    "  if(snow>.02)sprite(q,p.size,pal.paper,'snow',alpha*snow*.77,time*.35+p.phase);\n"
    "  if(petal>.02)sprite(q,p.size*1.08,blend([212,152,143],pal.paper,.36),'petal',alpha*petal*.7,time*.6+p.phase);\n"
    "  if(fire>.02)sprite(q,p.size*.48,[225,237,161],'firefly',alpha*fire*(.38+.48*Math.sin(time*1.6+p.phase)**2));",
    "const pal=region(p.x,p.z),alpha=smooth(p.life/3)*smooth((p.ttl-p.life)/5),q=[p.x+Math.sin(time*.8+p.phase)*6,p.y*(1-pal.void*.68),p.z];\n"
    "  const cr=pal.core,sh=pal.shimmer,vd=pal.void,dust=clamp(1-cr-sh,.02,1);\n"
    "  if(dust>.02)sprite(q,p.size*.54,blend(pal.paper,pal.sun,.16),'dust',alpha*dust*.47);\n"
    "  if(cr>.02)sprite(q,p.size*1.05,pal.paper,'snow',alpha*cr*.72,time*.35+p.phase);\n"
    "  if(sh>.02)sprite(q,p.size*.86,blend([226,238,248],pal.paper,.30),'petal',alpha*sh*.66,time*.6+p.phase);\n"
    "  if(vd>.02)sprite(q,p.size*.48,[214,226,240],'firefly',alpha*vd*(.38+.48*Math.sin(time*1.6+p.phase)**2));")

rep("poly(pts,p.treeDark,{alpha:.11*(1-p.night*.71)});", "poly(pts,p.treeDark,{alpha:.11*(1-p.void*.71)});")
rep("v.addColorStop(1,css(currentPalette.ink,currentPalette.night>.5?.075:.043));",
    "v.addColorStop(1,css(currentPalette.ink,currentPalette.void>.5?.075:.043));")

# --------------------------------------------------------------- the loop --
rep("drawSky();terrain();drawBirdShadows();structures();drawBirds();drawParticles();flush();paperFinish();",
    "drawSky();deepfield();drawBirdShadows();bodies();drawBirds();drawParticles();flush();paperFinish();")

# ------------------------------------------------ identifier renames (last) --
for old, new in [('riverPoint', 'lanePoint'), ('riverX', 'laneX'), ('riverD', 'laneD'),
                 ('riverW', 'laneW'), ('flightY', 'courseY')]:
    n = s.count(old)
    s = s.replace(old, new)
    print(f'  rename {old} -> {new}: {n}')

import re
for old, new in [(r'\briver\b', 'lane'), (r'\bclimate\b', 'region')]:
    s, n = re.subn(old, new, s)
    print(f'  rename {old} -> {new}: {n}')

open(PATH, 'w', encoding='utf-8', newline='').write(s)
print(f"wrote {PATH}: {before/1024/1024:.2f} -> {len(s)/1024/1024:.2f} MB")
