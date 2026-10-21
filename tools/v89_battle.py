"""V89: a battle that is still happening.

The piece already has wreck fields around the gates - the aftermath. The
request was to pass a war, not its remains: two lines of hulls trading slow
fire across the lane, every 53rd chunk.

The hulls go into the existing ships array, so they are drawn, faded, culled and
depth-sorted by the code that already does that. Only the beams need new
drawing: thin paper-white lines that fire in short bursts, with a muzzle glow at
each end. Both ends are fixed points, the pulse is a function of time, so
nothing has to be stepped.

The battle rolls its own rng: inserting draws into chunk()'s stream would
reshuffle every world and event after it, and this version has to stay
comparable to the last one.

Run:  python -I v89_battle.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)


OLD = """ // Deal random space events along the flight lane
 if(!horizon && !hasEncounter && k > 1 && (k % 4 === 2 || k % 4 === 0)){"""
NEW = """ // A battle still in progress: two lines of hulls trading slow fire across
 // the lane. The wrecks at the gates are the aftermath; this is the thing.
 // Its own rng, so the rest of the chunk's stream - worlds, events - is
 // exactly what it was before this existed.
 if(k > 1 && ((k % 37) + 37) % 37 === 23){
  const rb = rng((hash(k, 911) * 4294967295) >>> 0);
  const bz = z0 + CHUNK * (.32 + rb() * .34), bx = laneX(bz), by = courseY(bz);
  const craft = [], fire = [];
  for(let side = -1; side <= 1; side += 2) for(let i = 0; i < 5; i++){
   const s = {x: bx + side * (900 + rb() * 1500), y: by + (rb() - .5) * 1100,
    z: bz + (rb() - .5) * 2400, len: 360 + rb() * 600,
    roll: (side > 0 ? 0 : Math.PI) + (rb() - .5) * .25,
    ph: rb() * TAU, drift: .15 + rb() * .35, hull: rb(), lights: rb()};
   ships.push(s); craft.push(s);
  }
  for(let i = 0; i < 9; i++){
   const A = craft[i % 5], B = craft[5 + (i * 3 + 1) % 5];
   fire.push({x0: A.x, y0: A.y, z0: A.z, x1: B.x, y1: B.y, z1: B.z,
    period: 1.4 + rb() * 2.6, phase: rb() * TAU});
  }
  // Flak: paper bursts between the lines. A bolt is a scratch at 8,000
  // units; a burst is a flower, and it reads at any range.
  const bursts=[];
  for(let i=0;i<4;i++)bursts.push({x:bx+(rb()-.5)*4200,y:by+(rb()-.5)*1600,
    z:bz+(rb()-.5)*2600,period:1.8+rb()*3.2,phase:rb()*TAU,size:70+rb()*90});
  battles.push({x: bx, y: by, z: bz, fire, bursts});
 }
 // Deal random space events along the flight lane
 if(!horizon && !hasEncounter && k > 1 && (k % 4 === 2 || k % 4 === 0)){"""
rep(OLD, NEW)

# the accumulator list lives at the top of chunk()
rep("const r=rng((hash(k,71)*4294967295)>>>0),z0=k*CHUNK,masses=[],shards=[],plates=[],galaxies=[],ships=[],gates=[],events=[];let hasEncounter=false;",
    "const r=rng((hash(k,71)*4294967295)>>>0),z0=k*CHUNK,masses=[],shards=[],plates=[],galaxies=[],ships=[],gates=[],events=[],battles=[];let hasEncounter=false;")

rep(" const c={masses,shards,plates,galaxies,ships,gates,events,k};chunks.set(k,c);return c;",
    " const c={masses,shards,plates,galaxies,ships,gates,events,battles,k};chunks.set(k,c);return c;")

rep("  for(const ev of (c.events||[])){SpaceEventEngine.drawEvent(ev,time);}",
    "  for(const ev of (c.events||[])){SpaceEventEngine.drawEvent(ev,time);}\n"
    "  for(const b of (c.battles||[]))drawBattle(b,time);")

BATTLE = r"""/* Beams are the only part of a battle that is not a hull: short paper-white
 * bursts between two fixed points, with the muzzle lit for the frame or two it
 * is hot. The pulse is a pure function of time, so nothing is stepped and a
 * seek lands on the same shot a flight of the same length would have made. */
function drawBattle(b,t){
 const q=project([b.x,b.y,b.z]);
 if(!q||q[2]>34000)return;
 const vis=clamp((34000-q[2])/12000,0,1);
 for(const f of b.fire){
  const pulse=Math.sin(t*(TAU/f.period)+f.phase);
  if(pulse<.52)continue;
  const a=(pulse-.52)/.48, A=project([f.x0,f.y0,f.z0]), B=project([f.x1,f.y1,f.z1]);
  if(!A||!B)continue;
  // A bolt, not a wire: a dim tail and a hot head, so the eye reads fire
  // rather than a scratch across the plate.
  const mx=(f.x0+f.x1)*.5,my=(f.y0+f.y1)*.5,mz=(f.z0+f.z1)*.5;
  line([[f.x0,f.y0,f.z0],[mx,my,mz]],
       blend([255,250,242],currentPalette.sun,.35),a*.30*vis,1.0);
  line([[mx,my,mz],[f.x1,f.y1,f.z1]],
       blend([255,252,246],currentPalette.sun,.15),a*.95*vis,2.0+a*1.4);
  if(a>.5){
   glow([f.x0,f.y0,f.z0],30,[255,222,180],a*.50*vis,3.2);
   glow([f.x1,f.y1,f.z1],30,[255,222,180],a*.62*vis,3.2);
  }
 }
 for(const g of (b.bursts||[])){
  const ph=((t/g.period+g.phase)%1+1)%1;
  const qq=project([g.x,g.y,g.z]);if(!qq)continue;
  const rr=(g.size*(.30+ph*1.35))*qq[3], al=(1-ph)*(1-ph)*.95*vis;
  if(rr<.8||rr>W*.5)continue;
  ctx.save();ctx.translate(qq[0],qq[1]);
  ctx.strokeStyle=css(blend([255,250,242],currentPalette.sun,.22),al);
  ctx.lineWidth=Math.max(.7,1.4*qq[3]*g.size/60);
  ctx.beginPath();ctx.arc(0,0,rr,0,TAU);ctx.stroke();
  ctx.strokeStyle=css([255,255,255],al*.30);
  ctx.beginPath();ctx.arc(0,0,rr*.62,0,TAU);ctx.stroke();
  if(ph<.22){ctx.fillStyle=css([255,252,244],(1-ph/.22)*.85*vis);
   ctx.beginPath();ctx.arc(0,0,Math.max(1,rr*.16),0,TAU);ctx.fill();}
  ctx.restore();
 }
}
function drawMass(m, p, t){"""
rep("function drawMass(m, p, t){", BATTLE)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V89 written:", len(src), "chars")
