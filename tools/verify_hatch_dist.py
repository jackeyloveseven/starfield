"""Does the hatch table actually roll what it says? 2000 sessions per tier."""
import sys, os, subprocess, tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = """
<script>
setTimeout(function(){
  var out={};
  try{
    var H=window.StarfieldHatch;
    var res={};
    [15,30,60].forEach(function(m){
      H.clear();
      var c={}, n=1200;
      for(var i=0;i<n;i++){ var it=H.roll(m); c[it.tier]=(c[it.tier]||0)+1; }
      var pct={}; for(var k in c) pct[k]=Math.round(c[k]*1000/n)/10;
      res[m]=pct;
    });
    out.dist=res;
    H.clear();
    var a=H.roll(60), b=H.roll(60);
    out.sampleName1=a.name; out.sampleName2=b.name;
    out.stored=H.list().length;
    out.tiers=Object.keys(H.tiers).join(',');
  }catch(e){ out.error=String(e); }
  document.title=JSON.stringify(out);
}, 400);
</script>"""

src = open(html, encoding="utf-8").read()
tmp = tempfile.mkdtemp(prefix="hatch-")
ph = os.path.join(tmp, "p.html")
open(ph, "w", encoding="utf-8", newline="").write(src.replace("</body>", PROBE + "</body>", 1))

with tempfile.TemporaryDirectory(prefix="hatch-prof-") as prof:
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
                        "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
                        "--mute-audio", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                        "--disable-background-networking", "--window-size=1000,700",
                        "--user-data-dir=" + prof, "--virtual-time-budget=6000", "--dump-dom",
                        Path(ph).as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=150)
dom = r.stdout or ""
i, j = dom.find("<title>"), dom.find("</title>")
print(dom[i + 7:j] if i >= 0 else "NO TITLE")
