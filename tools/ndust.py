"""Probe: render nebulaTex() cells at large scale so the dust-lane language can
be judged directly, without the camera, the grade or the bloom in the way.

Injects a probe that (a) stops the artwork's own frame loop, (b) clears the body,
(c) draws a grid of nebulaTex(seed,idx) textures over a navy backdrop.

Run:  python -I ndust.py <html> <out.png> [--cols N] [--seed a,b,c] [--idx a,b,c]
"""
import re, sys, os, json, argparse, subprocess, tempfile
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('png')
ap.add_argument('--cols', type=int, default=4)
ap.add_argument('--seed', default='1,2,3,4,5,6,7,8')
ap.add_argument('--idx', default='2')
ap.add_argument('--size', default='1600x1200')
ap.add_argument('--zoom', type=float, default=1.0)
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))

seeds = [int(v) for v in a.seed.split(',')]
idxs = [int(v) for v in a.idx.split(',')]
combos = [[s, k] for k in idxs for s in seeds]

probe = '''
try{
 document.body.innerHTML='';
 const combos=%s;
 const cols=%d;
 const rows=Math.ceil(combos.length/cols);
 const cell=Math.floor(Math.min(window.innerWidth/cols,window.innerHeight/rows)*%f);
 const cv=document.createElement('canvas');
 cv.width=cols*cell; cv.height=rows*cell;
 cv.style.cssText='position:fixed;left:0;top:0;z-index:99999';
 const x=cv.getContext('2d');
 const bg=x.createLinearGradient(0,0,0,cv.height);
 bg.addColorStop(0,'#22384f'); bg.addColorStop(.55,'#16273a'); bg.addColorStop(1,'#0c1622');
 x.fillStyle=bg; x.fillRect(0,0,cv.width,cv.height);
 for(let i=0;i<combos.length;i++){
  const t=nebulaTex(combos[i][0],combos[i][1]);
  const cx=(i%%cols)*cell, cy=Math.floor(i/cols)*cell;
  x.drawImage(t,cx,cy,cell,cell);
 }
 document.body.appendChild(cv);
}catch(err){document.title=String(err)+' | '+String(err&&err.stack).slice(0,300);}
''' % (json.dumps(combos), a.cols, a.zoom)

src = open(a.html, encoding='utf-8').read()
if 'requestAnimationFrame(frame);\n})();' not in src:
    sys.exit('probe anchor not found')
src = src.replace('requestAnimationFrame(frame);\n})();',
                  probe + '\n/*frame loop disabled by probe*/\n})();', 1)
png = os.path.abspath(a.png)
os.makedirs(os.path.dirname(png), exist_ok=True)
out = png.replace('.png', '.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src)
url = 'file:///' + out.replace('\\', '/')
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']
with tempfile.TemporaryDirectory(prefix='nd-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', f'--screenshot={png}', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=180)
    dom = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                         capture_output=True, text=True, encoding='utf-8',
                         errors='replace', timeout=180).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
print('cells:', combos)
print('title:', (m.group(1)[:300] if m else 'NO TITLE'))
print('png bytes:', os.path.getsize(png) if os.path.exists(png) else 'MISSING')
