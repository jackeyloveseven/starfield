"""V11: the print finish. One grade, one bloom, one vignette, over 100% of the frame.

Why this round exists: pixel measurement of the previous four rounds showed that
every visible change lived inside ~3% of the frame - the mean |dL| OUTSIDE the
planet bounding box was 1.00, i.e. pixel-identical. A fix validated at 3x zoom is
invisible at 1x by construction, which is why the user kept saying nothing changed.

Two measured defects drive the design:

  * The frame has NO black and NO clipped highlight: p1 = 30, p99 = 217, sky floor
    L = 45. (The reference art measures p1 = 0, p99 = 250.) Everything sits in the
    middle of the range, which is exactly why the piece reads flat.
  * The cause of the missing black is one statement: the "vignette" at the end of
    paperFinish() multiplied in currentPalette.ink - and in this palette INK IS THE
    LIGHT COLOUR (#e6eff7) and PAPER is the dark one. So the corner treatment was a
    near-white veil at .043-.075, lifting the corners by +8..+14.

Why ctx.filter and not composite operations: every Canvas2D blend mode has 0 and
255 as fixed points or asymptotes. A contrast curve needs an affine map with a
NEGATIVE intercept - out = A*v + B, B < 0 - and no chain of screen/multiply/
overlay can produce a negative intercept. `contrast(c)` is defined as
out = c*v + 0.5 - 0.5c, which is that map. Composite passes can only asymptote
toward the endpoints, never clip a population, which is precisely what is wanted.

Cost: ~3.25 extra full-screen blits in CSS-px terms (fillMPx 8.5 -> ~13). Those
are plain blits and one multiply, unlike the existing 8.5 M px of gradients, paths
and clips, so it is not the 1.5x slowdown the number suggests.

Known measurement trap: headless Chrome with --disable-gpu rasterises ctx.filter
and blur() on the CPU, so the screenshot harness will report a pessimistic fps.
Verify postMs in a real GPU browser, not through shot.py.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:140]))
    s = s.replace(a, b, n)


# ---- 1. the inverted corner treatment: a near-white veil lifting the corners ----
rep(" const v=ctx.createRadialGradient(W*.45,H*.46,H*.22,W*.5,H*.5,Math.hypot(W,H)*.60);"
    "v.addColorStop(0,'rgba(0,0,0,0)');"
    "v.addColorStop(1,css(currentPalette.ink,currentPalette.void>.5?.075:.043));"
    "ctx.fillStyle=v;ctx.fillRect(0,0,W,H);ctx.restore();",
    " // The corner treatment used to live here, and it pulled the wrong way:\n"
    " // currentPalette.ink is the LIGHT colour (#e6eff7) - paper is the dark one -\n"
    " // so this was a near-white veil at .043-.075 over the whole frame, +8..+14 of\n"
    " // lift at the corners. Measured effect: the frame had no black anywhere\n"
    " // (p1 = 30, sky floor 45). It is a real vignette in postPass() now.\n"
    " ctx.restore();")

# ---- 2. feature detection + the switch, next to the other render globals ----
rep("let W=0,H=0,DPR=1,rotated=false;",
    "let W=0,H=0,DPR=1,rotated=false;\n"
    "// ctx.filter is the only way to get a negative intercept (a true black point)\n"
    "// out of Canvas2D; no chain of composite modes can produce one.\n"
    "let postOn=true;\n"
    "const canGrade=(()=>{try{ctx.filter='contrast(1.01)';"
    "const ok=ctx.filter!=='none'&&ctx.filter!=='';ctx.filter='none';return ok;}catch(_){return false;}})();")

# ---- 3. the pass itself, immediately after paperFinish() ----
ANCHOR = ("  const x=wind.filteredX*W,y=wind.filteredY*H,"
          "a=clamp(1-(time-wind.last)/1.5)*.24;"
          "ctx.strokeStyle=css(currentPalette.ink,a);ctx.lineWidth=.6;"
          "ctx.beginPath();ctx.arc(x,y,9+Math.hypot(wind.x,wind.y)*8,.15,Math.PI*1.35);ctx.stroke();"
          "ctx.beginPath();ctx.arc(x,y,2,0,TAU);ctx.stroke();\n }\n}")

POST = ANCHOR + """
/* ---- The print finish -----------------------------------------------------
 * Everything above this is the depth-sorted scene. This is the plate going
 * through the press: one grade, one bloom, one vignette, in that order.
 *
 * Order is not a preference. Vignette first undoes the bloom in the corners;
 * bloom last re-lifts the corners the vignette just killed. And the whole thing
 * has to run after paperFinish(), because the grain and the wind arc are part of
 * the plate and must go through the press with it.
 *
 * The HUD is not affected and cannot be: every piece of typography in this piece
 * is a DOM element stacked above the canvas. Only #landscape is graded.
 * --------------------------------------------------------------------------*/
const post=document.createElement('canvas'),postCtx=post.getContext('2d',{alpha:false});
const bloom=document.createElement('canvas'),bloomCtx=bloom.getContext('2d',{alpha:false});
const vig=document.createElement('canvas'),vigCtx=vig.getContext('2d',{alpha:false});
/* brightness(1.10) contrast(1.33) is the affine map out = 1.463v - 42.1 (0..255):
 * black point 28.8 (so p1 = 30 becomes literally 0), white point 203 (so p99 = 217
 * and every star core clip to 255). pivot 90.9. saturate above 1.25 and the
 * near-neutral navy starts reading as a saturated blue, which breaks the ink. */
