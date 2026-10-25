"""Acceptance probe for v143_naming.py.

Two headless Chrome runs share one profile and one probe URL so localStorage
survives the restart:

  run 1: a. clear + roll(15) + openFor -> naming button exists on the back face
         b. click button, type "归途", submit -> card name, named flag and
            localStorage all updated
         c. reopen the same (stale) roll object -> button disabled, "已命名"
         e. second planet rejects "" and 13 chars without changing its record
  run 2: d. fresh process, same profile -> the name is still "归途" on the card
            and in the collection list

Run:  python -I verify_naming.py <out.html>
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PREFIX = "__NAMING_VERIFY__"
HTML = sys.argv[1] if len(sys.argv) > 1 else "starfield-v143.html"

PROBE = r"""
<script>
(function () {
  var errors = [];
  window.addEventListener('error', function (e) { errors.push(String(e.message || e)); });
  window.addEventListener('unhandledrejection', function (e) { errors.push(String(e.reason)); });
  var PREFIX = '__NAMING_VERIFY__';

  function q(sel, root) { return (root || document).querySelector(sel); }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function waitFor(fn, ms) {
    var left = ms || 4000;
    return (function step() {
      var v = null;
      try { v = fn(); } catch (e) {}
      if (v) return Promise.resolve(v);
      if (left <= 0) return Promise.resolve(null);
      left -= 50;
      return sleep(50).then(step);
    })();
  }
  function finish(o) {
    o.errors = errors;
    document.title = PREFIX + JSON.stringify(o);
  }
  function stored(id) {
    var H = window.StarfieldHatch, list = (H && H.list) ? H.list() : [];
    for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
    return null;
  }
  function cardName() {
    var e = q('#sf-hatch .sf-hatch-name');
    return e ? e.textContent : null;
  }
  function foilText() {
    var e = q('#sf-hatch .sf-foil');
    return e ? e.textContent : null;
  }
  function btnState() {
    var b = q('#sf-hatch .sf-hb-name-btn');
    return b ? { exists: true, disabled: !!b.disabled, text: b.textContent } :
               { exists: false, disabled: null, text: null };
  }

  async function phase1() {
    var H = window.StarfieldHatch;
    var out = { phase: '1', api: !!(H && H.roll && H.list && H.clear && H.openFor && H.hide) };
    if (!out.api) { finish(out); return; }

    /* a */
    H.clear();
    var it = H.roll(15);
    out.roll = { id: it.id, name: it.name, tier: it.tier, minutes: it.minutes };
    H.openFor(it);
    await waitFor(function () { return q('#sf-hatch .sf-hatch-back .sf-hb-name-btn'); });
    var back = q('#sf-hatch .sf-hatch-back');
    var btn0 = btnState();
    out.a = {
      backExists: !!back,
      buttonExists: btn0.exists,
      buttonText: btn0.text,
      buttonDisabled: btn0.disabled,
      rowCount: back ? back.querySelectorAll('.sf-hb-row').length : 0
    };
    if (!btn0.exists) { finish(out); return; }

    /* flip the card (tap to reveal, tap again to flip) then use the button */
    var card = q('#sf-hatch .sf-hatch-card');
    card.click();
    await sleep(30);
    card.click();
    await sleep(60);
    out.flippedBeforeName = card.classList.contains('flipped');
    q('#sf-hatch .sf-hb-name-btn').click();
    await waitFor(function () { return q('#sf-hatch .sf-hb-name-form.on'); });
    var form = q('#sf-hatch .sf-hb-name-form');
    var input = q('#sf-hatch .sf-hb-name-input');
    if (!form || !input) { out.error = 'naming form/input missing'; finish(out); return; }

    /* b */
    input.value = '归途';
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    await waitFor(function () { return stored(it.id) && stored(it.id).named === true; }, 3000);
    await sleep(80);
    var rec = stored(it.id) || {};
    var raw = [];
    try { raw = JSON.parse(localStorage.getItem('sf_collection_v1') || '[]'); } catch (e) {}
    var rawRec = null;
    for (var i = 0; i < raw.length; i++) if (raw[i].id === it.id) rawRec = raw[i];
    out.b = {
      cardName: cardName(),
      named: rec.named === true,
      listName: rec.name,
      storedName: rawRec ? rawRec.name : null,
      storedNamed: rawRec ? rawRec.named === true : null,
      foil: foilText(),
      buttonText: btnState().text,
      buttonDisabled: btnState().disabled
    };

    /* c: reopen the same item, passing the stale pre-rename object */
    H.hide();
    await sleep(100);
    H.openFor(it);
    await waitFor(function () { return q('#sf-hatch .sf-hb-name-btn'); });
    await sleep(150);
    out.c = {
      buttonDisabled: btnState().disabled,
      buttonText: btnState().text,
      cardName: cardName()
    };

    /* e: a second planet must reject invalid names without consuming the slot */
    var it2 = H.roll(15);
    H.hide();
    await sleep(80);
    H.openFor(it2);
    await waitFor(function () { return q('#sf-hatch .sf-hb-name-btn'); });
    await sleep(100);
    var before = stored(it2.id) || {};
    q('#sf-hatch .sf-hb-name-btn').click();
    await waitFor(function () { return q('#sf-hatch .sf-hb-name-form.on'); });
    var form2 = q('#sf-hatch .sf-hb-name-form');
    var input2 = q('#sf-hatch .sf-hb-name-input');
    var msg2 = q('#sf-hatch .sf-hb-name-msg');

    input2.value = '';
    form2.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    await sleep(150);
    var afterEmpty = stored(it2.id) || {};
    out.e = {
      before: { name: before.name, named: !!before.named },
      empty: { name: afterEmpty.name, named: !!afterEmpty.named, msg: msg2 ? msg2.textContent : null },
      emptyFormOpen: form2.classList.contains('on')
    };

    input2.value = '一二三四五六七八九十甲乙丙';
    form2.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    await sleep(150);
    var afterLong = stored(it2.id) || {};
    out.e.long = { name: afterLong.name, named: !!afterLong.named, msg: msg2 ? msg2.textContent : null };
    out.e.longFormOpen = form2.classList.contains('on');
    out.e.inputLength = Array.from(input2.value).length;
    out.e.buttonText = btnState().text;
    out.e.buttonDisabled = btnState().disabled;

    localStorage.setItem('sf_naming_target', it.id);
    localStorage.setItem('sf_naming_phase', '2');
    finish(out);
  }

  async function phase2() {
    var H = window.StarfieldHatch;
    var targetId = localStorage.getItem('sf_naming_target');
    var rec = stored(targetId);
    var out = {
      phase: '2',
      api: !!(H && H.list && H.openFor && H.openList),
      targetId: targetId,
      found: !!rec
    };
    if (!out.api || !rec) { finish(out); return; }

    H.openFor(rec);
    await waitFor(function () { return q('#sf-hatch .sf-hb-name-btn'); });
    await sleep(200);
    out.d = {
      name: rec.name,
      named: rec.named === true,
      cardName: cardName(),
      foil: foilText(),
      buttonText: btnState().text,
      buttonDisabled: btnState().disabled
    };

    H.openList();
    await waitFor(function () { return q('#sf-hatch-list.on'); });
    await sleep(150);
    var names = Array.prototype.map.call(
      document.querySelectorAll('#sf-hatch-list .sf-hl-name'),
      function (e) { return e.textContent; });
    out.d.listNames = names;
    out.d.listHasName = names.indexOf('归途') >= 0;
    finish(out);
  }

  setTimeout(function () {
    var phase = localStorage.getItem('sf_naming_phase') || '1';
    (phase === '2' ? phase2() : phase1()).catch(function (e) {
      finish({ phase: phase, error: String((e && e.stack) || e) });
    });
  }, 250);
})();
</script>
"""


def run_once(probe_path, profile):
    url = Path(probe_path).as_uri()
    flags = [
        CHROME, "--headless=new", "--disable-gpu",
        "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-gpu-compositing", "--no-sandbox", "--mute-audio",
        "--hide-scrollbars", "--no-first-run", "--disable-extensions",
        "--disable-background-networking",
        "--autoplay-policy=no-user-gesture-required",
        "--window-size=1000,760",
        "--user-data-dir=" + profile,
        "--virtual-time-budget=15000",
        "--dump-dom", url,
    ]
    r = subprocess.run(flags, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    m = re.search(r"<title>(.*?)</title>", r.stdout or "", re.S)
    if not m:
        return {"error": "NO TITLE", "stderr": (r.stderr or "")[-500:]}
    title = html.unescape(m.group(1)).strip()
    if not title.startswith(PREFIX):
        return {"error": "NO PROBE TITLE", "title": title[:300]}
    try:
        return json.loads(title[len(PREFIX):])
    except Exception as e:
        return {"error": "BAD JSON: " + str(e), "title": title[:400]}


def check(p1, p2):
    a = p1.get("a") or {}
    b = p1.get("b") or {}
    c = p1.get("c") or {}
    e = p1.get("e") or {}
    e0 = e.get("before") or {}
    ee = e.get("empty") or {}
    el = e.get("long") or {}
    d = p2.get("d") or {}
    chk = {}
    chk["api_present"] = bool(p1.get("api")) and bool(p2.get("api"))
    chk["a_back_exists"] = a.get("backExists") is True
    chk["a_naming_button"] = a.get("buttonExists") is True
    chk["a_button_enabled"] = a.get("buttonDisabled") is False
    chk["b_card_name"] = b.get("cardName") == "归途"
    chk["b_named_true"] = b.get("named") is True
    chk["b_list_name"] = b.get("listName") == "归途"
    chk["b_stored_name"] = b.get("storedName") == "归途"
    chk["b_stored_named"] = b.get("storedNamed") is True
    chk["b_foil_keeps_serial"] = "NO." in str(b.get("foil") or "")
    chk["b_foil_serial"] = str(b.get("foil") or "").startswith("NO.001")
    chk["b_foil_self_named"] = "自命名" in str(b.get("foil") or "")
    chk["c_button_disabled"] = c.get("buttonDisabled") is True
    chk["c_button_text"] = str(c.get("buttonText") or "").strip() == "已命名"
    chk["c_card_name"] = c.get("cardName") == "归途"
    chk["e_empty_rejected"] = (
        (ee.get("name") == e0.get("name")) and (ee.get("named") is False)
        and bool(str(ee.get("msg") or "").strip()) and e.get("emptyFormOpen") is True)
    chk["e_long_rejected"] = (
        (el.get("name") == e0.get("name")) and (el.get("named") is False)
        and bool(str(el.get("msg") or "").strip()) and e.get("longFormOpen") is True)
    chk["e_slot_still_open"] = e.get("buttonDisabled") is False and \
        str(e.get("buttonText") or "").strip() == "命名"
    chk["d_persisted_name"] = d.get("name") == "归途"
    chk["d_persisted_named"] = d.get("named") is True
    chk["d_card_name"] = d.get("cardName") == "归途"
    chk["d_button_disabled"] = d.get("buttonDisabled") is True
    chk["d_button_text"] = str(d.get("buttonText") or "").strip() == "已命名"
    chk["d_foil_self_named"] = "自命名" in str(d.get("foil") or "")
    chk["d_foil_target_serial"] = str(d.get("foil") or "").startswith("NO.001")
    chk["d_list_has_name"] = d.get("listHasName") is True
    chk["no_probe_errors"] = (
        not (p1.get("errors") or []) and not p1.get("error")
        and not (p2.get("errors") or []) and not p2.get("error"))
    return chk


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    src = open(HTML, encoding="utf-8", newline="").read()
    if src.count("</body>") != 1:
        sys.exit("expected exactly one </body>")

    root = tempfile.mkdtemp(prefix="naming-verify-")
    profile = os.path.join(root, "profile")
    os.makedirs(profile)
    probe_path = os.path.join(root, "probe.html")
    try:
        with open(probe_path, "w", encoding="utf-8", newline="") as f:
            f.write(src.replace("</body>", PROBE + "</body>", 1))
        p1 = run_once(probe_path, profile)
        p2 = run_once(probe_path, profile)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    chk = check(p1, p2)
    report = {
        "file": os.path.abspath(HTML),
        "run1": p1,
        "run2": p2,
        "checks": chk,
        "pass": all(chk.values()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["pass"] else 1)


if __name__ == "__main__":
    main()
