"""Quantify the "planet pops out instead of fading" bug.

Walks the simulation with Starfield.seek() in fixed steps and, for every
sample, runs the REAL bodies() pass on a throw-away queue with the masses loop
instrumented. Records how many masses were considered, how many were actually
drawn, and which cull branch rejected the rest:

  behind   project() returned null
  far      pj[2] > 70000
  offscreen  screen-bounds cull
  faded    massVis <= 0

Also records the camera basis so an abrupt look-target switch (the ang > .62
gaze filter) is visible as a one-frame camera rotation.

  python -I probe_pop.py <html> [seconds] [step]
"""
import re
import sys
import os
import json
import subprocess
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

html = sys.argv[1]
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
step = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
outjson = sys.argv[4] if len(sys.argv) > 4 else None

src = open(html, encoding='utf-8').read()
patched = 'v137-pop-fade' in src

# ---- instrument the masses loop inside bodies() (probe copy only) ----------
if patched:
    subs = [
        # every mass examined: record it before the fade is applied
        ('  for(const m of c.masses){\n   const pj=project([m.x,m.y,m.z]);\n   if(!pj){',
         '  for(const m of c.masses){\n'
         '   window.__pbStats.total++;'
         '   const pj=project([m.x,m.y,m.z]);'
         '   const __mr={kind:m.kind,wx:+m.x.toFixed(1),wy:+m.y.toFixed(1),wz:+m.z.toFixed(1),'
         'x:pj?Math.round(pj[0]):-9999,y:pj?Math.round(pj[1]):-9999,d:pj?Math.round(pj[2]):999999,'
         'r:pj?Math.round(m.r*pj[3]):0,a:0,st:"behind"};'
         'window.__pbMass.push(__mr);'
         'if(!pj){window.__pbStats.behind++;'),
        # fade reached zero: this is the only allowed skip
        ('   if(m.fade<=0.0005){m.fade=0;continue;}',
         '   if(m.fade<=0.0005){m.fade=0;window.__pbStats.faded++;__mr.st="fade";continue;}'),
        ('   massVis=m.fade;',
         '   massVis=m.fade;__mr.st="drawn";__mr.a=m.fade;'),
        ('    if(m.fade!==undefined)m.fade=Math.max(0,m.fade-popMax);\n    continue;',
         '    if(m.fade!==undefined)m.fade=Math.max(0,m.fade-popMax);\n    __mr.a=m.fade||0;\n    continue;'),
        ('   {const rp=m.r*pj[3];if(rp>H*.42)massVis*=clamp(H*.42/rp,.30,1);}',
         '   {const rp=m.r*pj[3];if(rp>H*.42)massVis*=clamp(H*.42/rp,.30,1);}window.__pbStats.drawn++;'),
    ]
else:
    subs = [
        # every mass examined: record where it is before applying any cull
        ('  for(const m of c.masses){\n   const pj=project([m.x,m.y,m.z]);if(!pj||pj[2]>70000)continue;',
         '  for(const m of c.masses){\n'
         '   window.__pbStats.total++;'
         '   const pj=project([m.x,m.y,m.z]);'
         '   const __mr={kind:m.kind,wx:+m.x.toFixed(1),wy:+m.y.toFixed(1),wz:+m.z.toFixed(1),'
         'x:pj?Math.round(pj[0]):-9999,y:pj?Math.round(pj[1]):-9999,d:pj?Math.round(pj[2]):999999,'
         'r:pj?Math.round(m.r*pj[3]):0,a:pj?+clamp((70000-pj[2])/45000).toFixed(3):0,st:""};'
         'window.__pbMass.push(__mr);'
         'if(!pj){window.__pbStats.behind++;__mr.st="behind";continue;}'
         'if(pj[2]>70000){window.__pbStats.far++;__mr.st="far";continue;}'),
        # screen rectangle
        ('if(pj[0]+cullR<0||pj[0]-cullR>W||pj[1]+cullR<0||pj[1]-cullR>H)continue;',
         'if(pj[0]+cullR<0||pj[0]-cullR>W||pj[1]+cullR<0||pj[1]-cullR>H){window.__pbStats.offscreen++;__mr.st="off";continue;}'),
        # distance fade reached zero
        ('massVis=clamp((70000-pj[2])/45000);if(massVis<=0)continue;',
         'massVis=clamp((70000-pj[2])/45000);__mr.a=+massVis.toFixed(3);if(massVis<=0){window.__pbStats.faded++;__mr.st="fade";continue;}'),
        # survived every cull and entered the painter
        ('drawMass(m,region(m.x,m.z),time);massVis=1;',
         '__mr.st="drawn";window.__pbStats.drawn++;drawMass(m,region(m.x,m.z),time);massVis=1;'),
    ]
