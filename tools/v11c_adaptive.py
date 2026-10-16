"""V11c: the grade must follow the region, because it is the offset that kills.

contrast() is an affine map with an OFFSET: out = A*v - A*v0. The offset is what
creates a black point, and it is also the only part that can destroy a frame. A
fixed black point at 28.8 measured fine on FOIL (floor 45) and catastrophically on
ABYSS, whose own measured p50 was 21.1 - 71.44% of that frame went to literal zero.

The vignette cannot do this: it multiplies, so it is scale-invariant and safe at
any level. Only the subtractive term needs to adapt.

So the white point is held fixed at 206 (highlights clip identically everywhere)
and the black point follows 62% of the palette's own sky luminance. Two equations:
    A = 255/(v1 - v0)
    c = 1 + 2*A*v0/255      (since the offset B = -A*v0 = 0.5*(1-c)*255)
    k = A/c
which reproduces brightness(1.10) contrast(1.33) on FOIL and backs off to roughly
brightness(1.16) contrast(1.13) on ABYSS, where it is needed.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:140]))
    s = s.replace(a, b, n)


rep("""/* brightness(1.10) contrast(1.33) is the affine map out = 1.463v - 42.1 (0..255):
 * black point 28.8 (so p1 = 30 becomes literally 0), white point 203 (so p99 = 217
 * and every star core clip to 255). pivot 90.9. saturate above 1.25 and the
 * near-neutral navy starts reading as a saturated blue, which breaks the ink. */
const gradeFilter='brightness(1.10) contrast(1.33) saturate(1.18)';
let postMs=0;""",
    """/* The grade is computed from the region's OWN floor, not fixed.
 *
 * contrast() is an affine map with an offset: out = A*v - A*v0. That offset is
 * what makes a black point, and it is the only part that can destroy a frame - a
 * fixed black point at 28.8 measured fine on FOIL (floor 45) and catastrophic on
 * ABYSS, whose own p50 is 21.1: 71% of that frame went to literal zero.
 *
 * The vignette cannot do that, because it multiplies and is therefore
 * scale-invariant. Only the subtractive term has to adapt.
 *
 * So the white point is held at 206 - highlights clip identically everywhere -
 * and the black point follows the palette's own sky luminance. Two equations:
 *   A = 255/(v1-v0)   c = 1 + 2*A*v0/255   k = A/c
 * which lands on brightness(1.10) contrast(1.33) at FOIL and backs off to about
 * brightness(1.16) contrast(1.13) at ABYSS. */
let gradeCache='',gradeKey=-1;
function gradeFor(p){
 const L=.2126*p.sky[0]+.7152*p.sky[1]+.0722*p.sky[2];
 const v0=clamp(L*.62,4,30),v1=206,k0=v0|0;
 if(k0===gradeKey)return gradeCache;
 gradeKey=k0;
 const A=255/(v1-v0),c=clamp(1+2*A*v0/255,.02,3),k=A/c;
 gradeCache='brightness('+k.toFixed(3)+') contrast('+c.toFixed(3)+') saturate(1.14)';
 return gradeCache;
}
let postMs=0;""")

rep("ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.filter=gradeFilter;",
    "ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.filter=gradeFor(currentPalette);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V11c applied:", len(s), "chars")
