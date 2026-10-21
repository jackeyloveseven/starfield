"""V80: do not aim at a speck.

The director biases the gaze toward the nearest world ahead, with no test of
whether that world will read on the plate or whether it is even roughly in front.
Two of the six frames in the ten-minute sweep were an empty star field with the
flock at the edge: the camera was dutifully looking at a body 30,000 units off
the bow, 2,000 to the side.

A world now has to be ahead within 35 degrees and subtend at least .05 of the
focal length (about 50 px at 900p) before it can pull the gaze. Otherwise the
corridor stays the subject, which is where the birds are.

Run:  python -I v80_gaze.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """   const dz = m.z - travel;
   if(dz < -1200 || dz > 32000) continue;
   const dx = m.x - routeX(travel), dy = m.y - courseY(travel);
   const d = Math.hypot(dx, dy, dz);
   if(d < gd){gd = d; gm = m;}"""
NEW = """   const dz = m.z - travel;
   if(dz < -1200 || dz > 32000) continue;
   const dx = m.x - routeX(travel), dy = m.y - courseY(travel);
   const d = Math.hypot(dx, dy, dz);
   // A speck 30,000 units off the bow is not a subject. It has to be roughly
   // ahead and big enough to read on the plate before it may pull the gaze -
   // otherwise the frame is empty sky with the flock pushed to the edge.
   const ang = Math.atan2(Math.hypot(dx, dy), Math.max(1, dz));
   if(ang > .62 || m.r / Math.max(1, d) < .05) continue;
   if(d < gd){gd = d; gm = m;}"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V80 written:", len(src), "chars")
