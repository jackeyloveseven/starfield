"""V4e: fix the sky, which V4c/V4d made lighter instead of darker.

In this palette `ink` is the LIGHT colour (#e6eff7, the ink the stars are printed
with) and `paper` is the DARK one (#111b27). Blending the sky toward `ink` pushed
it toward white, which is why every frame came back lavender. Fall toward `paper`
instead - and the original sky/horizon/fog stops were already dark, so only the
bottom needs anything.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = " g.addColorStop(0,css(blend(p.sky,p.ink,.60)));g.addColorStop(.55,css(blend(p.horizon,p.ink,.72)));g.addColorStop(1,css(blend(p.fog,p.ink,.91)));"
b = " g.addColorStop(0,css(p.sky));g.addColorStop(.55,css(p.horizon));g.addColorStop(1,css(blend(p.fog,p.paper,.58)));"
if s.count(a) != 1:
    sys.exit("sky gradient: count=%d" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4e applied:", len(s), "bytes")
