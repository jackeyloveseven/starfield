"""Why is body.modal-open not applied? Read it off the dumped DOM."""
import sys, os, json, subprocess, tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_modal.js"),
             encoding="utf-8").read()

src = open(html, encoding="utf-8").read()
tmp = tempfile.mkdtemp()
ph = os.path.join(tmp, "p.html")
open(ph, "w", encoding="utf-8", newline="").write(src.replace("</body>", PROBE + "</body>", 1))

with tempfile.TemporaryDirectory() as prof:
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
                        "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
                        "--mute-audio", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                        "--disable-background-networking", "--window-size=800,900",
                        "--user-data-dir=" + prof, "--virtual-time-budget=3000", "--dump-dom",
                        Path(ph).as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
dom = r.stdout or ""
i, j = dom.find("<title>"), dom.find("</title>")
print("title:", dom[i + 7:j] if i >= 0 else "NO TITLE")
k = dom.find("<body")
print("body :", dom[k:k + 120].split(">")[0] + ">")
