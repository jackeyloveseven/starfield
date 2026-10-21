"""Read the director's actual dolly: which lens plays, at what orbit radius.

The playtester's complaint was "the camera pushes in and out like a glitch".
Before changing the director, measure it: walk the simulation in .25 s steps and
log every shot change with its distance. No drawing, so this is fast.

  python -I distprobe.py <html> [seconds]
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0

probe = f'''<script>
window.__errors=[];window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[1];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;S.seek(1);
 let seq=[],prev=null,dmin=1e9,dmax=0,rev=0,last=0;
 for(let i=0;i<{int(secs*4)};i++){{
  S.seek(.25);const st=S.getState();const D=st.distance;
  if(prev!==null){{if(D>last+1)rev++;if(D<last-1)rev--;}}
  last=D;dmin=Math.min(dmin,D);dmax=Math.max(dmax,D);
  if(st.lens!==prev){{seq.push([st.lens,+D.toFixed(0),+st.travel.toFixed(0)]);prev=st.lens;}}
 }}
 document.title=JSON.stringify({{errors:window.__errors,min:Math.round(dmin),max:Math.round(dmax),net:rev,seq}});
}}catch(e){{document.title=JSON.stringify({{err:String(e)}});}}
</script>'''

src = open(html, encoding='utf-8').read()
png = os.path.abspath('shots/distprobe.png')
os.makedirs(os.path.dirname(png), exist_ok=True)
probe_html = png.replace('.png', '.probe.html')
open(probe_html, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + probe_html.replace('\\', '/')

base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--window-size=1600,900']
with tempfile.TemporaryDirectory(prefix='dist-') as profile:
    dom = subprocess.run(base + [f'--user-data-dir={profile}', '--dump-dom', url],
                         capture_output=True, text=True, encoding='utf-8',
                         errors='replace', timeout=180).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
if not m:
    sys.exit('NO TITLE')
d = json.loads(m.group(1))
print('errors:', d.get('errors'), 'min:', d.get('min'), 'max:', d.get('max'), 'net drift:', d.get('net'))
span = d['max'] / max(1, d['min'])
print(f'range: {d["min"]}..{d["max"]}  ({span:.2f}x)')
seq = d.get('seq', [])
if len(seq) > 1:
    rr = [max(a[1], b[1]) / max(1, min(a[1], b[1])) for a, b in zip(seq, seq[1:])]
    print(f'shot-to-shot ratio: mean {sum(rr)/len(rr):.2f}  max {max(rr):.2f}')
for name, dist, tv in seq:
    print(f'  {dist:>5}  {name}')
