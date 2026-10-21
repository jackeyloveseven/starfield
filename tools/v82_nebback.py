"""V82: gas belongs behind the solid sky, not in front of the black hole.

V71 put the nebulae into the depth queue so worlds would occlude them. That was
right for one direction and wrong for the other: a 15,000-unit cloud between the
camera and Gargantua now paints over the hole. The 事件视界 departure frame is a
flat pale-yellow plate - the showpiece is under a sheet of amber gas.

Nebulae are gas; a world in front of one should still hide it, but a cloud in
front of a world should read as haze, not as paint. They are enqueued behind
every solid (d + 1e6) and keep their world position, scale, parallax and roll.
The one thing lost is gas occluding a world that is farther than it, which the
eye reads as atmosphere anyway.

Run:  python -I v82_nebback.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """   // Enqueued at its own depth, so a world nearer than the cloud prints over
   // it and one behind it does not. This is the whole point of the rewrite.
   queue.push({type:4, d, alpha:1, fn:()=>{"""
NEW = """   // Enqueued behind every solid. A world in front of a cloud still hides it;
   // a cloud in front of a world reads as haze instead of paint. With a true
   // depth the 事件视界 departure was a flat amber plate - the hole was under a
   // sheet of gas 15,000 units out.
   queue.push({type:4, d:1e6+d, alpha:1, fn:()=>{"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V82 written:", len(src), "chars")
