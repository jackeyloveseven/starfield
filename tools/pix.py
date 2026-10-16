"""Sample what the frame is actually made of: live palette values and the pixel
colours the canvas ends up with. Guessing at a wrong colour from a screenshot
costs more than measuring it."""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
AT = sys.argv[3] if len(sys.argv) > 3 else '1'
SEEK = sys.argv[4] if len(sys.argv) > 4 else '40'

probe = ('<script>try{const d=document.querySelectorAll(".destination")[' + AT + '];if(d)d.click();'
         'const b=document.getElementById("begin");if(b)b.click();'
         'const S=window.Starfield;S.seek(' + SEEK + ');'
         'document.getElementById("intro").style.display="none";'
         'document.querySelectorAll(".hud").forEach(e=>e.style.opacity="1");'
         'requestAnimationFrame(()=>requestAnimationFrame(()=>{'
         'const c=document.getElementById("landscape"),g=c.getContext("2d");'
         'const px=(x,y)=>{const d=g.getImageData(Math.round(x*c.width),Math.round(y*c.height),1,1).data;'
         'return [d[0],d[1],d[2]];};'
         'const p=window.__pal||null;'
         'document.title=JSON.stringify({top:px(.5,.04),upper:px(.5,.18),mid:px(.5,.32),'
         'horizon:px(.5,.60),lower:px(.5,.80),left:px(.08,.20),right:px(.92,.20),pal:S.palette()});'
         '}));}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>')

src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('pix.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
with tempfile.TemporaryDirectory(prefix='pix-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
                        '--no-first-run', f'--user-data-dir={prof}', '--window-size=1280,720',
                        '--dump-dom',
                        'file:///' + out.replace(os.sep, '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'])
print(f'--- canvas pixels, seed={SEED} at={AT} seek={SEEK} ---')
for k, v in d.items():
    if k == 'pal':
        print('  palette  :', {a: b for a, b in v.items()})
    else:
        print(f'  {k:<9} rgb({v[0]:>3},{v[1]:>3},{v[2]:>3})')
