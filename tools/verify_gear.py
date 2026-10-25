"""Does the gear actually move? The narrowest possible check.

The long press needs a pointer event plus two timers, and the full-page probe
kept hanging Chrome. The endpoint it calls, Starfield.setWarpGear, can be
checked on its own in under a second: if the gear moves here, the only link left
unproven is pointer -> setTimeout, which is plain DOM.
"""
import sys, os, subprocess, tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = """
<script>
window.ontouchstart=null;
try{Object.defineProperty(navigator,"maxTouchPoints",{get:function(){return 5}});}catch(e){}
setTimeout(function(){
  var out={};
  try{
    document.getElementById('begin').click();
    out.api = typeof window.Starfield.setWarpGear;
    out.before = window.Starfield.getState().warpGear;
    window.Starfield.setWarpGear(1);
    out.after1 = window.Starfield.getState().warpGear;
    window.Starfield.setWarpGear(2);
    out.after2 = window.Starfield.getState().warpGear;
    window.Starfield.setWarpGear(0);
    out.after0 = window.Starfield.getState().warpGear;
    out.started = window.Starfield.getState().started;
  }catch(e){ out.error=String(e); }
  document.title=JSON.stringify(out);
}, 600);
</script>"""

src = open(html, encoding="utf-8").read().replace("<head>",
    '<head><!-- probe -->', 1)
tmp = tempfile.mkdtemp(prefix="warp-")
ph = os.path.join(tmp, "p.html")
open(ph, "w", encoding="utf-8", newline="").write(src.replace("</body>", PROBE + "</body>", 1))

with tempfile.TemporaryDirectory(prefix="warp-prof-") as prof:
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
                        "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
                        "--mute-audio", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                        "--disable-background-networking", "--window-size=1280,800",
                        "--user-data-dir=" + prof, "--virtual-time-budget=2600", "--dump-dom",
                        Path(ph).as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
dom = r.stdout or ""
i, j = dom.find("<title>"), dom.find("</title>")
print(dom[i + 7:j] if i >= 0 else "NO TITLE")
