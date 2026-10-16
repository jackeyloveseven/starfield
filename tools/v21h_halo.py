"""v21h_halo -- a distant supernova, and the halo of light it throws.

The user: "还可以把远处超新星照射的光线做一下照射光晕的效果."
(add the illumination-halo effect of the light from a distant supernova)

WHAT A SUPERNOVA SHOULD LOOK LIKE HERE
The reference the user pointed at twice is flat graphic art, not a render: broad
bands of near-flat colour, crisp boundaries, a clean geometric shadow, one thin
sharp photon ring, and no softness anywhere. So the supernova's SHAPES are flat
and hard-edged - twelve tapered spokes at a single alpha each, two broken shock
arcs of constant width, one thin expanding shell - and only its LIGHT is soft,
because light is the one thing that actually does fall off. A radial blob with
a gradient along every spoke is what reads as "blurred pixels"; that is the
complaint being answered.

WHERE IT LIVES
On the sky dome, beside the nebulae and the bright stars, because a supernova is
not an encounter you fly past - it is a light in the deep field, and on the dome
it can never parallax. Its direction is drawn IN THE BAND PLANE (BAND_BASIS),
the same plane the band stars use and for the same reason: the director spends
most of its time looking at that plane, so the light is seen instead of burning
behind the camera.

WHICH MECHANISM CARRIES IT
A direct draw at the end of drawSky(), the same layer the nebulae, the bright
stars and the band already print on. Type 3 glow() cannot do it: glow() is a
radial gradient by construction and the whole point here is flat shapes with
hard edges. The queue's type 4 (screen-space composite) also works - pushed with
d = 1e9 it sorts in front of every mass in the chunk, drawHole included, since a
horizon is queued at its own q[2]. The sky layer was chosen over it because the
supernova is a dome object like the nebulae and the bright stars, it belongs
under the scene rather than inside the depth sort, and it needs no closure. The
one thing it gives up is being drawn before deepfield()'s corridor bloom and the
craft shadows, which is where a light in the deep field belongs.

DOES IT LIGHT THE NEBULA, AND HOW
Yes, and not by painting over it. novaGas() raises the nebula's OWN alpha in the
nebulae loop, weighted by the angular distance from the supernova measured in
units of that nebula's own angular radius, so a big nebula lights over its whole
face and a small one only near the source. A halo drawn on top of the texture
would grey the dust lanes the nebula is made of, which is the opposite of
lighting it. The soft additive halo in drawNova() is the light in the air, and
lands on top of the now-brighter gas.

HOW RARE
One ignition every six chunks of travel (~178s at cruise), phased by the seed,
with the light standing for 58s - so a supernova is in the sky about a third of
the time. Rarer than a star system (one chunk in three), about as common as the
ink well (one chunk in seven), and on a schedule rather than a die roll, which is
the argument the horizon line already makes for itself.

NOTHING INTEGRATES
The event's age is a pure function of travel, so a seek lands on the same sky a
flight of the same length would have made, and neither frame() nor seek() needs
a new update call or any new state.

Reads the artwork, asserts each replaced string occurs exactly once, writes a
working copy. Two explicit paths are required: a bare run must not be able to
touch the shared original.

Run:  python -I v21h_halo.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v21h_halo.py <in.html> <out.html>")
src_p, out_p = sys.argv[1], sys.argv[2]
s = open(src_p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:160]))
    s = s.replace(a, b, n)


# ---- 1. The sky knows whether a supernova is standing in it -----------------
# drawSky() computes the event once, at the top, so the nebulae loop and the
# light itself read the same state. Pure function of travel: no per-frame state.
rep(
    "function drawSky(){\n const p=currentPalette,g=ctx.createLinearGradient(0,0,0,H);",
    "function drawSky(){\n"
    " const p=currentPalette,nova=novaState(),g=ctx.createLinearGradient(0,0,0,H);",
)

# ---- 2. The nebula it stands in brightens --------------------------------
# The nebula's own alpha, not a veil over it. The .78 ceiling was tuned for
# unlit gas and it ate the first version of this gain whole - a lit nebula has to
# be allowed to print harder, in proportion to the gain. It stops short of 1: the
# texture's own alpha mask is what gives the gas a body, and full opacity erases it.
rep(
    "   const al=clamp(n.alpha*wash,0,.78);",
    "   const ng=novaGas(n,nova),al=clamp(n.alpha*wash*ng,0,.78+(ng-1)*.16);",
)

# ---- 3. The light itself, at the end of drawSky() ------------------------
# After the band and after the region's own sun wash, so the supernova is the
# brightest thing in the sky; before bodies(), because the sky is drawn first.
NOVA = """ drawNova(nova);
}

