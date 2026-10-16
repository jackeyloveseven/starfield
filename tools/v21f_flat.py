"""v21f_flat -- the black hole as FLAT GRAPHIC ART, and rare.

Two complaints, verbatim:

  "太糊了全是像素点" / "黑洞粒子特效还是太糊太糊了"
  (too blurry, all pixel dots / the black hole particle effect is still far too
   blurry)

  "减少除事件视界外黑洞出现频率"
  (reduce how often black holes appear, apart from the event horizon)

The reference the user pointed at (cosmicbroth.com) is NOT a render. Its disc is
broad bands of near-flat colour with crisp boundaries, a clean geometric dark
shadow, and a thin sharp photon ring. Nothing on it is soft. The current sprite
is soft for four independent reasons, each fixed here:

  F1  the 18-stop radial LUT is linearly interpolated and its UPPER/GRAZING
      split is a smoothstep cross-fade -> the gradient is manufactured. Replaced
      with four flat tone steps and a hard incidence threshold.
  F2  the fbm anti-aliasing window was calibrated a full octave late, so
      sub-Nyquist octaves (periods of 1.75 / 0.87 sprite px) were passed through
      at full amplitude. That is the "pixel dots". Window moved to
      smoothstep(0.25,0.50).
  F3  the disc density was a 5-octave fbm raised to 2.25, times a second fbm -
      the body of the "gas". Removed for the flat route; one low octave of edge
      wobble remains so a band boundary reads as drawn by hand.
  F4  the photon ring was a 0.76 px core plus a sigma=2.5 px gaussian halo, both
      then smeared by the 24 px full-frame bloom. Replaced with a flat-topped
      hard-shouldered stroke, painted with mix rather than added.
  F5  the shadow was a glow, not a shape: alpha=max(shadow,lum*2.2) with
      uInner=2.2 below the shadow radius, so plasma lit it from inside. uInner
      raised above the shadow and two flat blue steps filled in.
  F6  the outer fade was 2.6x wider than the reference's. Narrowed.
  F7  the "silk" term was a per-pixel +/-42% brightness multiplier. Quantised.
  F8  the primary image's occlusion of the secondary was a sigma=5 gaussian.
      Replaced with a hard step.
  F10 the palette was warm amber; the reference is neutral white disc, blue
      shadow. Band colours replaced.
  F11 the inclination was 11 deg off the plane, collapsing the disc to a band.

And (b) the schedule: a horizon every seventh chunk is too common. Every
nineteenth - still a fixed modulus, so they stay evenly spaced, which is the fix
that stopped them clumping in the first place.

Owns: the GLSL_HOLE string, every drawHole uniform, the sprite-size line, and
the chunk() horizon schedule line. Does NOT touch the capture tuning: r stays
1100 and the capture test stays dist < m.r*0.60.

Run:  python -I v21f_flat.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v21f_flat.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- (b) FREQUENCY: every nineteenth chunk, not every seventh.
# A fixed modulus, not a die roll: the schedule is what keeps them evenly spaced.
rep(""" // One horizon per chunk at most, and rare outside the abyss: an encounter
 // should be an event, not scenery.
 // A horizon is on a schedule, not a die roll. It used to be r() < .07+void*.40
 // per chunk, which clumped them hard in the void and left long stretches with
 // none at all - which reads as "the black holes are unevenly distributed".
 // Every seventh chunk is a rhythm you can feel instead.
 const horizon=(k%7===0);""",
""" // One horizon per chunk at most, and rare outside the abyss: an encounter
 // should be an event, not scenery.
 // A horizon is on a schedule, not a die roll. It used to be r() < .07+void*.40
 // per chunk, which clumped them hard in the void and left long stretches with
 // none at all - which reads as "the black holes are unevenly distributed".
 // Every seventh chunk was still too common for an event; every nineteenth is a
 // rhythm you can feel. Still a fixed modulus, so the spacing stays even.
 const horizon=(k%19===0);""")

# ---- F2: the anti-aliasing window, one octave late -> sub-Nyquist dots.
rep("""float fbmP(vec2 p,float period,float footprint){float n=0.0,amp=0.52;
 for(int i=0;i<5;i++){float aa=1.0-smoothstep(0.65,2.1,footprint);""",
"""float fbmP(vec2 p,float period,float footprint){float n=0.0,amp=0.52;
 // Period >= 4 px kept whole, <= 2 px dropped whole. The old (0.65,2.1) window
 // was the inverse of the period, so 1.54 px still passed at full amplitude and
 // only 0.48 px was culled: a full octave of sub-Nyquist detail, which cannot be
 // imaged and can only alias into the screen-scale dots.
 for(int i=0;i<5;i++){float aa=1.0-smoothstep(0.25,0.50,footprint);""")

# ---- F10: the tone tables. Four flat bands, neutral-to-cool, not warm amber.
# Every entry of a band is the same value, so the flat steps survive any index
# that lands inside a band.
rep("""const vec3 UPPER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.255777,0.166983,0.130913),vec3(0.137799,0.112648,0.095081),
 vec3(0.264506,0.176011,0.157152),vec3(0.454691,0.277004,0.215472),
 vec3(0.804536,0.516623,0.372846),vec3(1.150769,0.757494,0.551068),
 vec3(1.673280,1.122596,0.815232),vec3(1.971796,1.355241,0.988191),
 vec3(1.381316,0.953994,0.710846),vec3(1.212427,0.769973,0.538510),
 vec3(0.632655,0.452315,0.354578),vec3(0.504023,0.315987,0.231414),
 vec3(0.303187,0.201846,0.163637),vec3(0.012821,0.011026,0.008847),
 vec3(0.001271,0.001093,0.000877),vec3(0.000438,0.000377,0.000303),
 vec3(0.000001,0.000000,0.000000),vec3(0.000000,0.000000,0.000000));""",
"""const vec3 UPPER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000));""")

rep("""const vec3 LOWER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.000000,0.000000,0.000000),vec3(0.233461,0.154232,0.134631),
 vec3(0.392270,0.241803,0.181831),vec3(0.553336,0.335322,0.237910),
 vec3(0.720745,0.450136,0.316339),vec3(0.930359,0.597947,0.426111),
 vec3(1.302152,0.882694,0.646073),vec3(1.496130,1.043103,0.770311),
 vec3(1.466698,1.060739,0.801137),vec3(1.110652,0.758425,0.554937),
 vec3(0.974833,0.643935,0.452933),vec3(0.489304,0.319002,0.232886),
 vec3(0.459541,0.279972,0.193965),vec3(0.207503,0.128341,0.098463),
 vec3(0.019420,0.016701,0.013400),vec3(0.006035,0.005190,0.004164),
 vec3(0.002372,0.002040,0.001636),vec3(0.000000,0.000000,0.000000));""",
"""const vec3 LOWER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000));""")

rep("""const vec3 GRAZING[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.501431,0.383656,0.323421),vec3(0.594023,0.435577,0.352526),
 vec3(0.444722,0.360840,0.306858),vec3(0.530725,0.417036,0.366201),
 vec3(0.889255,0.628932,0.505206),vec3(1.389388,0.980254,0.755381),
 vec3(1.798031,1.323533,1.027938),vec3(2.046291,1.551282,1.215553),
 vec3(2.129368,1.670683,1.322172),vec3(1.976563,1.561564,1.261436),
 vec3(1.794290,1.370349,1.106133),vec3(1.308990,0.979743,0.789233),
 vec3(0.924975,0.641772,0.498919),vec3(0.479225,0.351105,0.285022),
 vec3(0.200028,0.149638,0.130981),vec3(0.054028,0.046464,0.037279),
 vec3(0.011962,0.010287,0.008254),vec3(0.000000,0.000000,0.000000));""",
"""const vec3 GRAZING[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.140000,0.170000,0.420000),vec3(0.140000,0.170000,0.420000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(0.300000,0.350000,0.840000),vec3(0.300000,0.350000,0.840000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(1.100000,1.120000,1.200000),vec3(1.100000,1.120000,1.200000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000),
 vec3(0.660000,0.720000,0.960000),vec3(0.660000,0.720000,0.960000));""")

# ---- F1: stepped LUT, four flat bands, hard incidence threshold.
rep(""" int k=0;
 for(int i=0;i<PROFILE_N-2;i++) if(radius>RADII[i+1]) k=i+1;
 float f=clamp((radius-RADII[k])/(RADII[k+1]-RADII[k]),0.0,1.0);
 vec3 a=upper?mix(UPPER[k],UPPER[k+1],f):mix(LOWER[k],LOWER[k+1],f);
 vec3 b=mix(GRAZING[k],GRAZING[k+1],f);
 return mix(a,b,1.0-smoothstep(0.12,0.32,incidence));}""",
""" int k=0;
 for(int i=0;i<PROFILE_N-2;i++) if(radius>RADII[i+1]) k=i+1;
 // Flat art, not a volume. The 18 fitted stops collapse to four flat tones,
 // sampled at their heads with no interpolation between them: the reference's
 // crispness is four tone steps with hard boundaries, not a smooth radial ramp.
 int band=min(k/4,PROFILE_N/4-1),kk=band*4;
 vec3 a=upper?UPPER[kk]:LOWER[kk];
 vec3 b=GRAZING[kk];
 // A hard threshold, not a cross-fade: a grazing crossing and a steep one are
 // two different tones, and blending them is what manufactured the gradient.
 return incidence<0.22?b:a;}""")

# ---- F3: the disc is flat. One low octave of edge wobble, no per-pixel fbm.
rep(""" float r=d.x; if(r<0.1)return vec3(0.0);
 float phi=d.y,a=phi/TAU,t=uTime/8.0;
 float inner=1.0-smoothstep(3.5,9.0,r);
 float n0=noiseP(vec2(r*1.7,a*48.0-t*12.0),12.0);
 float n1=noiseP(vec2(r*1.7+19.6,a*48.0-t*24.0),12.0);
 float swirl=mix(n0,n1,inner*0.65);
 float finewarp=noiseP(vec2(r*5.3,a*64.0-t*32.0+r*0.3),16.0);
 float rw=r+(swirl-0.5)*0.25+(finewarp-0.5)*0.055;
 float footprint=abs(dFdx(r))+abs(dFdy(r));
 float filament=fbmP(vec2(rw*8.0,a*60.0-t*15.0+rw*0.18),15.0,footprint*8.0);
 float filament2=fbmP(vec2(rw*2.0+72.0,a*128.0-t*64.0),32.0,footprint*2.0);
 float density=pow(0.10+1.64*filament,2.25);
 density*=0.65+0.74*filament2;
 float front=pow(max(0.0,sin(phi)),8.0)*(1.0-smoothstep(0.12,0.32,d.z));
 float frontBoost=1.0+1.9*front*smoothstep(6.0,9.5,r);
 float outerFade=1.0-smoothstep(11.8,15.0,r);
 return fittedRadiance(r,d.z,side>=0.0)*(density/0.84)*frontBoost*outerFade;}""",
""" float r=d.x; if(r<0.1)return vec3(0.0);
 float phi=d.y,a=phi/TAU;
 // No per-pixel texture: the reference is flat art and the multi-octave fbm was
 // the mush. One low octave of edge wobble only, so a band boundary reads as
 // drawn by hand rather than as a compass circle.
 float warp=noiseP(vec2(a*6.0,r*0.9),6.0);
 float rw=r+(warp-0.5)*0.22;
 float front=pow(max(0.0,sin(phi)),8.0)*(1.0-smoothstep(0.12,0.32,d.z));
 float frontBoost=1.0+0.35*front*smoothstep(6.0,9.5,r);
 // The reference's outer fade is 8.8% of the shadow radius, not 17%.
 float outerFade=1.0-smoothstep(13.4,14.5,r);
 return fittedRadiance(rw,d.z,side>=0.0)*frontBoost*outerFade;}""")

# ---- F8: hard occlusion instead of a sigma=5 gaussian veil.
rep(""" float opacity=0.72*exp(-pow((m0.x-13.0)/5.0,2.0))*(1.0-smoothstep(0.12,0.32,m0.z));""",
""" // A hard shoulder, not a gaussian: the secondary image should appear at a
 // radius, not fade in through a 280 px veil.
 float opacity=0.72*step(9.0,m0.x)*(1.0-smoothstep(0.16,0.22,m0.z));""")

# ---- F12: keep the near-side band through the shadow sharp.
rep(""" col*=max(smoothstep(2.61,2.68,radius),1.0-smoothstep(0.040,0.058,abs(q.y)));""",
""" col*=max(smoothstep(2.61,2.68,radius),1.0-step(0.052,abs(q.y)));""")

# ---- F7: the silk multiplier, quantised to three levels and de-contrasted.
rep(""" col*=mix(1.0,0.58+0.84*silk,smoothstep(0.018,0.055,abs(q.y)));""",
""" // Three flat steps, not a continuous +/-42% multiplier: a continuous one is
 // texture, three steps are tone.
 float silkQ=floor(silk*3.0)/3.0;
 col*=mix(1.0,0.78+0.44*silkQ,smoothstep(0.018,0.030,abs(q.y)));""")

# ---- F4: the photon ring is a stroke, not a gaussian glow.
rep(""" // The photon ring, at the critical impact parameter sqrt(27)/2.
 float px=27.5/uRes.y, d=abs(radius-2.598);
 float ring=(1.0-smoothstep(px*0.08,px*0.76,d))*0.54;
 ring+=0.055*exp(-pow(d/(px*2.5),2.0));
 ring*=mix(0.42,1.0,smoothstep(-0.01,0.03,p.y));
 col+=ring*vec3(1.0,0.64,0.46);""",
""" // The photon ring, at the critical impact parameter sqrt(27)/2 - a STROKE.
 // Flat top, hard shoulders, painted with mix rather than added, so the tonemap
 // cannot flatten it into a gradient.
 float px=27.5/uRes.y, d=abs(radius-2.598);
 float hw=px*2.2;
 float ring=0.54*(1.0-smoothstep(hw*0.75,hw,d));
 ring*=mix(0.42,1.0,step(-0.01,p.y));
 col=mix(col,vec3(3.400000,3.500000,3.800000),ring);""")

# ---- F5: the shadow is a filled shape, not a glowing void.
rep(""" float shadow=1.0-smoothstep(2.55,2.80,length(p));
 float alpha=max(shadow,clamp(lum*2.2,0.0,1.0));
 fragColor=vec4(tone*alpha,alpha);""",
""" // Two flat blue steps, not a black glow. uInner now sits above the shadow
 // radius, so no plasma leaks in to light it from inside; the only thing within
 // is the near-side disc band crossing the front, which the lum gate preserves.
 float rp=length(p);
 float shadow=1.0-smoothstep(2.57,2.66,rp);
 vec3 shadowCol=mix(vec3(0.045000,0.060000,0.172000),vec3(0.033000,0.045000,0.120000),step(2.05,rp));
 vec3 outc=tone+shadowCol*shadow*(1.0-clamp(lum*3.0,0.0,1.0));
 float alpha=max(shadow,clamp(lum*2.2,0.0,1.0));
 fragColor=vec4(outc*alpha,alpha);""")

# ---- F5 (uniform) and F11 (composition): uInner above the shadow; more tilt.
rep("  g.uniform1f(G.u.inner,2.2);",
    "  g.uniform1f(G.u.inner,2.62);")

rep("  g.uniform1f(G.u.incl,0.20);",
    "  g.uniform1f(G.u.incl,0.45);")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V21f applied:", len(s), "chars ->", out_p)
