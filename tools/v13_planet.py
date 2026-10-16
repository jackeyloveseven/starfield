"""V13: the planet's peak, not its ramp, was the problem.

V12 compressed the Lambert ramp into .20...80 of the range, and the planet still
measured p50 = 249.8, p90 = 254.1, max 255 - more than half the disc pinned above
250, i.e. a light source rather than a lit surface. Compressing the ramp was not
enough because it is not the last stage: the bloom adds the graded frame back on
top of itself, and a large area at 255 feeds the bloom hardest.

Measured target: a day side that lands around 215 after grade AND bloom, so the
term-ward falloff is still readable. The peak moves from .80 to .60 of the range.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = "  const v=b>=0?.20+.60*b:.20*Math.pow(1+b,1.5);"
b = "  const v=b>=0?.18+.42*b:.18*Math.pow(1+b,1.5);"

if s.count(a) != 1:
    sys.exit("count=%d: planet ramp not found" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V13 applied:", len(s), "chars")
