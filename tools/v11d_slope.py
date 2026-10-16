"""V11d: hold the SLOPE, move the offset.

v11c made the grade adaptive but pinned the white point at 206, which meant a dark
region (ABYSS, p99 = 190) got almost no contrast at all - it changed by 8.77 and
still did not clip anything.

What the eye reads as "punch" is the slope A, not the black point. So the slope is
now the constant and the offset is what moves:

    v0 = clamp(skyLuminance*0.62, 4, 30)     the black point follows the region floor
    A  = 1.40                                the punch is the same everywhere
    v1 = v0 + 255/A                          the white point follows from the two

FOIL gets v0 = 28, v1 = 210; ABYSS gets v0 = 13, v1 = 195. Both clip their top
percentile and neither crushes its own floor.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = """ const v0=clamp(L*.62,4,30),v1=206,k0=v0|0;
 if(k0===gradeKey)return gradeCache;
 gradeKey=k0;
 const A=255/(v1-v0),c=clamp(1+2*A*v0/255,.02,3),k=A/c;"""

b = """ const v0=clamp(L*.62,4,30),A=1.40,k0=v0|0;
 if(k0===gradeKey)return gradeCache;
 gradeKey=k0;
 const c=clamp(1+2*A*v0/255,.02,3),k=A/c;"""

if s.count(a) != 1:
    sys.exit("count=%d: gradeFor core not found" % s.count(a))
s = s.replace(a, b, 1)

a2 = """ * So the white point is held at 206 - highlights clip identically everywhere -
 * and the black point follows the palette's own sky luminance. Two equations:
 *   A = 255/(v1-v0)   c = 1 + 2*A*v0/255   k = A/c
 * which lands on brightness(1.10) contrast(1.33) at FOIL and backs off to about
 * brightness(1.16) contrast(1.13) at ABYSS. */"""

b2 = """ * So the SLOPE is held constant - the punch is what the eye reads - and only the
 * offset moves, so the black point follows the region's own floor:
 *   v0 = clamp(skyLum*0.62, 4, 30)   A = 1.40   c = 1 + 2*A*v0/255   k = A/c
 * FOIL gets v0 = 28 / v1 = 210, ABYSS gets v0 = 13 / v1 = 195. Both clip their
 * top percentile; neither crushes its own floor. */"""

if s.count(a2) != 1:
    sys.exit("count=%d: grade comment not found" % s.count(a2))
s = s.replace(a2, b2, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V11d applied:", len(s), "chars")
