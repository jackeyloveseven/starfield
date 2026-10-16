"""Where does the band actually land on screen?

Records the projected band polyline and the camera basis, so "off frame" and
"not drawn" stop looking the same.
"""
import re
import sys
import os
import json
import subprocess
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\machine\Downloads\starfield.html"
AT = sys.argv[2] if len(sys.argv) > 2 else '2'
SEEK = sys.argv[3] if len(sys.argv) > 3 else '200'

src = open(HTML, encoding='utf-8').read()
a = "  ctx.save();ctx.lineCap='round';ctx.lineJoin='round';"
b = "  window.__segs=segs.map(s=>[s.length/2,s[0],s[1],s[Math.floor(s.length/4)*2],s[Math.floor(s.length/4)*2+1]]);\n" + a
assert src.count(a) == 1, src.count(a)
src = src.replace(a, b, 1)

probe = ('<script>try{const d=document.querySelectorAll(".destination")[' + AT + '];if(d)d.click();'
         'const b=document.getElementById("begin");if(b)b.click();'
         'const S=window.Starfield;S.seek(' + SEEK + ');'
         'requestAnimationFrame(()=>requestAnimationFrame(()=>{'
         'const st=S.getState();'
         'document.title=JSON.stringify({w:st.width,h:st.height,pitch:st.pitch,yaw:st.yaw,'
         'segs:window.__segs,eye:st.eye});}));}'
         'catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>')

out = os.path.abspath('bandprobe.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
with tempfile.TemporaryDirectory(prefix='bp-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
                        '--no-first-run', f'--user-data-dir={prof}', '--window-size=1280,720',
                        '--dump-dom', 'file:///' + out.replace(os.sep, '/') + '?seed=1a2b'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
print('screen', d.get('w'), 'x', d.get('h'), ' pitch', round(d.get('pitch', 0), 3), ' yaw', round(d.get('yaw', 0), 3))
segs = d.get('segs') or []
print('segments:', len(segs))
for i, s in enumerate(segs[:8]):
    n = s[0]
    pts = [(round(s[j]), round(s[j + 1])) for j in (1, 3)]
    print(f'  seg{i}: {n:.0f} pts  first={pts[0]}  mid={pts[1]}')
