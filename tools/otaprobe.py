"""Exercise the OTA handshake without an APK.

Injects a fake StarfieldNative bridge, drives the same calls the Android build
makes, and reports what the page actually shows: the toast text, and the OTA
pill's title/description. Before v99 an OTA_ERROR produced nothing at all and an
OTA_READY always announced the hard-coded v1.1.0.

  python -I otaprobe.py starfield-v99.html
"""
import sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html = sys.argv[1]

PROBE = """
<script>
setTimeout(function(){},0);
window.__r={};
window.StarfieldNative={
  checkOtaUpdate:function(){
    window.onStarfieldOtaNotify('OTA_READY',{version:'1.1.3',build:105,changelog:'竖屏 UI 修复 + 热更新修复'});
  },
  getAppVersion:function(){return '1.1.2'},
  getBuildNumber:function(){return 104},
  reloadApp:function(){}
};
try{
  window.checkStarfieldUpdates(true);
  var pill=document.getElementById('sf-ota-banner');
  window.__r.pill=pill?pill.innerText.replace(/\\s+/g,' ').trim():null;
  // now the failure path
  if(pill)pill.remove();
  window.onStarfieldOtaNotify('OTA_ERROR','云端检查失败 (HTTP 502)');
  window.__r.errToast=(document.getElementById('toast')||{}).textContent||'';
  window.onStarfieldOtaNotify('OTA_UP_TO_DATE','1.1.2');
  window.__r.upToast=(document.getElementById('toast')||{}).textContent||'';
  // string payload, as the old bridge sent it
  window.onStarfieldOtaNotify('OTA_READY','1.1.4');
  var p2=document.getElementById('sf-ota-banner');
  window.__r.pillString=p2?p2.innerText.replace(/\\s+/g,' ').trim():null;
  // and the settings tag
  var tag=document.getElementById('sf-version-tag');
  window.__r.svgTag=tag?tag.textContent:null;
}catch(e){window.__r.error=String(e);}
document.title=JSON.stringify(window.__r);
</script>"""

src = open(html, encoding='utf-8').read()
tmp = tempfile.mkdtemp(prefix='otaprobe-')
ph = os.path.join(tmp, 'p.html')
open(ph, 'w', encoding='utf-8', newline='').write(src.replace('</body>', PROBE + '</body>', 1))
url = 'file:///' + ph.replace('\\', '/')

with tempfile.TemporaryDirectory(prefix='otaprobe-prof-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
                        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
                        '--mute-audio', '--hide-scrollbars', '--no-first-run',
                        '--disable-extensions', '--disable-background-networking',
                        '--window-size=1200,800', '--user-data-dir=' + prof, '--dump-dom', url],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
dom = r.stdout or ''
i, j = dom.find('<title>'), dom.find('</title>')
print('--- OTA handshake ---')
if i < 0:
    print('NO TITLE'); print(dom[:300]); sys.exit(1)
print(json.dumps(json.loads(dom[i + 7:j]), ensure_ascii=True, indent=2))
