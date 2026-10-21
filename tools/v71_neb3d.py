"""V71: give the nebulae a place in the world.

They were unit directions. The camera could never approach one, no world could
pass in front of one, and every cloud sat at the same infinity - which is why
turning the view made the sky feel pasted on. Each now owns a centre and a
radius in world units, is drawn through project(), and is enqueued at its own
depth so the worlds in front of it occlude it.

Two details matter beyond the projection:

  * the billboard is rotated by camera roll, or a banked camera spins every
    cloud against the sky;
  * a cloud you run at fades out before its 384 px texture is stretched over
    the whole plate.

Run:  python -I v71_neb3d.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

# ---- 1. the field: world anchors with a rolling spawn window ----------------
START = "const nebulae=Array.from({length:coarse?26:44},(_,i)=>{"
END = "alpha:.17+hash(i,215)*.38};\n});"
if src.count(START) != 1:
    sys.exit("array start count=%d" % src.count(START))
i0 = src.index(START)
i1 = src.index(END, i0) + len(END)

ARR = r"""/* Billboards with a place in the world, not a painted dome.
 *
 * These used to be unit directions, and that had three consequences the eye
 * reads immediately: the camera could never approach one, nothing could pass in
 * front of one, and every cloud was pinned to the same infinity. Each now owns a
 * centre and a radius in world units, so it grows as the convoy closes on it,
 * slides against the far field, and sorts against the worlds in the same queue.
 *
 * Its distance is chosen from the apparent size we want rather than the other
 * way round: 1.6-4.0 radii off the centre gives the 0.14-0.32 rad the old
 * constant gave, but now as a consequence of where the cloud is. The unit
 * direction survives only for novaGas(), which asks "is this gas in the flash's
 * direction". */
const nebulae=Array.from({length:coarse?26:44},(_,i)=>({
 i:i,gen:0,wx:0,wy:0,wz:-1e18,wr:0,
 x:1,y:0,z:0,size:.3,seed:1+Math.floor(hash(i,213)*6),
 rot:hash(i,214)*TAU,alpha:.17+hash(i,215)*.38
}));
let nebReady=false;
function nebulaPlace(n,ahead){
 const r=rng((SEED^Math.imul((n.i+1)|0,0x9e3779b1)^Math.imul(n.gen+1,0x85ebca6b))>>>0);
 const z=travel+ahead,R=6000+r()*11000;
 const L=R*(1.6+r()*2.4),a0=r()*TAU;
 n.wr=R;
 n.wx=routeX(z)+Math.cos(a0)*L;
 n.wy=courseY(z)+Math.sin(a0)*L;
 n.wz=z+(r()-.5)*L*.8;
 const dx=n.wx-routeX(z),dy=n.wy-courseY(z),dz=n.wz-z,dd=Math.hypot(dx,dy,dz)||1;
 n.x=dx/dd;n.y=dy/dd;n.z=dz/dd;n.size=clamp(R/dd,.05,1.2);
 n.rot=r()*TAU;
}
function nebulaUpdate(){
 if(!nebReady){nebReady=true;
  for(const n of nebulae)nebulaPlace(n,-45000+((n.i+.5)/nebulae.length)*150000);
 }
 // Recycle well behind the eye, never in front of it: a cloud that is 80k
 // behind the camera cannot be on screen even at the widest yaw.
 for(const n of nebulae)if(n.wz<travel-80000){n.gen++;nebulaPlace(n,110000+hash(n.i,301+n.gen)*45000);}
}"""
src = src[:i0] + ARR + src[i1:]

# ---- 2. the draw: project + depth queue ------------------------------------
S2 = " if(wash>.06){"
E2 = "  ctx.globalAlpha = 1;\n }"
if src.count(S2) != 1:
    sys.exit("draw start count=%d" % src.count(S2))
j0 = src.index(S2)
j1 = src.index(E2, j0) + len(E2)

DRAW = r""" nebulaUpdate();
 if(wash>.06){
  const list = lowQuality ? nebulae.slice(0, 8) : nebulae;
  const pal0 = NEB_PAL[p.index] || NEB_PAL[0];
  const aT = p.t, a0 = p.a, b0 = p.b, tw = p.t < 1, roll = camera.roll || 0;
  for (const n of list) {
   const q = project([n.wx, n.wy, n.wz]); if (!q) continue;
   const d = q[2];
   if (d > 150000) continue;
   const rad = n.wr * q[3];
   if (rad < 6) continue;
   const pad = rad * 0.62;
   if (q[0] < -pad || q[0] > W + pad || q[1] < -pad || q[1] > H + pad) continue;
   // Past 1.35 radii the gas dissolves rather than becoming a wall. Running
   // through one should be a wash of light, not 384 px stretched over the plate.
   const near = clamp((d - n.wr * 1.35) / (n.wr * 0.9), 0, 1);
   const far  = clamp((150000 - d) / 55000, 0, 1);
   const ng = novaGas(n, nova), al = clamp(n.alpha * wash * 2.9 * ng * near * far, 0, 0.94);
   if (al < .004) continue;
   const qx = q[0], qy = q[1], rr = rad, aa = al, nn = n;
   // Enqueued at its own depth, so a world nearer than the cloud prints over
   // it and one behind it does not. This is the whole point of the rewrite.
   queue.push({type:4, d, alpha:1, fn:()=>{
    // Pass 1: the ionised core, added rather than painted.
    const coreRad = rr * 0.46;
    ctx.save();
    ctx.translate(qx, qy);
    ctx.globalCompositeOperation = 'lighter';
    const nGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, coreRad);
    nGrad.addColorStop(0, css(blend(pal0[0], [255,255,255], 0.20), aa * 0.26));
    nGrad.addColorStop(0.30, css(pal0[0], aa * 0.14));
    nGrad.addColorStop(0.66, css(pal0[1], aa * 0.10));
    nGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = nGrad;
    ctx.beginPath(); ctx.arc(0, 0, coreRad, 0, TAU); ctx.fill();
    ctx.restore();
    // Pass 2: the dust, at the world's own screen angle. Camera roll belongs
    // in here - without it a banked camera spins every cloud against the sky.
    ctx.save();
    ctx.translate(qx, qy);
    ctx.rotate(nn.rot + roll);
    ctx.globalCompositeOperation = 'source-over';
    if (tw) {
     ctx.globalAlpha = aa * (1 - aT);
     ctx.drawImage(nebulaTex(nn.seed, a0), -rr, -rr, rr * 2, rr * 2);
     ctx.globalAlpha = aa * aT;
     ctx.drawImage(nebulaTex(nn.seed, b0), -rr, -rr, rr * 2, rr * 2);
    } else {
     ctx.globalAlpha = aa;
     ctx.drawImage(nebulaTex(nn.seed, p.index), -rr, -rr, rr * 2, rr * 2);
    }
    fillPx += rr * 2 * rr * 2 * (tw ? 2 : 1);
    ctx.restore();
   }});
  }
  ctx.globalAlpha = 1;
 }"""
src = src[:j0] + DRAW + src[j1:]

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V71 written:", len(src), "chars")
