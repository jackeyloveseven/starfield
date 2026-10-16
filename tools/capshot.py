"""Screenshot the capture at its flash moment.

shot.py's --until-capture cannot reach one any more: the gate now requires real
steering, and its probe never touches the pointer. This drives the pointer the way
captest.py does, synchronously, and stops the seek inside the flash phase.
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
INTO = sys.argv[5] if len(sys.argv) > 5 else '0.3'

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{AT}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield,c=document.getElementById("landscape");
 const move=(x,y)=>c.dispatchEvent(new PointerEvent("pointermove",{{clientX:x,clientY:y,pointerId:1,bubbles:true,pointerType:"mouse"}}));
 let g=0,found=false;
 while(g++<4000){{
  const h=S.holeDir();
  if(h)move(h.right>0?innerWidth*0.97:innerWidth*0.03,innerHeight*0.5);
  S.seek(0.5);
  if(S.getState().capture===3){{found=true;break;}}
 }}
 if(found)S.seek({INTO});
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 document.title=JSON.stringify({{errors:window.__errors,found,loops:g,state:S.getState()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err)}});}}</script>'''

src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('capshot.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={SEED}'
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--window-size=1600,900']


def run(extra):
    with tempfile.TemporaryDirectory(prefix='cap-') as prof:
        return subprocess.run(base + [f'--user-data-dir={prof}'] + extra + [url],
                              capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=600)


run([f'--screenshot={PNG}'])
dom = run(['--dump-dom']).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
print(f'--- {PNG} (seed={SEED}, at={AT}, into={INTO}) ---')
if m:
    d = json.loads(m.group(1))
    print('  probeError:', d.get('probeError'))
    print('  errors    :', d.get('errors'))
    print('  reached   :', d.get('found'), 'after', d.get('loops'), 'seeks')
    st = d.get('state') or {}
    for k in ('travel', 'capture', 'region', 'fillMPx', 'fps'):
        if k in st:
            print(f'  {k:<10}: {st[k]}')
else:
    print('  NO TITLE')
print('  png bytes :', os.path.getsize(PNG) if os.path.exists(PNG) else 'MISSING')
