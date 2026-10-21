"""V72b: a cloud may not become the whole plate.

v71 let the camera approach a nebula, and the first close pass showed the cost:
a billboard that covers the frame is a field of fog, whatever is painted on it.
The worlds already solve this at the other end - drawMass() dims a planet whose
disc grows past H*.42 - so the gas gets the same rule.

The cap is on the SCREEN radius, not the distance, so it behaves the same for
the big clouds and the small ones: past ~.40 of the frame height the gas starts
to dissolve, and by .62 it is gone. Flying through one now reads as entering and
leaving, not as a wash that never ends.

Run:  python -I v72b_sizefade.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """   const near = clamp((d - n.wr * 1.35) / (n.wr * 0.9), 0, 1);
   const far  = clamp((150000 - d) / 55000, 0, 1);
   const ng = novaGas(n, nova), al = clamp(n.alpha * wash * 2.9 * ng * near * far, 0, 0.94);"""
NEW = """   const near = clamp((d - n.wr * 1.35) / (n.wr * 0.9), 0, 1);
   const far  = clamp((150000 - d) / 55000, 0, 1);
   // The same rule the worlds get: a billboard that covers the plate stops
   // being a cloud. Measured against the frame, so it holds at every FOV.
   const cap = Math.min(W, H), big = clamp((cap * .62 - rad) / (cap * .22), 0, 1);
   const ng = novaGas(n, nova), al = clamp(n.alpha * wash * 2.9 * ng * near * far * big, 0, 0.94);"""
if src.count(OLD) != 1:
    sys.exit("anchor count=%d" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V72b written:", len(src), "chars")
