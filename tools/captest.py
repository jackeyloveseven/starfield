"""Is the capture set piece still reachable, and is it still avoidable?

Drives the real pointer input: hold the cursor hard over toward the nearest
horizon and see whether committing to it triggers a capture. Uses the page's
own wind pipeline, so this tests the same path a player does.
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
AT = sys.argv[3] if len(sys.argv) > 3 else '0'
TOTAL = float(sys.argv[4]) if len(sys.argv) > 4 else 900.0
STEP = 0.5   # the wind energy envelope decays in ~1.35 s, so a real
             # player's pointer is effectively continuous; a coarse probe is not
STEER = sys.argv[5] if len(sys.argv) > 5 else 'on'

JS = '''<script>window.__r={cap:0,steered:0,samples:0,bad:false,minDist:1e9,minW:9,maxW:0,gate:null};
try{
 const d=document.querySelectorAll(".destination")[__AT__];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield,c=document.getElementById("landscape");
 const move=(x,y)=>c.dispatchEvent(new PointerEvent("pointermove",{clientX:x,clientY:y,pointerId:1,bubbles:true,pointerType:"mouse"}));
 let prev=0;
 for(let i=0;i<__N__;i++){
  if(__STEER__){
   const h=S.holeDir();
   if(h){
    if(h.dist<__r__.minDist)__r__.minDist=h.dist;
    // steer the cursor toward the side the horizon is on
    move(h.right>0?innerWidth*0.97:innerWidth*0.03, innerHeight*0.5);
    __r__.steered++;
   }
  }
  S.seek(__STEP__);
  const st=S.getState();
  __r__.samples++;
  if(prev===0&&st.capture!==0)__r__.cap++;
  prev=st.capture;
  if(S.flock().bad)__r__.bad=true;
  const w=Math.abs(S.windX());if(w<__r__.minW)__r__.minW=w;if(w>__r__.maxW)__r__.maxW=w;
 }
 __r__.travel=Math.round(S.getState().travel);
 document.title=JSON.stringify(__r__);
}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>'''

probe = (JS.replace('__AT__', AT).replace('__N__', str(int(TOTAL / STEP)))
           .replace('__STEP__', str(STEP)).replace('__r__', 'window.__r')
           .replace('__STEER__', 'true' if STEER == 'on' else 'false'))
src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('captest.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))
with tempfile.TemporaryDirectory(prefix='cap-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', '--mute-audio',
                        '--no-first-run', f'--user-data-dir={prof}', '--window-size=1280,720',
                        '--dump-dom', 'file:///' + out.replace(os.sep, '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=900)
m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print(f'--- capture reachability: seed={SEED} at={AT} steer={STEER} total={TOTAL}s ---')
if not m:
    sys.exit('NO TITLE — ' + (r.stderr or '')[-300:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'])
print(f"  captures        : {d['cap']}")
print(f"  closest approach: {d['minDist']}")
print(f"  steered frames  : {d['steered']} / {d['samples']}")
print(f"  nan/runaway     : {d['bad']}")
print(f"  |wind.x| range  : {d.get('minW')} .. {d.get('maxW')}")
print(f"  travel          : {d['travel']}")
