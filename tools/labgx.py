"""Galaxy lab: render ONE synthetic galaxy centred in front of the camera, with
all masses suppressed, so drawGalaxy's own look can be judged without a planet
sitting on top of it.  (Probe harness only - not part of the deliverable.)

Run: python -I labgx.py <html> <out.png> [--seed X] [--at N] [--seek S]
        [--rad R] [--arms A] [--tilt T] [--ang G] [--tone O] [--D D] [--offy Y]
"""
import re, sys, os, json, argparse, subprocess, tempfile
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('png')
ap.add_argument('--seed', default='1a2b'); ap.add_argument('--at', type=int, default=1)
ap.add_argument('--seek', type=float, default=60.0)
ap.add_argument('--rad', type=float, default=1500); ap.add_argument('--arms', type=int, default=4)
ap.add_argument('--tilt', type=float, default=0.55); ap.add_argument('--ang', type=float, default=0.6)
ap.add_argument('--tone', type=float, default=0.4); ap.add_argument('--D', type=float, default=2600)
ap.add_argument('--offy', type=float, default=0.0)
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))

hook = '''window.__lab=(o)=>{window.__labO=o;};
bodies=()=>{const o=window.__labO;if(!o)return;
 const e=camera.eye,f=camera.forward,r=camera.right,u=camera.up,D=o.D;
 const g={x:e[0]+f[0]*D+u[0]*o.offy,y:e[1]+f[1]*D+u[1]*o.offy,z:e[2]+f[2]*D+u[2]*o.offy,
  rad:o.rad,arms:o.arms,ang:o.ang,tilt:o.tilt,tone:o.tone};
 drawGalaxy(g,region(g.x,g.z),time);flush();};
drawFleet=()=>{};drawCraftShadows=()=>{};drawParticles=()=>{};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 window.Starfield.seek(%f);
 window.__lab({rad:%f,arms:%d,ang:%f,tilt:%f,tone:%f,D:%f,offy:%f});
 const iv=document.getElementById('intro');if(iv)iv.style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='0');
 document.title=JSON.stringify({errors:window.__e});
}catch(err){document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});}</script>''' % (
    a.at, a.seek, a.rad, a.arms, a.ang, a.tilt, a.tone, a.D, a.offy)

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
assert '__labO' in src
png = os.path.abspath(a.png)
os.makedirs(os.path.dirname(png), exist_ok=True)
out = png.replace('.png', '.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={a.seed}'
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='lab-') as prof:
    subprocess.run(base + [f'--user-data-dir={prof}', f'--screenshot={png}', url],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print('probe:', m.group(1)[:200] if m else 'NO TITLE')
print('png:', png, os.path.getsize(png) if os.path.exists(png) else 'MISSING')
