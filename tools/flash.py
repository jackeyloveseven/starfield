"""Find the flash by measuring the symptom, not by guessing the cause.

The page holds an AudioContext once 起航 is pressed, and virtual time never
reaches its budget while one is alive (see README). Stubbing AudioContext out
before the click lets --virtual-time-budget drive thousands of real rendered
frames in one launch, so this samples the canvas per frame and reports the
biggest frame-to-frame jump in mean luminance, with the ink-well distance at
that moment. A whole-screen flash reads as a jump of tens of levels.
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
FRAMES = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
STEP = 0.5
# Virtual time advances one rAF at a time and the page re-renders every one, so
# the budget has to cover our ticks and not much more, or we pay for tens of
# thousands of full renders we never sample.
BUDGET = int(FRAMES * 17 * 1.25)

JS = '''<script>window.__samples=[];window.__err=null;
(function(){
 Object.defineProperty(window,"AudioContext",{value:undefined,configurable:true});
 window.webkitAudioContext=undefined;
 const S=window.Starfield;
 const small=document.createElement("canvas");small.width=32;small.height=18;
 const sctx=small.getContext("2d",{willReadFrequently:true});
 const big=document.getElementById("landscape");
 const b=document.getElementById("begin");if(b)b.click();
 let i=0,prevPhase=0,captures=0;
 function tick(){
  try{
   S.seek(__STEP__);
   const st=S.getState();
   if(prevPhase===0&&st.capture!==0)captures++;
   prevPhase=st.capture;
   sctx.drawImage(big,0,0,32,18);
   const d=sctx.getImageData(0,0,32,18).data;
   let sum=0;for(let k=0;k<d.length;k+=4)sum+=(d[k]*.299+d[k+1]*.587+d[k+2]*.114);
   const h=S.holeDir();
   window.__samples.push([Math.round(st.travel),+(sum/(d.length/4)).toFixed(2),st.capture,
     h?Math.round(h.dist):-1,st.region]);
   i++;
   if(i<__N__)requestAnimationFrame(tick);
   else document.title=JSON.stringify({done:true,n:i,captures});
  }catch(e){document.title=JSON.stringify({probeError:String(e)});}
 }
 requestAnimationFrame(tick);
})();</script>'''

probe = JS.replace('__N__', str(FRAMES)).replace('__STEP__', str(STEP))
src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('flash.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

with tempfile.TemporaryDirectory(prefix='flash-') as profile:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--mute-audio', '--no-first-run', f'--user-data-dir={profile}',
                        '--window-size=1280,720', f'--virtual-time-budget={BUDGET}',
                        '--dump-dom',
                        'file:///' + out.replace('\\', '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-400:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'])

mm = re.search(r'window\.__samples\s*=\s*(\[.*?\]);', r.stdout or '', re.S)
if not mm:
    sys.exit('samples not found in dump (frames=%s)' % d.get('n'))
s = json.loads(mm.group(1))
print(f'--- luminance sweep: seed={SEED} frames={len(s)} captures={d.get("captures")} ---')
lum = [x[1] for x in s]
print(f'  luminance: min={min(lum)} max={max(lum)} avg={sum(lum)/len(lum):.1f}')
jumps = sorted(((abs(s[i][1] - s[i - 1][1]), i) for i in range(1, len(s))), reverse=True)
print('  biggest frame-to-frame jumps:')
for delta, i in jumps[:10]:
    print(f'    d={delta:6.2f}  travel={s[i][0]:>7}  capture={s[i][2]}  holeDist={s[i][3]:>6}'
          f'  region={s[i][4]}  lum {s[i-1][1]:.1f} -> {s[i][1]:.1f}')
for t in (3, 8, 16, 32):
    n = sum(1 for delta, _ in jumps if delta > t)
    print(f'  frames with a jump >{t:>2} levels: {n}')
