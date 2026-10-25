"""V124: the reveal and the card.

The hatch table shipped without a way to see what came out. This adds the rest
of the moment: a silhouette, a tap, and the planet. Nothing existing is touched -
the overlay is built when called, and a MutationObserver appends one button to
the focus result sheet if that sheet ever appears.

  window.StarfieldHatch.show()          roll + reveal the latest session
  window.StarfieldHatch.openFor(item)   reveal a given item

Run:  python -I v124_card.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

CSS = """
<style id="sf-hatch-css">
#sf-hatch{position:fixed;inset:0;z-index:900;display:none;align-items:center;justify-content:center;
  background:rgba(4,7,12,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px)}
#sf-hatch.on{display:flex}
.sf-hatch-card{position:relative;width:min(300px,74vw);aspect-ratio:3/4;border-radius:22px;
  background:linear-gradient(160deg,rgba(26,36,50,.96),rgba(8,12,18,.98));
  border:1px solid rgba(255,255,255,.14);box-shadow:0 24px 60px rgba(0,0,0,.7),inset 0 1px 0 rgba(255,255,255,.08);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;
  cursor:pointer;overflow:hidden;transition:transform .4s cubic-bezier(.22,1,.36,1)}
.sf-hatch-card:active{transform:scale(.98)}
.sf-hatch-orb{width:46%;aspect-ratio:1;border-radius:50%;filter:blur(1px);
  background:radial-gradient(circle at 34% 30%,rgba(255,255,255,.05),rgba(0,0,0,.9) 62%);
  border:1px solid rgba(255,255,255,.16);transition:all .7s cubic-bezier(.22,1,.36,1)}
.sf-hatch-card.revealed .sf-hatch-orb{filter:blur(0);box-shadow:0 0 42px var(--tier),0 0 12px var(--tier) inset}
.sf-hatch-card.revealed .sf-hatch-orb{background:radial-gradient(circle at 34% 30%,hsl(var(--hue) 55% 62%),hsl(var(--hue) 60% 26%) 58%,#05070b 92%)}
.sf-hatch-name{font-size:19px;letter-spacing:.16em;opacity:0;transition:opacity .5s .25s}
.sf-hatch-meta{font-size:9px;letter-spacing:.22em;opacity:0;transition:opacity .5s .35s;color:var(--tier)}
.sf-hatch-card.revealed .sf-hatch-name,.sf-hatch-card.revealed .sf-hatch-meta{opacity:1}
.sf-hatch-hint{position:absolute;bottom:14px;font-size:9px;letter-spacing:.24em;opacity:.45}
.sf-hatch-card.revealed .sf-hatch-hint{display:none}
.sf-hatch-close{position:absolute;top:calc(env(safe-area-inset-top,0px) + 16px);right:18px;
  background:none;border:1px solid rgba(255,255,255,.25);border-radius:20px;color:#e6edf2;
  font-size:11px;padding:5px 12px;cursor:pointer}
</style>
"""

JS = """
<script>
(function(){
  var TIERS = (window.StarfieldHatch && window.StarfieldHatch.tiers) || {};
  function el(tag, cls, txt){ var e=document.createElement(tag); if(cls)e.className=cls; if(txt)e.textContent=txt; return e; }
  var root=null, card=null, orb=null, nameEl=null, metaEl=null, cur=null;

  function build(){
    if(root) return;
    root=el('div'); root.id='sf-hatch';
    card=el('div','sf-hatch-card');
    orb=el('div','sf-hatch-orb');
    nameEl=el('div','sf-hatch-name');
    metaEl=el('div','sf-hatch-meta');
    var hint=el('div','sf-hatch-hint','轻触点亮');
    card.appendChild(orb); card.appendChild(nameEl); card.appendChild(metaEl); card.appendChild(hint);
    var close=el('button','sf-hatch-close','关闭');
    close.addEventListener('click',function(e){ e.stopPropagation(); hide(); });
    root.appendChild(card); root.appendChild(close);
    card.addEventListener('click',function(){ card.classList.add('revealed');
      if(window.toast) toast('已收入领地 · ' + (cur?cur.name:''), 2.2); });
    document.body.appendChild(root);
  }
  function openFor(item){
    build(); cur=item;
    var t=TIERS[item.tier]||{color:'#fff',cn:item.tier};
    card.classList.remove('revealed');
    card.style.setProperty('--tier',t.color);
    card.style.setProperty('--hue',String(item.hue|0));
    nameEl.textContent=item.name;
    metaEl.textContent=t.cn+' · '+item.minutes+' 分钟 · '+item.at;
    root.classList.add('on');
  }
  function hide(){ if(root) root.classList.remove('on'); }
  function show(){ var it=window.StarfieldHatch.roll(15); openFor(it); return it; }

  var api={show:show, openFor:openFor, hide:hide};
  window.StarfieldHatch=Object.assign(window.StarfieldHatch||{},api);

  // Additive only: if the focus result sheet is on screen, offer the hatch.
  try{
    new MutationObserver(function(){
      var box=document.querySelector('.sf-focus-modal-box'); if(!box||box.dataset.hatch)return;
      box.dataset.hatch='1';
      var b=document.createElement('button');
      b.className='sf-focus-confirm-btn'; b.textContent='孵化这颗星球';
      b.style.cssText='margin-top:14px;width:100%;padding:12px;border-radius:12px;border:1px solid rgba(255,215,0,.5);background:rgba(255,215,0,.12);color:#ffd700;font-size:13px;letter-spacing:.12em;cursor:pointer';
      b.addEventListener('click',function(){
        var end=document.querySelector('.sf-focus-modal-box'); if(end)end.parentNode.removeChild(end.parentNode.classList.contains('sf-focus-modal-overlay')?end.parentNode:end);
        api.show();
      });
      box.appendChild(b);
    }).observe(document.body,{childList:true,subtree:true});
  }catch(e){}
})();
</script>
"""

src = src.replace("</body>", CSS + JS + "</body>", 1)
open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V124 written:", len(src), "chars")
