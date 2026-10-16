"""Numeric check on gravity: the failure mode that matters is a silent NaN or a
runaway, which no screenshot would show.

Seeks the simulation forward in steps, sampling the flock and the capture
machine, and reports anything non-finite or unbounded.
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\machine\Downloads\starfield.html"
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
AT = sys.argv[3] if len(sys.argv) > 3 else '4'
TOTAL = float(sys.argv[4]) if len(sys.argv) > 4 else 900.0
STEP = 4.0

JS = '''<script>window.__log=[];
try{
 const b=document.getElementById("begin");if(b)b.click();
 const S=window.Starfield;
 let prev=0,captures=0,phases={},maxFlash=0,frames=0,bad=false,maxSpeed=0;
 for(let i=0;i<__N__;i++){
  S.seek(__STEP__);
  const st=S.getState(),f=S.flock();
  if(f.bad)bad=true;
  if(f.speed>maxSpeed)maxSpeed=f.speed;
  phases[st.capture]=(phases[st.capture]||0)+1;
  // a capture episode is a rising edge out of FREE, not a one-off flag
  if(prev===0&&st.capture!==0)captures++;
  prev=st.capture;
  frames++;
 }
 const st=S.getState();
 document.title=JSON.stringify({bad,captures,maxSpeed,phases,
   perMin:+(captures/(__N__*__STEP__)*60).toFixed(2),
   travel:Math.round(st.travel),masses:st.masses,
   shareCaptured:+(1-(phases[0]||0)/frames).toFixed(3)});
}catch(e){document.title=JSON.stringify({probeError:String(e)});}</script>'''
probe = JS.replace('__N__', str(int(TOTAL / STEP))).replace('__STEP__', str(STEP))
src = open(HTML, encoding='utf-8').read()
out = os.path.abspath('grav.probe.html')
open(out, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

with tempfile.TemporaryDirectory(prefix='grav-') as profile:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
                        '--mute-audio', '--no-first-run', f'--user-data-dir={profile}',
                        '--window-size=900,560', '--dump-dom',
                        'file:///' + out.replace('\\', '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=600)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
print(f'--- gravity sweep: seed={SEED} at={AT} total={TOTAL}s step={STEP}s ---')
if m:
    try:
        d = json.loads(m.group(1))
        for k in ('bad', 'captures', 'perMin', 'shareCaptured', 'maxSpeed', 'phases', 'travel', 'masses'):
            print(f'  {k:<10}: {d.get(k)}')
    except Exception:
        print('  raw:', m.group(1)[:300])
else:
    print('  NO TITLE —', (r.stderr or '')[-300:])
