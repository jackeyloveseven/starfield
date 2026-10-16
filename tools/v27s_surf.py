"""v27s_surf -- kill the SURFACE mottle on the black hole's disc.

The user, looking at their own build:

    "你看看这像素感"   (look at this pixel feel)

not about the EDGES - the previous round (v26a) anti-aliased those and the band
boundaries now measure smooth at 8x - but about the disc's flat SURFACES, which
carry a fine mottled/blotchy texture the reference does not have. The reference
(R-C.jpg) is smooth: its flat tones are genuinely flat, with only soft
filaments over them.

--- WHAT WAS MEASURED (seed 1a2b, encounter framing, hole ~560 px radius,
    sprite 2048 drawn at 2.88x, so one sprite pixel is ~3 screen pixels)

Local std-dev of the LUMINANCE over a 24x24 patch of flat blue disc band, plus
the same over the shadow, with one source at a time neutralised:

    variant        blue band sd      shadow sd
    base (live)        3.05-3.47       1.86
    silk fbm off       1.90-2.11       1.84     <- the disc's mottle
    paper grain off    2.78-3.14       0.65     <- the shadow's speckle
    reference (R-C)    1.60-1.84        -       <- the target

Read across: the fbm that multiplies the disc (the "silk") is what pushes the
band from the reference's ~1.8 up to ~3.4; removing it lands the disc exactly on
the reference. It is invisible on the shadow only because a captured ray never
crosses the disc, so plasma() returns 0 there and the multiplier has nothing to
multiply.

At 8x the base band shows soft 8-15 px blobs; with the fbm off the surface is
uniform. Those blobs are the fbm's octave-0/1 cells (6.2 and 3.1 SPRITE px) blown
up 2.88x - real imaged structure, just the wrong structure for flat art.

--- RULED OUT, with the same measurements

  * the sprite upscale      the band EDGES measure smooth at 8x; the mottle is
                            inside the bands, not on their boundaries.
  * the bloom (contrast 3.4)  grain-off drops the band sd only 3.47 -> 3.14.
  * a per-pixel hash/dither   no hash is applied to the surface colour; the only
                            full-frame dither is the paper grain, below.

--- THE FIX

Delete the fbm "silk" multiplier. Its intent (see the removed comment) was three
flat tone STEPS - "three steps are tone" - but the field it quantised is noise,
so every step boundary is a noisy curve and the result is texture, not tone. The
disc's real tone structure is already carried by fittedRadiance (four flat bands
with anti-aliased boundaries) and the hand-drawn `warp` wobble on those
boundaries; both are kept untouched. Nothing else in the shader moves.

fbmP existed only to build this field, so it goes with it. noiseP stays: the
band-boundary `warp` still uses it.

--- NOT FIXED HERE, AND WHY

The paper grain (paperFinish: a 192 px tile of 2-level 250/75 noise at
globalAlpha .40, then amplified by the post pass's contrast(3.4) bloom) is the
dominant speckle on the SHADOW and on the flat paper everywhere. It is a
full-frame, deliberate "printed paper" treatment, not part of the black hole's
shader, and it is outside this workstream's ownership (GLSL_HOLE + drawHole).
After the fix below the disc sits at the reference's own noise level, so the
grain is left alone and reported instead.

Owns: the GLSL_HOLE string only. No uniform, no drawHole, no camera.

Run:  python -I v27s_surf.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v27s_surf.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:200]))
    s = s.replace(a, b, n)


# ---- the silk fbm: the disc's surface mottle. Remove it whole.
rep(""" float az=atan(q.y,q.x)/TAU;
 float stream=noiseP(vec2(radius*2.2,az*20.0-uTime/8.0*5.0),5.0);
 float silk=fbmP(vec2(radius*12.0+(stream-0.5)*0.6,az*32.0-uTime/8.0*8.0),8.0,
                 27.5/uRes.y*12.0);
 // Three flat steps, not a continuous +/-42% multiplier: a continuous one is
 // texture, three steps are tone. A floor() quantiser puts a 1-px staircase on
 // every step edge; each edge is now spread over 0.3 of a level instead.
 float s3=silk*3.0,qf=floor(s3);
 float silkQ=(qf+smoothstep(0.35,0.65,s3-qf))/3.0;
 col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));""",
""" // No surface texture. A quantised fbm used to sit here ("silk": three flat
 // steps of +/-22%), on the argument that three steps are tone and not texture.
 // They are not: the field being quantised is noise at 6.2 and 3.1 SPRITE px per
 // cell, so every step boundary is a noisy curve and the whole disc came out
 // mottled - measured at 3.4 sd against the reference's 1.8, and plainly visible
 // as 8-15 px blobs once the sprite is drawn at 2.88x. The disc's tone structure
 // is the four flat bands in fittedRadiance, whose boundaries are anti-aliased
 // and wobbled by the warp term; that is the flat art the reference has, and it
 // enough on its own.""")

# ---- fbmP existed only to build that field.
rep("""float fbmP(vec2 p,float period,float footprint){float n=0.0,amp=0.52;
 // Period >= 4 px kept whole, <= 2 px dropped whole. The old (0.65,2.1) window
 // was the inverse of the period, so 1.54 px still passed at full amplitude and
 // only 0.48 px was culled: a full octave of sub-Nyquist detail, which cannot be
 // imaged and can only alias into the screen-scale dots.
 for(int i=0;i<5;i++){float aa=1.0-smoothstep(0.25,0.50,footprint);
  n+=amp*mix(0.5,noiseP(p,period),aa);p*=2.0;period*=2.0;footprint*=2.0;amp*=0.49;}
 return n;}
""", "")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V27s applied:", len(s), "chars ->", out_p)
