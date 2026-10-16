"""Probe: at one seek, list every primary in the drawn chunk range with its
chunk index, z, and projected screen position, plus the camera eye and k0.
Run:  python -I nprobe.py <html> [--seed X] [--at N] [--seek S]
"""
import re, sys, os, json, argparse, subprocess, tempfile
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('--seed', default=None)
ap.add_argument('--at', type=int, default=1); ap.add_argument('--seek', type=float, default=213.0)
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

hook = '''window.__list=(kind)=>{const S=window.Starfield,eye=S.getState().eye;
 const k0=Math.floor(eye[2]/CHUNK),out={eye:eye.map(Math.round),k0,travel:Math.round(S.getState().travel),drawn:[],all:[]};
 for(const c of chunks.values())for(const m of c.masses){
  const q=project([m.x,m.y,m.z]);
  const rec={k:Math.floor(m.z/CHUNK),kind:m.kind,r:Math.round(m.r),
   z:Math.round(m.z),orb:!!m.orb,p:q?[Math.round(q[0]),Math.round(q[1]),Math.round(q[2])]:null};
  if(m.kind===kind){out.all.push(rec);
   if(Math.abs(rec.k-k0)<=9&&rec.p&&rec.p[2]>30&&rec.p[2]<=18000)out.drawn.push(rec);}
 }
 return out;};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 window.Starfield.seek(%f);
 const out=window.__list(7);out.errors=window.__e;
 document.title=JSON.stringify(out);
}catch(err){document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});}</script>''' % (a.at, a.seek)

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
out = a.html.replace('.html', '.nprobe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + os.path.abspath(out).replace('\\', '/') + query
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='np-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
d = json.loads(m.group(1))
print('eye:', d['eye'], 'k0:', d['k0'], 'travel:', d['travel'], 'errors:', d['errors'])
print('kind-7 masses anywhere:', len(d['all']))
print('kind-7 in the drawn range:', json.dumps(d['drawn']))
print('all:', json.dumps(d['all'])[:400])
