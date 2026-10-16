"""Find a seek that lands inside a supernova, and shoot it.

Modeled on shot.py: the probe runs synchronously at parse time, presses 起航,
then seeks the simulation forward in 2s steps until window.Starfield.nova()
reports a live event whose halo is on screen, and prints the seek it stopped at.
This is a probe, not the verification: the verification is shot.py at that seek.

  python -I haloprobe.py <html> <png> <seed> <at>
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html, png, seed, at = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
AMIN = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
AMAX = float(sys.argv[6]) if len(sys.argv) > 6 else 999.0
W, H = 1600, 900

probe = f'''<style>*,*::before,*::after{{animation:none!important;transition:none!important}}</style>
<script>window.__errors=[];
window.addEventListener("error",e=>window.__errors.push(String(e.message)));
try{{
 const d=document.querySelectorAll(".destination")[{at}];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let hits=[],g=0;
 while(g++<1300){{
  const n=S.nova();
  if(n&&n.age>={AMIN}&&n.age<={AMAX}&&n.x>240&&n.x<1360&&n.y>140&&n.y<760)
   hits.push({{seek:(g-1)*0.5,state:n,region:S.getState().region,hole:S.holeDir()}});
  S.seek(0.5);
 }}
 document.getElementById('intro').style.display='none';
 document.querySelectorAll('.hud').forEach(e=>e.style.opacity='1');
 window.__probe={{errors:window.__errors,hits:hits.length?hits:null,state:S.getState()}};
 document.title=JSON.stringify(window.__probe);
}}catch(err){{document.title=JSON.stringify({{probeError:String(err),stack:String(err&&err.stack).slice(0,300)}});}}</script>'''

src = open(html, encoding='utf-8').read()
png = os.path.abspath(png)
probe_html = png.replace('.png', '.probe.html')
open(probe_html, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
url = 'file:///' + probe_html.replace('\\', '/') + f'?seed={seed}'
base = [CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
        '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', f'--window-size={W},{H}']


def run(extra, timeout=180):
    with tempfile.TemporaryDirectory(prefix='shot-') as profile:
        return subprocess.run(base + [f'--user-data-dir={profile}'] + extra + [url],
                              capture_output=True, text=True, encoding='utf-8',
                              errors='replace', timeout=timeout)


run([f'--screenshot={png}'])
dom = run(['--dump-dom']).stdout or ''
m = re.search(r'<title>(.*?)</title>', dom, re.S)
print(f'--- {png} ---')
if m:
    d = json.loads(m.group(1))
    if d.get('probeError'):
        print('  PROBE FAILED:', d['probeError'], d.get('stack', ''))
    print('  errors :', d.get('errors'))
    for hit in (d.get('hits') or []):
        hd = hit.get('hole')
        print('  seek %4d  region %-8s age %5.1f life %.2f at (%d,%d)  hole %s'
              % (hit['seek'], hit['region'], hit['state']['age'], hit['state']['life'],
                 hit['state']['x'], hit['state']['y'],
                 'none' if hd is None else 'dist %d' % hd['dist']))
    st = d.get('state') or {}
    print('  travel :', st.get('travel'), ' region:', st.get('region'), ' fps:', st.get('fps'))
else:
    print('  NO TITLE')
