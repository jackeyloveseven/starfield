"""V18n: rebuild the nebulae from the four reference photographs.

The user sent four emission-nebula photographs and a stylised reference scene,
and said the nebulae should be redone from them. Read against the old code, the
photographs share three things the old nebulae had none of:

  1. SATURATION. They are emission gas - a hot rim of red, gold or rose around a
     cooler blue or teal core. The old `tint` was blend(tree, water|sun|craft,
     .38) then 14% toward white: a muted navy-grey, and the same muted navy-grey
     in every region, which is why the sky read as one pale wash.
  2. STRUCTURE. The old texture was 34 uniform soft blobs under a broad radial
     mask whose first two stops were 1.00 and .82 - a plateau of alpha one, so
     every nebula printed as a flat disc. Here the gas is knots around a few
     nuclei plus ~130 accumulating filament strokes, and the mask falls off
     fast, so there is a body and a halo instead of a disc.
  3. DARK LANES. The old dust was 8 soft radial holes. Real dust occlusion has a
     HARD edge with a soft shoulder - that is what makes a nebula read as gas at
     all - so each lane is now a wide faint stroke under a narrow opaque one,
     and the lanes curve along the gas instead of radiating from the middle
     (radial spokes read as a starburst, not as dust).

Scale is the fourth change. `size` was .30...88 of the focal length, so a
nebula was routinely wider than the whole frame and the camera sat *inside* one:
a 192px texture blown up 10x is mush, which is most of why the sky read as a
featureless wash. Sizes are now .22...68 and there are 44 of them instead of 34,
so you meet several distinct nebulae instead of being submerged in one.

Two constraints held. It must not become a photograph: the lanes are cut with
`destination-out` (the sky and its stars show through the dust), the colour is a
single flat tint per pixel with three stops (no photographic gradients), and
paperFinish() lays the paper grain over the whole plate afterwards, nebulae
included. And the grade maps 210 to white, so every channel of every emission
colour is capped at 192 - brighter than that loses its hue to the bloom instead
of reading as colour.

The alpha ceiling in the wash loop drops from .86 to .78: at .86 the lane cuts
are buried under their own wash.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:150]))
    s = s.replace(a, b, n)


NEW = r"""/* Emission colours, one pair per region: [warm rim, cool core]. The reference
 * photographs are high-saturation emission nebulae, and the old single flat
 * tint could not say that - it was blend(tree, water|sun|craft, .38) pulled 14%
 * toward white, a muted navy-grey, and the same navy-grey in every region. Each
 * region now gets a warm rim and a cool core that sit inside its own palette
 * instead of fighting it. Every channel is capped at 192: the grade maps 210 to
 * white, so anything brighter loses its hue to the bloom rather than reading as
 * colour. */
