"""V92: the same visibility rule for the thirteen named events.

drawEvent announced an event at 4,500 units whether or not it was on the plate.
A toast naming a thing the eye cannot find reads as a bug, which is exactly what
the skirmish annunciation was fixed for in v91; this applies the same screen
test to the event table.

Run:  python -I v92_event_toast.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = "    if (!ev.notified && distToFleet < 4500) {"
NEW = """    // Same rule as the skirmish: an event 4,500 units to the side is still
    // off the plate, and a named thing the eye cannot find reads as a bug.
    if (!ev.notified && distToFleet < 4500 &&
        q[0] > -120 && q[0] < W + 120 && q[1] > -120 && q[1] < H + 120) {"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V92 written:", len(src), "chars")
