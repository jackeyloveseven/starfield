"""v26a_planets2 -- two planet-domain items on top of the v21w per-kind merge.

(a) THE BROKEN OCEAN WORLD
    shots/v25-hole.png carries a blue disc at ~(1000,320) with white blobs on it
    that read as a broken sprite. It is kind 1 (the ocean world), and the defect
    is in the cloud placement, not in the merge: kindSurface() placed each of its
    six white patches up to .80 of the radius out and up to .46 of it across, so a
    patch's body could reach 1.26 rad - well past the limb. drawWorld clips the
    whole surface layer to the disc, so a patch that reaches the limb is sliced
    into a straight-edged chord, and several of those merging into one connected
    white mass with a chopped edge is exactly what "reads as broken" describes.
    The patches are now anchored to the sub-solar direction, kept inside .46 rad
    of the centre and at most .26 rad across (so nothing reaches past .72), and
    given a high `lit` bar at their centre, so a patch is either in real sunlight
    or not drawn at all.

(b) THE RING SYSTEM
    Kind 8 was reserved for a ringed giant but the ring it drew was a single pale
    beige pair of bands at .24/.18 alpha - washed out over both the paper and the
    planet, so it read as a smudge rather than as a ring, and every ringed giant
    in the frame was the same colour. The reference the user keeps pointing at
    (TheKeyDU/cosmic-flight) has "Saturn with a dark-gold ring, Neptune with an
    ice-blue ring, ice planets with pale cyan/violet rings". ringHalf() now draws
    three flat toned annuli with two clean gaps from one of four ring families,
    picked once per body from its phase; the family also supplies the body's own
    tint, because a violet ring on a tan planet is a colour clash rather than a
    Neptune. The rolled-and-squashed frame, and the existing back/front depth
    split, are kept: that is what makes the far half sit behind the planet and the
    near half in front of it instead of pasting an ellipse over the disc.

Owns: kindSurface (kind 1), ringHalf, RINGFAM, massTint's kind-8 case. Does NOT
touch GLSL_HOLE, drawHole, updateCapture, postPass, or chunk().

Run:  python -I v26a_planets2.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v26a_planets2.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit("count=%d (want %d): %r" % (c, n, a[:200]))
    s = s.replace(a, b, n)


# ---- (a) the ocean world's clouds stay inside the disc and on the day side ----
rep("""  for(let j=0;j<6;j++){
   const a=hash(hb,60+j,91)*TAU, rr=Math.sqrt(hash(hb,60+j,92))*rad*.80;
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.16+.30*hash(hb,60+j,93));
   const al=lit(bx,by); if(al<.15)continue;
   ctx.save();ctx.translate(bx,by);ctx.rotate(hash(hb,60+j,94)*TAU);ctx.scale(1,.42);ctx.translate(-bx,-by);
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(blend(tint,[255,255,255],.90),.52*al);ctx.fill();ctx.restore();
  }
  return;""",
"""  // The patches have to stay WELL INSIDE the disc. They used to be placed up to
  // .80 of the radius out and could be .46 of it across, so a patch's body could
  // reach 1.26 rad - past the limb, where the disc clip slices a bright patch into
  // a straight-edged chord. Several of those merging into one connected white
  // mass with a chopped edge is what read as broken. Now the centre sits within
  // .46 rad and the patch is at most .26 across, so nothing reaches past .72, and
  // the direction is anchored to the sub-solar point so a patch is either in real
  // sunlight or not drawn at all.
  const sa=Math.atan2(l[1],l[0]);
  for(let j=0;j<5;j++){
   const a=sa+(hash(hb,60+j,91)-.5)*2.8;
   const rr=rad*(.14+.44*hash(hb,60+j,92));
   const bx=cx+Math.cos(a)*rr, by=cy+Math.sin(a)*rr, br=rad*(.10+.12*hash(hb,60+j,93));
   const al=lit(bx,by); if(al<.72)continue;
   ctx.save();ctx.translate(bx,by);ctx.rotate(hash(hb,60+j,94)*TAU);ctx.scale(1,.46);ctx.translate(-bx,-by);
   ctx.beginPath();ctx.arc(bx,by,br,0,TAU);
   ctx.fillStyle=css(blend(tint,[255,255,255],.78+.12*hash(hb,60+j,95)),.40*al);ctx.fill();ctx.restore();
  }
  return;""")

# ---- (b0) the four ring families, and the body's own tint comes from the same
#           entry so the planet and its ring are one object.
rep("""function massTint(m,p){""",
"""/* The four ring families of a ringed giant: [main tone, division tone, outer
 * tone, the body's own tint]. The reference is Saturn - a dark-gold ring on a tan
 * world - but the same code has to make a Neptune with an ice-blue ring and an ice
 * world with a pale cyan or violet one, so the family is picked once per body from
 * its phase and stays with it as it crosses regions. The body's tint comes out of
 * the same entry: a violet ring on a tan planet is a colour clash, not a Neptune. */
const RINGFAM=[
 {t:[218,182,106],d:[146,112, 58],o:[244,222,166],body:[206,176,140]}, // dark gold
 {t:[132,190,232],d:[ 70,128,188],o:[198,230,248],body:[150,170,200]}, // ice blue
 {t:[168,218,216],d:[100,168,176],o:[216,244,240],body:[176,204,200]}, // pale cyan
 {t:[180,156,218],d:[114, 92,166],o:[222,208,244],body:[186,174,212]}  // violet
];
const ringFam=h=>(h>>>0)%RINGFAM.length;
function massTint(m,p){""")

rep("  case 8:return blend([206,176,140],p.sun,.22);  // ringed giant",
    "  case 8:return blend(RINGFAM[ringFam((m.phase*4096)|0)].body,p.sun,.22); // ringed giant")

# ---- (b1) the ring itself: flat toned annuli, two gaps, the body's own colour.
rep("""/* The ring system of a ringed giant, split into the half behind the planet and
 * the half in front of it so the planet really does sit inside its rings. The two
 * halves are separate depth-sorted draws at q[2]+/-1, so the sort puts the far
 * half down first, the planet over it, and the near half on top. */
function ringHalf(m,q,rad,back){
 const hb=(m.phase*4096)|0, squash=.20+.30*hash(hb,7,61), roll=(hash(hb,8,62)-.5)*.7;
 const col=blend(massTint(m,currentPalette),[232,220,202],.30);
 const bands=[[1.10,1.32,.24],[1.44,1.96,.18]];
 queue.push({type:4,d:q[2]+(back?1:-1),alpha:1,fn:()=>{
  ctx.save();ctx.translate(q[0],q[1]);ctx.rotate(roll);ctx.scale(1,squash);
  const a0=back?Math.PI:0, a1=back?TAU:Math.PI;
  for(const b of bands){
   ctx.beginPath();
   ctx.arc(0,0,rad*b[1],a0,a1,false);
   ctx.arc(0,0,rad*b[0],a1,a0,true);
   ctx.closePath();
   ctx.fillStyle=css(col,b[2]);
   ctx.fill();
  }
  ctx.restore();
 }});
}""",
"""/* The ring system of a ringed giant, split into the half behind the planet and
 * the half in front of it so the planet really does sit inside its rings. The two
 * halves are separate depth-sorted draws at q[2]+/-1, so the sort puts the far
 * half down first, the planet over it, and the near half on top.
 *
 * FLAT GRAPHIC ART: three flat toned annuli, hard edges, two clean divisions -
 * nothing soft anywhere. Everything is drawn inside one rolled-and-squashed
 * frame, which is what makes it read as a ring seen at an angle rather than as an
 * ellipse sticker: the far half sits visibly higher on screen than the near half,
 * and both are the same projected annulus, so the planet is threaded through it.
 * The inner edge stops at 1.20 rad, well clear of the limb, so the gap between
 * the world and its rings stays open and the disc does not grow a rim. */
function ringHalf(m,q,rad,back){
 const hb=(m.phase*4096)|0;
 const squash=.24+.20*hash(hb,7,61), roll=(hash(hb,8,62)-.5)*.9;
 const pal=RINGFAM[ringFam(hb)];
 // [inner, outer, tone, alpha] in planet radii. The divisions at 1.46..1.55 and
 // 1.82..1.88 are the Cassini-style gaps; the thin outer band fades first.
 const bands=[[1.20,1.46,pal.t,.70],[1.55,1.82,pal.d,.60],[1.88,2.00,pal.o,.38]];
 queue.push({type:4,d:q[2]+(back?1:-1),alpha:1,fn:()=>{
  ctx.save();ctx.translate(q[0],q[1]);ctx.rotate(roll);ctx.scale(1,squash);
  const a0=back?Math.PI:0, a1=back?TAU:Math.PI;
  for(const b of bands){
   ctx.beginPath();
   ctx.arc(0,0,rad*b[1],a0,a1,false);
   ctx.arc(0,0,rad*b[0],a1,a0,true);
   ctx.closePath();
   ctx.fillStyle=css(b[2],b[3]);
   ctx.fill();
  }
  ctx.restore();
 }});
}""")

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("V26a planets2 applied:", len(s), "chars ->", out_p)
