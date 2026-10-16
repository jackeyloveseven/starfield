"""Probe: are there star systems, where are they on screen, and do they move?

Injects a synchronous probe, seeks, and reports from the page title:
  - mass counts by kind in the loaded chunks
  - the nearest primary (kind 5..7): distance, radius, screen xy
  - how far the orbiting worlds of the loaded chunks travel over 20 sim seconds
Run:  python -I orbitprobe.py <html> [--seed X] [--at N] [--seek S]
"""
import re, sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--seed', default=None)
ap.add_argument('--at', type=int, default=1)
ap.add_argument('--seek', type=float, default=60.0)
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

hook = '''window.__hookErr=null;
try{
window.__famSnap=()=>{const out={};for(const c of chunks.values())for(const m of c.masses)
 if(m.orb){const key=m.kind+':'+Math.round(m.orb.cx)+':'+Math.round(m.orb.cz)+':'+Math.round(m.orb.a);out[key]=[Math.round(m.x),Math.round(m.y),Math.round(m.z)];}return out;};
window.__orbitProbe=()=>{const byKind={};let near=null,nd=1e9;
 for(const m of activeMasses){byKind[m.kind]=(byKind[m.kind]||0)+1;
  if(m.kind>=5){const lw=craftWorld(fleet[LEAD]);const dd=Math.hypot(lw[0]-m.x,lw[1]-m.y,lw[2]-m.z);if(dd<nd){nd=dd;near=m;}}}
 const fam=[];if(near){const k0=Math.floor(near.z/CHUNK);
  for(let k=k0-1;k<=k0+1;k++)for(const m of chunk(k).masses)
   if(m.orb&&Math.hypot(m.orb.cx-near.x,m.orb.cz-near.z)<1)fam.push({kind:m.kind,r:Math.round(m.r),x:Math.round(m.x),y:Math.round(m.y),z:Math.round(m.z)});}
 const p=near?project([near.x,near.y,near.z]):null;
 return {byKind,orbiting:Object.keys(window.__famSnap()).length,
  near:!!near,starKind:near?near.kind:null,starR:near?Math.round(near.r):null,dist:Math.round(nd),
  screen:p?[Math.round(p[0]),Math.round(p[1]),Math.round(p[2])]:null,family:fam};};
}catch(e){window.__hookErr=String(e);}'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;S.seek(%f);
 const out={errors:window.__e,hookErr:window.__hookErr,probeType:typeof window.__orbitProbe,travel:Math.round(S.getState().travel),masses:S.getState().masses};
 out.sys=window.__orbitProbe();
 const s1=window.__famSnap();S.seek(20);const s2=window.__famSnap();
 let mx=0,mn=1e9,cnt=0;
 for(const k in s1)if(s2[k]){const A=s1[k],B=s2[k];
  const dd=Math.hypot(A[0]-B[0],A[1]-B[1],A[2]-B[2]);if(dd>mx)mx=dd;if(dd<mn)mn=dd;cnt++;}
 out.orbiters=cnt;out.maxMove20s=Math.round(mx);out.minMove20s=Math.round(mn);
 document.title=JSON.stringify(out);
}catch(err){document.title=JSON.stringify({probeError:String(err),hookErr:window.__hookErr,probeType:typeof window.__orbitProbe,famType:typeof window.__famSnap,stack:String(err&&err.stack).slice(0,300)});}</script>''' % (a.at, a.seek)

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
if '</body>' not in src: sys.exit('no </body>')
out = a.html.replace('.html', '.orbitprobe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + os.path.abspath(out).replace('\\', '/') + query
base = [CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='orb-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m: sys.exit('NO TITLE')
d = json.loads(m.group(1))
print('RAW      :', json.dumps(d, ensure_ascii=False)[:600])
print('errors   :', d.get('errors'))
print('travel   :', d.get('travel'), ' activeMasses:', d.get('masses'))
sysm = d.get('sys') or {}
print('byKind   :', sysm.get('byKind'))
print('nearest primary: kind=%s r=%s dist=%s screen=%s' % (sysm.get('starKind'), sysm.get('starR'), sysm.get('dist'), sysm.get('screen')))
print('family   :', sysm.get('family'))
print('orbiters in loaded chunks: %s   moved over 20s: min=%s max=%s' % (d.get('orbiters'), d.get('minMove20s'), d.get('maxMove20s')))
