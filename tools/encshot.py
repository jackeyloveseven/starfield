"""Screenshot the encounter at a chosen phase.

capshot.py stops inside the flash (phase 3) and can only walk forward from there,
so it cannot see GRIP (phase 1) or the run-up to the fall. This stops the seek the
moment the capture reaches a target phase, then advances a chosen number of
seconds, so any beat of the sequence can be framed.

  python -I encshot.py <html> <png> <seed> <at> <phase> <intoSeconds>
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
AT = sys.argv[4] if len(sys.argv) > 4 else '0'
PHASE = int(sys.argv[5]) if len(sys.argv) > 5 else 1
INTO = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{AT}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield,c=document.getElementById("landscape");
 const move=(x,y)=>c.dispatchEvent(new PointerEvent("pointermove",{{clientX:x,clientY:y,pointerId:1,bubbles:true,pointerType:"mouse"}}));
 let g=0,found=false,seen=[];
 while(g++<5000){{
  const h=S.holeDir();
  if(h)move(h.right>0?innerWidth*0.97:innerWidth*0.03,innerHeight*0.5);
  S.seek(0.25);
  const ph=S.getState().capture;
  if(seen[seen.length-1]!==ph)seen.push(ph);
  if(ph>={PHASE}){{found=true;break;}}
 }}
 if(found)S.seek({INTO});
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 const st=S.getState();
 document.title=JSON.stringify({{errors:window.__errors,found,loops:g,seen,state:st,flock:S.flock()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err)}});}}</script>'''

src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('encshot-' + os.path.basename(PNG).replace('.png', '') + '.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={SEED}'
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--window-size=1600,900']


def run(extra):
    with tempfile.TemporaryDirectory(prefix='enc-') as prof:
        return subprocess.run(base + [f'--user-data-dir={prof}'] + extra + [url],
                              capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=900)


run([f'--screenshot={PNG}'])
dom = run(['--dump-dom']).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
print(f'--- {PNG} (seed={SEED}, at={AT}, phase>={PHASE}, into={INTO}) ---')
if m:
    d = json.loads(m.group(1))
    print('  probeError:', d.get('probeError'))
    print('  errors    :', d.get('errors'))
    print('  reached   :', d.get('found'), 'after', d.get('loops'), 'seeks; phases seen:', d.get('seen'))
    print('  flock     :', d.get('flock'))
    st = d.get('state') or {}
    for k in ('travel', 'capture', 'region', 'distance', 'focal', 'fillMPx', 'fps', 'postMs'):
        if k in st:
            print(f'  {k:<10}: {st[k]}')
else:
    print('  NO TITLE')
print('  png bytes :', os.path.getsize(PNG) if os.path.exists(PNG) else 'MISSING')
