"""v25a_haze -- port the two pieces of the reference black-hole renderer that were
deliberately skipped: the multi-level bloom chain and the blue plane haze.

Source: sayed1145/glsl-black-hole (MIT License, Copyright (c) 2026 sayed1145) -
shaders/blur.frag and shaders/composite.frag. The notice stays in CREDITS.md.

(a) THE BLOOM CHAIN
    Ours was one quarter-res pass: `brightness(1.06) contrast(3.4) blur(3px)`
    added with `lighter` at alpha .28. It was JUST retuned to that to keep the
    flat disc crisp, so the port must ADD highlight reach without re-softening
    the disc. The reference wires four levels (bloom0..bloom3) and - this is the
    load-bearing detail - adds only the TWO TIGHTEST to the white bloom
    (`hdr = base*0.96 + 0.13*b0 + 0.035*b1`); the two widest go to the blue haze
    instead. We mirror that: level 0 is the existing quarter-res pass, byte for
    byte unchanged; levels 1 and 2 are new eighth- and sixteenth-res buffers, each
    at a HIGHER black point (contrast 4.6 then 5.4 against 3.4). A flat mid-tone
    band cannot clear contrast 4.6 - the black point sits at 104 - so the disc's
    four tone bands do not pass the wide levels at all, and only genuine
    highlights (the photon ring, suns, the hole's rim, bright stars) reach out
    further. Alphas follow the reference's 0.13 : 0.035 ratio, scaled to our .28.

(b) THE BLUE PLANE HAZE
    composite.frag carries it as two terms plus a darkness gate:
        blue  = 0.205*exp(-|q/e|^2)                       // core ellipse
        plane = 0.35*exp(-(x/a)^4 - (y/b)^2)              // flat, thin plane
        plane*= (1-exp(-(x/c)^2))*(0.7+0.4*tanh(x*6))     // hollow centre, +x bias
        col  += vec3(0.26,0.59,0.83)*blue*pow(1-max(col),0.8)
    The last line is the point: the blue is gated by how DARK the pixel already
    is, so it fills the gaps and rings the rim and never washes out the disc.
    Ported into GLSL_HOLE, where `q` is already the disc-frame coordinate and the
    shadow sits at length(q)=2.6, so hq=q/2.6 is in shadow radii and the
    reference's constants transfer directly. `outc` stands in for their `col`:
    over the background it is ~0 (full haze), over the disc it is bright (none).
    The haze is also given coverage in alpha, so it shows over the paper.

Owns: the GLSL_HOLE string and postPass (plus the two extra bloom canvases next
to it). Does NOT touch drawWorld, drawMass, drawHole, or chunk().

Run:  python -I v25a_haze.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v25a_haze.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- (a0) two more bloom buffers beside the original one.
rep("""const bloom=document.createElement('canvas'),bloomCtx=bloom.getContext('2d',{alpha:false});""",
"""const bloom=document.createElement('canvas'),bloomCtx=bloom.getContext('2d',{alpha:false});
/* Levels 1 and 2 of the reference's bloom chain (blur.frag run at two coarser
 * resolutions). Level 0 stays the original quarter-res pass. */
