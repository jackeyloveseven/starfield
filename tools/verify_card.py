import sys, os, subprocess, tempfile
from pathlib import Path
CHROME=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
html=sys.argv[1]
PROBE="""
<script>
setTimeout(function(){
 var o={};
 try{
  var H=window.StarfieldHatch; H.clear(); H.show();
  var root=document.getElementById('sf-hatch'), card=root&&root.querySelector('.sf-hatch-card');
  o.opened = !!(root && root.classList.contains('on'));
  o.revealedBefore = card.classList.contains('revealed');
  o.hint = !!root.querySelector('.sf-hatch-hint');
  card.click();
  o.revealedAfter = card.classList.contains('revealed');
  o.name = root.querySelector('.sf-hatch-name').textContent;
  o.meta = root.querySelector('.sf-hatch-meta').textContent;
  o.tierColor = getComputedStyle(card).getPropertyValue('--tier').trim();
  root.querySelector('.sf-hatch-close').click();
  o.closed = !root.classList.contains('on');
  o.stored = H.list().length;
 }catch(e){ o.error=String(e); }
 document.title=JSON.stringify(o);
}, 500);
</script>"""
src=open(html,encoding='utf-8').read()
tmp=tempfile.mkdtemp(prefix="card-")
ph=os.path.join(tmp,'p.html')
open(ph,'w',encoding='utf-8',newline='').write(src.replace('</body>',PROBE+'</body>',1))
with tempfile.TemporaryDirectory(prefix="card-prof-") as prof:
 r=subprocess.run([CHROME,'--headless=new','--disable-gpu','--use-angle=swiftshader',
  '--enable-unsafe-swiftshader','--disable-gpu-compositing','--no-sandbox','--mute-audio',
  '--hide-scrollbars','--no-first-run','--disable-extensions','--disable-background-networking',
  '--window-size=1000,700','--user-data-dir='+prof,'--virtual-time-budget=3000','--dump-dom',
  Path(ph).as_uri()],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
dom=r.stdout or ''
i,j=dom.find('<title>'),dom.find('</title>')
print(dom[i+7:j] if i>=0 else 'NO TITLE')
