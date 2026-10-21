"""V74: rings are bands, not four flat fills.

A close ringed pass at 5,800 units put the camera inside the ring system, and
the frame became a solid amber field - the same fog the nebulae had, from the
same cause: one flat fill stretched past the point where a surface reads as a
surface. Saturn's answer is density: dozens of bands, gaps inside bands, and a
plane you can see stars through.

Each of the four macro bands is cut into five sub-bands with their own density,
and the whole ring is thinned as it grows past .75 of the frame height so a
close pass reads as gas and ice rather than paint.

Run:  python -I v74_rings.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """      for (const rL of ringLayers) {
        ctx.beginPath();
        ctx.arc(0, 0, rad * rL.r1, a0, a1, false);
        ctx.arc(0, 0, rad * rL.r0, a1, a0, true);
        ctx.closePath();
        ctx.fillStyle = css(rL.c, rL.a);
        ctx.fill();
      }"""

NEW = """      // Density inside each macro band. Five sub-bands with their own alpha
      // is the minimum that stops a close pass from printing as one flat fill;
      // the gaps fall where the hash puts them, never at a regular pitch.
      const veil = 1 - .45 * clamp(rad / (H * .75), 0, 1);
      for (const rL of ringLayers) {
        for (let k = 0; k < 5; k++) {
          const u0 = rL.r0 + (rL.r1 - rL.r0) * k / 5;
          const u1 = rL.r0 + (rL.r1 - rL.r0) * (k + 1) / 5;
          const dens = .55 + hash(hb, 40 + Math.round(rL.r0 * 100), k) * .9;
          ctx.beginPath();
          ctx.arc(0, 0, rad * u1, a0, a1, false);
          ctx.arc(0, 0, rad * u0, a1, a0, true);
          ctx.closePath();
          ctx.fillStyle = css(rL.c, Math.min(.92, rL.a * dens * veil));
          ctx.fill();
        }
      }"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V74 written:", len(src), "chars")