const bloom2=document.createElement('canvas'),bloom2Ctx=bloom2.getContext('2d',{alpha:false});
const bloom3=document.createElement('canvas'),bloom3Ctx=bloom3.getContext('2d',{alpha:false});""")

# ---- (a1) the bloom block itself: keep level 0, add the two wider levels.
rep(""" // Bloom: quarter-res bright pass, deliberately small. The reference (Gargantua)
 // has no screen-space blur at all - every pixel of its disc is the analytic
 // falloff - so this pass must not be what draws the photon ring. contrast(3.4)
 // puts the black point at 90, above the graded sky floor, so only genuine
 // highlights survive to be added back; blur(3px) at quarter res upscales to a
 // ~12px halo, not the ~24px veil of blur(6px). `lighter` is the one composite
 // that can push past 255, which is where the clipped highlights come from.
 const bw=Math.max(1,dw>>2),bh=Math.max(1,dh>>2);
 if(bloom.width!==bw||bloom.height!==bh){bloom.width=bw;bloom.height=bh;}
 bloomCtx.setTransform(1,0,0,1,0,0);bloomCtx.globalCompositeOperation='copy';
 bloomCtx.filter='brightness(1.06) contrast(3.4) blur(3px)';
 bloomCtx.drawImage(canvas,0,0,bw,bh);bloomCtx.filter='none';
 ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalCompositeOperation='lighter';
 ctx.globalAlpha=.28;ctx.imageSmoothingQuality='low';ctx.drawImage(bloom,0,0,dw,dh);ctx.restore();""",
""" // Bloom: the reference's blur.frag chain, three levels. Level 0 is the original
 // quarter-res bright pass, UNCHANGED - contrast(3.4) puts its black point at 90,
 // above the graded sky floor, so only genuine highlights survive to be added
 // back, and blur(3px) at quarter res upscales to a ~12px halo. It is the tight
 // level that keeps the disc's four flat tone bands crisp.
 //
 // Levels 1 and 2 are new and are what the port adds: eighth- and sixteenth-res
 // buffers at contrast 4.6 (black point 104) and 5.4 (black point 122). A flat
 // mid-tone band cannot clear either, so the disc does not pass them and its
 // hard edges cannot smear; only the true highlights - the photon ring, suns,
 // the hole's rim, the brightest stars - reach out to a ~20px and ~32px halo.
 // Alphas are the reference's own 0.13 : 0.035 ratio (their hdr add), scaled to
 // our .28. `lighter` is the one composite that can push past 255, which is
 // where the clipped highlights come from.
 const bw=Math.max(1,dw>>2),bh=Math.max(1,dh>>2);
 if(bloom.width!==bw||bloom.height!==bh){bloom.width=bw;bloom.height=bh;}
 bloomCtx.setTransform(1,0,0,1,0,0);bloomCtx.globalCompositeOperation='copy';
 bloomCtx.filter='brightness(1.06) contrast(3.4) blur(3px)';
 bloomCtx.drawImage(canvas,0,0,bw,bh);bloomCtx.filter='none';
 const mw=Math.max(1,dw>>3),mh=Math.max(1,dh>>3);
 if(bloom2.width!==mw||bloom2.height!==mh){bloom2.width=mw;bloom2.height=mh;}
 bloom2Ctx.setTransform(1,0,0,1,0,0);bloom2Ctx.globalCompositeOperation='copy';
 bloom2Ctx.filter='brightness(1.06) contrast(4.6) blur(2.5px)';
 bloom2Ctx.drawImage(canvas,0,0,mw,mh);bloom2Ctx.filter='none';
 const ww=Math.max(1,dw>>4),wh=Math.max(1,dh>>4);
 if(bloom3.width!==ww||bloom3.height!==wh){bloom3.width=ww;bloom3.height=wh;}
 bloom3Ctx.setTransform(1,0,0,1,0,0);bloom3Ctx.globalCompositeOperation='copy';
 bloom3Ctx.filter='brightness(1.06) contrast(5.4) blur(2px)';
 bloom3Ctx.drawImage(canvas,0,0,ww,wh);bloom3Ctx.filter='none';
 ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalCompositeOperation='lighter';
 ctx.imageSmoothingQuality='low';
 ctx.globalAlpha=.28;ctx.drawImage(bloom,0,0,dw,dh);
 ctx.globalAlpha=.09;ctx.drawImage(bloom2,0,0,dw,dh);
 ctx.globalAlpha=.035;ctx.drawImage(bloom3,0,0,dw,dh);
 ctx.restore();""")

# ---- (b) the blue plane haze, in the shader, just before the alpha composite.
rep(""" float rp=length(p);
 float shadow=1.0-smoothstep(2.57,2.66,rp);
 vec3 shadowCol=mix(vec3(0.045000,0.060000,0.172000),vec3(0.033000,0.045000,0.120000),step(2.05,rp));
 vec3 outc=tone+shadowCol*shadow*(1.0-clamp(lum*3.0,0.0,1.0));
 float alpha=max(shadow,clamp(lum*2.2,0.0,1.0));
 fragColor=vec4(outc*alpha,alpha);""",
""" float rp=length(p);
 float shadow=1.0-smoothstep(2.57,2.66,rp);
 vec3 shadowCol=mix(vec3(0.045000,0.060000,0.172000),vec3(0.033000,0.045000,0.120000),step(2.05,rp));
 vec3 outc=tone+shadowCol*shadow*(1.0-clamp(lum*3.0,0.0,1.0));
 // The blue plane haze, ported from the reference's composite.frag. Two parts:
 // a soft elliptical core hugging the shadow, and a flat THIN plane band along
 // the disc - hollow at the centre and brighter on the +x side. hq=q/2.6 is the
 // disc-frame coordinate in units of the shadow radius (the shadow sits at
 // length(q)=2.6), so the reference's constants transfer unchanged. Both parts
 // are then gated by how dark the pixel already is, which is the line that makes
 // the haze read as light in the gaps rather than as a blue film over the disc:
 // over the paper outc is ~0 and the haze is at full strength, over a bright
 // band it is suppressed to nothing. outc here is the same role their col plays.
 vec2 hq=q/2.6;
 float haze=0.205*exp(-dot(hq/vec2(2.476,1.686),hq/vec2(2.476,1.686)));
 float plane=0.35*exp(-pow(hq.x/3.689,4.0)-pow(hq.y/0.717,2.0));
 plane*=(1.0-exp(-pow(hq.x/1.476,2.0)))*(0.7+0.4*tanh(hq.x*0.632));
 haze+=plane;
 float hazeDark=pow(max(0.0,1.0-max(outc.r,max(outc.g,outc.b))),0.8);
 float hazeA=clamp(haze*hazeDark*0.62,0.0,1.0);
 outc+=vec3(0.26,0.59,0.83)*hazeA;
 float alpha=max(max(shadow,clamp(lum*2.2,0.0,1.0)),hazeA);
 fragColor=vec4(outc*alpha,alpha);""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V25a applied:", len(s), "chars ->", out_p)
