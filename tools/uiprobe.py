"""DOM geometry probe: what actually overlaps what, on a phone-sized page.

Headless Chrome refuses a window narrower than 500 CSS px, so the page is loaded
inside an iframe of exactly the requested size; inside it, innerWidth/innerHeight
and every media query behave like the phone. --allow-file-access-from-files lets
the outer page read the inner title.

Reports, for every piece of UI that is actually visible (ancestor opacity
included): its rect, and every pair that overlaps by more than 2 px.

  python -I uiprobe.py starfield.html --size 390x844 --mode intro
  python -I uiprobe.py starfield.html --size 390x844 --mode flying
  python -I uiprobe.py starfield.html --size 844x390 --mode flying
"""
import sys, os, json, argparse, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('--size', default='390x844')
ap.add_argument('--mode', default='intro', choices=['intro', 'flying'])
ap.add_argument('--seek', type=float, default=30.0)
ap.add_argument('--seed', default='1a2b')
ap.add_argument('--open', default='', help='comma separated ids to click before measuring')
ap.add_argument('--touch', action='store_true', help='pretend to be a touch device')
a = ap.parse_args()

W, H = (int(v) for v in a.size.lower().split('x'))

SEL = ['#starfield-touch-overlay', '.sf-touch-cluster', '.sf-touch-primary-row',
       '.sf-touch-more-tray', '.sf-touch-joy-base', '.sf-touch-joy-zone']
IDS = [
    'masthead', 'orientation-toggle-btn', 'edition', 'intro', 'begin',
    'camera-hud', 'camera-name', 'camera-mode-label', 'flight-stats',
    'poem', 'journey', 'route', 'distance', 'flight-time',
    'controls', 'warp-toggle', 'camera-toggle', 'sound-toggle', 'codex-toggle',
    'photo-toggle', 'radar-toggle', 'formation-toggle', 'hangar-toggle',
    'settings-toggle', 'poem-toggle', 'pause-toggle', 'fullscreen-toggle',
    'hint', 'toast', 'comms-hud', 'pause-label', 'photo-ui', 'settings-drawer',
    'codex-modal', 'sf-version-tag', 'sf-focus-ticker', 'sf-ota-pill',
]

SEL = ['#' + i for i in IDS] + SEL

start = ''
if a.mode == 'flying':
    start = (
        "document.getElementById('begin').click();"
        "const S=window.Starfield;if(S&&S.seek)S.seek(" + str(a.seek) + ");"
    )
for oid in [s for s in a.open.split(',') if s]:
    start += "var __o=document.getElementById('%s');if(__o)__o.click();" % oid

JS = """
<style>*,*::before,*::after{animation:none!important;transition:none!important}</style>
<script>
window.__errors=[];window.addEventListener('error',e=>window.__errors.push(String(e.message)));
try{
 __START__
 const out={vw:innerWidth,vh:innerHeight,dpr:devicePixelRatio,
   scrollW:document.documentElement.scrollWidth,
   scrollH:document.documentElement.scrollHeight,els:[]};
 const R=function(e){var r=e.getBoundingClientRect();
   return [Math.round(r.left*10)/10,Math.round(r.top*10)/10,
           Math.round(r.width*10)/10,Math.round(r.height*10)/10];};
 // Effective visibility: an element inside a .hud at opacity 0 is not on screen.
 const eff=function(e){
   var o=1,n=e;
   while(n&&n.nodeType===1){
     var s=getComputedStyle(n);
     if(s.display==='none'||s.visibility==='hidden')return 0;
     o*=parseFloat(s.opacity);
     n=n.parentElement;
   }
   return o;
 };
 var seen=[];
 var IDS=__SEL__;
 for(var ii=0;ii<IDS.length;ii++){
   var id=IDS[ii].replace(/^#/,'');
   var e=document.querySelector(IDS[ii]);if(!e)continue;
   var cs=getComputedStyle(e);var r=R(e);
   var op=eff(e);
   var vis=op>0.02&&r[2]>0.5&&r[3]>0.5;
   var big=(r[2]>=innerWidth*0.9&&r[3]>=innerHeight*0.9);   // full-stage container
   out.els.push({id:id,r:r,vis:vis,op:Math.round(op*100)/100,big:big,
                 disp:cs.display,pe:cs.pointerEvents,fs:cs.fontSize,z:cs.zIndex});
   if(vis&&!big)seen.push({id:id,r:r,el:e});
 }
 out.overflow=[];
 for(var k=0;k<IDS.length;k++){
   var host=document.querySelector(IDS[k]);if(!host)continue;
   if(eff(host)<0.02)continue;
   var kids=host.querySelectorAll('*');
   for(var q=0;q<kids.length;q++){
     var c=kids[q];
     if(eff(c)<0.02)continue;
     var cr=c.getBoundingClientRect();
     if(cr.width<1||cr.height<1)continue;
     if(cr.left<-0.5||cr.right>innerWidth+0.5)
       out.overflow.push({id:IDS[k].replace(/^#/,''),tag:c.tagName+'.'+c.className,
         r:[Math.round(cr.left),Math.round(cr.top),Math.round(cr.width),Math.round(cr.height)]});
   }
 }
 out.overlaps=[];
 for(var i2=0;i2<seen.length;i2++)for(var j2=i2+1;j2<seen.length;j2++){
   var A=seen[i2],B=seen[j2];
   if(A.el.contains(B.el)||B.el.contains(A.el))continue;
   var ox=Math.min(A.r[0]+A.r[2],B.r[0]+B.r[2])-Math.max(A.r[0],B.r[0]);
   var oy=Math.min(A.r[1]+A.r[3],B.r[1]+B.r[3])-Math.max(A.r[1],B.r[1]);
   if(ox>2&&oy>2)out.overlaps.push([A.id,B.id,Math.round(ox),Math.round(oy)]);
 }
 document.title=JSON.stringify(out);
}catch(err){
 document.title=JSON.stringify({probeError:String(err),stack:String(err&&err.stack).slice(0,300)});
}
</script>
"""

