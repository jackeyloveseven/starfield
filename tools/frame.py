"""Measure the flicker, not the vibes.

seek() does not draw, so a texture regenerated inside the render loop only shows
up during real frames. Park the camera mid-crossfade (where the palette blends
continuously) and count how many offscreen nebula textures get built while real
frames run. Virtual-time-immune: a miss is a miss.
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
SEEK = float(sys.argv[3]) if len(sys.argv) > 3 else 35.0
BUDGET = int(sys.argv[4]) if len(sys.argv) > 4 else 12000

probe = ('<script>try{const b=document.getElementById("begin");if(b)b.click();'
         'const S=window.Starfield;S.seek(' + str(SEEK) + ');'
         'document.getElementById("intro").style.display="none";'
         'const t0=S.getState();'
         'setTimeout(()=>{const t1=S.getState();'
         'document.title=JSON.stringify({before:{tex:t0.nebTex,gens:t0.nebGens},'
         'after:{tex:t1.nebTex,gens:t1.nebGens},region:t1.region,'
         'travel:Math.round(t1.travel),drawCalls:t1.drawCalls});},' + str(BUDGET - 1500) + ');'
         '}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>')

src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('frame.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
with tempfile.TemporaryDirectory(prefix='frame-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
                        '--no-first-run', f'--user-data-dir={prof}', '--window-size=1280,720',
                        f'--virtual-time-budget={BUDGET}', '--dump-dom',
                        'file:///' + out.replace(os.sep, '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print(f'--- frame probe: seed={SEED} seek={SEEK}s budget={BUDGET}ms ---')
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'])
b, a = d['before'], d['after']
print(f"  textures built before : {b['gens']}  (cache {b['tex']})")
print(f"  textures built after  : {a['gens']}  (cache {a['tex']})")
print(f"  NEW during the run    : {a['gens'] - b['gens']}   <- want 0")
print(f"  cache grew by         : {a['tex'] - b['tex']}   <- want 0")
print(f"  region={d['region']} travel={d['travel']} drawCalls={d['drawCalls']}")
