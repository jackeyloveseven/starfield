"""Acceptance probe for v140_bind.py.

Runs the patched page in headless Chrome and drives StarfieldHatch directly:

  a. fake pending {kind:'ocean', name:'蓝海', hue:210} -> roll(30) is bound,
     name/hue come from the pending record, id carries the kind, and the
     pending key is cleared;
  b. no pending -> roll(15) is unbound and still returns a normal planet;
  c. five consecutive rolls produce five distinct ids.

Run:  python -I verify_bind.py <out.html>
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1] if len(sys.argv) > 1 else "starfield-v140.html"

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
    out.api = !!(H && H.roll && H.list && H.tiers);
    out.pendingKey = 'sf_pending_planet_v1';

    /* a. bound roll from a fake encounter */
    localStorage.removeItem('sf_pending_planet_v1');
    var fake = { kind: 'ocean', name: '蓝海', hue: 210,
                 at: '2026-10-25T00:00:00.000Z', travel: 12345 };
    localStorage.setItem('sf_pending_planet_v1', JSON.stringify(fake));
    out.fakePending = fake;
    var a = H.roll(30);
    out.a = a;
    out.pendingAfterA = localStorage.getItem('sf_pending_planet_v1');
    out.aPersisted = H.list().some(function (x) { return x.id === a.id; });

    /* b. unbound roll after the pending record was consumed */
    var b = H.roll(15);
    out.b = b;
    out.pendingAfterB = localStorage.getItem('sf_pending_planet_v1');

    /* c. five consecutive rolls, ids must differ */
    var runs = [];
    for (var i = 0; i < 5; i++) runs.push(H.roll(15));
    out.runs = runs;
    out.ids = runs.map(function (x) { return x.id; });
    out.uniqueIds = out.ids.filter(function (v, i, arr) { return arr.indexOf(v) === i; }).length;
    out.listSize = H.list().length;
  } catch (e) {
    out.error = String((e && e.stack) || e);
  }
  out.probeErrors = window.__probeErrors;
  document.title = JSON.stringify(out);
}, 800);
</script>
"""


def run_once(path):
    src = open(path, encoding="utf-8", newline="").read()
    tmp = tempfile.mkdtemp(prefix="bind-")
    probe_path = os.path.join(tmp, "probe.html")
    open(probe_path, "w", encoding="utf-8", newline="").write(
        src.replace("</body>", PROBE + "</body>", 1))
    flags = [CHROME, "--headless=new", "--disable-gpu", "--use-angle=swiftshader",
             "--enable-unsafe-swiftshader", "--disable-gpu-compositing",
             "--no-sandbox", "--mute-audio", "--hide-scrollbars", "--no-first-run",
             "--disable-extensions", "--disable-background-networking",
             "--autoplay-policy=no-user-gesture-required",
             "--window-size=1000,760",
             "--user-data-dir=" + tempfile.mkdtemp(prefix="bind-prof-"),
             "--virtual-time-budget=4000", "--dump-dom"]
    flags.append(Path(probe_path).as_uri())
    r = subprocess.run(flags, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    m = re.search(r"<title>(.*?)</title>", r.stdout or "", re.S)
    if not m:
        return {"error": "NO TITLE", "stderr": (r.stderr or "")[-400:]}
    try:
        return json.loads(m.group(1))
    except Exception as e:
        return {"error": "BAD JSON: " + str(e), "title": m.group(1)[:400]}


def check(d):
    a = d.get("a") or {}
    b = d.get("b") or {}
    runs = d.get("runs") or []
    ids = d.get("ids") or []
    c = {}
    c["api_present"] = bool(d.get("api"))
    # a: fake pending drives identity, tier still from the 30m table
    c["a_bound"] = a.get("bound") is True
    c["a_name_from_pending"] = a.get("name") == "蓝海"
    c["a_hue_from_pending"] = a.get("hue") == 210
    c["a_from_kind"] = (a.get("from") or {}).get("kind") == "ocean"
    c["a_from_name"] = (a.get("from") or {}).get("name") == "蓝海"
    c["a_id_has_kind"] = str(a.get("id") or "").startswith("b") and "ocean" in str(a.get("id") or "")
    c["a_tier_from_table"] = a.get("tier") in ("common", "rare", "epic", "legend")
    c["a_minutes"] = a.get("minutes") == 30
    c["a_pending_cleared"] = d.get("pendingAfterA") is None
    c["a_persisted"] = bool(d.get("aPersisted"))
    # b: no pending -> legacy random path
    c["b_unbound"] = b.get("bound") is False
    c["b_from_null"] = b.get("from") is None
    c["b_name_present"] = bool(b.get("name"))
    c["b_tier_from_table"] = b.get("tier") in ("common", "rare", "epic")
    c["b_minutes"] = b.get("minutes") == 15
    c["b_pending_still_clear"] = d.get("pendingAfterB") is None
    # c: ids differ
    c["c_five_rolls"] = len(runs) == 5
    c["c_five_ids"] = len(ids) == 5 and all(ids)
    c["c_unique_ids"] = d.get("uniqueIds") == 5
    c["c_all_unbound"] = all(x.get("bound") is False for x in runs)
    c["c_names_present"] = all(bool(x.get("name")) for x in runs)
    # page health
    c["no_probe_errors"] = not (d.get("probeErrors") or []) and not d.get("error")
    return c


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    d = run_once(HTML)
    c = check(d)
    report = {
        "file": os.path.abspath(HTML),
        "a_bound_roll": d.get("a"),
        "a_pending_after": d.get("pendingAfterA"),
        "a_persisted": d.get("aPersisted"),
        "b_unbound_roll": d.get("b"),
        "b_pending_after": d.get("pendingAfterB"),
        "c_ids": d.get("ids"),
        "c_unique": d.get("uniqueIds"),
        "c_rolls": d.get("runs"),
        "probe_errors": d.get("probeErrors"),
        "error": d.get("error"),
        "checks": c,
        "pass": all(c.values()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
