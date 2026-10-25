"""V116: the departure row slides, and the sky travels instead of cutting.

Two continuities were missing:

  * the five departure chips swapped a background on the selected one - a state
    change, not a movement. A single thumb now travels between the chips with a
    spring curve, which is the iOS pattern people already read as "selection".
  * chooseDeparture() assigned travel to the new region and cleared the chunk
    cache in one frame: the sky behind the intro cut to a different place. It
    now flies there - travel is eased over ~1 s (longer for a longer jump), the
    world streams past, and the same function runs at the end to land exactly.

Run:  python -I v116_depart.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)


# ---------------- 1. CSS: the thumb --------------------------------------
rep("/* --- Responsive Native Mobile Portrait",
    """/* --- Departure row: one thumb that travels ---------------------------- */
.destinations{position:relative}
.dest-thumb{
  position:absolute;left:0;top:0;border-radius:20px;
  background:var(--soft);border:1px solid var(--line);
  pointer-events:none;z-index:0;
  transition:transform .5s cubic-bezier(.22,1,.36,1),width .5s cubic-bezier(.22,1,.36,1),
             height .5s cubic-bezier(.22,1,.36,1),opacity .3s ease;
  opacity:0;
}
.dest-thumb.on{opacity:1}
.destination{position:relative;z-index:1}
.destination[aria-checked=true]{background:transparent;border-color:transparent}

/* --- Responsive Native Mobile Portrait""")

# ---------------- 2. JS: thumb + dolly -----------------------------------
rep("""for(const el of document.querySelectorAll('.destination'))el.addEventListener('click',()=>chooseDeparture(Number(el.dataset.region)));""",
    """// --- departure: a travelling thumb, and a sky that moves instead of cutting
const __destRow=document.querySelector('.destinations');
let __destThumb=null, __depart=null;
function __placeThumb(){
 if(!__destRow)return;
 if(!__destThumb){__destThumb=document.createElement('span');__destThumb.className='dest-thumb';__destRow.appendChild(__destThumb);}
 const cur=__destRow.querySelector('.destination[aria-checked="true"]');
 if(!cur){__destThumb.classList.remove('on');return;}
 __destThumb.style.width=cur.offsetWidth+'px';
 __destThumb.style.height=cur.offsetHeight+'px';
 __destThumb.style.transform='translate('+cur.offsetLeft+'px,'+cur.offsetTop+'px)';
 __destThumb.classList.add('on');
}
function __departDolly(i){
 const from=travel, to=i*SEGMENT+SEGMENT*.5;
 for(const el of document.querySelectorAll('.destination'))el.setAttribute('aria-checked',String(Number(el.dataset.region)===i));
 __placeThumb();
 if(started||Math.abs(to-from)<80){chooseDeparture(i);return;}
 // longer jumps take longer; ~1s for a neighbouring band
 __depart={from:from,to:to,i:i,t0:performance.now(),dur:Math.min(2200,700+Math.abs(to-from)/14)};
 if(typeof gateFlash!=='undefined')gateFlash=0.18;
}
for(const el of document.querySelectorAll('.destination'))el.addEventListener('click',()=>__departDolly(Number(el.dataset.region)));
window.addEventListener('resize',()=>setTimeout(__placeThumb,60));
setTimeout(__placeThumb,0);""")

rep(""" if(document.hidden)return;""",
    """ if(document.hidden)return;
 if(__depart){
  const k=Math.min(1,(now-__depart.t0)/__depart.dur);
  const e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2;   // easeInOutCubic
  travel=__depart.from+(__depart.to-__depart.from)*e;
  if(k>=1){const i=__depart.i;__depart=null;chooseDeparture(i);}
 }""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V116 written:", len(src), "chars")
