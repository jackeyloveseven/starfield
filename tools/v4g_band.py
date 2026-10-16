"""V4g: aim the band through the frame.

With BAND_REF=[.70,.50,-.14] the band's normal came out at (.769,.487,-.414), so
the great circle sat ~24 degrees off the view axis - off the top and the right of
a ~50x30 degree frame. Anchor it to the forward direction instead, tilted, so it
runs lower-right to upper-left across the middle of the frame.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = "const BAND_U=[.26,.44,1],BAND_REF=[.70,.50,-.14];"
b = "const BAND_U=[0,0,1],BAND_REF=[.574,.819,0];"
if s.count(a) != 1:
    sys.exit("band basis: count=%d" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4g applied:", len(s), "bytes")
