"""V122: the long press reached for WarpDrive from a scope that does not have it.

The touch HUD lives in its own module; WarpDrive is a page-level const. The
handler therefore threw on the first press and the gear never moved - which on a
phone looks like "holding the screen does nothing". It now goes through the
public API, which is visible everywhere:

    window.Starfield.setWarpGear(i)

Run:  python -I v122_warp.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)

rep(' stepDeparture:(dt)=>stepDeparture(dt),',
    ' stepDeparture:(dt)=>stepDeparture(dt),\n setWarpGear:(i)=>{WarpDrive.gearIndex=i;WarpDrive.updateUI();},')

rep("""    const gear = (i) => {
      if (WarpDrive.gearIndex === i) return;
      WarpDrive.gearIndex = i;
      WarpDrive.updateUI();
      toast(i === 0 ? '巡航 1×' : i === 1 ? '跃迁 5×' : '超曲 15×', 1.1);
    };""",
    """    const gear = (i) => {
      const S = window.Starfield;
      if (!S || !S.setWarpGear) return;
      S.setWarpGear(i);
      if (window.toast) toast(i === 0 ? '巡航 1×' : i === 1 ? '跃迁 5×' : '超曲 15×', 1.1);
    };""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V122 written:", len(src), "chars")
