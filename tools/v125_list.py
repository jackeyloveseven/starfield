"""V125: a collection you can actually open.

The hatch produces cards, but nothing shows them again - a collection with no
index is a dead end. This adds a full-screen list (grid of orbs with their tier
rim), opened with L or StarfieldHatch.openList().

Run:  python -I v125_list.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

CSS = """
<style id="sf-hatch-list-css">
#sf-hatch-list{position:fixed;inset:0;z-index:880;display:none;flex-direction:column;
 background:rgba(4,7,12,.9);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
 padding:calc(env(safe-area-inset-top,0px) + 26px) 18px 18px;box-sizing:border-box}
#sf-hatch-list.on{display:flex}
.sf-hl-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:16px}
.sf-hl-title{font-size:15px;letter-spacing:.2em}
.sf-hl-count{font-size:10px;letter-spacing:.14em;opacity:.5}
.sf-hl-grid{flex:1;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:10px;
 -webkit-overflow-scrolling:touch}
.sf-hl-item{display:flex;flex-direction:column;align-items:center;gap:7px;padding:10px 6px;border-radius:14px;
 background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
.sf-hl-orb{width:54px;height:54px;border-radius:50%;
 background:radial-gradient(circle at 34% 30%,hsl(var(--hue) 55% 62%),hsl(var(--hue) 60% 26%) 58%,#05070b 92%);
 box-shadow:0 0 16px var(--tier),inset 0 0 10px rgba(0,0,0,.6);border:1px solid var(--tier)}
.sf-hl-name{font-size:10px;letter-spacing:.08em;opacity:.85;text-align:center}
.sf-hl-empty{opacity:.4;font-size:11px;letter-spacing:.16em;margin:24px 0}
.sf-hl-close{position:absolute;top:calc(env(safe-area-inset-top,0px) + 16px);right:18px;background:none;
 border:1px solid rgba(255,255,255,.25);border-radius:20px;color:#e6edf2;font-size:11px;padding:5px 12px;cursor:pointer}
</style>
"""

JS = """
<script>
(function(){
  var root=null;
  function render(){
    var H=window.StarfieldHatch, TIERS=(H&&H.tiers)||{}, list=(H&&H.list)?H.list():[];
    if(!root){
      root=document.createElement('div'); root.id='sf-hatch-list';
      root.innerHTML='<div class="sf-hl-head"><span class="sf-hl-title">我的星球</span>'+
        '<span class="sf-hl-count"></span></div><div class="sf-hl-grid"></div>'+
        '<button class="sf-hl-close">关闭</button>';
      root.querySelector('.sf-hl-close').addEventListener('click',function(){ root.classList.remove('on'); });
      document.body.appendChild(root);
    }
    root.querySelector('.sf-hl-count').textContent=list.length?('共 '+list.length+' 颗'):'';
    var g=root.querySelector('.sf-hl-grid'); g.innerHTML='';
    if(!list.length){ var e=document.createElement('div'); e.className='sf-hl-empty';
      e.textContent='还没有星球。完成一次专注后孵化第一颗。'; g.appendChild(e); return; }
    list.slice().reverse().forEach(function(it){
      var t=TIERS[it.tier]||{color:'#fff'};
      var d=document.createElement('div'); d.className='sf-hl-item';
      d.style.setProperty('--tier',t.color); d.style.setProperty('--hue',String(it.hue|0));
      d.innerHTML='<div class="sf-hl-orb"></div><div class="sf-hl-name"></div>';
      d.querySelector('.sf-hl-name').textContent=it.name;
      g.appendChild(d);
    });
  }
  function openList(){ render(); root.classList.add('on'); }
  window.StarfieldHatch=Object.assign(window.StarfieldHatch||{},{openList:openList});
})();
</script>
"""

src = src.replace("</body>", CSS + JS + "</body>", 1)
old = "else if(e.key==='5'){if(window.triggerTesseract)"
new = ("else if(e.key.toLowerCase()==='l'){if(window.StarfieldHatch&&window.StarfieldHatch.openList)"
       "window.StarfieldHatch.openList();}\n else if(e.key==='5'){if(window.triggerTesseract)")
if src.count(old)!=1: sys.exit('key anchor count=%d'%src.count(old))
src = src.replace(old,new,1)
open(out_p,"w",encoding="utf-8",newline="").write(src)
print("V125 written:", len(src), "chars")
