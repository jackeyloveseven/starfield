"""Scan seeks for the frame where a galaxy is most prominent on screen.
Run:  python -I gxscan.py <html> [--seed X] [--at N] [--step S] [--max M]
"""
import re, sys, os, json, argparse, subprocess, tempfile
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('--seed', default=None)
ap.add_argument('--at', type=int, default=1); ap.add_argument('--step', type=float, default=2.0)
ap.add_argument('--max', type=float, default=600.0)
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

hook = '''window.__gxscan=(step,max)=>{const S=window.Starfield,best=[];
 const mpx=()=>{const a=[];for(const c of chunks.values())for(const m of c.masses){const q=project([m.x,m.y,m.z]);if(q&&q[2]<18000)a.push([q[0],q[1],m.r*q[3],q[2]]);}return a;};
 for(let s=0;s<max;s+=step){
  S.seek(step);
  const M=mpx();
  for(const c of chunks.values())for(const g of c.galaxies){
   const q=project([g.x,g.y,g.z]);if(!q)continue;
   const R=g.rad*q[3],cx=q[0],cy=q[1];
   if(cx>40&&cx<W-40&&cy>40&&cy<H-40){
    let clear=1e9;for(const m of M){const d=Math.hypot(m[0]-cx,m[1]-cy)-m[2];if(d<clear)clear=d;}
    best.push({t:Math.round(s+step),s:Math.round(S.getState().travel),r:Math.round(R),x:Math.round(cx),y:Math.round(cy),z:Math.round(q[2]),cl:Math.round(clear)});
   }
  }
 }
 best.sort((p,q)=>q.r-p.r);return best.slice(0,24);};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const top=window.__gxscan(%f,%f);
 document.title=JSON.stringify({top,errors:window.__e});
}catch(err){document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});}</script>''' % (a.at, a.step, a.max)

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();',
                  hook + '\nrequestAnimationFrame(frame);\n})();', 1)
assert '__gxscan' in src
out = a.html.replace('.html', '.gxscan.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + os.path.abspath(out).replace('\\', '/') + query
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='gs-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + str(d.get('stack')))
print('errors:', d['errors'])
for t in d['top']:
    print(f"  seek {t['t']:>6}  travel {t['s']:>6}  R {t['r']:>4}px  screen ({t['x']:>4},{t['y']:>4})  z {t['z']}  clear {t['cl']}")
