"""Deterministic screenshot harness for the single-file artwork.

The probe runs *synchronously* at parse time (no setTimeout — headless
--screenshot does not honour timer-based probes): it optionally picks a
departure region, presses 起航, seeks the simulation forward without drawing
(window.Starfield.seek), and freezes CSS animation so the captured frame is a
pure function of (seed, at, seek). Prints the diagnostic payload so every shot
doubles as a state assertion.

  python -I shot.py starfield.html shots/p1-core.png --seed 1a2b --at 3 --seek 120
"""
import re, sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('png')
ap.add_argument('--seed', default=None, help='hex or decimal SEED')
ap.add_argument('--at', type=int, default=None, help='click departure button N first')
ap.add_argument('--seek', type=float, default=0.0, help='simulated seconds before the shot')
ap.add_argument('--size', default='1600x900')
ap.add_argument('--keep-intro', action='store_true', help='do not press 起航')
ap.add_argument('--keep-hud', action='store_true', help='leave the flying HUD hidden')
ap.add_argument('--until-capture', action='store_true', help='seek until a capture begins')
ap.add_argument('--after', type=float, default=0.0, help='extra seconds after detection')
a = ap.parse_args()

W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

click_dep = (f'const d=document.querySelectorAll(".destination")[{a.at}];if(d)d.click();'
             if a.at is not None else '')
click_begin = 'const b=document.getElementById("begin");if(b)b.click();' if not a.keep_intro else ''
hide_intro = '' if a.keep_intro else "document.getElementById('intro').style.display='none';"
show_hud = '' if a.keep_hud else "document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');"

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 {click_dep}
 {click_begin}
 const S=window.Starfield;
 let seeked=null;
 if(S&&S.seek&&{'true' if a.until_capture else 'false'}){{let g=0;while(g++<500&&S.getState().capture===0)S.seek(4);seeked={{phase:S.getState().capture,travel:S.getState().travel}};}}
 else if(S&&S.seek&&{a.seek}>0)seeked=S.seek({a.seek});
 if(S&&S.seek&&{a.after}>0){{S.seek({a.after});if(seeked)seeked.after=S.getState().capture;}}
 {hide_intro}
 {show_hud}
 window.__probe={{errors:window.__errors,seeked,state:S?S.getState():null}};
 document.title=JSON.stringify(window.__probe);
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,300)}});}}</script>'''

src = open(a.html, encoding='utf-8').read()
if '</body>' not in src:
    sys.exit('no </body>')
png = os.path.abspath(a.png)
os.makedirs(os.path.dirname(png), exist_ok=True)
probe_html = png.replace('.png', '.probe.html')
open(probe_html, 'w', encoding='utf-8', newline='').write(
    src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + probe_html.replace('\\', '/') + query

base = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']


def run(extra, timeout=120):
    # A private profile per run: concurrent headless instances otherwise fight
    # over the default profile and hang.
    with tempfile.TemporaryDirectory(prefix='shot-') as profile:
        return subprocess.run(base + [f'--user-data-dir={profile}'] + extra + [url],
                              capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=timeout)


run([f'--screenshot={png}'])
# No --virtual-time-budget here: once the probe has pressed 起航 the page owns a
# live AudioContext, virtual time never reaches its budget, and Chrome hangs.
# The probe is synchronous, so the title is already final at the load event.
dom = run(['--dump-dom']).stdout or ''

m = re.search(r'<title>(.*?)</title>', dom, re.S)
print(f'--- {a.png}  ({W}x{H}, seed={a.seed}, at={a.at}, seek={a.seek}) ---')
if m:
    try:
        d = json.loads(m.group(1))
        if d.get('probeError'):
            print('  PROBE FAILED:', d['probeError'])
            print('  ', d.get('stack', ''))
        st = d.get('state') or {}
        print('  errors :', d.get('errors'))
        print('  seeked :', d.get('seeked'))
        for k in ('region', 'regionMix', 'travel', 'fps', 'drawCalls', 'loadedChunks',
                  'lens', 'distance', 'pitch', 'birds', 'particles',
                  'capture', 'sling', 'masses', 'fillMPx', 'nebTex', 'nebGens', 'holeGL', 'postMs', 'holeDraws', 'holeLastRad'):
            if k in st:
                v = st[k]
                print(f'  {k:<13}: {v if not isinstance(v, float) else round(v, 2)}')
    except Exception:
        print('  raw title:', m.group(1)[:300])
else:
    print('  NO TITLE')
print('  png bytes:', os.path.getsize(png) if os.path.exists(png) else 'MISSING')
