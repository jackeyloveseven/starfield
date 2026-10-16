"""V4h: the band was drawing at 22% alpha and invisible.

bw was .30 + wash*.85 + core*.40, and `wash`/`core` are 0 in every region except
1 and 3 - so outside those the whole band ran at a base of .30. The Milky Way
should be present the length of the corridor and only modulated by the region,
not switched on by it.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = " const bw=.30+p.wash*.85+p.core*.40;"
b = " const bw=.62+p.wash*.40+p.core*.28;"
if s.count(a) != 1:
    sys.exit("bw: count=%d" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4h applied:", len(s), "bytes")
