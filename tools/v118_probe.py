"""V118: expose the three things a headless probe cannot otherwise see.

  warpGear   the current fast-forward gear (0/1/2)
  departing  true while the departure dolly is easing
  clips      how many narrator clips are embedded

None of this is UI; it exists so the behaviours added in v109-v117 can be
verified without a phone. `clips` also doubles as a cheap integrity check after
the OTA merges a new page.

Run:  python -I v118_probe.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old = "postMs:+(postMs).toFixed(2),postOn,holeGL:!!holeGL,"
new = ("postMs:+(postMs).toFixed(2),postOn,holeGL:!!holeGL,"
       "warpGear:WarpDrive.gearIndex,departing:!!__depart,"
       "clips:(typeof NarratorClips!=='undefined')?Object.keys(NarratorClips).length:0,")
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V118 written:', len(src), 'chars')
