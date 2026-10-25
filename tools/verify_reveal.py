"""Acceptance probe for v135_reveal.py.

Runs the patched page in headless Chrome, opens the hatch with
StarfieldHatch.show(), clicks the card, and reads back:
  * .revealed on the card
  * the CSS animation name (computed style + getAnimations())
  * the @keyframes rules present in the stylesheets
  * window.__sfRevealSfxFired after the click
  * the legend halo ring (forced via openFor)
Then repeats once with --force-prefers-reduced-motion to confirm the 200ms fade.

Run:  python -I verify_reveal.py <out.html>
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1] if len(sys.argv) > 1 else "starfield-v135.html"

PROBE = r"""
<script>
window.__probeErrors = [];
window.addEventListener('error', function (e) {
  window.__probeErrors.push(String(e.message));
});
setTimeout(function () {
  var out = {};
  try {
    var H = window.StarfieldHatch;
    out.api = !!(H && H.show && H.openFor && H.tiers);
    H.show();
    var root = document.getElementById('sf-hatch');
    var card = root && root.querySelector('.sf-hatch-card');
    out.opened = !!(root && root.classList.contains('on'));
    out.revealedBefore = card.classList.contains('revealed');
    out.sfxBefore = !!window.__sfRevealSfxFired;
    card.click();
    out.revealedAfter = card.classList.contains('revealed');
    out.sfxAfter = !!window.__sfRevealSfxFired;
    out.sfxTier = window.__sfRevealSfxTier || null;
    out.sfxNotes = window.__sfRevealSfxNotes || 0;
    out.sfxState = window.__sfRevealSfxState || null;
    var cs = getComputedStyle(card);
    out.animationName = cs.animationName;
    out.animationDuration = cs.animationDuration;
    out.animations = card.getAnimations
      ? card.getAnimations().map(function (a) { return a.animationName; })
      : [];
    out.tierColor = String(card.style.getPropertyValue('--tier') || '').trim();
    out.flashDurVar = String(card.style.getPropertyValue('--sf-flash-dur') || '').trim();
    out.flashVar = String(card.style.getPropertyValue('--sf-flash') || '').trim();

    var names = [];
    for (var i = 0; i < document.styleSheets.length; i++) {
      try {
        var rs = document.styleSheets[i].cssRules;
        for (var j = 0; j < rs.length; j++) {
          if (rs[j].type === 7) names.push(rs[j].name);
        }
      } catch (e) {}
    }
    out.keyframes = names.filter(function (n) { return /^sf-(reveal|halo)/.test(n); });

    /* Deterministic legend pass: tier-scaled 5th note + 600ms halo. */
    H.openFor({ id: 'v135-probe', tier: 'legend', name: 'V135 Legend',
                minutes: 30, hue: 35, at: '2026-10-25' });
    var root2 = document.getElementById('sf-hatch');
    var card2 = root2.querySelector('.sf-hatch-card');
    out.legendRevealReset = !card2.classList.contains('revealed');
    card2.click();
    out.legendRevealed = card2.classList.contains('revealed');
    out.legendTier = window.__sfRevealSfxTier || null;
    out.legendNotes = window.__sfRevealSfxNotes || 0;
    out.haloClass = root2.classList.contains('sf-halo');
    var ps = getComputedStyle(root2, '::after');
    out.haloAnimation = ps.animationName;
    out.haloDuration = ps.animationDuration;
    out.haloDisplay = ps.display;
    out.reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  } catch (e) {
    out.error = String((e && e.stack) || e);
  }
  out.probeErrors = window.__probeErrors;
  document.title = JSON.stringify(out);
}, 500);
</script>
"""


def run_once(path, force_reduce):
    src = open(path, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="reveal-")
    probe_path = os.path.join(tmp, "probe.html")
    open(probe_path, "w", encoding="utf-8", newline="").write(
        src.replace("</body>", PROBE + "</body>", 1))
    flags = [CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
             "--enable-unsafe-swiftshader", "--disable-gpu-compositing",
             "--no-sandbox", "--mute-audio", "--hide-scrollbars", "--no-first-run",
             "--disable-extensions", "--disable-background-networking",
             "--autoplay-policy=no-user-gesture-required",
             "--window-size=1000,760", "--user-data-dir=" + tempfile.mkdtemp(prefix="reveal-prof-"),
             "--virtual-time-budget=3200", "--dump-dom"]
    if force_reduce:
        flags.insert(1, "--force-prefers-reduced-motion")
    flags.append(Path(probe_path).as_uri())
    r = subprocess.run(flags, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=240)
    m = re.search(r"<title>(.*?)</title>", r.stdout or "", re.S)
    if not m:
        return {"error": "NO TITLE", "stderr": (r.stderr or "")[-400:]}
    try:
        return json.loads(m.group(1))
    except Exception as e:
        return {"error": "BAD JSON: " + str(e), "title": m.group(1)[:400]}


def seconds(value):
    try:
        return float(str(value).strip().rstrip("s"))
    except Exception:
        return None


def check(d, reduce_mode):
    c = {}
    c["api"] = bool(d.get("api"))
    c["opened"] = bool(d.get("opened"))
    c["revealed_before_click"] = d.get("revealedBefore") is False
    c["revealed_after_click"] = bool(d.get("revealedAfter"))
    c["sfx_flag_before_click"] = d.get("sfxBefore") is False
    c["sfx_flag_after_click"] = bool(d.get("sfxAfter"))
    name = str(d.get("animationName") or "")
    anims = " ".join(d.get("animations") or [])
    dur = seconds(d.get("animationDuration"))
    if reduce_mode:
        c["computed_animation_is_fade"] = "sf-reveal-fade" in name
        c["get_animations_is_fade"] = "sf-reveal-fade" in anims
        c["duration_0_2s"] = dur is not None and abs(dur - 0.2) < 1e-6
        c["halo_suppressed"] = (d.get("haloAnimation") in (None, "none", "")) or \
                               d.get("haloDisplay") == "none"
    else:
        c["computed_animation_is_lift"] = "sf-reveal-lift" in name
        c["get_animations_is_lift"] = "sf-reveal-lift" in anims
        c["duration_in_120_200ms"] = dur is not None and 0.119 <= dur <= 0.201
        c["keyframes_reveal_defined"] = "sf-reveal-lift" in (d.get("keyframes") or [])
        c["keyframes_halo_defined"] = "sf-halo-ring" in (d.get("keyframes") or [])
        c["legend_tier"] = d.get("legendTier") == "legend"
        c["legend_five_notes"] = d.get("legendNotes") == 5
        c["legend_revealed"] = bool(d.get("legendRevealed"))
        c["legend_halo_class"] = bool(d.get("haloClass"))
        c["legend_halo_animation"] = "sf-halo-ring" in str(d.get("haloAnimation") or "")
        c["legend_halo_600ms"] = seconds(d.get("haloDuration")) == 0.6
    c["no_probe_errors"] = not (d.get("probeErrors") or []) and not d.get("error")
    return c


def main():
    normal = run_once(HTML, False)
    reduced = run_once(HTML, True)
    cn = check(normal, False)
    cr = check(reduced, True)
    # The reduced-motion run only counts if the flag actually emulated it.
    emulated = reduced.get("reduced") is True
    if not emulated:
        cr["reduced_emulated"] = False
    else:
        cr["reduced_emulated"] = True
    report = {
        "file": os.path.abspath(HTML),
        "normal": normal,
        "normal_checks": cn,
        "reduced": reduced,
        "reduced_checks": cr,
        "pass": all(cn.values()) and all(cr.values()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
