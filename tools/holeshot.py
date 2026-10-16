"""Screenshot a black hole properly framed, so its geometry can actually be judged.

Seeks until the nearest ink well is close and near the middle of the frame, then
stops - a hole cropped by the frame edge says nothing about whether the disc, the
photon ring and the lensed far side are in the right places.
"""
import re
import sys
import os
import json
import subprocess
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
PNG = os.path.abspath(sys.argv[2])
SEED = sys.argv[3] if len(sys.argv) > 3 else '1a2b'
AT = sys.argv[4] if len(sys.argv) > 4 else '4'
MAXD = float(sys.argv[5]) if len(sys.argv) > 5 else 1600.0
MAXR = float(sys.argv[6]) if len(sys.argv) > 6 else 260.0

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{AT}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let g=0,found=false,last=null;
 while(g++<3000){{
  S.seek(0.4);
  const h=S.holeDir();
  if(h){{last=h;
   if(h.dist<{MAXD}&&h.fwd>400&&Math.abs(h.right)<{MAXR}){{found=true;break;}}
  }}
 }}
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 document.title=JSON.stringify({{errors:window.__errors,found,loops:g,last,state:S.getState()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err)}});}}</script>'''

src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('holeshot.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={SEED}'
base = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--window-size=1600,900']


def run(extra):
    with tempfile.TemporaryDirectory(prefix='hole-') as prof:
        return subprocess.run(base + [f'--user-data-dir={prof}'] + extra + [url],
                              capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=600)


run([f'--screenshot={PNG}'])
dom = run(['--dump-dom']).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
print(f'--- {PNG} (seed={SEED}, at={AT}) ---')
if m:
    d = json.loads(m.group(1))
    print('  probeError:', d.get('probeError'), ' errors:', d.get('errors'))
    print('  framed    :', d.get('found'), 'after', d.get('loops'), 'seeks')
    print('  hole      :', d.get('last'))
    st = d.get('state') or {}
    for k in ('travel', 'region', 'fillMPx', 'fps'):
        if k in st:
            print(f'  {k:<10}: {st[k]}')
else:
    print('  NO TITLE')
print('  png bytes :', os.path.getsize(PNG) if os.path.exists(PNG) else 'MISSING')
