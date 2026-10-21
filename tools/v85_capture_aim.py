"""V85: the capture looks at the black hole.

captureCam() aimed at a point 42-65% of the way from the flock to the hole, so
that both would share the frame. The consequence was not a composition: the
orbit is measured from the look target, so with the target off the hole the eye
ended up 0.95 r from the centre - inside the disc's outer edge and inside the
photon sphere - and the shader (which assumes an observer outside the disc)
painted the plate brown. At 52 s the frame was a featureless amber sheet with
the shadow somewhere off the bottom of the plate.

Aimed at the hole the eye sits at 2.3-2.95 r, the shadow lands in the middle of
the frame, and the lensed disc reads as a disc. The flock is not in these frames;
at 85% of the plate there is no room for it, and the twelve-second blend in and
out still carries it.

Run:  python -I v85_capture_aim.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """ // Compose BOTH the paper crane migration flock in foreground and Gargantua in background
 const focusFactor = mix(0.42, 0.65, Math.sin(Math.PI * u));"""
NEW = """ // Aim at the hole itself. A look target between the flock and the hole put
 // the eye at .95 r - inside the disc's outer edge - and the shader, which
 // assumes an observer outside the disc, painted the frame a flat amber.
 const focusFactor = 1.0;"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V85 written:", len(src), "chars")
