"""Headless checks for v144 gravitational time dilation.

  a. window.sfTimeDilation(rs/r) is the pure d = sqrt(1 - rs/r):
     rs/r = 0.5 -> 0.7071, 0.1 -> 0.9487, -> 0 -> 1.
  b. With d = 0.5 injected, 10 wall-clock seconds advance the focus timer by
     exactly 5 seconds. The real StarfieldFocusEngine.tick() is exercised with
     a synthetic 10 s wall-clock gap, so no 60 Hz dependence.
  c. window.SF_TIME_DILATION = false resolves d to 1: the same 10 s simulation
     records 10 seconds, and the prototype currentDilation() returns 1.

Run:  python -I verify_dilation.py <patched.html>
"""
import html
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile

def find_chrome():
    if os.environ.get("CHROME_PATH") and os.path.exists(os.environ["CHROME_PATH"]):
        return os.environ["CHROME_PATH"]
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "google-chrome"

CHROME = find_chrome()

if len(sys.argv) != 2:
    sys.exit("usage: python -I verify_dilation.py <patched.html>")
SRC = os.path.abspath(sys.argv[1])
src = open(SRC, encoding="utf-8", newline="").read()

hook = (
    '<script>window.__errors=[];'
    'window.addEventListener("error",e=>window.__errors.push(String(e.message)));'
    '</script>'
)
assert src.count("<meta charset=\"utf-8\">") == 1, "meta charset anchor"
src = src.replace("<meta charset=\"utf-8\">", "<meta charset=\"utf-8\">" + hook, 1)

probe = r"""
<script>
document.title = JSON.stringify((function () {
  var out = { checks: {} };
  function chk(name, cond, value) {
    out.checks[name] = { ok: !!cond, value: value };
  }
  try {
    var defaultFlag = window.SF_TIME_DILATION;
    var f = window.sfTimeDilation;
    chk('sfTimeDilation is a function', typeof f === 'function', typeof f);

    var d05 = f(0.5), d01 = f(0.1), dtiny = f(1e-9), d0 = f(0);
    out.d_0_5 = d05; out.d_0_1 = d01; out.d_tiny = dtiny; out.d_0 = d0;
    chk('a: d(rs/r=0.5) = 0.707', Math.abs(d05 - Math.SQRT1_2) <= 0.01, d05);
    chk('a: d(rs/r=0.1) = 0.949', Math.abs(d01 - Math.sqrt(0.9)) <= 0.01, d01);
    chk('a: d(rs/r->0) = 1', Math.abs(dtiny - 1) <= 0.01, dtiny);
    chk('a: d(rs/r=0) = 1', Math.abs(d0 - 1) <= 1e-12, d0);

    var advance = window.sfFocusAdvance;
    chk('sfFocusAdvance is a function', typeof advance === 'function', typeof advance);
    out.advance_d_0_5 = advance(0, 10, 0.5);
    chk('b: 10 wall s at d=0.5 records 5 s',
        Math.abs(out.advance_d_0_5 - 5) <= 1e-9, out.advance_d_0_5);

    var E = window.StarfieldFocusEngine;
    chk('focus engine exists', !!E, !!E);
    E.state = 'RUNNING';
    E.targetDurationSec = 999999;
    E.elapsedSec = 0;
    E.currentDilation = function () { return 0.5; };
    E.lastTickMs = performance.now() - 10000;
    E.tick();
    out.tick_d_0_5 = E.elapsedSec;
    chk('b: engine tick, 10 wall s at d=0.5 records 5 s',
        Math.abs(out.tick_d_0_5 - 5) <= 0.1, out.tick_d_0_5);

    E.dilation = 0.5;
    E.updateTickerHUD(true);
    var tk = document.getElementById('sf-focus-ticker');
    out.ticker_has_d = !!tk && tk.textContent.indexOf('×0.50') >= 0;
    out.ticker_has_warn = !!tk && tk.textContent.indexOf('洞外时间更快') >= 0;
    chk('ui: ticker shows the current d', out.ticker_has_d, out.ticker_has_d);
    chk('ui: ticker warns when d < 0.95', out.ticker_has_warn, out.ticker_has_warn);

    delete E.currentDilation;
    window.SF_TIME_DILATION = false;
    E.dilation = 0.5;
    E.updateTickerHUD(true);
    out.ticker_off_hides = !!tk && tk.textContent.indexOf('引力时间') < 0;
    chk('ui: flag off hides the dilation readout',
        out.ticker_off_hides, out.ticker_off_hides);
    out.default_flag = defaultFlag;
    out.proto_d_off = E.currentDilation();
    out.resolver_off = window.sfFocusDilation(0.5);
    out.advance_off = advance(0, 10, window.sfFocusDilation(0.5));
    E.currentDilation = function () { return window.sfFocusDilation(0.5); };
    E.elapsedSec = 0;
    E.lastTickMs = performance.now() - 10000;
    E.tick();
    out.tick_off = E.elapsedSec;

    chk('c: flag defaults to true', defaultFlag === true, defaultFlag);
    chk('c: flag off resolves d = 1', out.resolver_off === 1, out.resolver_off);
    chk('c: flag off, 10 wall s records 10 s',
        Math.abs(out.advance_off - 10) <= 1e-9, out.advance_off);
    chk('c: flag off, engine tick records 10 s',
        Math.abs(out.tick_off - 10) <= 0.1, out.tick_off);
    chk('c: flag off, prototype currentDilation = 1',
        out.proto_d_off === 1, out.proto_d_off);

    window.SF_TIME_DILATION = true;
    E.state = 'IDLE';
    E.elapsedSec = 0;
    E.targetDurationSec = 1800;
    if (E.updateTickerHUD) E.updateTickerHUD(false);

    chk('Starfield.getTimeDilation exists',
        !!(window.Starfield && typeof window.Starfield.getTimeDilation === 'function'),
        !!(window.Starfield && window.Starfield.getTimeDilation));
    out.errors = window.__errors || [];
  } catch (e) {
    out.fatal = String(e && e.stack || e);
  }
  out.ok = !out.fatal && Object.keys(out.checks).length > 0 &&
           Object.keys(out.checks).every(function (k) { return out.checks[k].ok; });
  return out;
})());
</script>
"""
assert src.count("</body>") >= 1, "body close"
src = src.replace("</body>", probe + "</body>", 1)

with tempfile.TemporaryDirectory(prefix="sf144-") as td:
    probe_path = os.path.join(td, "verify.probe.html")
    with open(probe_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(src)
    url = "file:///" + probe_path.replace(os.sep, "/") + "?seed=1a2b"
    with tempfile.TemporaryDirectory(prefix="sf144-prof-") as prof:
        r = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
             "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
             "--mute-audio", "--no-first-run", f"--user-data-dir={prof}",
             "--window-size=1280,720", "--dump-dom", url],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=300,
        )

m = re.search(r"<title>(.*?)</title>", r.stdout or "", re.S)
if not m:
    sys.exit("NO TITLE - " + (r.stderr or "")[-500:])
try:
    data = json.loads(html.unescape(m.group(1)))
except Exception as exc:
    sys.exit(f"BAD TITLE JSON ({exc}): {m.group(1)[:500]}")

print(json.dumps(data, ensure_ascii=False, indent=2))
sys.exit(0 if data.get("ok") else 1)
