"""v18h_hole_shadow -- rescale GLSL_HOLE's shadow/ring masks out of the stale
uScale=0.654 units into the current uScale=27.5 units.

Reads the artwork, asserts each replaced string occurs exactly once, and writes
a working copy (never the original).

Run:  python -I v18h_hole_shadow.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

EDITS = [
    # p is already the impact parameter in rs (uScale=27.5), so the extra 27.5
    # left over from the reference's unscaled emission.frag p is a double scale.
    (" float radius=length(p)*27.5;", " float radius=length(p);"),
    # The shadow edge is at length(p)=CRIT=2.598, not 0.0949 (the old 0.654
    # scale).  With the stale mask the sprite was transparent inside the photon
    # sphere, so the sky showed through where the black shadow should be.
    (" float shadow=1.0-smoothstep(0.093,0.102,length(p));",
     " float shadow=1.0-smoothstep(2.55,2.80,length(p));"),
]

for a, b in EDITS:
    n = src.count(a)
    assert n == 1, f"expected 1 occurrence, found {n}: {a!r}"
    src = src.replace(a, b)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("wrote", out_p)
