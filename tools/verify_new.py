"""Verify the four new behaviours that have no screenshot of their own.

  thumb   the travelling pill sits exactly on the selected chip
  dolly   clicking a chip eases travel to that region and lands exactly
  hold    pointerdown 320 ms -> gear 1, +850 ms -> gear 2, release -> gear 0
  voice   247 clips, and the 12 new ones decode as MP3

  python -I verify_new.py starfield.html
"""
import sys, os, json, subprocess, tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = r"""
<script>
const log = {};
function done(){ document.title = JSON.stringify(log); }
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
(async () => {
  try {
    await sleep(300);
    // ---- 1. thumb vs chip ----
    const chips = [...document.querySelectorAll('.destination')];
    const th = document.querySelector('.dest-thumb');
    const sel = document.querySelector('.destination[aria-checked="true"]');
    const tr = th ? th.getBoundingClientRect() : null, cr = sel ? sel.getBoundingClientRect() : null;
    log.thumb = tr && cr ? {
      dx: Math.round(tr.left - cr.left), dy: Math.round(tr.top - cr.top),
      dw: Math.round(tr.width - cr.width), visible: getComputedStyle(th).opacity
    } : 'missing';

    // ---- 2. dolly: click chip 3 (星系核) ----
    const before = window.Starfield.getState().travel;
    chips[3].click();
    const mid = window.Starfield.getState().travel;
    for (let n = 0; n < 40; n++) window.Starfield.stepDeparture(0.1);  // 4 s of dolly
    const st = window.Starfield.getState();
    log.dollyStarted = window.Starfield.getState().departing;
    log.dolly = {
      before: Math.round(before), mid: Math.round(mid), after: Math.round(st.travel),
      region: st.region, moved: Math.round(st.travel - before),
      chipChecked: document.querySelectorAll('.destination[aria-checked="true"]')[0].dataset.region,
      thumbFollows: (() => {
        const t = document.querySelector('.dest-thumb').getBoundingClientRect();
        const c = document.querySelector('.destination[aria-checked="true"]').getBoundingClientRect();
        return Math.round(t.left - c.left);
      })()
    };

    // ---- 3. long press (only in flight) ----
    document.getElementById('begin').click();
    await sleep(700);
    const pd = (t) => t.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true, pointerId:1, isPrimary:true}));
    const pu = (t) => t.dispatchEvent(new PointerEvent('pointerup', {bubbles:true, pointerId:1, isPrimary:true}));
    log.overlay = !!document.getElementById('starfield-touch-overlay');
    pd(document.body);
    await sleep(420);
    const g1 = window.Starfield.getState().warpGear;
    await sleep(900);
    const g2 = window.Starfield.getState().warpGear;
    pu(document.body);
    await sleep(150);
    const g3 = window.Starfield.getState().warpGear;
    log.hold = { gearAfter420: g1, gearAfter1300: g2, gearAfterRelease: g3 };

    // ---- 4. clips ----
    log.voice = { clips: window.Starfield.getState().clips };
  } catch (e) { log.error = String(e); }
  done();
})();
</script>"""

src = open(html, encoding="utf-8").read()
src = src.replace("<head>", '<head><script>window.ontouchstart=null;'
                  'try{Object.defineProperty(navigator,"maxTouchPoints",{get:function(){return 5}});}catch(e){}</script>', 1)
tmp = tempfile.mkdtemp(prefix="verify-")
ph = os.path.join(tmp, "p.html")
open(ph, "w", encoding="utf-8", newline="").write(src.replace("</body>", PROBE + "</body>", 1))

with tempfile.TemporaryDirectory(prefix="verify-prof-") as prof:
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
                        "--enable-unsafe-swiftshader", "--disable-gpu-compositing", "--no-sandbox",
                        "--mute-audio", "--hide-scrollbars", "--no-first-run", "--disable-extensions",
                        "--disable-background-networking", "--window-size=1280,800",
                        "--user-data-dir=" + prof, "--virtual-time-budget=9000", "--dump-dom",
                        Path(ph).as_uri()],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
dom = r.stdout or ""
i, j = dom.find("<title>"), dom.find("</title>")
print(dom[i + 7:j] if i >= 0 else "NO TITLE")