probe = JS.replace('__START__', start).replace('__SEL__', json.dumps(SEL))

src = open(a.html, encoding='utf-8').read()
if a.touch:
    spoof = ('<script>window.ontouchstart=null;'
             'try{Object.defineProperty(navigator,"maxTouchPoints",{get:function(){return 5}});}'
             'catch(e){}</script>')
    src = src.replace('<head>', '<head>' + spoof, 1)
if '</body>' not in src:
    sys.exit('no </body>')
tmpdir = tempfile.mkdtemp(prefix='uiprobe-')
ph = os.path.join(tmpdir, 'probe.html')
open(ph, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

wrapper = os.path.join(tmpdir, 'frame.html')
open(wrapper, 'w', encoding='utf-8', newline='').write(
    '<!doctype html><html><head><meta charset="utf-8"><title>pending</title>'
    '<style>html,body{margin:0;background:#000}iframe{border:0;display:block}</style>'
    '</head><body><iframe id="f" width="%d" height="%d" src="probe.html?seed=%s"'
    ' onload="document.title=this.contentDocument.title"></iframe></body></html>'
    % (W, H, a.seed))

url = 'file:///' + wrapper.replace('\\', '/')
base = [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
        '--disable-background-networking', '--allow-file-access-from-files',
        '--window-size=%d,%d' % (max(W, 520), max(H, 400))]
with tempfile.TemporaryDirectory(prefix='uiprobe-prof-') as prof:
    r = subprocess.run(base + ['--user-data-dir=' + prof, '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=180)
dom = r.stdout or ''
i, j = dom.find('<title>'), dom.find('</title>')
print('--- %s mode=%s ---' % (a.size, a.mode))
if i < 0 or j < 0:
    print('NO TITLE'); print(dom[:400]); sys.exit(1)
try:
    d = json.loads(dom[i + 7:j])
except Exception:
    print('raw:', dom[i + 7:j][:400]); sys.exit(1)
if d.get('probeError'):
    print('PROBE FAILED:', d['probeError']); print(d.get('stack')); sys.exit(1)
print('  viewport %dx%d  scroll %dx%d' % (d['vw'], d['vh'], d['scrollW'], d['scrollH']))
print('  visible:')
for e in d['els']:
    if not e['vis']:
        continue
    x, y, w, h = e['r']
    flag = ''
    if x < -0.5 or y < -0.5 or x + w > d['vw'] + 0.5 or y + h > d['vh'] + 0.5:
        flag = '  <== OUT OF VIEWPORT'
    print('    %-22s (%6.1f,%6.1f) %6.1fx%-6.1f op=%.2f fs=%s%s'
          % (e['id'], x, y, w, h, e['op'], e['fs'], flag))
print('  hidden :', ', '.join([e['id'] for e in d['els'] if not e['vis']]))
print('  overlaps:', d['overlaps'] or 'none')
print('  child overflow:')
for o in d['overflow'][:25]:
    print('    %-22s %-48s %s' % (o['id'], o['tag'][:46], o['r']))
if not d['overflow']:
    print('    none')
