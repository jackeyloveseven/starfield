"""V91: only announce a battle you can actually see.

v90 fired the toast at 5,200 units of the battle's centre, which can be off the
side of the frame - the player is told "SKIRMISH" and sees an empty sky. The
annunciation now also requires the battle to project onto the plate.

Run:  python -I v91_toast_visible.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """   for(const b of (c.battles||[])){
    if(b.notified)continue;
    if(Math.abs(b.z-travel)<5200){b.notified=true;toast('遭遇战 · SKIRMISH',5);}
   }"""
NEW = """   for(const b of (c.battles||[])){
    if(b.notified)continue;
    const bq=project([b.x,b.y,b.z]);
    if(bq&&bq[2]<22000&&bq[0]>-160&&bq[0]<W+160&&bq[1]>-160&&bq[1]<H+160&&Math.abs(b.z-travel)<5200){
     b.notified=true;toast('遭遇战 · SKIRMISH',5);
    }
   }"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V91 written:", len(src), "chars")
