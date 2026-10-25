"""Acceptance probe for v142 sky events.

Headless Chrome, synchronous probe (same harness style as smoke.py):

  1. force a burst with window.sfTriggerGRB()
  2. flash intensity > 0.5 after 0.1 simulated seconds
  3. flash intensity < 0.05 after 1 more second (and exactly 0 after the burst)
  4. two consecutive triggers in the same chunk return the same duration
  5. the trigger changes no simulation state
  6. window.SF_SKY_EVENTS = false makes the trigger a no-op
  7. two separate browser runs with the same seed agree (determinism)

  python -I verify_skyevent.py <patched.html>
"""
import json
import os
import re
import subprocess
import sys
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SRC = sys.argv[1]
src0 = open(SRC, encoding="utf-8").read()

HOOK = ('<script>window.__errors=[];'
        'window.addEventListener("error",e=>window.__errors.push(String(e.message)));'
        '</script>')

STATE_KEYS = ("seed", "travel", "started", "masses", "kinds", "capture",
              "loadedChunks", "eye")


def probe(with_events, tag):
    probe_js = """
<script>try{
  if (%(events)s) window.SF_SKY_EVENTS = false;
  const b=document.getElementById('begin'); if(b) b.click();
  const S=window.Starfield;
  const pick=()=>{const s=S.getState(),o={};for(const k of %(keys)s)o[k]=s[k];return o;};
  const st0=pick();
  const g0=window.sfTriggerGRB();
  const st1=pick();
  const d1=window.__grbDuration;
  S.seek(0.1);
  const g1=window.__grb;
  S.seek(1.0);
  const g2=window.__grb;
  const g2s=S.getState();
  const sky1=window.__skyEventState();
  S.seek(19.0);
  const sky20=window.__skyEventState();
  window.sfTriggerGRB();
  const d2=window.__grbDuration;
  S.seek(0.1);
  const g3=window.__grb;
  document.title=JSON.stringify({
    tag:%(tag)r, enabled:window.SF_SKY_EVENTS!==false,
    errors:window.__errors,
    g0:g0, g1:g1, g2:g2, g3:g3, duration1:d1, duration2:d2,
    sameDuration:d1===d2,
    stateUnchanged:JSON.stringify(st0)===JSON.stringify(st1),
    simStateBefore:st0, simStateAfterFlash:st1,
    travelAfter:g2s.travel,
    sky:window.__skyEventState(),
    afterglow1s:sky1.afterglow, afterglow20s:sky20.afterglow
  });
}catch(e){document.title=JSON.stringify({tag:%(tag)r,probeError:String(e),stack:String(e&&e.stack).slice(0,400)});}
</script>""" % {"events": "true" if with_events else "false",
                 "keys": json.dumps(list(STATE_KEYS)),
                 "tag": tag}

    src = src0.replace('<meta charset="utf-8">',
                       '<meta charset="utf-8">' + HOOK, 1)
    src = src.replace('</body>', probe_js + '</body>', 1)
    out = os.path.abspath('verify_skyevent_%s.probe.html' % tag)
    open(out, 'w', encoding='utf-8', newline='').write(src)
    url = 'file:///' + out.replace(os.sep, '/') + '?seed=1a2b'

    with tempfile.TemporaryDirectory(prefix='skyevent-') as prof:
        r = subprocess.run(
            [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
             '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
             '--mute-audio', '--no-first-run', f'--user-data-dir={prof}',
             '--window-size=1280,720', '--dump-dom', url],
            capture_output=True, text=True, encoding='utf-8',
            errors='replace', timeout=300)
    m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
    if not m:
        raise SystemExit('NO TITLE for %s - %s' % (tag, (r.stderr or '')[-300:]))
    return json.loads(m.group(1))


def fp(x):
    return round(float(x), 4) if isinstance(x, (int, float)) else x


run_a = probe(False, 'a')
run_b = probe(False, 'b')
run_off = probe(True, 'off')

checks = {
    'flash_gt_0.5_at_0.1s': run_a.get('g1', 0) > 0.5,
    'flash_lt_0.05_at_1.1s': run_a.get('g2', 1) < 0.05,
    'flash_exactly_off_after_burst': run_a.get('g2') == 0,
    'same_duration_twice': run_a.get('sameDuration') is True,
    'deterministic_across_runs': fp(run_a.get('duration1')) == fp(run_b.get('duration1')),
    'state_unchanged_by_trigger': run_a.get('stateUnchanged') is True,
    'kill_switch_no_flash': run_off.get('enabled') is False and run_off.get('g1', 1) == 0
                             and run_off.get('g0', 1) == 0,
    'no_page_errors': not run_a.get('errors') and not run_b.get('errors'),
    'ring_lit_after_flash': run_a.get('afterglow1s', 0) > 0.05,
    'ring_gone_after_20s': run_a.get('afterglow20s', 1) < 0.005,
}
ok = all(checks.values())

report = {
    'file': SRC,
    'checks': checks,
    'run_a': {k: fp(v) for k, v in run_a.items()
              if k not in ('simStateBefore', 'simStateAfterFlash')},
    'run_b_duration1': fp(run_b.get('duration1')),
    'kill_switch': {k: fp(v) for k, v in run_off.items()
                    if k not in ('simStateBefore', 'simStateAfterFlash')},
    'pass': ok,
}
print(json.dumps(report, ensure_ascii=False, indent=2))
sys.exit(0 if ok else 1)
