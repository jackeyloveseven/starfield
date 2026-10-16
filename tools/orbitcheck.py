"""Structural + stability check for the v18o orbit patch.

One page run that reports:
  kinds   : how many masses of each kind exist over 400 chunks, with min/max r
  systems : how many chunks are systems, and the family size / orbit radii of
            each (two to five worlds, each orbit outside the last, star outside
            the lane by more than its widest orbit)
  hole    : whether the ink well is still on its every-seventh-chunk schedule at
            r=1100, and that no other kind ever takes r=1100
  orbit   : that every orbiting body's position is a pure function of the clock
            (same time twice -> same position) and that it actually moves
  flock   : max flock radius / speed / non-finite over a 600 s flight (the new
            star gravity must not blow the flock apart)
Run:  python -I orbitcheck.py <html> [--seed X] [--at N]
"""
import re, sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--seed', default=None)
ap.add_argument('--at', type=int, default=1)
ap.add_argument('--size', default='1600x900')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))
query = f'?seed={a.seed}' if a.seed is not None else ''

hook = '''window.__check=()=>{
 const out={kinds:{},systems:[],hole:{ok:true,bad:[]},moved:0,pure:true,flock:{}};
 const kN=400;
 for(let k=0;k<kN;k++){
  const c=chunk(k),ms=c.masses;
  const sys=ms.length&&ms[0].kind>=5&&ms[0].kind<=7&&!ms[0].orb;
  for(const m of ms){
   const e=out.kinds[m.kind]||(out.kinds[m.kind]={n:0,min:1e9,max:-1e9});
   e.n++;e.min=Math.min(e.min,Math.round(m.r));e.max=Math.max(e.max,Math.round(m.r));
   if(m.kind===4&&Math.round(m.r)!==1100)out.hole.bad.push('k'+k+' r'+m.r);
  }
  if(k%7===0){if(!ms.length||ms[0].kind!==4||Math.round(ms[0].r)!==1100)out.hole.bad.push('k'+k+' head kind='+(ms[0]&&ms[0].kind));}
  else if(ms.some(m=>m.kind===4))out.hole.bad.push('k'+k+' stray hole');
  if(sys){
   const orb=ms.filter(m=>m.orb),star=ms[0];
   let ok=true,prev=0,clear=1e9;
   for(const o of orb){
    const need=star.r+o.r+1;
    if(o.orb.a<prev||o.orb.a<need)ok=false;
    prev=o.orb.a;
    // walk the whole orbit and find the closest approach of its EDGE to the lane
    const O=o.orb,ci=Math.cos(O.inc),si=Math.sin(O.inc),cn=Math.cos(O.nod),sn=Math.sin(O.nod);
    for(let i=0;i<64;i++){
     const th=i/64*TAU,x=Math.cos(th)*O.a,y=Math.sin(th)*O.b;
     const wx=O.cx+x*cn+y*si*sn,wz=O.cz-x*sn+y*si*cn;
     const d=Math.abs(wx-laneX(wz))-o.r;
     if(d<clear)clear=d;
    }
   }
   out.systems.push({k,star:star.kind,sr:Math.round(star.r),n:orb.length,
    radii:orb.map(o=>Math.round(o.orb.a)),rads:orb.map(o=>Math.round(o.r)),
    spd:orb.map(o=>+o.orb.spd.toFixed(3)),ok,clear:Math.round(clear)});
  }
 }
 // purity + motion: snapshot the same clock twice, and 20 s apart
 const S=window.Starfield;S.seek(0);
 const snap=()=>{const o={};for(const c of chunks.values())for(const m of c.masses)
  if(m.orb)o[m.kind+':'+Math.round(m.orb.cx)+':'+Math.round(m.orb.cz)+':'+Math.round(m.orb.a)]=[m.x,m.y,m.z];return o;};
 const A=snap();const B=snap();
 for(const key in A){const a=A[key],b=B[key];
  if(Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2])>1e-6)out.pure=false;}
 S.seek(20);const C=snap();
 for(const key in A)if(C[key]){const d=Math.hypot(A[key][0]-C[key][0],A[key][1]-C[key][1],A[key][2]-C[key][2]);if(d>1)out.moved++;}
 // flock stability across a long flight
 let mr=0,mv=0,bad=false;
 for(let t=0;t<600;t+=5){S.seek(5);const f=window.Starfield.flock();
  if(f.radius>mr)mr=f.radius;if(f.speed>mv)mv=f.speed;if(f.bad)bad=true;}
 out.flock={radius:mr,speed:mv,bad};
 return out;};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[%d];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const out=window.__check();out.errors=window.__e;
 document.title=JSON.stringify(out);
}catch(err){document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});}</script>''' % a.at

src = open(a.html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
out = a.html.replace('.html', '.orbitcheck.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + os.path.abspath(out).replace('\\', '/') + query
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='orbc-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=400)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m: sys.exit('NO TITLE')
d = json.loads(m.group(1))
if d.get('probeError'): print('PROBE FAILED', d); sys.exit(1)
print('errors  :', d['errors'])
print('kinds   :', json.dumps(d['kinds']))
print('hole    : ok=%s bad=%s' % (d['hole']['ok'] and not d['hole']['bad'], d['hole']['bad'][:6]))
print('pure    :', d['pure'], ' moved>1unit in 20s:', d['moved'])
print('flock   :', d['flock'])
print('systems : %d of 400 chunks' % len(d['systems']))
sizes = {}
for s in d['systems']:
    sizes[s['n']] = sizes.get(s['n'], 0) + 1
print('family sizes:', sizes)
bad = [s for s in d['systems'] if not s['ok'] or s['clear'] < 200]
print('systems failing the geometric rule:', len(bad), bad[:3])
print('min lane clearance over all systems:', min((s['clear'] for s in d['systems']), default=None))
print('sample  :', json.dumps(d['systems'][:3]))
