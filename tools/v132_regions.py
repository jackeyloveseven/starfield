"""V132: give the five regions a different geometry and motion, not a different
star count or a different hue.

The two previous attempts (scaling `limit`, returning early from the nebula loop
in ABYSS) changed 0.13 and 0.36 mean |dL| whole-frame: a starfield with fewer
points and a sky without clouds is still the same composition. This patch moves
things instead:

  1. camera pitch / roll offset from the region mix (auto camera only)
  2. the paper's horizon stop moves up or down per region
  3. nebula screen scale (INKWASH large, PAPER small, ABYSS absent as before)
  4. Milky Way band width AND its position along the band-plane normal
  5. bright-star diffraction cross size
  6. warp/sling trail length, and dust mote fall speed

Everything is driven from `regionGeom(paperW(...))`, so crossings interpolate;
nothing here touches the star count (`limit`) or an RGB value.

Measured with shot.py (seed 1a2b, 1600x900, seek 5, --at <region>) and
framecompare.py, before vs after this patch, same region:

  region    mean |dL|    |dL|>30
  PAPER      7.37         1.41 %
  INKWASH    9.54         6.51 %
  FOIL      10.51         8.60 %
  CORE       7.00         0.30 %   (see caveat)
  ABYSS      1.63         0.37 %   (see caveat)

  The WebGL hole/bloom layer is not always ready at the same instant in
  headless Chrome; a re-shot PAPER frame differs from the first by 0.11 mean.
  The numbers above are the final-artifact run.

  CORE at --at 3 renders a gradient-only frame with no star layer before and
  after this patch, so its number measures the horizon stop alone.
  ABYSS is under 2 because the existing v129 early return in drawSky skips the
  stars and the band in the void; only the horizon and the ships can move there.

Adjacent-region whole-frame comparisons after the patch (same seed 1a2b, seek 5,
different departure routes, so these include the route's own scene difference):
  PAPER vs ABYSS    24.85 mean, 33.73 % >30   (baseline 28.19 / 45.62)
  INKWASH vs FOIL   31.60 mean, 36.18 % >30   (baseline 28.80 / 36.35)

  python -I v132_regions.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def sub(old, new, tag):
    n = src.count(old)
    if n != 1:
        sys.exit("%s: count=%d (want 1)" % (tag, n))
    return src.replace(old, new, 1)


# 1. continuous region weights + the geometry table -------------------------
src = sub(
    " p.front=Math.sin(Math.PI*t)*((a===4||b===4)?1:.38);\n return p;\n}",
    " p.front=Math.sin(Math.PI*t)*((a===4||b===4)?1:.38);\n return p;\n}\n"
    "/* v132: PAPER is the one region with no positive mix term - it is the\n"
    " * remainder. The geometry is keyed off these continuous weights, so a\n"
    " * crossing interpolates instead of stepping. No counts, no hues. */\n"
    "function paperW(p){return clamp(1-(p.wash||0)-(p.shimmer||0)-(p.core||0)-(p.void||0),0,1);}\n"
    "function regionGeom(p){\n"
    " const pa=paperW(p),wa=p.wash||0,sh=p.shimmer||0,co=p.core||0,vo=p.void||0;\n"
    " return {\n"
    "  pitch: pa*.105-wa*.025-sh*.085+co*.170-vo*.195,\n"
    "  roll:  pa*.022-wa*.040+sh*.055-co*.065+vo*.010,\n"
    "  horizon: pa*-.180+wa*.120+sh*-.050+co*.220+vo*.040,\n"
    "  neb:   clamp(pa*.62+wa*1.35+sh*.88+co*1.15-vo*.50,.35,1.6),\n"
    "  bandS: clamp(pa*.65+wa*.95+sh*.30+co*1.05-vo*.55,.08,1.25),\n"
    "  bandG: pa*.060-wa*.150+sh*.100-co*.020+vo*.200,\n"
    "  cross: clamp(pa*1.0+wa*1.25+sh*1.6+co*2.2-vo*.6,.25,2.4)\n"
    " };\n"
    "}",
    "regionGeom")

# 2. camera pose offset, after the capture pose so captures carry it too -----
src = sub(
    "  lookTarget = [mix(lookTarget[0], c.tx, c.blend), mix(lookTarget[1], c.ty, c.blend), mix(lookTarget[2], c.tz, c.blend)];\n }",
    "  lookTarget = [mix(lookTarget[0], c.tx, c.blend), mix(lookTarget[1], c.ty, c.blend), mix(lookTarget[2], c.tz, c.blend)];\n }\n"
    "\n"
    " // v132: the region moves the camera, not just its ink. Pitch and roll are\n"
    " // the differences that survive a frame with no palette-bearing object in\n"
    " // it. Auto only: a hand-driven camera keeps the pose the viewer chose.\n"
    " if(autoCamera && started){const _rg=regionGeom(currentPalette);goal.pitch=clamp(goal.pitch+_rg.pitch,-.20,1.45);goal.roll+=_rg.roll;}",
    "camera-offset")

# 3. horizon stop position ---------------------------------------------------
src = sub(
    " const p=currentPalette,nova=novaState(),g=ctx.createLinearGradient(0,0,0,H);",
    " const p=currentPalette,nova=novaState(),g=ctx.createLinearGradient(0,0,0,H);\n"
    " // v132: where the paper's horizon sits is a composition choice per region.\n"
    " const _rg=regionGeom(p);",
    "horizon-decl")

src = sub(
    " g.addColorStop(0,css(p.sky));g.addColorStop(.55,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.paper,.58)));",
    " g.addColorStop(0,css(p.sky));g.addColorStop(clamp(.55+_rg.horizon,.30,.80),css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.paper,.58)));",
    "horizon-stop")

# 4. nebula screen scale -----------------------------------------------------
src = sub(
    "   const rad = n.wr * q[3];",
    "   const rad = n.wr * q[3] * _rg.neb;",
    "nebula-scale")

# 5. Milky Way band: width and position along the plane normal --------------
src = sub(
    "   const a2=i/260*TAU,d=bdir(Math.cos(a2),Math.sin(a2),0),q=skyPoint(d);",
    "   const a2=i/260*TAU,d=bdir(Math.cos(a2),Math.sin(a2),_rg.bandG),q=skyPoint(d);",
    "band-ribbon")

src = sub(
    "    const d1=bdir(Math.cos(a2),Math.sin(a2),0),d2=bdir(Math.cos(a2+sp),Math.sin(a2+sp),0);",
    "    const d1=bdir(Math.cos(a2),Math.sin(a2),_rg.bandG),d2=bdir(Math.cos(a2+sp),Math.sin(a2+sp),_rg.bandG);",
    "band-glints")

src = sub(
    "    const d=bdir(st.ca,st.sa,st.g),q=skyPoint(d);if(!q)continue;",
    "    const d=bdir(st.ca,st.sa,st.g+_rg.bandG),q=skyPoint(d);if(!q)continue;",
    "band-stars-drag")

src = sub(
    "    const q=skyPoint(bdir(st.ca,st.sa,st.g));if(!q)continue;",
    "    const q=skyPoint(bdir(st.ca,st.sa,st.g+_rg.bandG));if(!q)continue;",
    "band-stars-still")

src = sub(
    "   for(const L of [[300,.012],[120,.024],[40,.050]]){",
    "   for(const L of [[300*_rg.bandS,.012],[120*_rg.bandS,.024],[40*_rg.bandS,.050]]){",
    "band-width")

# 6. bright-star cross size --------------------------------------------------
src = sub(
    "   else{ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);}\n"
    "  }else{ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);}",
    "   else{ctx.moveTo(x-r*3.2*_rg.cross,y);ctx.lineTo(x+r*3.2*_rg.cross,y);ctx.moveTo(x,y-r*3.2*_rg.cross);ctx.lineTo(x,y+r*3.2*_rg.cross);}\n"
    "  }else{ctx.moveTo(x-r*3.2*_rg.cross,y);ctx.lineTo(x+r*3.2*_rg.cross,y);ctx.moveTo(x,y-r*3.2*_rg.cross);ctx.lineTo(x,y+r*3.2*_rg.cross);}",
    "star-cross")

# 7. warp/sling trail length -------------------------------------------------
src = sub(
    " const eps=burst*(lowQuality?.034:.075);",
    " // v132: trail LENGTH is geometry, and it is a region property. Only the\n"
    " // warp/sling drag is scaled; a still sky keeps its still-point stars.\n"
    " const _trail=clamp(.50+(currentPalette.wash||0)*.85+(currentPalette.core||0)*.55+(currentPalette.shimmer||0)*.20-(currentPalette.void||0)*.45,.22,1.6);\n"
    " const eps=burst*(lowQuality?.034:.075)*_trail;",
    "trail-length")

# 8. dust-mote fall speed ----------------------------------------------------
src = sub(
    "p.y-=(3+pal.wash*15)*dt;",
    "p.y-=(3+pal.wash*15+pal.shimmer*9-pal.void*1.5)*dt;",
    "dust-fall")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V132 written:", out_p, len(src), "chars")
