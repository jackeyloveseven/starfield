"""V11b: deepen the vignette so the frame actually reaches true black.

v11 got p1 from 28.0 to 1.2 and p99 from 215 to 251, but only 0.13% of the frame
was literally 0 - the gradient only reached zero at the very corners. The falloff
now completes at 0.93 of the radius instead of 0.98, which puts the black boundary
far enough in that ~1% of the frame is genuinely black.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = (" g.addColorStop(0.00,'rgb(255,255,255)');g.addColorStop(0.24,'rgb(255,255,255)');\n"
     " g.addColorStop(0.50,'rgb(242,245,250)');g.addColorStop(0.68,'rgb(206,213,224)');\n"
     " g.addColorStop(0.82,'rgb(146,155,169)');g.addColorStop(0.92,'rgb(66,72,84)');\n"
     " g.addColorStop(0.98,'rgb(14,16,20)');g.addColorStop(1.00,'rgb(0,0,0)');")

b = (" g.addColorStop(0.00,'rgb(255,255,255)');g.addColorStop(0.22,'rgb(255,255,255)');\n"
     " g.addColorStop(0.46,'rgb(244,247,251)');g.addColorStop(0.62,'rgb(210,217,227)');\n"
     " g.addColorStop(0.74,'rgb(150,159,173)');g.addColorStop(0.84,'rgb(74,81,93)');\n"
     " g.addColorStop(0.90,'rgb(26,29,35)');g.addColorStop(0.93,'rgb(0,0,0)');\n"
     " g.addColorStop(1.00,'rgb(0,0,0)');")

if s.count(a) != 1:
    sys.exit("count=%d: vignette stops not found" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V11b applied:", len(s), "chars")
