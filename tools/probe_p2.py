"""TEMP diagnostic (not part of the deliverable): dump the on-screen masses for the
exact holeshot frame so the blue disc at (1000,320) can be attributed to a kind and
its cloud-blob geometry read off.

  python -I probe_p2.py <html> <seed> <at> <maxd> <maxr>
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html, seed, at, maxd, maxr = sys.argv[1:6]

DBG = (
 "_mdbg:()=>{const out=[];for(const m of activeMasses){const pj=project([m.x,m.y,m.z]);"
 "if(!pj)continue;const rad=m.r*pj[3];if(pj[0]<0||pj[0]>W||pj[1]<0||pj[1]>H)continue;"
 "out.push([m.kind,Math.round(pj[0]),Math.round(pj[1]),+rad.toFixed(1),m.r,+(m.phase*4096|0)]);}"
 "return {m:out.sort((a,b)=>b[3]-a[3]).slice(0,14)};},"
)

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{at}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let g=0,found=false,last=null;
 while(g++<3000){{
  S.seek(0.4);
  const h=S.holeDir();
  if(h){{last=h;
   if(h.dist<{maxd}&&h.fwd>400&&Math.abs(h.right)<{maxr}){{found=true;break;}}
  }}
 }}
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 const md=S._mdbg();
 document.title=JSON.stringify({{errors:window.__errors,found,loops:g,last,md:md.m,state:S.getState()}});
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,400)}});}}</script>'''

src = open(html, encoding='utf-8').read()
anchor = 'window.Starfield=Object.freeze({'
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + '\n ' + DBG, 1)
out = os.path.abspath('shots/_p2.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={seed}'
base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='p2-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=600)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + (d.get('stack') or ''))
print('errors :', d.get('errors'), 'found:', d.get('found'), 'loops:', d.get('loops'))
st = d.get('state') or {}
for k in ('travel', 'region', 'masses', 'kinds', 'fps'):
    print(' ', k, ':', st.get(k))
print('  [kind, sx, sy, radpx, radw, hb]')
for v in d.get('md', []):
    print('   ', v)
