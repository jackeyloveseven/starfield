"""TEMP diagnostic: dump the screen-space masses near a pixel so a defect can be
attributed to a kind. Not part of the deliverable.

  python -I probe_mpos.py <dbg.html> <seed> <at> <seek> <x> <y> <radius>
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html, seed, at, seek, X, Y, R = sys.argv[1:8]

probe = f'''<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{at}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;S.seek({seek});
 document.getElementById("intro").style.display='none';
 document.title=JSON.stringify({{errors:window.__errors,state:S.getState()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,400)}});}}</script>'''

src = open(html, encoding='utf-8').read()
out = os.path.abspath('shots/_mpos.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={seed}'
base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='mp-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=180)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE')
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + d.get('stack', ''))
st = d.get('state') or {}
print('errors :', d.get('errors'))
print('kinds  :', st.get('kinds'))
for key in ('mdump', 'mpos'):
    for v in st.get(key, []):
        print('  ', key, v)
