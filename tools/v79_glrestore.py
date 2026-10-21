"""V79: the black hole survives a lost GL context.

The hole is one WebGL sprite. If the driver resets or the tab is parked long
enough for the browser to reclaim the context, every gl call becomes a no-op and
drawImage() of a lost canvas draws nothing: the signature object of the piece is
gone for the rest of the session, with no error and no way back.

The initialiser becomes a function that can run again, it asks the browser to
restore the context (a lost context is only restorable if the lost event is
prevented), and it rebuilds the program and the two textures on restore.

The two texture data URIs are 244 KB and 352 KB lines; this patch never reads
them, it only moves the two lines that open and close the initialiser.

Run:  python -I v79_glrestore.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
lines = open(src_p, encoding="utf-8", newline="").read().split("\n")

OPEN = "const holeGL=(()=>{"
i = [k for k, s in enumerate(lines) if s == OPEN]
if len(i) != 1:
    sys.exit("open anchor count=%d" % len(i))
i = i[0]

# the first `})();` after the opening line closes this IIFE
js = [k for k in range(i + 1, min(i + 120, len(lines))) if lines[k] == "})();"]
if not js:
    sys.exit("no closing })(); within 120 lines")
j = js[0]

lines[i] = "let holeGL=null;\nfunction bootHoleGL(){"
lines[j] = r"""  // A lost context cannot be revived in place: the program, the two textures
  // and the buffer are all gone. Ask for restoration, then build it again.
  cv.addEventListener('webglcontextlost',ev=>{ev.preventDefault();},false);
  cv.addEventListener('webglcontextrestored',()=>{holeGL=bootHoleGL();},false);
  return {cv,gl,prog,u,texOrganic,texNoise};
}
holeGL=bootHoleGL();"""

# the old `return {...}` line is still there just above; remove the duplicate
old_ret = "  return {cv,gl,prog,u,texOrganic,texNoise};"
if j - 1 >= 0 and lines[j - 1].strip() == old_ret.strip():
    del lines[j - 1]

src = "\n".join(lines)
open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V79 written:", len(src), "chars")