for old, new in subs:
    n = src.count(old)
    assert n == 1, 'instrument anchor %r count=%d' % (old[:60], n)
    src = src.replace(old, new, 1)

# ---- expose a snapshot inside the IIFE ------------------------------------
TAIL = '\nrequestAnimationFrame(frame);\n})();'
assert src.count(TAIL) == 1
snap = '''
window.__pbStats={total:0,behind:0,far:0,offscreen:0,faded:0,drawn:0};
window.__pbMass=[];
window.__pbSnap=function(){
 const lpe=(typeof LivingPlanetEngine!=='undefined')?LivingPlanetEngine.enabled:null;
 if(lpe!==null)LivingPlanetEngine.enabled=false;
 window.__pbStats={total:0,behind:0,far:0,offscreen:0,faded:0,drawn:0};
 window.__pbMass=[];
 const q0=queue.length;
 try{bodies();}finally{
  queue.length=q0;
  if(lpe!==null)LivingPlanetEngine.enabled=lpe;
 }
 const st=window.__pbStats;
 return {t:+time.toFixed(2),tr:+travel.toFixed(1),v:st.drawn,tot:st.total,
  b:st.behind,f:st.far,o:st.offscreen,fd:st.faded,
  sk:+LowOrbitSkimmer.skimW.toFixed(3),cap:capturePhase,
  fx:+camera.forward[0].toFixed(4),fy:+camera.forward[1].toFixed(4),fz:+camera.forward[2].toFixed(4),
  p:+camera.pitch.toFixed(4),y:+camera.yaw.toFixed(4),ms:window.__pbMass};
};'''
src = src.replace(TAIL, '\n' + snap + TAIL, 1)

# ---- runner ---------------------------------------------------------------
n = max(1, int(round(secs / step)))
runner = '''<script>
window.__errors=[];window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;S.seek(1);
 const rec=[];
 for(let i=0;i<%d;i++){S.seek(%r);rec.push(window.__pbSnap());}
 document.title=JSON.stringify({errors:window.__errors,rec:rec});
}catch(e){document.title=JSON.stringify({probeError:String(e),stack:String(e&&e.stack).slice(0,400)});}
</script>''' % (n, step)
assert src.count('</body>') >= 1
src = src.replace('</body>', runner + '</body>', 1)

with tempfile.TemporaryDirectory(prefix='pop-probe-') as td:
    probe = os.path.join(td, 'pop.probe.html')
    with open(probe, 'w', encoding='utf-8', newline='') as f:
        f.write(src)
    url = 'file:///' + probe.replace('\\', '/') + '?seed=1a2b'
    base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
            '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
            '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
            '--disable-background-networking', '--window-size=1600,900']
    prof = os.path.join(td, 'profile')
    dom = subprocess.run(base + ['--user-data-dir=' + prof, '--dump-dom', url],
                         capture_output=True, text=True, encoding='utf-8',
                         errors='replace', timeout=600).stdout or ''

m = re.search(r'<title>(.*?)</title>', dom, re.S)
if not m:
    sys.exit('NO TITLE — probe failed to run')
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE ERROR: ' + d['probeError'] + '\n' + d.get('stack', ''))
rec = d['rec']
if outjson:
    with open(outjson, 'w', encoding='utf-8') as f:
        json.dump({'errors': d.get('errors'), 'rec': rec}, f)


def angle(a, b):
    dot = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    dot = max(-1.0, min(1.0, dot))
    fx = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    import math
    return math.degrees(math.acos(dot))


print('--- probe_pop: %s  (%.0f s, step %.2f s, %d frames) ---' % (html, secs, step, len(rec)))
print('errors:', d.get('errors'))

drops = []
for i in range(1, len(rec)):
    p, c = rec[i - 1], rec[i]
    dvis = c['v'] - p['v']
    pct = abs(dvis) / max(1, p['v'], c['v']) * 100.0
    drop_pct = max(0, -dvis) / max(1, p['v']) * 100.0
    rot = angle([p['fx'], p['fy'], p['fz']], [c['fx'], c['fy'], c['fz']])
    drops.append((drop_pct, -dvis, i, rot,
                  c['b'] - p['b'], c['f'] - p['f'], c['o'] - p['o'], c['fd'] - p['fd'],
                  c['tot'] - p['tot']))
drops.sort(reverse=True)


def why(ev):
    labels = ['behind', 'far', 'offscreen', 'faded']
    delta = ev[4:8]
    j = max(range(4), key=lambda k: delta[k])
    return labels[j], delta[j], delta


