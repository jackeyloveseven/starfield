"""TEMP diagnostic (not part of the deliverable): find a frame where a kind-8
ringed giant is large and near the middle of the frame, so the ring system can be
judged and screenshotted with shot.py --seek.

  python -I probe_ring.py <html> <seed> <at>
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html, seed, at = sys.argv[1:4]

DBG = (
 "_rdbg:()=>{let best=null;for(const m of activeMasses){if(m.kind!==8)continue;"
 "const pj=project([m.x,m.y,m.z]);if(!pj)continue;const rad=m.r*pj[3];"
 "if(pj[0]<250||pj[0]>W-250||pj[1]<200||pj[1]>H-200)continue;"
 "if(!best||rad>best[3])best=[m.kind,Math.round(pj[0]),Math.round(pj[1]),+rad.toFixed(1),m.r,+(m.phase*4096|0)];}"
 "return best;},"
)

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{at}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let g=0,hit=null,seeked=0;
 while(g++<2400){{
  S.seek(0.5);seeked+=0.5;
  const b8=S._rdbg();
  if(b8&&b8[3]>130){{hit=b8;break;}}
 }}
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 document.title=JSON.stringify({{errors:window.__errors,seeked,hit,state:S.getState()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,400)}});}}</script>'''

src = open(html, encoding='utf-8').read()
anchor = 'window.Starfield=Object.freeze({'
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + '\n ' + DBG, 1)
out = os.path.abspath('shots/_ring.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={seed}'
base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='ring-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + (d.get('stack') or ''))
print('errors :', d.get('errors'))
print('seeked :', d.get('seeked'))
print('kind8  :', d.get('hit'))
st = d.get('state') or {}
print('travel :', st.get('travel'), 'region:', st.get('region'), 'kinds:', st.get('kinds'))
