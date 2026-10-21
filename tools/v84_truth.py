"""V84: correct the note left by v82.

v82 blamed the flat 事件视界 frame on gas painting over the hole. That was wrong:
the capture camera was being pulled back by the flock clamp (fixed in v83). The
behaviour v82 introduced is still wanted - gas must not paint over the showpiece
- but the code must not carry a false explanation.

Run:  python -I v84_truth.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """   // Enqueued behind every solid. A world in front of a cloud still hides it;
   // a cloud in front of a world reads as haze instead of paint. With a true
   // depth the 事件视界 departure was a flat amber plate - the hole was under a
   // sheet of gas 15,000 units out."""
NEW = """   // Enqueued behind every solid. A world in front of a cloud still hides it;
   // a cloud in front of a world must read as haze, not as a sheet of paint
   // over the one object the whole piece is built around. (The flat 事件视界
   // frame that prompted this was the look clamp, not the gas - see the
   // capture exemption below - but a cloud between the eye and the hole at
   // 15,000 units out would do exactly the same thing.)"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V84 written:", len(src), "chars")