/* ---- Distant supernovae ---------------------------------------------------
 * A supernova is not an encounter: it is a light in the deep field, so it lives
 * on the sky dome beside the nebulae and the bright stars, where it can never
 * parallax or be flown past. Its SHAPES are flat and hard-edged - a fan of
 * tapered spokes, two broken shock arcs, one thin expanding shell - because
 * that is the art direction the horizon already set: flat toned bands with
 * crisp boundaries and a thin sharp ring, never a soft radial blob. Only its
 * LIGHT is soft, and that is the part the nebula gets to feel.
 *
 * Nothing here integrates: the event's age is a pure function of travel, so a
 * seek lands on the same sky a flight of the same length would have made and
 * neither frame() nor seek() carries any new state.
 * -------------------------------------------------------------------------*/
const NOVA_CHUNKS=6, NOVA_SPAN=NOVA_CHUNKS*CHUNK, NOVA_LIFE=58;
function novaState(){
 // Ignition on a schedule, not a die roll - the same argument the horizon's
 // every-seventh chunk makes for itself. One every six chunks is ~178s at
 // cruise: rarer than a star system (one chunk in three), about as common as
 // the ink well (one in seven), and its light stands for a minute afterwards.
 // Phased by the seed, so two seeds do not print the same sky.
 const ph=hash(730)*NOVA_SPAN, ev=Math.floor((travel+ph)/NOVA_SPAN), age=(travel+ph-ev*NOVA_SPAN)/SPEED;
 if(age>NOVA_LIFE)return null;
 // A direction IN THE BAND PLANE, like the band stars and for their reason:
 // the director spends most of its time looking at that plane, so the light is
 // seen instead of burning behind the camera. The normal offset keeps it off
 // the ribbon itself.
 const [BU,BV,BN]=BAND_BASIS,a=hash(ev,731)*TAU,ca=Math.cos(a),sa=Math.sin(a),g=(hash(ev,732)-.5)*.40;
 let x=BU[0]*ca+BV[0]*sa+BN[0]*g,y=BU[1]*ca+BV[1]*sa+BN[1]*g,z=BU[2]*ca+BV[2]*sa+BN[2]*g;
 const n=Math.hypot(x,y,z)||1;x/=n;y/=n;z/=n;
 const q=skyPoint([x,y,z]);if(!q)return null;
 const w=lensWarp(q[0],q[1]);
 // One envelope, shared by the shapes, the halo and the gas it lights, so the
 // whole event comes up in a second and goes out over nine.
 return {age,u:age/NOVA_LIFE,x:w[0],y:w[1],dir:[x,y,z],spin:a,
         life:smooth(age/.9)*smooth((NOVA_LIFE-age)/9)};
}
/* How much this nebula is lit by a supernova standing in it. The angular
 * distance is measured in units of the nebula's OWN angular radius, so a big
 * wash lights over its whole face and a small one only near the source. */
function novaGas(n,nova){
 if(!nova||nova.life<=0)return 1;
 const d=n.x*nova.dir[0]+n.y*nova.dir[1]+n.z*nova.dir[2];
 const ang=Math.acos(clamp(d,-1,1))/Math.max(.02,n.size);
 return 1+1.05*Math.exp(-ang*ang*.50)*nova.life;
}
/* A star's light does not take the region's palette - drawMass() settles that
 * for the suns - so the supernova carries its own colour: hot, and blue. */