const gradeFilter='brightness(1.10) contrast(1.33) saturate(1.18)';
let postMs=0;
function buildVignette(vw,vh){
 vig.width=vw;vig.height=vh;
 const R=Math.hypot(vw,vh)*.50,cx=vw*.5,cy=vh*.5;
 const g=vigCtx.createRadialGradient(cx,cy,0,cx,cy,R);
 // The circle passes exactly through the four corners, so the corners land on the
 // last stop and multiply to literally zero. A widescreen ellipse on purpose: the
 // flanks go to ink, top and bottom are barely touched, and the corridor - whose
 // vanishing point sits at W*.385,H*.465 - stays clean.
 g.addColorStop(0.00,'rgb(255,255,255)');g.addColorStop(0.24,'rgb(255,255,255)');
 g.addColorStop(0.50,'rgb(242,245,250)');g.addColorStop(0.68,'rgb(206,213,224)');
 g.addColorStop(0.82,'rgb(146,155,169)');g.addColorStop(0.92,'rgb(66,72,84)');
 g.addColorStop(0.98,'rgb(14,16,20)');g.addColorStop(1.00,'rgb(0,0,0)');
 vigCtx.setTransform(1,0,0,1,0,0);vigCtx.globalCompositeOperation='source-over';
 vigCtx.filter='none';vigCtx.fillStyle=g;vigCtx.fillRect(0,0,vw,vh);
}
function postPass(){
 if(!postOn)return;
 const t0=performance.now(),dw=canvas.width,dh=canvas.height;
 if(!dw||!dh)return;
 // Sizes are checked at the use site, not in resize(): a fullscreen toggle, an
 // orientation change and a window resize all reach this differently, and a stale
 // buffer silently scales the frame instead of failing loudly.
 if(post.width!==dw||post.height!==dh){post.width=dw;post.height=dh;}
 postCtx.setTransform(1,0,0,1,0,0);postCtx.globalCompositeOperation='copy';
 postCtx.filter='none';postCtx.drawImage(canvas,0,0);
 // The grade goes back with source-over, not copy: the source is opaque and
 // covers the canvas exactly, so it is already a full replace, and copy+filter is
 // a known Chrome slow path.
 if(canGrade){
  ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.filter=gradeFilter;
  ctx.drawImage(post,0,0);ctx.restore();
 }
 // Bloom: quarter-res bright pass. contrast(2.6) has its black point at 78.5, so
 // the entire graded sky floor (23.7) collapses to nothing and only the real
 // highlights survive to be added back. `lighter` is the one composite that can
 // push past 255, which is where the clipped highlights come from.
 const bw=Math.max(1,dw>>2),bh=Math.max(1,dh>>2);
 if(bloom.width!==bw||bloom.height!==bh){bloom.width=bw;bloom.height=bh;}
 bloomCtx.setTransform(1,0,0,1,0,0);bloomCtx.globalCompositeOperation='copy';
 bloomCtx.filter='brightness(1.06) contrast(2.6) blur(6px)';
 bloomCtx.drawImage(canvas,0,0,bw,bh);bloomCtx.filter='none';
 ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalCompositeOperation='lighter';
 ctx.globalAlpha=.62;ctx.imageSmoothingQuality='low';ctx.drawImage(bloom,0,0,dw,dh);ctx.restore();
 const vw=Math.max(64,Math.round(W/6)),vh=Math.max(36,Math.round(H/6));
 if(vig.width!==vw||vig.height!==vh)buildVignette(vw,vh);
 ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalCompositeOperation='multiply';
 ctx.imageSmoothingQuality='low';ctx.drawImage(vig,0,0,dw,dh);ctx.restore();
 postMs=postMs*.9+(performance.now()-t0)*.1;
 fillPx+=W*H*3.25;
}"""

rep(ANCHOR, POST)

# ---- 4. call it, last thing in the frame ----
rep("flush();paperFinish();", "flush();paperFinish();postPass();")

# ---- 5. expose the cost; fps alone cannot tell the post pass from the scene ----
rep("audio:sound.ready?sound.ac.state:'not-started',track:sound.index+1}),",
    "audio:sound.ready?sound.ac.state:'not-started',track:sound.index+1,postMs:+(postMs).toFixed(2),postOn}),")

# ---- 6. the route strip sits on a ~50% darker plate now, so it reads twice as loud ----
rep("routeCtx.strokeStyle=css(currentPalette.ink,.30);routeCtx.lineWidth=.7;",
    "routeCtx.strokeStyle=css(currentPalette.ink,.22);routeCtx.lineWidth=.7;")
rep("routeCtx.fillStyle=css(currentPalette.ink,i===currentPalette.index?.8:.22);",
    "routeCtx.fillStyle=css(currentPalette.ink,i===currentPalette.index?.55:.16);")
rep("routeCtx.strokeStyle=css(currentPalette.ink,.75);",
    "routeCtx.strokeStyle=css(currentPalette.ink,.55);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V11 applied:", len(s), "chars")
