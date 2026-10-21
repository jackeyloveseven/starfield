"""V76: the cockpit does not look through its own formation.

In the cockpit the camera sits with the flock, and the flock is 276 units wide.
Every crane nearer than ~350 units therefore projected at several hundred pixels
across the canopy, and at that size the fifteen-vertex hull is a white shard, not
a bird - the bottom of the first-person frame was a pile of paper.

Near craft now fade out with cockpitBlend, so the canopy is clear and the
formation still reads as a formation ahead. The blend is 0 in every other view,
and the distance is measured to the bird, so nothing else changes.

Run:  python -I v76_cockpit.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = "  const tri=(a,b,c,col)=>poly([world[a],world[b],world[c]],col);"
NEW = ("  // First person: a crane this close is a shard across the canopy, not a\n"
       "  // bird. Fade the ones inside the formation, only in the cockpit.\n"
       "  const dcam=Math.hypot(pos[0]-camera.eye[0],pos[1]-camera.eye[1],pos[2]-camera.eye[2]);\n"
       "  const nearCraft=cockpitBlend>.01?mix(1,clamp((dcam-90)/260,0,1),cockpitBlend):1;\n"
       "  if(nearCraft<.004)continue;\n"
       "  const tri=(a,b,c,col)=>poly([world[a],world[b],world[c]],col,{alpha:nearCraft});")
if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V76 written:", len(src), "chars")
