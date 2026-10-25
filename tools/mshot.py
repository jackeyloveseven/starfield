"""Phone-sized screenshot: the page runs in an iframe of exactly WxH.

Headless Chrome will not open a window narrower than 500 CSS px, so a 390-wide
screenshot taken with --window-size is really the left 390 px of a 500 px
layout - which reads as "the UI is cut off on the right" when nothing is wrong.
The iframe fixes innerWidth/innerHeight and every media query, and the capture
is cropped back to WxH.

  python -I mshot.py starfield.html shots/p.png --size 390x844 --mode intro
  python -I mshot.py starfield.html shots/p.png --size 390x844 --mode fly --seek 40
  python -I mshot.py starfield.html shots/p.png --size 390x844 --mode fly --open codex-toggle
"""
import sys, os, json, argparse, subprocess, tempfile
from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ap = argparse.ArgumentParser()
ap.add_argument('html')
ap.add_argument('png')
ap.add_argument('--size', default='390x844')
ap.add_argument('--mode', default='fly', choices=['intro', 'fly'])
ap.add_argument('--seek', type=float, default=0.0)
ap.add_argument('--seed', default='1a2b')
ap.add_argument('--dpr', type=float, default=2.0)
ap.add_argument('--open', default='')
ap.add_argument('--touch', action='store_true', help='pretend to be a touch device')
ap.add_argument('--wait', type=float, default=0.0)
a = ap.parse_args()

W, H = (int(v) for v in a.size.lower().split('x'))
# The iframe is exactly W x H CSS px; the device scale factor only affects how
# many pixels the capture has. Mixing the two is what made the first attempt
# render an 780 px wide layout and report "missing HUD".
px, py = W, H

start = ''
if a.mode == 'fly':
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
}catch(err){document.title=JSON.stringify({probeError:String(err)});}
</script>
"""

probe = JS.replace('__START__', start)
src = open(a.html, encoding='utf-8').read()
if a.touch:
    # Has to land before every other script: the touch HUD is built on the
    # result of 'ontouchstart' in window at boot.
    spoof = ('<script>window.ontouchstart=null;'
             'try{Object.defineProperty(navigator,"maxTouchPoints",{get:function(){return 5}});}'
             'catch(e){}</script>')
    src = src.replace('<head>', '<head>' + spoof, 1)
tmpdir = tempfile.mkdtemp(prefix='mshot-')
ph = os.path.join(tmpdir, 'probe.html')
open(ph, 'w', encoding='utf-8', newline='').write(src.replace('</body>', probe + '</body>', 1))

win_w, win_h = max(W, 520), max(H, 420)
wrapper = os.path.join(tmpdir, 'frame.html')
open(wrapper, 'w', encoding='utf-8', newline='').write(
    '<!doctype html><html><head><meta charset="utf-8">'
    '<style>html,body{margin:0;background:#000;overflow:hidden}'
    'iframe{border:0;display:block;width:%dpx;height:%dpx}</style></head><body>'
    '<iframe src="probe.html?seed=%s"></iframe></body></html>' % (px, py, a.seed))

url = 'file:///' + wrapper.replace('\\', '/')
out = os.path.abspath(a.png)
os.makedirs(os.path.dirname(out), exist_ok=True)
raw = out.replace('.png', '.raw.png')

with tempfile.TemporaryDirectory(prefix='mshot-prof-') as prof:
    r = subprocess.run(
        [CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
         '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
         '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
         '--disable-background-networking', '--allow-file-access-from-files',
         '--force-device-scale-factor=%s' % a.dpr,
         '--window-size=%d,%d' % (win_w, win_h),
         '--user-data-dir=' + prof, '--screenshot=' + raw, url],
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)

if not os.path.exists(raw):
    sys.exit('screenshot failed: ' + (r.stderr or '')[-300:])
img = Image.open(raw)
# Chrome may or may not fold the scale factor into --screenshot; derive it from
# the capture instead of assuming.
s = img.width / float(win_w)
img = img.crop((0, 0, int(round(W * s)), int(round(H * s))))
img.save(out)
os.remove(raw)
print('wrote %s  %dx%d (css %dx%d dpr %s)' % (a.png, img.width, img.height, W, H, a.dpr))
