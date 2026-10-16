"""v23c_post -- make the black hole SHARP by taking the screen-space blur off it.

Verbatim complaints this answers:

  "太糊了全是像素点"   (too blurry, all pixels)
  "还是太糊太糊了，能做成矢量吗"  (still too blurry - can it be vector)

A study of Haskely/Gargantua (a Shadertoy port) concluded:

  "Gargantua has NO screen-space blur at all - no bright pass, no second render
   target; every pixel is the analytic falloff of the disc. Its only blur is
   before the tonemap."

and prescribed, for this file: raise the bloom bright-pass threshold
(contrast 2.6 -> ~3.4), narrow the blur (6px -> 2.5-3px), and drop the bloom
globalAlpha (.62 -> ~.28).

WHY THAT IS THE RIGHT LEVER HERE. The disc is now drawn by a WebGL raymarcher
(GLSL_HOLE / drawHole) that is analytically sharp; the postPass bloom is the only
thing smearing it. The bloom is a quarter-res bright pass that is then upscaled
4x, so a "6px" blur is really a 24px full-res halo - that halo is the mush the
user sees, and it is drawn on top of the photon ring.

The bloom is ALSO what makes the stars and the nebula glow, so it is not deleted,
only made small and selective: the higher threshold keeps the graded sky floor
out of it entirely, so what survives to be added back is genuine highlight, not
haze.

Owned region: postPass() and the vignette/bloom it drives. This patch touches
NOTHING else - not GLSL_HOLE, drawHole, chunk(), drawMass, or the star loops.

Reads the artwork, asserts each replaced string occurs exactly once, writes a
working copy. A bare run edits only this workflow's own copy, never the shared
original.

Run:  python -I v23c_post.py [<in.html> [<out.html>]]     (default: work-crisp.html)
"""
import sys

in_p = sys.argv[1] if len(sys.argv) > 1 else "work-crisp.html"
out_p = sys.argv[2] if len(sys.argv) > 2 else in_p
s = open(in_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. the bright pass: a tighter threshold and a much narrower blur ----
# contrast(3.4) has its black point at 90, so the graded sky floor never reaches
# the bloom; blur(3px) at quarter res upscales to a ~12px halo instead of ~24px.
rep("bloomCtx.filter='brightness(1.06) contrast(2.6) blur(6px)';",
    "bloomCtx.filter='brightness(1.06) contrast(3.4) blur(3px)';")

# ---- 2. the bloom's weight: a glow on the highlights, not a veil over the frame
rep("ctx.globalAlpha=.62;ctx.imageSmoothingQuality='low';ctx.drawImage(bloom,0,0,dw,dh);ctx.restore();",
    "ctx.globalAlpha=.28;ctx.imageSmoothingQuality='low';ctx.drawImage(bloom,0,0,dw,dh);ctx.restore();")

# ---- 3. the comment above the pass described the old constants ----
rep(""" // Bloom: quarter-res bright pass. contrast(2.6) has its black point at 78.5, so
 // the entire graded sky floor (23.7) collapses to nothing and only the real
 // highlights survive to be added back. `lighter` is the one composite that can
 // push past 255, which is where the clipped highlights come from.""",
    """ // Bloom: quarter-res bright pass, deliberately small. The reference (Gargantua)
 // has no screen-space blur at all - every pixel of its disc is the analytic
 // falloff - so this pass must not be what draws the photon ring. contrast(3.4)
 // puts the black point at 90, above the graded sky floor, so only genuine
 // highlights survive to be added back; blur(3px) at quarter res upscales to a
 // ~12px halo, not the ~24px veil of blur(6px). `lighter` is the one composite
 // that can push past 255, which is where the clipped highlights come from.""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("v23c_post: wrote %s (%d chars)" % (out_p, len(s)))
