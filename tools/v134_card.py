"""V134: give the hatch card a physical card-craft layer.

The earlier attempt wrapped window.StarfieldHatch.openFor, but show() calls the
closure-local openFor directly. This version leaves the module alone and uses a
MutationObserver on #sf-hatch, building/filling the craft DOM only when the
overlay is open.

Run:  python -I v134_card.py <in.html> <out.html>
"""
import sys


def replace_once(src, old, new, label):
    n = src.count(old)
    assert n == 1, f"{label}: expected 1 occurrence, found {n}"
    return src.replace(old, new, 1)


CSS = """
<style id="sf-cardcraft-css">
.sf-hatch-card{perspective:900px;border-radius:18px;overflow:hidden}
/* inner hairline in the tier colour, 7px in from the edge */
.sf-foil-rim{position:absolute;inset:7px;border:1px solid var(--tier,#d9c08a);border-radius:12px;
 opacity:.28;pointer-events:none;z-index:2}
/* paper grain: a dot lattice blended over the face */
.sf-hatch-card::after{content:"";position:absolute;inset:0;border-radius:18px;pointer-events:none;z-index:3;
 background-image:radial-gradient(rgba(255,255,255,.08) 1px,transparent 1.2px);
 background-size:3px 3px;opacity:.55;mix-blend-mode:overlay}
/* thickness: a 1px top highlight and a deep bottom inner shadow */
.sf-hatch-card::before{content:"";position:absolute;inset:0;border-radius:18px;pointer-events:none;z-index:4;
 box-shadow:inset 0 1px 0 rgba(255,255,255,.18),inset 0 -30px 48px rgba(0,0,0,.52)}
/* foil serial, top-left, tier coloured, monospaced with wide tracking */
.sf-foil{position:absolute;left:14px;top:12px;z-index:5;opacity:.92;
 font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
 font-size:9.5px;line-height:1;font-weight:600;letter-spacing:.18em;white-space:nowrap;
 color:var(--tier,#d9c08a);text-shadow:0 0 10px var(--tier,#d9c08a),0 1px 0 rgba(255,255,255,.18)}
/* back face: orbit, discovery date, focus minutes, one narrative line */
.sf-hatch-back{position:absolute;inset:0;z-index:6;border-radius:18px;padding:22px 18px;box-sizing:border-box;
 display:flex;flex-direction:column;justify-content:center;gap:10px;text-align:left;
 background:linear-gradient(160deg,rgba(18,26,38,.985),rgba(6,9,14,.995));
 opacity:0;transform:rotateY(90deg);transform-origin:50% 50%;pointer-events:none;
 backface-visibility:hidden;transition:transform .42s cubic-bezier(.22,1,.36,1)}
.sf-hatch-card.flipped .sf-hatch-back{opacity:1;transform:rotateY(0deg);pointer-events:auto}
.sf-hatch-card.flipped .sf-hatch-orb,
.sf-hatch-card.flipped .sf-hatch-name,
.sf-hatch-card.flipped .sf-hatch-meta,
.sf-hatch-card.flipped .sf-hatch-hint{opacity:.05}
.sf-hatch-card.flipped .sf-hatch-orb{filter:blur(2px)}
.sf-hb-row{display:flex;justify-content:space-between;gap:14px;font-size:9px;letter-spacing:.14em;opacity:.62}
.sf-hb-row b{font-weight:400;color:#dfe9f5;opacity:.9;text-align:right}
.sf-hb-line{font-size:11px;line-height:1.8;letter-spacing:.1em;opacity:.7;margin-top:6px}
</style>
"""

JS = """
<script id="sf-cardcraft-js">
(function(){
  var lastOpen=false,lastId=null;

  function tierOf(item){
    var H=window.StarfieldHatch;
    return (H&&H.tiers&&H.tiers[item.tier])||{cn:item.tier,color:'#d9c08a'};
  }
  function current(){
    var H=window.StarfieldHatch, list=(H&&H.list)?H.list():[];
    return list.length?list[list.length-1]:null;
  }
  function serialOf(item){
    var H=window.StarfieldHatch, list=(H&&H.list)?H.list():[];
    var n=list.length||1;
    for(var i=list.length-1;i>=0;i--){
      if(list[i]&&list[i].id===item.id){ n=i+1; break; }
    }
    return String(n).padStart(3,'0');
  }
  function ensure(card){
    if(card.querySelector('.sf-foil')&&card.querySelector('.sf-hatch-back'))return;
    var foil=document.createElement('div'); foil.className='sf-foil';
    var rim=document.createElement('div'); rim.className='sf-foil-rim';
    var back=document.createElement('div'); back.className='sf-hatch-back';
    back.innerHTML='<div class="sf-hb-row"><span>轨道半径</span><b class="sf-hb-orbit">—</b></div>'+
      '<div class="sf-hb-row"><span>发现日期</span><b class="sf-hb-date">—</b></div>'+
      '<div class="sf-hb-row"><span>专注时长</span><b class="sf-hb-min">—</b></div>'+
      '<div class="sf-hb-line sf-hb-note"></div>';
    card.appendChild(foil); card.appendChild(rim); card.appendChild(back);
  }
  function fill(item){
    var card=document.querySelector('#sf-hatch .sf-hatch-card');
    if(!card||!item)return;
    ensure(card);
    var tier=tierOf(item);
    card.classList.remove('flipped');
    card.querySelector('.sf-foil').textContent='NO.'+serialOf(item)+' · '+tier.cn;
    card.querySelector('.sf-hb-orbit').textContent=(0.42+((Math.abs(item.hue|0)%40)/100)).toFixed(2)+' AU';
    card.querySelector('.sf-hb-date').textContent=item.at||'—';
    card.querySelector('.sf-hb-min').textContent=(item.minutes||0)+' 分钟';
    card.querySelector('.sf-hb-note').textContent='它在你专注的时候成形，此后再也不会重复。';
    lastId=item.id;
  }
  function maybeFill(){
    var root=document.getElementById('sf-hatch');
    if(!root||!root.classList.contains('on')){ lastOpen=false; return; }
    var item=current();
    if(!item)return;
    if(!lastOpen||lastId!==item.id){
      lastOpen=true;
      fill(item);
    }
  }

  // The published show() calls its closure-local openFor, so wrapping the
  // exported openFor never ran. Observe the overlay's class instead.
  new MutationObserver(maybeFill).observe(document.body,{
    childList:true,subtree:true,attributes:true,attributeFilter:['class']
  });
  setTimeout(maybeFill,0);

  // Capture phase runs before the card's own click handler adds .revealed,
  // so the first tap only reveals; the second tap flips.
  document.addEventListener('click',function(e){
    var t=e.target;
    if(!t||!t.closest)return;
    var card=t.closest('.sf-hatch-card');
    if(!card)return;
    if(card.classList.contains('revealed'))card.classList.toggle('flipped');
  },true);
})();
</script>
"""


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python -I v134_card.py <in.html> <out.html>")
    src_p, out_p = sys.argv[1], sys.argv[2]
    with open(src_p, encoding='utf-8', newline='') as f:
        src = f.read()

    block = CSS + JS
    src = replace_once(src, '</body>', block + '</body>', 'body close')
    with open(out_p, 'w', encoding='utf-8', newline='') as f:
        f.write(src)
    print('V134 written:', out_p, len(src), 'chars')


if __name__ == '__main__':
    main()
