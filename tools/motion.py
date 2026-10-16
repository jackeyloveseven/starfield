"""Find what breaks immersion, by measuring the camera rather than guessing.

Samples the camera basis every simulation frame and reports the largest
frame-to-frame jumps in eye position and orientation, tagged with the travel
distance, the lens and the capture phase at that moment. A hard cut in the world
shows up as a jump of hundreds or thousands of units in one frame.

Steers toward the nearest ink well so the capture sequence is exercised too - with
no pointer input a capture never fires, so its jump would never be sampled.
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
SECONDS = float(sys.argv[3]) if len(sys.argv) > 3 else 600.0
STEER = (sys.argv[4] if len(sys.argv) > 4 else 'on') == 'on'
N = int(SECONDS * 60)

JS = '''<script>window.__j=[];
try{
 const d=document.querySelectorAll(".destination")[0];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield,c=document.getElementById("landscape");
 const move=(x,y)=>c.dispatchEvent(new PointerEvent("pointermove",{clientX:x,clientY:y,pointerId:1,bubbles:true,pointerType:"mouse"}));
 let prev=null,maxJump=0,maxAng=0,captures=0,prevCap=0,capJump=0;
 for(let i=0;i<__N__;i++){
  if(__STEER__){const h=S.holeDir();if(h)move(h.right>0?innerWidth*0.97:innerWidth*0.03,innerHeight*0.5);}
  S.seek(1/60);
  const st=S.getState(),e=st.eye;
  if(prev){
   const dist=Math.hypot(e[0]-prev[0],e[1]-prev[1],e[2]-prev[2]);
   const ang=Math.abs(st.yaw-prev[3])+Math.abs(st.pitch-prev[4]);
   if(st.capture!==0&&st.capture!==prevCap&&dist>capJump)capJump=dist;
   if(dist>maxJump)maxJump=dist;
   if(ang>maxAng)maxAng=ang;
   window.__j.push([+dist.toFixed(1),Math.round(st.travel),st.capture,st.lens,+ang.toFixed(4)]);
  }
  prev=[e[0],e[1],e[2],st.yaw,st.pitch];
  prevCap=st.capture;
 }
 document.title=JSON.stringify({maxJump:Math.round(maxJump),maxAng:+maxAng.toFixed(4),
  capJump:Math.round(capJump),travel:Math.round(S.getState().travel),
  jumps:window.__j});
}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>'''

probe = JS.replace('__N__', str(N)).replace('__STEER__', 'true' if STEER else 'false')
src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('motion.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

with tempfile.TemporaryDirectory(prefix='motion-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
                        '--no-first-run', f'--user-data-dir={prof}', '--window-size=1280,720',
                        '--dump-dom', 'file:///' + out.replace(os.sep, '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'])
print(f'--- camera motion: seed={SEED} steer={STEER} seconds={SECONDS} ---')
print(f'  max eye jump per frame : {d["maxJump"]} units')
print(f'  max yaw+pitch per frame: {d["maxAng"]}')
print(f'  jump at capture entry  : {d["capJump"]} units')
j = d.get('jumps') or []
top = sorted(j, key=lambda v: -v[0])[:10]
print('  largest frame-to-frame eye jumps:')
for dist, travel, cap, lens, ang in top:
    print(f'    {dist:>9.1f} u  travel={travel:>7}  capture={cap}  lens={lens[:22]:<22} dang={ang}')
