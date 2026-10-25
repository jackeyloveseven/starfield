"""v137-pop: replace the one-frame celestial culls with a continuous fade.

Measured root cause (probe_pop.py on the 2026-10-25 15:33 build, 0..1600 s @30 fps): a kind-4
(Gargantua) body is drawn with its far beacon at alpha ~0.33 on screen and is
then dropped by `if(!pj||pj[2]>70000)continue;`, while drawHole() itself keeps
that beacon alive to 85,000 units. The three hard culls in the masses loop also
explain the count jumps. This patch:

  1. gives every mass a persistent `m.fade` in [0,1], driven continuously by
     distance, screen-edge overlap and the angle to the frame corner;
  2. caps the change at .012 per drawn frame, so even 5-6 bodies cannot move
     the visible count by more than ~7% in one frame;
  3. skips a mass only once its fade has reached zero;
  4. multiplies the fade into the star branch (kinds 5-7) and the black-hole
     beacon, both of which ignored massVis before;
  5. turns the director's `ang > .62 || r/d < .05` continue into weights, so
     the gaze pull also leaves continuously instead of switching off.

  python -I v137_pop.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit('usage: python -I v137_pop.py <in.html> <out.html>')

src = open(sys.argv[1], encoding='utf-8').read()

SENTINEL = 'v137-pop-fade'
if SENTINEL in src:
    sys.exit('input already patched (sentinel present)')

subs = []

# ---- 1. director: continuous gaze weight instead of a binary continue ------
subs.append((
    'let gm = null, gd = 1e9;',
    'let gm = null, gd = 1e9, gGaze = 1;'))

subs.append((
    '''   const ang = Math.atan2(Math.hypot(dx, dy), Math.max(1, dz));
   if(ang > .62 || m.r / Math.max(1, d) < .05) continue;
   if(d < gd){gd = d; gm = m;}''',
    '''   const ang = Math.atan2(Math.hypot(dx, dy), Math.max(1, dz));
   /* v137-pop-fade: the old `continue` switched the gaze off in one frame the
    * moment a world crossed .62 rad or .05 relative size. Weight the pull
    * instead, and let it reach zero before the candidate drops out. */
   const angW = clamp((.62 - ang) / .18, 0, 1);
   const sizeW = clamp((m.r / Math.max(1, d) - .02) / .03, 0, 1);
   const gaze = angW * sizeW;
   if(gaze <= 0) continue;
   if(d < gd){gd = d; gm = m; gGaze = gaze;}'''))

subs.append((
    '''   } else {
    w = clamp((6000 - gd) / 5000, 0, 1) * 0.32 + 0.10;
   }
   lookTarget = [mix(routeX(travel), gm.x, w), mix(courseY(travel) + camera.aimY, gm.y, w), mix(travel, gm.z, w * 0.80)];''',
    '''   } else {
    w = clamp((6000 - gd) / 5000, 0, 1) * 0.32 + 0.10;
   }
   w *= gGaze; /* v137-pop-fade: fade the gaze pull out continuously */
   lookTarget = [mix(routeX(travel), gm.x, w), mix(courseY(travel) + camera.aimY, gm.y, w), mix(travel, gm.z, w * 0.80)];'''))

# ---- 2. bodies(): per-frame fade timing -----------------------------------
subs.append((
    '''function bodies(){
 activeShips.length=0;''',
    '''function bodies(){
 activeShips.length=0;
 /* v137-pop-fade: distance / frame edge / angle only set a target. The
  * rendered alpha eases toward it, capped at .012 per drawn frame, so no cull
  * can remove a body that is still visible. */
 const popDt=Math.max(0,Math.min(.1,time-(bodies._popT===undefined?time:bodies._popT)));
 bodies._popT=time;
 const popK=1-Math.exp(-2.0*popDt);
 const popMax=.012;'''))

# ---- 3. bodies(): masses loop, culls -> fade -------------------------------
subs.append((
    '''  for(const m of c.masses){
   const pj=project([m.x,m.y,m.z]);if(!pj||pj[2]>70000)continue;
   const rad=m.r*pj[3];
   const cullR=(m.kind>=5&&m.kind<=7)?(rad*12+100):(m.kind===4?Math.max(rad*8,500):(m.w&&m.w.hasRings||m.kind===8?rad*4+80:rad*2.8+80));
   if(pj[0]+cullR<0||pj[0]-cullR>W||pj[1]+cullR<0||pj[1]-cullR>H)continue;
   massVis=clamp((70000-pj[2])/45000);if(massVis<=0)continue;
   {const rp=m.r*pj[3];if(rp>H*.42)massVis*=clamp(H*.42/rp,.30,1);}
   drawMass(m,region(m.x,m.z),time);massVis=1;
  }''',
    '''  for(const m of c.masses){
   const pj=project([m.x,m.y,m.z]);
   if(!pj){
    // Behind the near plane: no projection, so ease the fade out and stop.
    if(m.fade!==undefined)m.fade=Math.max(0,m.fade-popMax);
    continue;
   }
   const rad=m.r*pj[3];
   const cullR=(m.kind>=5&&m.kind<=7)?(rad*12+100):(m.kind===4?Math.max(rad*8,500):(m.w&&m.w.hasRings||m.kind===8?rad*4+80:rad*2.8+80));
   /* v137-pop-fade: the 70k / offscreen / near-plane `continue`s become three
    * continuous targets. kind 4 keeps drawHole's 85k beacon range. */
   const farDist=(m.kind===4)?85000:70000;
   const distFade=clamp((farDist-pj[2])/45000);
   const vw=Math.min(pj[0]+cullR,W)-Math.max(pj[0]-cullR,0);
   const vh=Math.min(pj[1]+cullR,H)-Math.max(pj[1]-cullR,0);
   const edgeFade=clamp(Math.min(vw,vh)/Math.max(180,cullR*.45));
   const bodyAng=Math.atan2(Math.hypot(pj[0]-camera.cx,pj[1]-camera.cy),camera.focal);
   const cornerAng=Math.atan2(Math.hypot(W*.5,H*.5),camera.focal);
   const angRad=Math.atan2(rad,Math.max(1,pj[2]));
   const angFade=clamp((cornerAng+.12+angRad-bodyAng)/.12);
   const target=Math.min(distFade,edgeFade,angFade);
   if(m.fade===undefined)m.fade=0;
   m.fade+=clamp((target-m.fade)*popK,-popMax,popMax);
   if(m.fade<=0.0005){m.fade=0;continue;}
   massVis=m.fade;
   {const rp=m.r*pj[3];if(rp>H*.42)massVis*=clamp(H*.42/rp,.30,1);}
   drawMass(m,region(m.x,m.z),time);massVis=1;
  }'''))

# ---- 4. star branch (kinds 5-7) must use the fade too ----------------------
subs.append((
    '  queue.push({type: 4, d: q[2], alpha: 1, fn: () => {',
    '  queue.push({type: 4, d: q[2], alpha: massVis, fn: () => {'))

subs.append((
    '  glow([m.x, m.y, m.z], m.r * halo, lit, m.kind === 7 ? .46 : .24, 2.2);',
    '  glow([m.x, m.y, m.z], m.r * halo, lit, (m.kind === 7 ? .46 : .24) * massVis, 2.2);'))

subs.append((
    '  glow([m.x, m.y, m.z], m.r * halo * .36, blend(lit, [255, 255, 255], .55), m.kind === 7 ? .85 : .52, 2.4);',
    '  glow([m.x, m.y, m.z], m.r * halo * .36, blend(lit, [255, 255, 255], .55), (m.kind === 7 ? .85 : .52) * massVis, 2.4);'))

# ---- 5. black-hole beacon: 85k fade, not the 70k cut -----------------------
subs.append((
    '''  const dist = q[2];
  const farFade = clamp((85000 - dist) / 45000, 0, 1);
  if (farFade > 0.01) {
    queue.push({
      type: 4, d: q[2] + 50, alpha: farFade, fn: () => {''',
    '''  /* v137-pop-fade: bodies() now hands kind 4 a fade that reaches zero at
   * 85,000 units, so the beacon is no longer cut off at 70,000. */
  if (massVis > 0.001) {
    queue.push({
      type: 4, d: q[2] + 50, alpha: massVis, fn: () => {'''))

for old, new in subs:
    n = src.count(old)
    if n != 1:
        sys.exit('anchor count %d (want 1): %r' % (n, old[:90]))
    src = src.replace(old, new, 1)

open(sys.argv[2], 'w', encoding='utf-8', newline='').write(src)
print('v137_pop: %d replacements -> %s' % (len(subs), sys.argv[2]))
