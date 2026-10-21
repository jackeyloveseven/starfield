"""V73: a dolly is a move, not a twitch.

Measured over five minutes, the director's orbit radius ran

    1284 1024 768 1480 1224 2063 1643 1212 1480 964 937 3098 1789 ...

in consecutive shots - a 3.3x swing every sixteen seconds, both ways. That is
the "camera pumps in and out" the playtesters reported, and it is also why a
world seems to change size while nothing about it changed.

The lens table is the vocabulary and it stays. Each plan is now compressed
around its OWN median, so the near shots stay near and the far shots stay far,
but no single cut can cross the whole table. A chained slew limit was tried
first and rejected: with nothing pulling the plan back, it random-walked the
orbits out to 6,400.

Run:  python -I v73_shots.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = "  result.push(p);previous=yaw;\n }\n plans.set(c,result);return result;"
NEW = ("  result.push(p);previous=yaw;\n }\n"
       " // Dolly compression, around this plan's own median. Ordering survives -\n"
       " // the intimate shots are still the nearest and the reveal still the\n"
       " // farthest - but the span a single cut can cross is halved, which is\n"
       " // the difference between a camera move and a stutter.\n"
       " const ds=result.map(p=>p.distance).sort((a,b)=>a-b);\n"
       " const med=(ds[2]+ds[3])*.5;\n"
       " for(const p of result)p.distance=med*Math.pow(p.distance/med,.52);\n"
       " plans.set(c,result);return result;")
if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V73 written:", len(src), "chars")
