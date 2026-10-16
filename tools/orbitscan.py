"""Scan sim time for the moment a star system is best framed, then report it.

Reports, over a walk of the simulation:
  best : the primary with the largest on-screen radius (full-frame test), with
         its time, kind, radius and view distance
  close: the smallest 3D distance from the flock to any primary, and its time
  off  : for the nearest primary at the close moment, its lateral offset from
         the lane and its family size

Run:  python -I orbitscan.py <html> [--seed X] [--at N] [--step S] [--until S]
"""
import re, sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--seed', default=None)
ap.add_argument('--at', type=int, default=1)
ap.add_argument('--step', type=float, default=3.0)
ap.add_argument('--until', type=float, default=420.0)
ap.add_argument('--kind', type=int, default=0, help='only this primary kind (0 = any of 5..7)')
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

hook = '''window.__scan=(step,until,K)=>{
 const best={score:-1},close={d:1e9},sysOff=[];
 let seen=0;
 for(let t=0;t<=until;t+=step){
  const S=window.Starfield;S.seek(t>0?step:0);
  const lw=craftWorld(fleet[LEAD]);
  const k0=Math.floor(S.getState().eye[2]/CHUNK);
  for(let k=k0-6;k<=k0+6;k++)for(const m of chunk(k).masses){
   if(m.kind<5||m.kind>7)continue;
   if(K&&m.kind!==K)continue;
   const dd=Math.hypot(lw[0]-m.x,lw[1]-m.y,lw[2]-m.z);
   if(dd<close.d){
    let fam=0;const kk=Math.floor(m.z/CHUNK);
    for(let j=kk-2;j<=kk+2;j++)for(const o of chunk(j).masses)
     if(o.orb&&Math.hypot(o.orb.cx-m.x,o.orb.cz-m.z)<1)fam++;
    close.d=Math.round(dd);close.t=Math.round(t);close.kind=m.kind;close.r=Math.round(m.r);
    close.off=Math.round(Math.abs(m.x-laneX(m.z)));close.fam=fam;close.tt=Math.round(t);
   }
   const q=project([m.x,m.y,m.z]);
   if(!q||q[2]<=40)continue;
   const rad=m.r*q[3];
   if(q[0]<200||q[0]>W-200||q[1]<180||q[1]>H-180)continue;
   seen++;
   if(rad>best.score){best.score=rad;best.tt=Math.round(t);best.travel=Math.round(S.getState().travel);
    best.kind=m.kind;best.r=Math.round(m.r);best.rad=Math.round(rad);best.dist=Math.round(q[2]);
    best.x=Math.round(q[0]);best.y=Math.round(q[1]);best.off=Math.round(Math.abs(m.x-laneX(m.z)));}
  }
 }
 return {best,close,onScreenSamples:seen};};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const out=window.__scan(%f,%f,%d);
 out.errors=window.__e;
 document.title=JSON.stringify(out);
}catch(err){document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});}</script>''' % (a.at, a.step, a.until, a.kind)

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
out = a.html.replace('.html', '.orbitscan.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + os.path.abspath(out).replace('\\', '/') + query
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='orbs-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m: sys.exit('NO TITLE')
print(json.dumps(json.loads(m.group(1)), ensure_ascii=False)[:800])
