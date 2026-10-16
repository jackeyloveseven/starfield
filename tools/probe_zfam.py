"""TEMP probe: where do the sub-400 z gaps actually come from?

For a handful of system chunks, print the star's z and every member's z, and
whether the chunk's bodies are within 400u of each other. Also print, for a
lattice chunk, the sorted z of its worlds.

  python -I probe_zfam.py <html> [seed]
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'

DBG = (
 "_dbg:()=>{const k0=Math.floor(camera.eye[2]/CHUNK),cs=[];"
 "for(let k=k0;k<=k0+14;k++)cs.push(chunk(k));stepOrbits();const out=[];"
 "for(const c of cs){const ms=c.masses.map(m=>({z:Math.round(m.z),y:Math.round(m.y),"
 "x:Math.round(m.x-laneX(m.z)),r:Math.round(m.r),k:m.kind,orb:m.orb?1:0,"
 "o:m.orb?[+m.orb.a.toFixed(0),+m.orb.b.toFixed(0),+m.orb.inc.toFixed(3),+m.orb.nod.toFixed(2),"
 "+(m.orb.ph).toFixed(2),+m.orb.spd.toFixed(3)]:null}));"
 "ms.sort((a,b)=>a.z-b.z);const gaps=[];for(let i=1;i<ms.length;i++)gaps.push(ms[i].z-ms[i-1].z);"
 "out.push({k:c.k,sys:ms.filter(v=>v.k>=5&&v.k<=7).length>0,ms,gaps,"
 "pair:ms.map((v,i)=>i?[ms[i-1].orb&&v.orb,ms[i-1].k,v.k]:null).slice(1)});}"
 "return {out};},"
)

probe = '''<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{
 const d=document.querySelectorAll(".destination")[0];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 for(let i=0;i<200;i++)S.seek(1);
 const db=S._dbg();
 document.title=JSON.stringify({errors:window.__errors,out:db.out});
}catch(e){document.title=JSON.stringify({probeError:String(e),stack:String(e.stack).slice(0,400)});}</script>'''

src = open(HTML, encoding='utf-8').read()
anchor = 'window.Starfield=Object.freeze({'
assert src.count(anchor) == 1, 'anchor for _dbg must occur exactly once'
src = src.replace(anchor, anchor + '\n ' + DBG, 1)
out = os.path.abspath('shots/_zfam.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/') + f'?seed={SEED}'
base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='zf-') as prof:
    r = subprocess.run(base + [f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE')
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + str(d.get('stack')))
print('errors:', d.get('errors'))
for c in d['out']:
    tag = 'SYSTEM' if c['sys'] else 'lattice'
    zs = [v['z'] for v in c['ms']]
    small = sum(1 for g in c['gaps'] if g < 400)
    print(f"chunk {c['k']:>4} {tag:<7} bodies={len(zs)} gaps<400={small}/{len(c['gaps'])}")
    print('   z :', zs)
    print('   y :', [v['y'] for v in c['ms']])
    print('   |x|:', [v['x'] for v in c['ms']], 'kinds', [v['k'] for v in c['ms']], 'orb', [v['orb'] for v in c['ms']])
    if c['sys']:
        print('   orb[a,b,inc,nod,ph,spd]:')
        for v in c['ms']:
            print('      ', v['k'], v['orb'], v['o'])

both = 0; bothsmall = 0; oth = 0; othsmall = 0
for c in d['out']:
    for i, g in enumerate(c['gaps']):
        isboth = c['pair'][i][0]
        if isboth:
            both += 1
            if g < 400: bothsmall += 1
        else:
            oth += 1
            if g < 400: othsmall += 1
print(f"\nwithin-family (both orbiting) gaps: {both}  <400: {bothsmall} ({bothsmall/max(1,both)*100:.1f}%)")
print(f"other gaps                        : {oth}  <400: {othsmall} ({othsmall/max(1,oth)*100:.1f}%)")