const NOVA_TINT=blend(blackbody(13000),[255,255,255],.42);
function drawNova(n){
 if(!n||n.life<=0)return;
 const S=Math.min(W,H);
 if(n.x<-S||n.x>W+S||n.y<-S||n.y>H+S)return;
 const x=n.x,y=n.y,u=n.u,life=n.life,fl=Math.max(0,1-n.age/2.0)**2;
 ctx.save();
 // The LIGHT is soft - it is the one thing here that physically falls off - and
 // it is ADDED, because the paper is dark and paint would grey the gas instead
 // of lighting it. Everything below it is a flat shape at one alpha.
 ctx.globalCompositeOperation='lighter';
 const halo=S*(.18+.32*smooth(n.age/7));
 const hg=ctx.createRadialGradient(x,y,0,x,y,halo);
 hg.addColorStop(0,css(NOVA_TINT,.26*life));
 hg.addColorStop(.22,css(NOVA_TINT,.10*life));
 hg.addColorStop(1,css(NOVA_TINT,0));
 ctx.fillStyle=hg;ctx.fillRect(x-halo,y-halo,halo*2,halo*2);fillPx+=halo*halo*4;
 // The ignition: a disc for a couple of seconds, never a full-frame white fill
 // - the capture bloom was cut down to a radial for exactly that reason.
 if(fl>.004){
  const fr=S*.30,fg=ctx.createRadialGradient(x,y,0,x,y,fr);
  fg.addColorStop(0,css(NOVA_TINT,.22*fl));fg.addColorStop(.4,css(NOVA_TINT,.06*fl));fg.addColorStop(1,css(NOVA_TINT,0));
  ctx.fillStyle=fg;ctx.fillRect(x-fr,y-fr,fr*2,fr*2);
 }
 // From here on: flat shapes, source-over, one alpha each, hard edges. Drawn
 // over the gas they must not average with it - that average, not the pixel
 // grid, is what the eye reads as blur.
 ctx.globalCompositeOperation='source-over';
 const rot=n.spin+time*.017,len=S*(.30+.34*smooth(n.age/8))*(1-.45*u),spoke=blend(NOVA_TINT,[255,255,255],.62);
 for(let i=0;i<12;i++){
  const long=i%2===0,ang=rot+i/12*TAU,ca=Math.cos(ang),sa=Math.sin(ang);
  const r0=long?5:3.5,r1=len*(long?1:.32),hw=long?2.1:1.3;
  ctx.beginPath();
  ctx.moveTo(x+ca*r0-sa*hw,y+sa*r0+ca*hw);
  ctx.lineTo(x+ca*r1,y+sa*r1);
  ctx.lineTo(x+ca*r0+sa*hw,y+sa*r0-ca*hw);
  ctx.closePath();
  ctx.fillStyle=css(spoke,(long?.80:.54)*life*(1-.35*u));ctx.fill();
 }
 // The shock: two thin shells, broken into arcs, expanding and thinning. This is
 // the piece's photon ring printed flat - no falloff along the stroke. The pair
 // stays around the source (a shell that runs off the frame stops reading as a
 // ring at all) and the arcs are broken because a whole circle reads as a lens
 // artefact rather than as a printed plate.
 const rr=S*(.05+.26*smooth(n.age/24));
 ctx.lineWidth=1.8;
 for(let i=0;i<2;i++){
  const r=rr*(1+i*.46),al=(.86-.42*u)*(1-i*.34)*life;
  if(al<.012)continue;
  ctx.strokeStyle=css(blend(NOVA_TINT,[255,255,255],.72),al);
  for(let k=0;k<3;k++){const a0=rot*1.7+k*TAU/3+i*.55;ctx.beginPath();ctx.arc(x,y,r,a0,a0+1.02);ctx.stroke();}
 }
 // The core: a small hard disc. The post pass blooms it for us; drawing a soft
 // core here as well would double the one thing that has to stay a point.
 ctx.fillStyle=css([255,255,255],.97*life);
 ctx.beginPath();ctx.arc(x,y,Math.max(1.4,S*.0042*(.8+1.5*smooth(n.age/.35))),0,TAU);ctx.fill();
 ctx.restore();
}
"""
rep(
    "  const glow=ctx.createRadialGradient(x,y,0,x,y,r);glow.addColorStop(0,css(p.sun,intensity));"
    "glow.addColorStop(.38,css(p.sun,intensity*.46));glow.addColorStop(1,css(p.sun,0));"
    "ctx.fillStyle=glow;ctx.fillRect(0,0,W,H);\n }\n}\nfunction paperFinish(){",
    "  const glow=ctx.createRadialGradient(x,y,0,x,y,r);glow.addColorStop(0,css(p.sun,intensity));"
    "glow.addColorStop(.38,css(p.sun,intensity*.46));glow.addColorStop(1,css(p.sun,0));"
    "ctx.fillStyle=glow;ctx.fillRect(0,0,W,H);\n }\n" + NOVA + "function paperFinish(){",
)

# ---- 4. A read-only handle on the event, beside the other diagnostics ----
# New line inside the frozen surface: the shot harness and a probe can then ask
# whether a supernova is up, instead of guessing a seek that lands on one.
rep(
    " cameras:Object.freeze(LENSES.map(p=>Object.freeze({name:p.name,en:p.en}))),",
    " nova:()=>{const n=novaState();return n?{age:+n.age.toFixed(1),life:+n.life.toFixed(3),"
    "x:Math.round(n.x),y:Math.round(n.y)}:null;},\n"
    " cameras:Object.freeze(LENSES.map(p=>Object.freeze({name:p.name,en:p.en}))),",
)

open(out_p, "w", encoding="utf-8", newline="").write(s)
print("wrote %s (%d bytes)" % (out_p, len(s)))