print('\ntop single-frame visible-count drops:')
shown = 0
for ev in drops:
    if ev[0] < 0.01:
        break
    shown += 1
    if shown > 8:
        break
    i = ev[2]
    p, c = rec[i - 1], rec[i]
    lab, val, delta = why(ev)
    print('  t=%7.1fs  travel=%8.0f  visible %d -> %d  drop %.1f%%  camRot %.2f deg  '
          'reason=%s (+%d)  d[behind,far,off,faded]=%s'
          % (c['t'], c['tr'], p['v'], c['v'], ev[0], ev[3], lab, val, delta))
    for j in (i - 1, i):
        r = rec[j]
        print('      frame t=%7.1f vis=%3d tot=%3d behind=%3d far=%3d off=%3d faded=%3d pitch=%.3f yaw=%.3f'
              % (r['t'], r['v'], r['tot'], r['b'], r['f'], r['o'], r['fd'], r['p'], r['y']))

max_pct = max((e[0] for e in drops), default=0.0)
big30 = [e for e in drops if e[0] >= 30.0]
big10 = [e for e in drops if e[0] >= 10.0]
print('\nmax single-frame visible-count change: %.1f%%' % max_pct)
print('frames with >=30%% drop: %d   >=10%% drop: %d' % (len(big30), len(big10)))
vis = [r['v'] for r in rec]
print('visible count range: %d .. %d  (mean %.1f)'
      % (min(vis), max(vis), sum(vis) / len(vis)))

# ---- effective (fade-weighted) visible population ---------------------------
def drawn_alpha(m):
    """The alpha the painter actually receives from this body, 0..1."""
    if m['st'] != 'drawn':
        return 0.0
    if patched:
        return max(0.0, min(1.0, m['a']))
    if m['kind'] == 4:
        # drawHole's beacon runs to 85k; bodies()' massVis reaches 0 at 70k
        return max(min(1.0, m['a']),
                   min(1.0, max(0.0, (85000 - m['d']) / 45000.0)))
    if 5 <= m['kind'] <= 7:
        # the star/colossus core is pushed at alpha 1, ignoring massVis
        return 1.0
    return max(0.0, min(1.0, m['a']))


def fade_state(m):
    """Per-body visibility coefficient used for the count metric.

    In the patched build this is the persistent m.fade itself, which keeps
    easing to zero even after a body leaves the frustum; that is exactly the
    quantity the fix introduces. In the original build there is no such state,
    so the rendered alpha is used.
    """
    if patched:
        return max(0.0, min(1.0, m['a']))
    return drawn_alpha(m)


eff = [sum(fade_state(m) for m in r['ms']) for r in rec]
eff_changes = []
for i in range(1, len(eff)):
    d_eff = eff[i] - eff[i - 1]
    eff_changes.append((abs(d_eff) / max(1.0, eff[i - 1], eff[i]) * 100.0, i, d_eff))
eff_changes.sort(reverse=True)
print('\neffective visible (sum of per-body fade state):')
print('  range %.2f .. %.2f  mean %.2f' % (min(eff), max(eff), sum(eff) / len(eff)))
print('  MAX single-frame change: %.2f%%'
      % (eff_changes[0][0] if eff_changes else 0.0))
for pct, i, d_eff in eff_changes[:8]:
    print('  t=%7.1fs  eff %.2f -> %.2f  change %.2f%%'
          % (rec[i]['t'], eff[i - 1], eff[i], pct))

# ---- per-body: largest one-frame alpha drop on a visible body ---------------
def mkey(m):
    return (m['kind'], round(m['wx']), round(m['wy']), round(m['wz']))


def onscreen(m):
    r = m['r']
    return (m['x'] + r > 0 and m['x'] - r < 1600 and
            m['y'] + r > 0 and m['y'] - r < 900)


pops = []
body_drops = []
for i in range(1, len(rec)):
    prev = {mkey(m): m for m in rec[i - 1]['ms'] if m['st'] == 'drawn'}
    cur = {mkey(m): m for m in rec[i]['ms']}
    for k, m in prev.items():
        p_prev = drawn_alpha(m)
        if p_prev < 0.05 or not onscreen(m):
            continue
        c = cur.get(k)
        p_cur = drawn_alpha(c) if c else 0.0
        body_drops.append((p_prev - p_cur, i, m, c))
        if p_cur <= 1e-9:
            pops.append((p_prev, i, m, c))
body_drops.sort(key=lambda e: e[0], reverse=True)
print('\nvisible bodies that vanished in one frame (alpha>=0.05): %d' % len(pops))
print('  max one-frame alpha drop on a visible body: %.3f'
      % (body_drops[0][0] if body_drops else 0.0))
for a, i, m, c in body_drops[:8]:
    if a < 0.05:
        break
    status = (c or {}).get('st', 'gone-from-chunks')
    nxt = '' if not c else ' next x=%d y=%d a=%.3f' % (c['x'], c['y'], c['a'])
    print('  t=%7.1fs kind=%d z=%9.0f  last screen (%4d,%4d) rad=%3dpx a=%.3f -> %s%s'
          % (rec[i]['t'], m['kind'], m['wz'], m['x'], m['y'], m['r'], a, status, nxt))

