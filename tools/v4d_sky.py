"""V4d: the palettes were built for sky-over-fog and are all light.

With the ground gone there is nothing for a pale sky to sit behind, so the whole
frame read as lavender wash. Fall much further toward the ink; the region colours
survive in the nebulae, the band, the worlds and the craft.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()

a = " g.addColorStop(0,css(blend(p.sky,p.ink,.36)));g.addColorStop(.55,css(blend(p.horizon,p.ink,.54)));g.addColorStop(1,css(blend(p.fog,p.ink,.86)));"
b = " g.addColorStop(0,css(blend(p.sky,p.ink,.60)));g.addColorStop(.55,css(blend(p.horizon,p.ink,.72)));g.addColorStop(1,css(blend(p.fog,p.ink,.91)));"
if s.count(a) != 1:
    sys.exit("sky gradient: count=%d" % s.count(a))
s = s.replace(a, b, 1)

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4d applied:", len(s), "bytes")
