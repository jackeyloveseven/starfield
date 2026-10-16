"""R3 + R4: folded-paper craft instead of cranes, and spiral galaxies.

The user's read: cranes in space do not say "starfield", and 200 torn-paper
scraps read as litter rather than as a galaxy. The material identity (paper,
ink, print) is kept - the craft are folded paper, the galaxies are printed
plates - so this is a change of silhouette and of background, not of world.
"""
import re
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:110]))
    s = s.replace(a, b, n)


# ---- R4a: far fewer scraps; a galaxy becomes the background ---------------
rep(" for(let i=0,n=7+Math.floor(r()*8);i<n;i++){\n"
    "  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=180+r()*1500;",
    " for(let i=0,n=1+Math.floor(r()*2);i<n;i++){\n"
    "  const z=z0+r()*CHUNK,side=r()>.5?1:-1,off=900+r()*2200;")
rep(" const c={masses,shards,plates,k};chunks.set(k,c);return c;",
    " const galaxies=[];\n"
    " for(let i=0,n=r()<.35?1:0;i<n;i++){\n"
    "  const z=z0+r()*CHUNK,side=r()>.5?1:-1;\n"
    "  galaxies.push({x:laneX(z)+side*(2500+r()*3500),y:200+r()*1400,z,\n"
    "   rad:900+r()*1300,arms:3+Math.floor(r()*3),ang:r()*TAU,tilt:(r()-.5)*.9,tone:r()});\n"
    " }\n"
    " const c={masses,shards,plates,galaxies,k};chunks.set(k,c);return c;")

# ---- R4b: the galaxy, drawn as a printed plate ---------------------------
rep("function bodies(){",
    """/* A spiral galaxy as a printed plate: a bloom for the core, engraved strokes
 * for the arms, and a dust lane laid across the disc. */
function drawGalaxy(g,p,t){
 const q=project([g.x,g.y,g.z]);if(!q)return;
 if(g.rad*q[3]<10)return;
 glow([g.x,g.y,g.z],g.rad*.32,blend(p.sun,[255,255,255],.35),.50,3.4);
 const u=[Math.cos(g.ang),0,Math.sin(g.ang)],ct=Math.cos(g.tilt),st=Math.sin(g.tilt);
 const v=[-Math.sin(g.ang)*ct,st,Math.cos(g.ang)*ct];
 const at=(a,b)=>[g.x+u[0]*a+v[0]*b,g.y+u[1]*a+v[1]*b,g.z+u[2]*a+v[2]*b];
 const ink=blend(p.craft,p.tree,.42),dim=blend(p.tree,p.paper,.35);
 for(let k=0;k<g.arms;k++){
  const pts=[],off0=k/g.arms*TAU+g.tone*2;
  for(let i=0;i<=16;i++){
   const f=i/16,th=off0+f*2.9,r=g.rad*(.10+.90*f);
   pts.push(at(Math.cos(th)*r,Math.sin(th)*r));
  }
  line(pts,ink,.30,.85);
  line(pts.slice(2),dim,.16,.55);
 }
 // the dust lane, laid across the near side of the disc
 const dust=[];
 for(let i=0;i<=12;i++){const a=(i/12-.5)*2.2,r=g.rad*.86;dust.push(at(Math.cos(a)*r,Math.sin(a)*r*.30));}
 line(dust,shade(p.treeDark,.82),.34,2.0);
}
function bodies(){""")
rep("  for(const m of c.masses){const pj=project([m.x,m.y,m.z]);if(!pj||pj[2]>18000)continue;drawMass(m,region(m.x,m.z),time);}",
    "  for(const g of c.galaxies){const pj=project([g.x,g.y,g.z]);if(!pj||pj[2]>26000)continue;drawGalaxy(g,region(g.x,g.z),time);}\n"
    "  for(const m of c.masses){const pj=project([m.x,m.y,m.z]);if(!pj||pj[2]>18000)continue;drawMass(m,region(m.x,m.z),time);}")

# ---- R4c: more ink washes, culled to their centres -----------------------
rep("const nebulae=Array.from({length:coarse?14:24},", "const nebulae=Array.from({length:coarse?20:34},")
rep("const rad=n.size*camera.focal,pad=rad*.18;", "const rad=n.size*camera.focal,pad=0;")

# ---- R3: cranes -> folded-paper craft ------------------------------------
rep("  const v={beak:[0,1,27],head:[0,6,18],hl:[-3.7,1.8,17],hr:[3.7,1.8,17],neck:[0,2,10],"
    "front:[0,3,7],left:[-5,1,3],right:[5,1,3],keel:[0,-6,-5],back:[0,1,-15],tail:[0,-1,-25],"
    "tl:[-7,1,-28],tr:[7,1,-28],le:[-17,flap*11+3,-2],re:[17,flap*11+3,-2],"
    "lt:[-36,flap*22,-13],rt:[36,flap*22,-13],lb:[-12,0,-16],rb:[12,0,-16]};",
    "  const v={nose:[0,0,30],spineTop:[0,5,7],spineBack:[0,4,-13],tail:[0,-1,-27],\n"
    "   wrl:[-9,1,4],wrr:[9,1,4],wtl:[-34,0,-14],wtr:[34,0,-14],\n"
    "   belly:[0,-5,3],keelF:[0,-3,15],keelB:[0,-3,-11],\n"
    "   fl:[-21,flap*7,-5],fr:[21,flap*7,-5],\n"
    "   finl:[-5,8,-22],finr:[5,8,-22],hl:[-13,0,-19],hr:[13,0,-19]};")