const NEB_PAL=[
 [[186,88,94],[84,124,178]],   // 素纸 PAPER   rose over steel
 [[176,80,156],[90,100,192]],  // 墨海 INKWASH magenta over indigo
 [[192,146,62],[70,146,174]],  // 箔野 FOIL    gold over cyan
 [[192,128,78],[170,86,148]],  // 星核 CORE    amber over magenta
 [[170,60,58],[92,102,148]]    // 深渊 ABYSS   ember over slate
];
function nebulaTex(seed,idx){
 const pal=NEB_PAL[idx]||NEB_PAL[0];
 const key=seed+'|'+idx;
 if(nebCache.has(key))return nebCache.get(key);
 // 384 rather than 192: the camera can sit inside one of these, and a dust lane
 // that is meant to have a hard edge does not survive a 10x upscale. The blob
 // fills are clipped to their own bounding box, so the extra pixels are cheap.
 const N=384,c=document.createElement('canvas');c.width=c.height=N;
 const g=c.getContext('2d'),r=rng((SEED^Math.imul(seed,0x9e3779b1)^Math.imul(idx+1,0x85ebca6b))>>>0);
 const cx=N*.5,cy=N*.5;
 // Two or three nuclei near the middle; the blobs gather around them, so the
 // gas has knots and arms instead of being spread evenly over the square.
 const nn=2+(r()*2|0),nuc=[];
 for(let i=0;i<nn;i++){const a=r()*TAU,d=N*(.03+r()*.16);nuc.push([cx+Math.cos(a)*d,cy+Math.sin(a)*d]);}
 g.globalCompositeOperation='source-over';
 for(let i=0;i<44;i++){
  const k=nuc[i%nn],a=r()*TAU,d=N*(.02+r()*.30);
  const x=k[0]+Math.cos(a)*d,y=k[1]+Math.sin(a)*d,rad=N*(.05+r()*.17);
  const gr=g.createRadialGradient(x,y,0,x,y,rad);
  gr.addColorStop(0,`rgba(255,255,255,${(.24+r()*.56).toFixed(3)})`);
  gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;
  const bx=Math.max(0,x-rad),by=Math.max(0,y-rad);
  g.fillRect(bx,by,Math.min(N,x+rad)-bx,Math.min(N,y+rad)-by);
 }
 // Filaments. Short quadratic strokes accumulated under `lighter`, so the gas
 // goes to full alpha along ridges rather than as a plateau - this is the
 // structure the eye reads as "nebula" and the old flat wash never had. Half of
 // them run around the gas and half run out of it, which is what the reference
 // photographs do; all of them bow, because a straight stroke reads as a rule.
 g.globalCompositeOperation='lighter';g.lineCap='round';
 for(let i=0;i<130;i++){
  // Two thirds run AROUND the gas and one third runs out of it. Half and half
  // was tried first and the radial third was enough to read as a starburst -
  // an emission nebula has ridges, but it does not have rays.
  const around=i%3!==0,a0=r()*TAU;
  let a1,r0,r1;
  if(around){a1=a0+.5+r()*1.5;r0=N*(.05+r()*.30);r1=r0*(1+(r()-.5)*.24);}
  else{a1=a0+(r()-.5)*.55;r0=N*(.03+r()*.26);r1=r0+N*(.10+r()*.26);}
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  const nx=-(y1-y0),ny=x1-x0,nl=Math.hypot(nx,ny)||1,bow=(r()-.5)*N*(around?.05:.10);
  g.strokeStyle=`rgba(255,255,255,${(.08+r()*.30).toFixed(3)})`;
  g.lineWidth=N*(.003+r()*.011);
  g.beginPath();g.moveTo(x0,y0);
  g.quadraticCurveTo((x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1);g.stroke();
 }
 // Dark dust in front of the lit gas: a nebula reads as gas only when something
 // occludes it. Hard edge, soft shoulder - one wide faint stroke under one
 // narrow opaque stroke - because a soft radial hole reads as a smudge and an
 // even softness all over reads as nothing at all.
 g.globalCompositeOperation='destination-out';g.lineCap='round';
 const lane=(x0,y0,mx,my,x1,y1,w,a)=>{
  g.strokeStyle=`rgba(0,0,0,${(a*.55).toFixed(3)})`;g.lineWidth=w*3.1;
  g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
  g.strokeStyle=`rgba(0,0,0,${a.toFixed(3)})`;g.lineWidth=w;
  g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
 };
 // Arcs: they curve along the gas rather than pointing at its middle, which is
 // the difference between a dust lane and a starburst. (The radius is `rr`, not
 // `r`: `r` is the rng, and shadowing it in the same declaration list is a
 // temporal-dead-zone ReferenceError that kills every frame.)
 for(let i=0;i<8;i++){
  const a0=r()*TAU,a1=a0+1.0+r()*1.8,rr=N*(.14+r()*.30);
  const x0=cx+Math.cos(a0)*rr,y0=cy+Math.sin(a0)*rr;
  const x1=cx+Math.cos(a1)*rr,y1=cy+Math.sin(a1)*rr;
  const nx=-(y1-y0),ny=x1-x0,nl=Math.hypot(nx,ny)||1,bow=(r()<.5?-1:1)*N*(.08+r()*.14);
  lane(x0,y0,(x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1,N*(.008+r()*.020),.40+r()*.45);
 }
 // Fingers: the short opaque tongues that hang off the edge of the gas.
 for(let i=0;i<5;i++){
  const a0=r()*TAU,r0=N*(.05+r()*.18),a1=a0+(r()-.5)*1.0,r1=r0+N*(.14+r()*.22);
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.09,(y0+y1)*.5+(r()-.5)*N*.09,x1,y1,N*(.010+r()*.022),.50+r()*.42);
 }
 // Two lanes that cut right across the body. They bow hard, because a straight
 // bar across the gas reads as a rule laid on top of the picture.
 for(let i=0;i<2;i++){
  const a0=r()*TAU,a1=a0+Math.PI+(r()-.5)*.7,r0=N*(.28+r()*.18),r1=N*(.28+r()*.18);
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.22,(y0+y1)*.5+(r()-.5)*N*.22,x1,y1,N*(.010+r()*.024),.45+r()*.40);
 }
 g.globalCompositeOperation='source-over';
 // The old mask was 1.00 at the centre and .82 at half the radius: a plateau of
 // alpha one under a soft edge, which is why every nebula printed as a flat
 // pale disc. This falls away fast, so the gas has a body and a halo.
 g.globalCompositeOperation='destination-in';
 const m=g.createRadialGradient(cx,cy,0,cx,cy,N*.5);
 m.addColorStop(0,'rgba(0,0,0,1)');m.addColorStop(.26,'rgba(0,0,0,.92)');
 m.addColorStop(.52,'rgba(0,0,0,.50)');m.addColorStop(.78,'rgba(0,0,0,.14)');
 m.addColorStop(1,'rgba(0,0,0,0)');
 g.fillStyle=m;g.fillRect(0,0,N,N);
 // Two-tone: a cool core inside a warm rim, or the reverse by seed, so the
 // same region does not print six identical nebulae. A single flat fill here
 // is what made them all look alike.
 const A=seed%2?pal[0]:pal[1],B=seed%2?pal[1]:pal[0];
 g.globalCompositeOperation='source-in';
 const cg=g.createRadialGradient(cx,cy,0,cx,cy,N*.5);
 cg.addColorStop(0,css(A));cg.addColorStop(.46,css(blend(A,B,.55)));cg.addColorStop(1,css(B));
 g.fillStyle=cg;g.fillRect(0,0,N,N);
 g.globalCompositeOperation='source-over';
 if(nebCache.size>40)nebCache.clear();
 nebCache.set(key,c);nebGens++;return c;
}"""

START = "function nebulaTex(seed,idx){"
END = "\n}\nfunction skyPoint(v){"
if s.count(START) != 1 or s.count(END) != 1:
    sys.exit("nebulaTex anchors: start=%d end=%d" % (s.count(START), s.count(END)))
i, j = s.find(START), s.find(END)
old = s[i:j + 2]
# Refuse to replace anything but the function we read: the flat tint, the blob
# loop and the soft radial dust are all in the old body and none of them are in
# the new one.
for probe in ("const tint=blend(blend(st.tree,alt,.38),[255,255,255],.14)",
              "for(let i=0;i<34;i++){",
              "m.addColorStop(.5,'rgba(0,0,0,.82)')",
              "for(let i=0;i<8;i++){"):
    if probe not in old:
        sys.exit("unexpected nebulaTex body, missing: %s" % probe)
s = s[:i] + NEW + s[j + 2:]

# ---- the nebulae get smaller, and there are more of them ----
rep("""const nebulae=Array.from({length:coarse?20:34},(_,i)=>{
 const a=hash(i,210)*TAU,y=hash(i,211)*2-1,r=Math.sqrt(Math.max(0,1-y*y));
 return {x:Math.cos(a)*r,y,z:Math.sin(a)*r,size:.30+hash(i,212)*.58,seed:1+Math.floor(hash(i,213)*6),rot:hash(i,214)*TAU,alpha:.17+hash(i,215)*.38};
});""",
    """const nebulae=Array.from({length:coarse?26:44},(_,i)=>{
 const a=hash(i,210)*TAU,y=hash(i,211)*2-1,r=Math.sqrt(Math.max(0,1-y*y));
 // Was .30...88 of the focal length: a nebula was routinely wider than the whole
 // frame, so the camera sat inside one and read a 192px texture blown up ten
 // times - a wash with no structure in it, however good the texture. .22...68
 // and six more of them, so you meet distinct nebulae instead of one flood.
 return {x:Math.cos(a)*r,y,z:Math.sin(a)*r,size:.22+hash(i,212)*.46,seed:1+Math.floor(hash(i,213)*6),rot:hash(i,214)*TAU,alpha:.17+hash(i,215)*.38};
});""")

rep("   const al=clamp(n.alpha*wash,0,.86);",
    "   // .86 buried the lane cuts under their own wash; the dust and the stars\n"
    "   // behind it only read below about .78.\n"
    "   const al=clamp(n.alpha*wash,0,.78);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V18n applied:", len(s), "chars")
