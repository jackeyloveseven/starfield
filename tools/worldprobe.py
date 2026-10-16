"""Dump the kind histogram the world is actually carrying, plus any page errors.

Same synchronous-probe trick as shot.py (no timers under headless --screenshot),
but this one only needs the title, so it never takes a picture. Proves that the
new kinds are genuinely out in the corridor and not just dead code.

  python -I worldprobe.py work-worlds-v18v.html --seed 1a2b --at 1 --seek 60
"""
import re, sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--seed', default='1a2b')
ap.add_argument('--at', type=int, default=1)
ap.add_argument('--seek', type=float, default=60.0)
a = ap.parse_args()

probe = f'''<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{a.at}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;S.seek({a.seek});
 document.getElementById("intro").style.display='none';
 window.__probe={{errors:window.__errors,state:S.getState()}};
 document.title=JSON.stringify(window.__probe);
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,300)}});}}</script>'''

src = open(a.html, encoding='utf-8').read()
out = os.path.abspath('shots/_worldprobe.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={a.seed}'

base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='wp-') as profile:
    r = subprocess.run(base + [f'--user-data-dir={profile}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE')
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + d.get('stack', ''))
st = d.get('state') or {}
kinds = st.get('kinds', '')
hist = {k: kinds.count(k) for k in '0123456789' if kinds.count(k)}
print('errors :', d.get('errors'))
print('travel :', round(st.get('travel', 0)))
print('masses :', st.get('masses'), 'kinds:', kinds, '->', hist)
print('fps    :', st.get('fps'), ' fillMPx:', st.get('fillMPx'), ' drawCalls:', st.get('drawCalls'))
