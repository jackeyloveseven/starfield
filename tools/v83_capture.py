"""V83: the capture owns its own camera.

The look-target clamp (keep the flock on the plate) was applied after the
capture pose had been blended in, so it pulled the shipped Gargantua camera back
toward the corridor. The 事件视界 departure frame - the one deliberate set piece
of the whole piece - became a plate of yellow atmosphere belonging to a planet
the capture was trying to look past.

For the sixty seconds of a capture the fleet is not the subject. The clamp now
applies only when no capture pose is active.

Run:  python -I v83_capture.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """ {
  const bx=routeX(travel),by=courseY(travel)+camera.aimY,bz=travel;"""
NEW = """ // A capture has its own six-DOF camera and the fleet is not its subject; the
 // clamp belongs to ordinary shots only.
 if(!captureCamPose){
  const bx=routeX(travel),by=courseY(travel)+camera.aimY,bz=travel;"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V83 written:", len(src), "chars")
