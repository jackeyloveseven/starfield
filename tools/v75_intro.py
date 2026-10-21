"""V75: the title screen must show the subject.

The intro is the first thing anyone sees, and it was an empty sky. The cause is
not the camera pose - it is the director's world-seeking: it biases the look
target up to 42% of the way to a world up to 32,000 units ahead, which leaves
the flock ~13,000 units off the look target, i.e. 83 degrees outside a 45 degree
frame. The cranes were being drawn; they were just never in shot.

The bias only makes sense once the flight has started. Before that the camera
should hold the corridor, which is where the flock is.

Run:  python -I v75_intro.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = " if(autoCamera && !capturePhase && (!skimRes || !skimRes.active) && !hm && activeMasses.length){"
NEW = " if(started && autoCamera && !capturePhase && (!skimRes || !skimRes.active) && !hm && activeMasses.length){"
if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V75 written:", len(src), "chars")
