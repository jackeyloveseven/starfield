"""v26a_abyss -- the black hole's LOOK: kill the aliasing, then exaggerate it.

Two complaints, verbatim:

  "黑洞锯齿感明显"
  (obvious aliasing / stair-stepping on the black hole)

  "我觉得事件视界可以做的夸张一点，放大也才只能一窥黑洞的全貌"
  (the event horizon could be more exaggerated - only by zooming in can you
   glimpse the whole thing)

--- (a) WHY IT STAIR-STEPS, AND WHY "KEEP THE FLAT LOOK" IS NOT IN TENSION WITH IT

The flat conversion (v21f) replaced every manufactured gradient with a HARD
threshold. Flat tone is correct - the reference is vector art - but a hard
threshold is not the same thing as a flat tone. A threshold has no width, so the
boundary is rasterised at sprite-pixel granularity, and this sprite is then drawn
at 2*DRAW (up to ~2x its buffer). A 1-sprite-px step becomes a 2-screen-px step,
and on a curve that reads as a staircase.

So nothing here softens a tone. Every tone stays flat; only the BOUNDARY between
two tones is given a width, and the width is chosen in sprite pixels so that it
survives the rasteriser and the upscale:

  A1  the four radial tone bands were selected by `int band=min(k/4,..)`, a hard
      integer step at RADII[4]/[8]/[12] = 2.7/4.3/7.6. That is the big one: those
      boundaries run the whole width of the disc and jump between very different
      colours. Now a smoothstep uAA wide in radius units.
  A2  the disc-plane band was `1.0-step(0.052,abs(q.y))` - a hard pair of nearly
      diagonal lines. Now a smoothstep capped at a fraction of the band's own
      half-width (uAA would erase a line only 6 sprite px wide).
  A3  the silk multiplier was quantised with floor(silk*3.0), which puts a 1-px
      staircase on every step edge. The edge is now spread over 0.3 of a level.
  A4  the photon ring's shoulder spanned 0.55 sprite px - narrower than the
      rasteriser can represent, so the brightest thing in the frame was the
      raggedest. Widened to ~1.2 sprite px.
  A5  the ring's brightness split was `step(-0.01,p.y)`, a hard line across the
      ring at the disc roll. Now a smoothstep.
  A6  the secondary-image gate was `step(9.0,m0.x)`, a hard ellipse. Now a
      smoothstep.
  A7  the shadow edge was a 0.09-wide smoothstep - five sprite px, which the
      upscale turned into a ~10 px halo. Tightened to 2*uAA: crisp, still
      stepped over more than one sprite pixel.

uAA is supplied by the host, in p units, as max(1.2 sprite px, 1.5 screen px).
Neither bound alone is enough: below one sprite pixel the rasteriser discards the
transition, and one sprite pixel is not enough once the sprite is upscaled.

--- (b) EXAGGERATE

The shadow is drawn at exactly rad = m.r*q[3] on screen (DRAW is calibrated for
it), so the only way to make it bigger is to make rad bigger. `m.r` is the right
lever and not the sprite multiplier: m.r also feeds the lensing source radius
(`clamp(m.r*q[3],4,...)`, Einstein radius 1.35x it), so growing m.r keeps the
lens warp registered with the drawn shadow. Growing only the sprite would leave
the lens warp buried inside an opaque disc.

  1100 -> 2200, and the capture factor .60 -> .30, which keeps the capture
  distance at exactly 660 as before. m.r is NOT the gravitational mass: the ship
  force uses GRAV*MASS_KIND[kind] and courseBend uses fixed constants, so the
  physics is untouched - only the drawn size and the lens radius.

  The sprite buffer cap goes 1536 -> 2048 so the upscale at the new size stays
  ~3x instead of ~4x (2048^2 is 1.78x the fragment work of 1536^2).

Owns: the GLSL_HOLE string, every drawHole uniform, the sprite-size line, the
black-hole radius in the mass table, and the one capture-factor constant (which
this brief explicitly authorises compensating: "If you change r, compensate the
capture factor to keep the capture distance"). Nothing else in updateCapture is
touched.

Run:  python -I v26a_abyss.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v26a_abyss.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:200]))
    s = s.replace(a, b, n)


# ---- uniform: the AA half-width, in the shader's radius units.
rep("uniform float uTilt,uIncl,uScale,uInner,uTime;",
    "uniform float uTilt,uIncl,uScale,uInner,uTime,uAA;")

# ---- A1: the four radial tone bands, boundaries anti-aliased, tones untouched.
rep("""vec3 fittedRadiance(float radius,float incidence,bool upper){
 if(radius<RADII[0]||radius>RADII[PROFILE_N-1])return vec3(0.0);
 int k=0;
 for(int i=0;i<PROFILE_N-2;i++) if(radius>RADII[i+1]) k=i+1;
 // Flat art, not a volume. The 18 fitted stops collapse to four flat tones,
 // sampled at their heads with no interpolation between them: the reference's
 // crispness is four tone steps with hard boundaries, not a smooth radial ramp.
 int band=min(k/4,PROFILE_N/4-1),kk=band*4;
 vec3 a=upper?UPPER[kk]:LOWER[kk];
 vec3 b=GRAZING[kk];
 // A hard threshold, not a cross-fade: a grazing crossing and a steep one are
 // two different tones, and blending them is what manufactured the gradient.
 return incidence<0.22?b:a;}""",
"""vec3 fittedRadiance(float radius,float incidence,bool upper){
 if(radius<RADII[0]||radius>RADII[PROFILE_N-1])return vec3(0.0);
 // Flat art, not a volume: four flat tones whose boundaries sit at RADII[4],
 // RADII[8], RADII[12] = 2.7 / 4.3 / 7.6. The BANDS are still flat - every stop
 // of a band is one colour - but a boundary is no longer a hard integer step.
 // A hard step has no width, so it rasterises at sprite-pixel granularity, and
 // this sprite is drawn at 2*DRAW (up to ~2x its buffer): one sprite pixel
 // becomes two screen pixels, which is the staircase. The step is uAA wide
 // now; the tone either side of it is exactly what it was.
 float w=uAA;
 vec3 a=mix(mix(mix(upper?UPPER[0]:LOWER[0],upper?UPPER[4]:LOWER[4],
          smoothstep(RADII[4]-w,RADII[4]+w,radius)),upper?UPPER[8]:LOWER[8],
          smoothstep(RADII[8]-w,RADII[8]+w,radius)),upper?UPPER[12]:LOWER[12],
          smoothstep(RADII[12]-w,RADII[12]+w,radius));
 // GRAZING is byte-identical to UPPER and LOWER, so the grazing/steep split is
 // invisible today; the smoothstep keeps it a clean edge if the tables diverge.
 vec3 b=mix(mix(mix(GRAZING[0],GRAZING[4],smoothstep(RADII[4]-w,RADII[4]+w,radius)),
          GRAZING[8],smoothstep(RADII[8]-w,RADII[8]+w,radius)),GRAZING[12],
          smoothstep(RADII[12]-w,RADII[12]+w,radius));
 return mix(a,b,smoothstep(0.22-w,0.22+w,incidence));}""")

# ---- A2: the disc-plane band's two edges.
rep(""" float radius=length(p);
 vec2 q=mat2(cos(uTilt),-sin(uTilt),sin(uTilt),cos(uTilt))*p;
 col*=max(smoothstep(2.61,2.68,radius),1.0-step(0.052,abs(q.y)));""",
""" float radius=length(p);
 vec2 q=mat2(cos(uTilt),-sin(uTilt),sin(uTilt),cos(uTilt))*p;
 // The plane band is 0.052 either side of the disc plane - about 6 sprite px -
 // so its AA is capped at a fraction of its own half-width: uAA would soften a
 // line that thin into nothing. Its edges are near-diagonal, which is the worst
 // case for a hard step.
 float pw=min(uAA,0.019);
 col*=max(smoothstep(2.61,2.68,radius),1.0-smoothstep(0.052-pw,0.052+pw,abs(q.y)));""")

# ---- A3: the silk quantiser, plus the mask window it is multiplied by.
rep(""" // Three flat steps, not a continuous +/-42% multiplier: a continuous one is
 // texture, three steps are tone.
 float silkQ=floor(silk*3.0)/3.0;
 col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));""",
""" // Three flat steps, not a continuous +/-42% multiplier: a continuous one is
 // texture, three steps are tone. A floor() quantiser puts a 1-px staircase on
 // every step edge; each edge is now spread over 0.3 of a level instead.
 float s3=silk*3.0,qf=floor(s3);
 float silkQ=(qf+smoothstep(0.35,0.65,s3-qf))/3.0;
 col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));""")

# ---- A4 / A5: the photon ring - a wider shoulder, and an AA'd brightness split.
rep(""" float px=27.5/uRes.y, d=abs(radius-2.598);
 float hw=px*2.2;
 float ring=0.54*(1.0-smoothstep(hw*0.75,hw,d));
 ring*=mix(0.42,1.0,step(-0.01,p.y));
 col=mix(col,vec3(3.400000,3.500000,3.800000),ring);""",
""" float px=27.5/uRes.y, d=abs(radius-2.598);
 // Flat top, hard shoulders - but the shoulder has to be at least a sprite
 // pixel wide, or the rasteriser throws it away and the brightest thing in the
 // frame is also the raggedest. 0.55 px -> 1.2 px at the same stroke width.
 float hw=px*2.4;
 float ring=0.54*(1.0-smoothstep(hw*0.50,hw,d));
 ring*=mix(0.42,1.0,smoothstep(-0.01-uAA,-0.01+uAA,p.y));
 col=mix(col,vec3(3.400000,3.500000,3.800000),ring);""")

# ---- A6: the secondary-image gate.
rep(" float opacity=0.72*step(9.0,m0.x)*(1.0-smoothstep(0.16,0.22,m0.z));",
    " float opacity=0.72*smoothstep(9.0-uAA,9.0+uAA,m0.x)*(1.0-smoothstep(0.16,0.22,m0.z));")

# ---- A7: the shadow edge, five sprite px of halo -> two.
rep(""" float rp=length(p);
 float shadow=1.0-smoothstep(2.57,2.66,rp);""",
""" float rp=length(p);
 // Was 0.09 wide - five sprite px, which the upscale smeared into a ~10 px
 // halo around a shape the reference draws crisp. 2*uAA keeps it crisp while
 // still stepping over more than one sprite pixel.
 float shadow=1.0-smoothstep(2.61-uAA,2.61+uAA,rp);""")

# ---- the AA uniform location.
rep("""  const u={res:U('uRes'),tilt:U('uTilt'),incl:U('uIncl'),scale:U('uScale'),
           inner:U('uInner'),time:U('uTime'),tint:U('uTint')};""",
"""  const u={res:U('uRes'),tilt:U('uTilt'),incl:U('uIncl'),scale:U('uScale'),
           inner:U('uInner'),time:U('uTime'),tint:U('uTint'),aa:U('uAA')};""")

# ---- sprite cap: 1536 -> 2048 (the sprite has to grow with the hole).
rep("const lensRoll=0.34;",
    "const lensRoll=0.34;\n// The sprite buffer cap. 1536 was sized for a shadow of ~300 px; the shadow can\n// now reach ~600 px, and a buffer that does not grow with it turns into upscale.\nconst SPRITE_CAP=2048;")

# ---- pass uAA, and raise the cap.
rep("""  const want=clamp(Math.round(DRAW*2/128)*128,256,1536);
  if(G.cv.width!==want){G.cv.width=want;G.cv.height=want;g.viewport(0,0,want,want);G.S=want;}
  g.uniform2f(G.u.res,G.S,G.S);""",
"""  const want=clamp(Math.round(DRAW*2/128)*128,256,SPRITE_CAP);
  if(G.cv.width!==want){G.cv.width=want;G.cv.height=want;g.viewport(0,0,want,want);G.S=want;}
  g.uniform2f(G.u.res,G.S,G.S);
  // One AA half-width for every hard boundary in the sprite, in the shader's
  // radius units. Two floors, because neither alone is enough:
  //   - 1.2 SPRITE pixels: a transition narrower than a sprite pixel is
  //     discarded by the rasteriser, so the boundary would be a hard step again.
  //   - 1.5 SCREEN pixels, but ONLY while the sprite is being upscaled. The
  //     sprite is drawn at 2*DRAW, and an upscale that lands between sprite
  //     pixels is the staircase. When the sprite is drawn SMALLER than its
  //     buffer the bilinear filter already smooths it, and asking for 1.5
  //     screen pixels there would smear a small hole into a blob.
  const aaUp=Math.max(1,(DRAW*2)/G.S);
  g.uniform1f(G.u.aa,Math.max(1.2,1.5/aaUp)*27.5/G.S);""")

# ---- (b) the black hole is twice the size on screen. Physics is untouched.
rep("""            :kind===8?200+r()*280:1100;
   // A horizon sits well off to the side: scenery with gravity, not a roadblock.
   // On the course it swallowed the fleet every ~200 seconds. Its 1100 and its
   // offset are untouched: the capture radius was tuned against them.""",
"""            :kind===8?200+r()*280:2200;
   // A horizon sits well off to the side: scenery with gravity, not a roadblock.
   // On the course it swallowed the fleet every ~200 seconds. Its offset is
   // untouched. Its 1100 became 2200 (the user: "the event horizon could be more
   // exaggerated") - the drawn shadow and the lensing radius both scale with it,
   // so the lens warp stays registered with the disc. The capture factor moved
   // with it, .60 -> .30, which leaves the capture distance at exactly 660.""")

# ---- (b) the compensated capture factor. This is the ONLY line touched in
#         updateCapture, and the brief authorises exactly this compensation.
rep("   if(dist<m.r*.60){",
    "   if(dist<m.r*.30){")

# ---- guard against the `}};` class of typo before writing (README, 5 occurrences).
if "'}};\\n}'" in s or "}};\n}" in s:
    sys.exit("refusing to write: found a bare `}};` block terminator")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V26a applied:", len(s), "chars ->", out_p)
