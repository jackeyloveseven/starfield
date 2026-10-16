"""V7: kill the teleport, and make the nebulae vivid.

Measured with motion.py: the largest frame-to-frame camera move is 2689 units,
and it happens on capture phase 3 - `travel += 2600` in a single frame. Everything
else in 600 seconds is under 43 units. That is the whole of "太跳脱": three times
in ten minutes the entire world jumps 2600 units between one frame and the next.

Replace it with a decaying speed burst - the same distance, but travelled. Reads
as being flung out of the well instead of cutting.

Then the nebulae: the tint was 42% white, which desaturates the ink toward grey,
and every wash in a region used one flat colour. Games get their look from
saturation and from colour variety within a field.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


# ------------------------------------------------------------ A. no teleport ----
rep("let activeMasses=[],sling=0,slingPrev=1e9,slingHold=0;",
    "let activeMasses=[],sling=0,slingPrev=1e9,slingHold=0,warp=0;")

rep("function updateSling(dt){\n const c=flockCentre();let near=1e9;",
    "function updateSling(dt){\n // The slingshot is a decaying speed burst, not a jump: see the capture release.\n warp*=Math.exp(-dt*1.16);\n const c=flockCentre();let near=1e9;")

rep("   captureJumped=true;travel+=2600;reseedFlock();",
    "   captureJumped=true;warp=28;reseedFlock();")

rep(" if(dt){time+=dt;if(started){travel+=SPEED*dt*(1+1.1*sling);flightTime+=dt;}else{previewTime+=dt;travel+=SPEED*.15*dt;}}",
    " if(dt){time+=dt;if(started){travel+=SPEED*dt*(1+1.1*sling+warp);flightTime+=dt;}else{previewTime+=dt;travel+=SPEED*.15*dt;}}")

rep("  time+=step;if(started){travel+=SPEED*step;flightTime+=step;}else{previewTime+=step;travel+=SPEED*.15*step;}",
    "  time+=step;if(started){travel+=SPEED*step*(1+1.1*sling+warp);flightTime+=step;}else{previewTime+=step;travel+=SPEED*.15*step;}")

# ------------------------------------------------------------- B. vivid washes ----
rep(""" const tint=blend(styles[idx].tree,[255,255,255],.42).map(v=>Math.round(v/24)*24);""",
    """ // Was 42% toward white, which washed the ink toward grey; and every wash in a
 // region was the same flat colour. Vary the second colour by the nebula's own
 // seed - the cache key already carries that seed, so the texture count is
 // unchanged at 6 x 5.
 const st=styles[idx],alt=seed%3===0?st.water:seed%3===1?st.sun:st.craft;
 const tint=blend(blend(st.tree,alt,.38),[255,255,255],.14).map(v=>Math.round(v/24)*24);""")

rep(" const wash=.22+p.wash*1.15+p.core*.55;", " const wash=.30+p.wash*1.35+p.core*.65;")
rep("   const al=clamp(n.alpha*wash,0,.72);", "   const al=clamp(n.alpha*wash,0,.86);")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V7 applied:", len(s), "bytes")
