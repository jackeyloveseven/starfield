import sys, os, subprocess, tempfile
from pathlib import Path
CHROME=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROBE="""
<script>
setTimeout(function(){
 var o={};
 try{
  var H=window.StarfieldHatch; H.clear();
  H.roll(15); H.roll(30); H.roll(60);
  H.openList();
  var r=document.getElementById('sf-hatch-list');
  o.opened=!!(r&&r.classList.contains('on'));
  o.items=r.querySelectorAll('.sf-hl-item').length;
  o.count=r.querySelector('.sf-hl-count').textContent;
  var orb=r.querySelector('.sf-hl-orb');
  o.orbHue=getComputedStyle(orb.parentNode).getPropertyValue('--hue').trim();
  o.orbTier=getComputedStyle(orb.parentNode).getPropertyValue('--tier').trim();
  r.querySelector('.sf-hl-close').click();
  o.closed=!r.classList.contains('on');
  H.clear(); H.openList();
  o.emptyShown=!!r.querySelector('.sf-hl-empty');
  o.stored=H.list().length;
 }catch(e){o.error=String(e);}
 document.title=JSON.stringify(o);
},500);
</script>"""
src=open(sys.argv[1],encoding='utf-8').read()
tmp=tempfile.mkdtemp(); ph=os.path.join(tmp,'p.html')
open(ph,'w',encoding='utf-8',newline='').write(src.replace('</body>',PROBE+'</body>',1))
with tempfile.TemporaryDirectory() as prof:
 r=subprocess.run([CHROME,'--headless=new','--disable-gpu','--use-angle=swiftshader',
  '--enable-unsafe-swiftshader','--disable-gpu-compositing','--no-sandbox','--mute-audio',
  '--hide-scrollbars','--no-first-run','--disable-extensions','--disable-background-networking',
  '--window-size=1000,700','--user-data-dir='+prof,'--virtual-time-budget=3000','--dump-dom',
  Path(ph).as_uri()],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
d=r.stdout or ''; i,j=d.find('<title>'),d.find('</title>')
print(d[i+7:j] if i>=0 else 'NO TITLE')
