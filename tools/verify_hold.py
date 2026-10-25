"""End-to-end long press: synthetic pointer -> timer -> gear -> release.

Narrower and shorter than the full probe (which hung Chrome with a 9 s budget
plus the departure dolly). If this passes, the only difference from a real
finger is who created the event.
"""
import sys, os, subprocess, tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = """
<script>
window.ontouchstart=null;
try{Object.defineProperty(navigator,"maxTouchPoints",{get:function(){return 5}});}catch(e){}
const sleep=(ms)=>new Promise(r=>setTimeout(r,ms));
async function run(){
  const out={};
  try{
    await sleep(250);
    document.getElementById('begin').click();
    await sleep(500);
    out.started=window.Starfield.getState().started;
    const ev=(t)=>new PointerEvent(t,{bubbles:true,cancelable:true,pointerId:1,isPrimary:true,pointerType:'touch'});
    document.body.dispatchEvent(ev('pointerdown'));
    await sleep(450);
    out.gear450=window.Starfield.getState().warpGear;
    await sleep(950);
    out.gear1400=window.Starfield.getState().warpGear;
    document.body.dispatchEvent(ev('pointerup'));
    await sleep(200);
    out.gearRelease=window.Starfield.getState().warpGear;
  }catch(e){out.error=String(e);}
  document.title=JSON.stringify(out);
}
run();
</script>"""

src = open(html, encoding="utf-8").read()
tmp = tempfile.mkdtemp(prefix="hold-")
ph = os.path.join(tmp, "p.html")
open(ph, "w", encoding="utf-8", newline="").write(src.replace("</body>", PROBE + "</body>", 1))

with tempfile.TemporaryDirectory(prefix="hold-prof-") as prof:
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
                        "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
                        "--mute-audio", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                        "--disable-background-networking", "--window-size=1100,760",
                        "--user-data-dir=" + prof, "--virtual-time-budget=3200", "--dump-dom",
                        Path(ph).as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
dom = r.stdout or ""
i, j = dom.find("<title>"), dom.find("</title>")
print(dom[i + 7:j] if i >= 0 else "NO TITLE")
