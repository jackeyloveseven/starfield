"""Measure how the world feels from the fleet's point of view.

Two questions the screenshots cannot answer: does the fleet hold formation while
flying past masses (gravity leaking into the ships), and does a capture fire when
nobody is steering (the auto camera drives wind.x, which the capture gate reads).

Reports flock radius against the 276-unit rest radius, and capture episodes as
rising edges out of FREE.
"""
import re
import sys
import os
import json
import subprocess
import tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\machine\Downloads\starfield.html"
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
TOTAL = float(sys.argv[3]) if len(sys.argv) > 3 else 1200.0
STEP = 4.0

JS = '''<script>window.__log=[];
try{
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let prev=0,captures=0,phases={},maxRadius=0,maxSpeed=0,sum=0,n=0,bad=false,over400=0;
 for(let i=0;i<__N__;i++){
  S.seek(__STEP__);
  const st=S.getState(),f=S.flock();
  if(f.bad)bad=true;
  if(f.radius>maxRadius)maxRadius=f.radius;
  if(f.radius>400)over400++;
  sum+=f.radius;n++;
  if(f.speed>maxSpeed)maxSpeed=f.speed;
  phases[st.capture]=(phases[st.capture]||0)+1;
  if(prev===0&&st.capture!==0)captures++;
  prev=st.capture;
 }
 const st=S.getState();
 document.title=JSON.stringify({bad,captures,perMin:+(captures/(__N__*__STEP__)*60).toFixed(2),
  phases,maxRadius,maxSpeed,avgRadius:Math.round(sum/n),
  pctOver400:+(over400/n*100).toFixed(1),
  travel:Math.round(st.travel),autoCamera:st.autoCamera,sling:st.sling});
}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>'''

probe = JS.replace('__N__', str(int(TOTAL / STEP))).replace('__STEP__', str(STEP))
src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('feel.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

with tempfile.TemporaryDirectory(prefix='feel-') as profile:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--mute-audio', '--no-first-run', f'--user-data-dir={profile}',
                        '--window-size=900,560', '--dump-dom',
                        'file:///' + out.replace('\\', '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print(f'--- fleet feel: seed={SEED} total={TOTAL}s step={STEP}s (no pointer input, autoCamera default) ---')
if m:
    try:
        d = json.loads(m.group(1))
        for k in ('bad', 'captures', 'perMin', 'phases', 'maxRadius', 'avgRadius',
                  'pctOver400', 'maxSpeed', 'travel', 'autoCamera', 'sling'):
            print(f'  {k:<12}: {d.get(k)}')
    except Exception:
        print('  raw:', m.group(1)[:300])
else:
    print('  NO TITLE —', (r.stderr or '')[-300:])