rep("  const base=p.bird,fold=blend(p.bird,p.birdShade,.60),edge=blend(p.bird,p.birdShade,.83);\n"
    "  const tri=(a,b,c,col)=>poly([world[a],world[b],world[c]],col);\n"
    "  tri('front','left','keel',fold);tri('front','keel','right',shade(base,.99));"
    "tri('keel','left','back',edge);tri('keel','back','right',fold);\n"
    "  tri('left','le','lt',shade(base,1.02));tri('left','lt','lb',fold);tri('left','lb','back',shade(base,.97));\n"
    "  tri('right','rt','re',shade(base,1.04));tri('right','rb','rt',blend(base,fold,.44));"
    "tri('right','back','rb',shade(base,.98));\n"
    "  tri('back','tl','tail',fold);tri('back','tail','tr',base);tri('front','neck','hl',fold);"
    "tri('front','hr','neck',base);\n"
    "  tri('hl','head','beak',base);tri('head','hr','beak',shade(base,1.05));tri('hl','beak','hr',fold);\n"
    "  const pp=project(pos);if(pp&&pp[3]>.4){line([world.front,world.back],p.birdShade,.30,.5);"
    "line([world.left,world.lt],p.birdShade,.23,.45);}",
    "  const lead=b===fleet[LEAD];\n"
    "  const base=p.craft,fold=lead?blend([178,58,44],p.craft,.22):blend(p.craft,p.craftShade,.60),"
    "edge=blend(p.craft,p.craftShade,.83);\n"
    "  const tri=(a,b,c,col)=>poly([world[a],world[b],world[c]],col);\n"
    "  // Upper surface split by the spine ridge, underside folded under it.\n"
    "  tri('nose','spineTop','wrl',base);tri('spineTop','spineBack','wrl',fold);tri('spineBack','wtl','wrl',edge);\n"
    "  tri('nose','wrr','spineTop',shade(base,.98));tri('spineTop','wrr','spineBack',fold);"
    "tri('spineBack','wrr','wtr',edge);\n"
    "  tri('nose','keelF','belly',shade(base,.94));tri('keelF','keelB','belly',shade(base,.88));\n"
    "  tri('keelB','wrl','belly',shade(base,.90));tri('keelB','belly','wrr',shade(base,.92));\n"
    "  tri('wtl','fl','wrl',shade(base,.96));tri('wtr','wrr','fr',shade(base,.96));\n"
    "  tri('spineBack','finl','tail',fold);tri('spineBack','tail','finr',base);\n"
    "  tri('tail','hl','finl',edge);tri('tail','finr','hr',edge);\n"
    "  tri('nose','belly','wrl',shade(base,.86));tri('nose','wrr','belly',shade(base,.86));\n"
    "  const pp=project(pos);if(pp&&pp[3]>.4){line([world.nose,world.tail],p.craftShade,.30,.5);"
    "line([world.wtl,world.wtr],p.craftShade,.23,.45);}")

# ---- identifiers: a fleet, not a flock -----------------------------------
for a, b in [('BIRD_COUNT', 'FLEET_COUNT'), ('drawBirdShadows', 'drawCraftShadows'),
             ('drawBirds', 'drawFleet'), ('birdWorld', 'craftWorld'),
             ('birdTransform', 'craftTransform'), ('birdShade', 'craftShade')]:
    n = s.count(a)
    s = s.replace(a, b)
    print(f'  {a} -> {b}: {n}')
s, n = re.subn(r'\bbirds\b', 'fleet', s)
print(f'  birds -> fleet: {n}')
s, n = re.subn(r'\bbird\b', 'craft', s)
print(f'  bird -> craft: {n}')

# the lead craft, and copy that no longer says WINGS
rep("fleet[2].bold=2.45;", "fleet[LEAD].bold=2.45;fleet[LEAD].scale=1.5;")
for a, b in [('30 WINGS. &nbsp; ONE OPEN SKY.', '30 CRAFT. &nbsp; ONE OPEN SKY.'),
             ('22 WINGS.  ONE OPEN SKY.', '22 CRAFT.  ONE OPEN SKY.'),
             ('/ &nbsp; 30 WINGS', '/ &nbsp; 30 CRAFT'),
             ('aria-label="程序化星海、星云、陨石与纸鹤；移动鼠标或触摸屏幕来引导航向"',
              'aria-label="程序化星海、星云、陨石与折纸船队；移动鼠标或触摸屏幕来引导航向"')]:
    if s.count(a) >= 1:
        s = s.replace(a, b)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("R3 + R4 applied")
