"""Probe: time a full nebCache regeneration (the worst case for the new dust
chains) and a per-frame draw, so the patch cannot have bought looks with frames.

Run:  python -I ndperf.py <html>
"""
import re, sys, os, json, subprocess, tempfile
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

hook = '''window.__perf=()=>{
 nebCache.clear();
 const t0=performance.now();
 for(let i=0;i<40;i++)nebulaTex(1+(i%6),i%5);
 const gen=performance.now()-t0;
 const c=nebulaTex(1,2);
 const cv=document.createElement('canvas');cv.width=cv.height=800;
 const x=cv.getContext('2d');
 const t1=performance.now();
 for(let i=0;i<200;i++)x.drawImage(c,0,0,800,800);
 const draw=performance.now()-t1;
 return {gen40:+gen.toFixed(1),genOne:+(gen/40).toFixed(2),draw200:+draw.toFixed(1)};
};'''

probe = '''<script>window.__e=[];
window.addEventListener("error",e=>window.__e.push(String(e.message)));
try{const b=document.getElementById("begin");if(b)b.click();
 window.Starfield.seek(30);
 document.title=JSON.stringify(Object.assign(window.__perf(),{errors:window.__e}));
}catch(err){document.title=JSON.stringify({probeError:String(err)});}</script>'''

src = open(html, encoding='utf-8').read()
src = src.replace('requestAnimationFrame(frame);\n})();', hook + '\nrequestAnimationFrame(frame);\n})();', 1)
out = os.path.abspath('ndperf.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + out.replace('\\', '/')
with tempfile.TemporaryDirectory(prefix='np-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
                        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
                        '--disable-background-networking', '--window-size=1600,900',
                        f'--user-data-dir={prof}', '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print(json.dumps(json.loads(m.group(1)), indent=1) if m else 'NO TITLE')
