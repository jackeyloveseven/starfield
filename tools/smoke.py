"""Headless check: does the page build six audio elements, play, and stay clean?"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SRC = sys.argv[1]
src = open(SRC, encoding='utf-8').read()

hook = ('<script>window.__audio=0;window.__errors=[];'
        'window.addEventListener("error",e=>window.__errors.push(String(e.message)));'
        '(function(){const A=window.Audio;window.Audio=function(){window.__audio++;return new A(...arguments);};})();'
        '</script>')
src = src.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + hook, 1)

probe = ('<script>try{const b=document.getElementById("begin");if(b)b.click();'
         'const S=window.Starfield;S.seek(45);'
         'document.title=JSON.stringify({audio:window.__audio,errors:window.__errors,'
         'titles:S.scoreTitles,state:S.getState(),flock:S.flock()});}'
         'catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>')
out = os.path.abspath('smoke.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

url = 'file:///' + out.replace(os.sep, '/') + '?seed=1a2b'
with tempfile.TemporaryDirectory(prefix='smoke-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox',
                        '--mute-audio', '--no-first-run', f'--user-data-dir={prof}',
                        '--window-size=1280,720', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=300)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
print('probe error :', d.get('probeError', 'none'))
print('audio built :', d.get('audio'), '(want 6)')
print('errors      :', d.get('errors'))
print('titles      :', ' | '.join(d.get('titles', [])))
st = d.get('state') or {}
for k in ('region', 'travel', 'fps', 'drawCalls', 'capture', 'masses', 'track'):
    print(f'  {k:<11}:', st.get(k))
print('flock       :', d.get('flock'))
