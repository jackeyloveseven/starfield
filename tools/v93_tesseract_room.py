"""V93: the tesseract as a room, third attempt.

The two failures were both a corridor of flat cards. A card wall leaves black
seams between cells, and seams read as a broken grid. A room has no seams: three
walls meeting at corners, subdivided in perspective, each cell a window with a
mullion. That is the difference this patch makes.

  back wall   z = 3000      x in [-2400, 2400]   y in [-1500, 1500]
  side walls  x = +-2400    z in [ 600, 3000]

The camera floats inside it with a slow sway and a slower yaw, so the walls
converge and the mullions are not parallel - the one cue that says "room" rather
than "overlay".

Each window is pale paper with the region's light in its lower half; the
mullions are the dark of the room. It is the same idea as v88 - windows holding
moments - but now the frames are architecture.

Run:  python -I v93_tesseract_room.py <in.html> <out.html>
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


TESS = r"""/* ---- the tesseract: a room, not a grid -------------------------------
 * Three walls in perspective, subdivided into windows, with the camera floating
 * inside. Cells share their edges - there is no seam to read as a broken grid,
 * and the mullions converge, which is the only cue that says "room".
 * -------------------------------------------------------------------------*/
let tessT=0;
const TESS_DUR=9.0;
function drawTesseract(){
 const a=smooth(clamp(tessT/1.6,0,1))*smooth(clamp((TESS_DUR-tessT)/2.2,0,1));
 if(a<=.002)return;
 const p=currentPalette,cx=W*.5,cy=H*.47,f=Math.min(W,H)*1.10;
 const t=tessT;
 ctx.save();
 ctx.globalAlpha=a;
 ctx.fillStyle=css(blend(p.paper,[0,0,0],.90));ctx.fillRect(0,0,W,H);
 // the camera floats: a slow sway, a slower yaw. Never a walk - the room must
 // stay a room for the eight seconds it is on screen.
 const yaw=Math.sin(t*.27)*.115, pit=Math.sin(t*.19)*.055;
 const ox=Math.sin(t*.41)*95, oy=Math.sin(t*.29)*62, oz=Math.sin(t*.23)*130;
 const cyw=Math.cos(yaw),syw=Math.sin(yaw),cp=Math.cos(pit),sp=Math.sin(pit);
 const pj=(x,y,z)=>{
  const X=x-ox,Y=y-oy,Z=z-oz;
  const X2=X*cyw-Z*syw, Z2=X*syw+Z*cyw;
  const Y2=Y*cp-Z2*sp,  Z3=Y*sp+Z2*cp;
  if(Z3<160)return null;
  const k=f/Z3;
  return [cx+X2*k,cy-Y2*k,Z3];
 };
 const mull=blend(p.paper,[0,0,0],.55);
 const lerp3=(A,B,t0)=>[A[0]+(B[0]-A[0])*t0,A[1]+(B[1]-A[1])*t0,A[2]+(B[2]-A[2])*t0];
 // A wall given by its four corners (u0v0,u1v0,u1v1,u0v1) and a cell count.
 const wall=(C,nu,nv,seed)=>{
  for(let j=0;j<nv;j++)for(let i=0;i<nu;i++){
   const u0=i/nu,u1=(i+1)/nu,v0=j/nv,v1=(j+1)/nv;
   const P=(uu,vv)=>{
    const top=lerp3(C[0],C[1],uu), bot=lerp3(C[3],C[2],uu);
    return lerp3(top,bot,vv);
   };
   const A=pj(...P(u0,v0)),B=pj(...P(u1,v0)),Cq=pj(...P(u1,v1)),D=pj(...P(u0,v1));
   if(!A||!B||!Cq||!D)continue;
   const minY=Math.min(A[1],B[1],Cq[1],D[1]),maxY=Math.max(A[1],B[1],Cq[1],D[1]);
   if(maxY<-20||minY>H+20)continue;
   const minX=Math.min(A[0],B[0],Cq[0],D[0]),maxX=Math.max(A[0],B[0],Cq[0],D[0]);
   if(maxX<-20||minX>W+20)continue;
   const hj=hash(seed+i,seed+j,seed);
   // styles, not rawStyles: the latter holds hex strings, and blend() on a
   // string yields NaN, which css() renders as pure blue.
   const st=styles[(Math.abs(i*3+j*5+seed)|0)%styles.length];
   const light=st?blend([250,248,243],st.sun,.10):[250,248,243];
   const g=ctx.createLinearGradient(0,minY,0,maxY);
   // A wall of identical white panes is a lightbox. The windows are given a
   // spread of brightness first, then some of them are given a view.
   const glow=.24+.76*Math.pow(hj,1.4);
   const warm=blend(light,st?st.sun:[255,255,255],.55);
   g.addColorStop(0,css(blend(light,[255,255,255],.30),.42*glow));
   g.addColorStop(.58,css(blend(light,warm,.55),.82*glow));
   g.addColorStop(1,css(blend(light,[255,255,255],.40),.97*glow));
   ctx.beginPath();
   ctx.moveTo(A[0],A[1]);ctx.lineTo(B[0],B[1]);ctx.lineTo(Cq[0],Cq[1]);ctx.lineTo(D[0],D[1]);
   ctx.closePath();
   ctx.fillStyle=g;ctx.fill();
   // the mullion: dark, and thick enough to read as a frame at any depth
   const near=clamp(1-(A[2]+Cq[2])*.5/3200,0,1);
   // Inside the window: a horizon line, and sometimes a world, drawn between
   // the quad's edges so they keep the wall's perspective.
   if(hj<.72){
    const L2=(q)=>[A[0]+(D[0]-A[0])*q,A[1]+(D[1]-A[1])*q];
    const R2=(q)=>[B[0]+(Cq[0]-B[0])*q,B[1]+(Cq[1]-B[1])*q];
    const hy=.52+.22*hash(seed+j,seed+i,7);
    const h0=L2(hy),h1=R2(hy);
    ctx.strokeStyle=css(blend(mull,[0,0,0],.25),.20+.16*glow);
    ctx.lineWidth=Math.max(.7,2.0*(f/((A[2]+Cq[2])*.5)));
    ctx.beginPath();ctx.moveTo(h0[0],h0[1]);ctx.lineTo(h1[0],h1[1]);ctx.stroke();
    if(hj<.40){
     const mx=(A[0]+Cq[0])*.5,my=h0[1]*(.72)+h1[1]*.28;
     const rr=Math.max(1.5,Math.hypot(h1[0]-h0[0],h1[1]-h0[1])*(.07+.05*hash(seed+i,seed+j,3)));
     ctx.fillStyle=css(blend(mull,[0,0,0],.35),.62);
     ctx.beginPath();ctx.arc(mx,my,rr,0,TAU);ctx.fill();
    }
   }
   ctx.strokeStyle=css(mull,.55+.35*near);
   ctx.lineWidth=Math.max(1.0,3.4*(f/((A[2]+Cq[2])*.5)));
   ctx.stroke();
  }
 };
 // back wall, then the two sides: right first, so the corner joint reads
 // 1,700 wide and 2,800 deep puts all three walls inside the frustum; at
 // 2,400 the sides sat exactly on the frame edge and read as two stripes.
 wall([[-1700,-1000,2800],[1700,-1000,2800],[1700,1000,2800],[-1700,1000,2800]],6,4,1);
 wall([[1700,-1000,2800],[1700,-1000,900],[1700,1000,900],[1700,1000,2800]],5,4,2);
 wall([[-1700,-1000,900],[-1700,-1000,2800],[-1700,1000,2800],[-1700,1000,900]],5,4,3);
 // the edge of the paper: a thin bright line where the walls meet
 ctx.strokeStyle=css(blend(p.ink,[255,255,255],.5),.18*a);
 ctx.lineWidth=1;
 ctx.restore();
}
function paperFinish(){"""
rep("function paperFinish(){", TESS)

OLD = """  sound.setTension(false);
  toast('重返浩瀚深空 · DEEP SPACE RESUMED', 5);"""
NEW = """  sound.setTension(false);
  toast('重返浩瀚深空 · DEEP SPACE RESUMED', 5);
  // Once in a while the flight comes out the other side of the page.
  if(hash(cycle,707)<.45){tessT=1e-4;toast('五维空间 · TESSERACT',9);}"""
rep(OLD, NEW)

OLD2 = """ cockpitBlend+=((cockpitMode?1:0)-cockpitBlend)*Math.min(1,realDt*3.2);"""
NEW2 = """ if(tessT>0){tessT+=realDt;drawTesseract();if(tessT>TESS_DUR)tessT=0;}
 cockpitBlend+=((cockpitMode?1:0)-cockpitBlend)*Math.min(1,realDt*3.2);"""
rep(OLD2, NEW2)

OLD3 = """   updateDirector(step);updateWind(step);updateGravity();updateBirds(step);updateCapture(step);updateSling(step);updateParticles(step);updatePoem(step);Narrator.update(step);"""
NEW3 = """   updateDirector(step);updateWind(step);updateGravity();updateBirds(step);updateCapture(step);updateSling(step);updateParticles(step);updatePoem(step);Narrator.update(step);
   if(tessT>0){tessT+=step;if(tessT>TESS_DUR)tessT=0;}"""
rep(OLD3, NEW3)

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V93 written:", len(src), "chars")
