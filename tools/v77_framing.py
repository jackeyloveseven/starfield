"""V77: keep the flock inside the frame it is actually drawn into.

The look target is clamped to a cone around the corridor so the subject cannot
leave the plate. The clamp was `max(800, distance*.55)` - 29 degrees - but the
vertical half-angle of a 16:9 frame at focal = H*1.12 is only 24 degrees, and
the 800 floor made it worse on close shots (at distance 880 the cap was 800,
i.e. 42 degrees). One frame in the ten-minute sweep had the flock entirely off
screen while the HUD still read "14 CRAFT".

.42 of the orbit radius is 22.8 degrees: inside the frame at every aspect ratio
the piece is shown at, and still enough freedom to put a world off centre.

Run:  python -I v77_framing.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = "  const d=Math.hypot(dx,dy,dz),cap=Math.max(800,camera.distance*.55);"
NEW = ("  // .42 of the orbit radius is 22.8 deg. The vertical half-frame is 24 deg\n"
       "  // at 16:9 (focal = H*1.12), so the old 29 deg cap - and the 800 floor\n"
       "  // under it - could put the whole flock outside a frame that still read\n"
       "  // \"14 CRAFT\" in the corner.\n"
       "  const d=Math.hypot(dx,dy,dz),cap=Math.max(260,camera.distance*.42);")
if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V77 written:", len(src), "chars")
