"""V90: say that it is a battle.

Ten capital hulls and thin fire at 8,000 units is easy to read as a convoy. The
piece already announces its set pieces - wormhole, Gargantua, resumed deep space
- so the skirmish gets the same one-line annunciation the first time the flight
comes within 5,200 units of it.

The flag lives on the battle, which lives on the chunk, which is regenerated
deterministically, so the toast appears once per encounter and never repeats
inside the same chunk.

Run:  python -I v90_battle_toast.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

OLD = """  for(const g of c.gates){"""
NEW = """   for(const b of (c.battles||[])){
    if(b.notified)continue;
    if(Math.abs(b.z-travel)<5200){b.notified=true;toast('遭遇战 · SKIRMISH',5);}
   }
   for(const g of c.gates){"""

if src.count(OLD) != 1:
    sys.exit("count=%d (want 1)" % src.count(OLD))
src = src.replace(OLD, NEW, 1)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V90 written:", len(src), "chars")
