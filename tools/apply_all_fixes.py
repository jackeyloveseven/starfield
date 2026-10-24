import os
import sys

def apply_fixes():
    target_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Detect line endings
    crlf = "\r\n" in content
    nl = "\r\n" if crlf else "\n"

    def rep(old_block, new_block, name=""):
        nonlocal content
        old_normalized = old_block.replace("\r\n", "\n").replace("\n", nl)
        new_normalized = new_block.replace("\r\n", "\n").replace("\n", nl)
        cnt = content.count(old_normalized)
        if cnt != 1:
            raise ValueError(f"Failed replacement for [{name}]: found {cnt} occurrences (expected 1)")
        content = content.replace(old_normalized, new_normalized, 1)
        print(f"Applied fix: [{name}]")

    # -------------------------------------------------------------
    # 1. bodies() - Back chunk horizon expansion & safe eviction
    # -------------------------------------------------------------
    old_bodies = """function bodies(){
 activeShips.length=0;
 const k0=Math.floor(camera.eye[2]/CHUNK);
 const backRadius = autoCamera ? 3 : 6;
 const fwdRadius = lowQuality ? 14 : 22;
 const active = [];
 for(let k=k0-backRadius;k<=k0+fwdRadius;k++)active.push(chunk(k));
 for(const [k] of chunks)if(k < k0 - backRadius - 2 || k > k0 + fwdRadius + 2)chunks.delete(k);"""

    new_bodies = """function bodies(){
 activeShips.length=0;
 const k0=Math.floor(camera.eye[2]/CHUNK);
 const backRadius = 8;
 const fwdRadius = lowQuality ? 14 : 24;
 const active = [];
 for(let k=k0-backRadius;k<=k0+fwdRadius;k++)active.push(chunk(k));
 for(const [k] of chunks)if(k < k0 - 12 || k > k0 + fwdRadius + 6)chunks.delete(k);"""

    rep(old_bodies, new_bodies, "bodies() chunk horizon and eviction hysteresis")

    # -------------------------------------------------------------
    # 2. bodies() - Frustum culling margin expansion for star halos & rings
    # -------------------------------------------------------------
    old_cull = """   const cullR=(m.kind===4)?Math.max(rad*4.5,320):(rad*2.2+20);"""
    new_cull = """   const cullR=(m.kind>=5&&m.kind<=7)?(rad*12+100):(m.kind===4?Math.max(rad*8,500):(m.w&&m.w.hasRings||m.kind===8?rad*4+80:rad*2.8+80));"""
    rep(old_cull, new_cull, "bodies() cullR margin")

    # -------------------------------------------------------------
    # 3. drawMass() - Smooth distant glow transition
    # -------------------------------------------------------------
    old_glow = """ if(rad < 8) glow([m.x, m.y, m.z], m.r * 1.15, tint, .65, 3.2);
 drawWorld(m, q, p, t, rad, tint);"""

    new_glow = """ const glowA = clamp((12 - rad) / 4, 0, 1);
 if(glowA > 0.01) glow([m.x, m.y, m.z], m.r * 1.15, tint, .65 * glowA, 3.2);
 drawWorld(m, q, p, t, rad, tint);"""
    rep(old_glow, new_glow, "drawMass() smooth glow transition")

    # -------------------------------------------------------------
    # 4. drawWorld() - Smooth continuous 2D/3D LOD cross-fade
    # -------------------------------------------------------------
    old_lod = """      // Three.js 3D Procedural Living Planet Engine (Islands, Oceans, Trees, Monuments, Birds & Whales)
      // Rendered with pixel-exact orthographic sizing and high-performance hardware filtering (rad >= 8.0)
      if (typeof LivingPlanetEngine !== 'undefined' && LivingPlanetEngine.enabled && rad >= 8.0 && typeof THREE !== 'undefined') {
        const offCanvas = LivingPlanetEngine.renderPlanet(m, rad, [lx, ly, lz]);
        if (offCanvas) {
          const drawD = LivingPlanetEngine.getDrawSize(rad);
          ctx.imageSmoothingEnabled = true;
          ctx.drawImage(offCanvas, cx - drawD * 0.5, cy - drawD * 0.5, drawD, drawD);
          return;
        }
      }"""

    new_lod = """      // Three.js 3D Procedural Living Planet Engine (Islands, Oceans, Trees, Monuments, Birds & Whales)
      // Rendered with continuous sub-pixel LOD cross-fading (rad >= 7.5) to eliminate any 1-frame distance pops
      let blended3DCanvas = null;
      if (typeof LivingPlanetEngine !== 'undefined' && LivingPlanetEngine.enabled && rad >= 7.5 && typeof THREE !== 'undefined') {
        const offCanvas = LivingPlanetEngine.renderPlanet(m, rad, [lx, ly, lz]);
        if (offCanvas) {
          const drawD = LivingPlanetEngine.getDrawSize(rad);
          const blendAlpha3D = clamp((rad - 7.5) / 3.0, 0, 1);
          if (blendAlpha3D >= 0.99) {
            ctx.imageSmoothingEnabled = true;
            ctx.drawImage(offCanvas, cx - drawD * 0.5, cy - drawD * 0.5, drawD, drawD);
            return;
          } else {
            blended3DCanvas = { canvas: offCanvas, drawD, alpha: blendAlpha3D };
          }
        }
      }"""
    rep(old_lod, new_lod, "drawWorld() LOD 3D check")

    old_world_end = """      ctx.restore();
    }
  });
}

/* Tanner Helland's blackbody approximation"""

    new_world_end = """      ctx.restore();
      if (blended3DCanvas && blended3DCanvas.alpha > 0.01) {
        ctx.save();
        ctx.globalAlpha = blended3DCanvas.alpha;
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(blended3DCanvas.canvas, cx - blended3DCanvas.drawD * 0.5, cy - blended3DCanvas.drawD * 0.5, blended3DCanvas.drawD, blended3DCanvas.drawD);
        ctx.restore();
      }
    }
  });
}

/* Tanner Helland's blackbody approximation"""
    rep(old_world_end, new_world_end, "drawWorld() LOD 3D overlay blend")

    # -------------------------------------------------------------
    # 5. drawTesseract() - 5D Hypercube & Gravitational Ribbons
    # -------------------------------------------------------------
    old_tess = """/* ---- the tesseract: a room, not a grid -------------------------------
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
 // The page turns: a paper-white bloom for the first half second, so the
 // room arrives as a change of medium rather than as an overlay fading in.
 if(tessT<.55){
  const fl=1-tessT/.55;
  ctx.fillStyle=css([255,253,248],fl*.62);ctx.fillRect(0,0,W,H);
 }
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
     const bw=Math.abs(h1[0]-h0[0])||1;
     const mx=(A[0]+Cq[0])*.5+(hash(seed+i,seed+j,9)-.5)*bw*.44,my=h0[1]*(.72)+h1[1]*.28;
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
}"""

    new_tess = """/* ---- the tesseract: a room, not a grid -------------------------------
 * Three walls in perspective, subdivided into windows, with the camera floating
 * inside. Cells share their edges - there is no seam to read as a broken grid,
 * and the mullions converge, which is the only cue that says "room".
 * Elevated 5D Spacetime: 4D hypercube lattice projection + flowing gravitational
 * timeline ribbons + quantum singularity metrics.
 * -------------------------------------------------------------------------*/
let tessT=0;
const TESS_DUR=9.0;
window.triggerTesseract = () => { tessT = 1e-4; if(typeof toast === 'function') toast('五维空间 · TESSERACT', 9); };

// Pre-computed 4D hypercube geometry (16 vertices, 32 edges)
const TESS_VERTS_4D = [];
for(let i=0; i<16; i++){
  TESS_VERTS_4D.push([
    (i & 1) ? 1 : -1,
    (i & 2) ? 1 : -1,
    (i & 4) ? 1 : -1,
    (i & 8) ? 1 : -1
  ]);
}
const TESS_EDGES_4D = [];
for(let i=0; i<16; i++){
  for(let j=i+1; j<16; j++){
    const d = (i ^ j);
    if(d === 1 || d === 2 || d === 4 || d === 8) {
      TESS_EDGES_4D.push([i, j]);
    }
  }
}

function drawTesseract(){
 const a=smooth(clamp(tessT/1.6,0,1))*smooth(clamp((TESS_DUR-tessT)/2.2,0,1));
 if(a<=.002)return;
 const p=currentPalette,cx=W*.5,cy=H*.47,f=Math.min(W,H)*1.10;
 const t=tessT;
 ctx.save();
 ctx.globalAlpha=a;
 ctx.fillStyle=css(blend(p.paper,[0,0,0],.90));ctx.fillRect(0,0,W,H);
 // The page turns: a paper-white bloom for the first half second, so the
 // room arrives as a change of medium rather than as an overlay fading in.
 if(tessT<.55){
  const fl=1-tessT/.55;
  ctx.fillStyle=css([255,253,248],fl*.62);ctx.fillRect(0,0,W,H);
 }
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
     const bw=Math.abs(h1[0]-h0[0])||1;
     const mx=(A[0]+Cq[0])*.5+(hash(seed+i,seed+j,9)-.5)*bw*.44,my=h0[1]*(.72)+h1[1]*.28;
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

 // -------------------------------------------------------------------------
 // 5D BULK GRAVITATIONAL TIMELINE RIBBONS (时间线引力弦束)
 // Infinite vertical & depth strands representing physicalized moments of time
 // -------------------------------------------------------------------------
 const numStrands = 7;
 for(let s=0; s<numStrands; s++){
  const sx = -1200 + s * 400 + Math.sin(t * 0.4 + s) * 35;
  const sz0 = 1000, sz1 = 2700;
  const pTop = pj(sx, -950, sz0), pBot = pj(sx, 950, sz0);
  const pDeepTop = pj(sx, -950, sz1), pDeepBot = pj(sx, 950, sz1);
  if(pTop && pBot && pDeepTop && pDeepBot){
   // Glowing timeline thread
   ctx.beginPath();
   ctx.moveTo(pTop[0], pTop[1]); ctx.lineTo(pDeepTop[0], pDeepTop[1]);
   ctx.moveTo(pBot[0], pBot[1]); ctx.lineTo(pDeepBot[0], pDeepBot[1]);
   ctx.strokeStyle = css(blend(p.ink, [120, 220, 255], 0.65), 0.22);
   ctx.lineWidth = 1.0;
   ctx.stroke();

   // Flowing temporal quantum nodes drifting along the time axis
   const timePhase = (t * 0.45 + s * 0.23) % 1.0;
   const curZ = sz0 + (sz1 - sz0) * timePhase;
   const curY = Math.sin(t * 1.2 + s * 1.5) * 500;
   const pNode = pj(sx, curY, curZ);
   if(pNode){
    const nodeR = Math.max(1.5, 4.5 * (f / pNode[2]));
    ctx.beginPath(); ctx.arc(pNode[0], pNode[1], nodeR, 0, TAU);
    ctx.fillStyle = css(blend(p.paper, [255, 235, 160], 0.85), 0.75);
    ctx.fill();
   }
  }
 }

 // -------------------------------------------------------------------------
 // 4D HYPERCUBE ROTATIONAL LATTICE (四维超立方体量子时空晶格投影)
 // Projected 4D vertices (+-1, +-1, +-1, +-1) rotating across X-W and Y-Z hyperplanes
 // -------------------------------------------------------------------------
 const S = 480 + 35 * Math.sin(t * 0.55);
 const rotXW = t * 0.28, rotYZ = t * 0.19;
 const c1 = Math.cos(rotXW), s1 = Math.sin(rotXW);
 const c2 = Math.cos(rotYZ), s2 = Math.sin(rotYZ);
 const projected4D = [];

 for(let i=0; i<16; i++){
  const v = TESS_VERTS_4D[i];
  const x0 = v[0] * S, y0 = v[1] * S, z0 = v[2] * S, w0 = v[3] * S;
  // 4D Plane Rotations
  const x1 = x0 * c1 - w0 * s1;
  const w1 = x0 * s1 + w0 * c1;
  const y1 = y0 * c2 - z0 * s2;
  const z1 = y0 * s2 + z0 * c2;
  // Perspective 4D to 3D bulk space
  const Dw = 1450;
  const factor = Dw / Math.max(300, Dw - w1);
  const X3D = x1 * factor;
  const Y3D = y1 * factor;
  const Z3D = 1850 + z1 * factor;
  projected4D.push(pj(X3D, Y3D, Z3D));
 }

 // Draw 32 4D hypercube lattice edges
 ctx.save();
 for(let e=0; e<TESS_EDGES_4D.length; e++){
  const [i0, i1] = TESS_EDGES_4D[e];
  const pA = projected4D[i0], pB = projected4D[i1];
  if(!pA || !pB) continue;
  const avgZ = (pA[2] + pB[2]) * 0.5;
  const edgeAlpha = clamp(1.0 - (avgZ - 1200) / 2200, 0.2, 0.95);
  ctx.beginPath();
  ctx.moveTo(pA[0], pA[1]);
  ctx.lineTo(pB[0], pB[1]);
  ctx.strokeStyle = css(blend(p.paper, [160, 240, 255], 0.78), edgeAlpha * 0.65);
  ctx.lineWidth = Math.max(0.8, 2.6 * (f / avgZ));
  ctx.stroke();
 }

 // Draw luminous vertex quantum nodes (16 Bulk singularity junctions)
 for(let i=0; i<projected4D.length; i++){
  const pN = projected4D[i];
  if(!pN) continue;
  const nodeR = Math.max(2.0, 5.5 * (f / pN[2]));
  const nodeG = ctx.createRadialGradient(pN[0], pN[1], 0, pN[0], pN[1], nodeR * 2.2);
  nodeG.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
  nodeG.addColorStop(0.4, css(blend(p.paper, [180, 230, 255], 0.8), 0.75));
  nodeG.addColorStop(1.0, 'rgba(100, 200, 255, 0)');
  ctx.beginPath();
  ctx.arc(pN[0], pN[1], nodeR * 2.2, 0, TAU);
  ctx.fillStyle = nodeG;
  ctx.fill();
 }
 ctx.restore();

 // -------------------------------------------------------------------------
 // 5D BULK METRIC TYPOGRAPHIC READOUT & AMBIENT AESTHETICS
 // -------------------------------------------------------------------------
 ctx.save();
 ctx.font = '11px monospace';
 ctx.fillStyle = css(blend(p.paper, [240, 250, 255], 0.8), 0.42 * a);
 ctx.fillText(`5D BULK METRIC · TESSERACT NEXUS  [τ = ${(t).toFixed(2)}s / ${TESS_DUR.toFixed(1)}s]`, 38, H - 36);
 ctx.fillStyle = css(blend(p.paper, [180, 225, 255], 0.7), 0.32 * a);
 ctx.fillText('∇_μ T^μν = 0  ·  BULK GRAVITATIONAL WAVE HARMONICS  ·  NON-EUCLIDEAN TIME LATTICE', 38, H - 20);
 ctx.restore();

 // the edge of the paper: a thin bright line where the walls meet
 ctx.strokeStyle=css(blend(p.ink,[255,255,255],.5),.18*a);
 ctx.lineWidth=1;
 ctx.restore();
}"""
    rep(old_tess, new_tess, "drawTesseract() 5D hypercube & timeline ribbons")

    # -------------------------------------------------------------
    # 6. playStringNote() - Acoustic bridge hill & solo violin resonance
    # -------------------------------------------------------------
    old_strings = """    // Play a Chamber String Note with Warm Expressive Vibrato & Slow Romantic Attack
    playStringNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);

      const filter = ac.createBiquadFilter();
      filter.type = 'lowpass';
      // Solo Violin Acoustic Formant & Bridge Hill (小提琴独奏高频穿透力与泛音共振)
      const filterCutoff = Math.max(1800, freq * 2.8 + velocity * 1800);
      filter.frequency.setValueAtTime(filterCutoff, t0);
      filter.Q.value = 2.4;

      const noteGain = ac.createGain();
      const peakGain = 0.12 * velocity;
      const attackTime = Math.min(0.18, Math.max(0.025, durationSeconds * 0.25));
      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + attackTime);
      noteGain.gain.setValueAtTime(peakGain * 0.90, t0 + Math.max(attackTime, durationSeconds * 0.8));
      noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.35); // smooth bow release

      // Dual detuned saw/triangle cluster for lush orchestral string section
      const osc1 = ac.createOscillator();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(freq, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(freq * 1.002, t0);

      // Natural violin/cello vibrato (5.4 Hz) with dynamic pitch-proportional depth
      const vibrato = ac.createOscillator();
      const vibGain = ac.createGain();
      vibrato.frequency.value = 5.4;
      vibGain.gain.value = freq * 0.008; // subtle vibrato depth
      vibrato.connect(vibGain);
      vibGain.connect(osc1.frequency);
      vibGain.connect(osc2.frequency);
      vibrato.start(t0 + 0.2); // vibrato begins after bow onset

      osc1.connect(filter);
      osc2.connect(filter);
      filter.connect(noteGain);
      noteGain.connect(this.masterGain);

      const stopTime = t0 + durationSeconds + 0.7;
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      vibrato.stop(stopTime);

      this.activeNodes.push(osc1, osc2, vibrato, noteGain);
    }"""

    new_strings = """    // Play a Chamber String Note with Warm Expressive Vibrato & Slow Romantic Attack
    // Elevated Solo Violin Physical Acoustics: Bridge Hill Formant (~2850 Hz), Wood Cavity Resonance (~480 Hz)
    // Dynamic Spiccato vs Legato Bow Articulation & Soloist Concert Hall Staging
    playStringNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);

      // 1. Acoustic Body Resonance & Formants:
      // Violin bridge hill formant (~2850 Hz) + Wood cavity resonance (~480 Hz)
      const bodyFilter = ac.createBiquadFilter();
      bodyFilter.type = 'peaking';
      bodyFilter.frequency.setValueAtTime(2850, t0);
      bodyFilter.Q.value = 3.0;
      bodyFilter.gain.setValueAtTime(6.0, t0); // +6dB bridge hill brilliance

      const warmFilter = ac.createBiquadFilter();
      warmFilter.type = 'peaking';
      warmFilter.frequency.setValueAtTime(480, t0);
      warmFilter.Q.value = 2.5;
      warmFilter.gain.setValueAtTime(3.5, t0); // +3.5dB warm wooden body resonance

      // Dynamic lowpass tracking string harmonic roll-off
      const lowpass = ac.createBiquadFilter();
      lowpass.type = 'lowpass';
      const cutoff = Math.min(12000, Math.max(2200, freq * 3.2 + velocity * 2200));
      lowpass.frequency.setValueAtTime(cutoff, t0);
      lowpass.Q.value = 1.8;

      // 2. Dynamic Bow Envelope (Articulated Spiccato vs Cantabile Legato)
      const isFast = durationSeconds < 0.35;
      const noteGain = ac.createGain();
      const peakGain = (isFast ? 0.15 : 0.12) * velocity;
      const attackTime = isFast ? 0.016 : Math.min(0.12, Math.max(0.04, durationSeconds * 0.22));

      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + attackTime);
      if (isFast) {
        // Fast Spanish Rondo spiccato attack & snappy release
        noteGain.gain.exponentialRampToValueAtTime(peakGain * 0.3, t0 + durationSeconds * 0.75);
        noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.12);
      } else {
        // Expressive lyrical Andante cantabile bow swell & silky release
        noteGain.gain.linearRampToValueAtTime(peakGain * 0.95, t0 + durationSeconds * 0.6);
        noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.38);
      }

      // 3. Multi-timbral rich string oscillators
      const osc1 = ac.createOscillator();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(freq, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'sawtooth';
      osc2.frequency.setValueAtTime(freq * 1.0018, t0);
      const g2 = ac.createGain();
      g2.gain.value = 0.55;
      osc2.connect(g2);

      const osc3 = ac.createOscillator();
      osc3.type = 'triangle';
      osc3.frequency.setValueAtTime(freq, t0);
      const g3 = ac.createGain();
      g3.gain.value = 0.35;
      osc3.connect(g3);

      // 4. Natural 5.4 Hz Violin Vibrato with realistic onset delay (120ms)
      const vibrato = ac.createOscillator();
      const vibGain = ac.createGain();
      vibrato.frequency.value = 5.4;
      const targetDepth = freq * (isFast ? 0.004 : 0.009);
      vibGain.gain.setValueAtTime(0.00001, t0);
      vibGain.gain.setValueAtTime(0.00001, t0 + 0.12);
      vibGain.gain.linearRampToValueAtTime(targetDepth, t0 + 0.35);

      vibrato.connect(vibGain);
      vibGain.connect(osc1.frequency);
      vibGain.connect(osc2.frequency);
      vibGain.connect(osc3.frequency);
      vibrato.start(t0 + 0.1);

      // 5. Soloist Stereo Placement & Acoustic Concert Hall Staging
      const panner = ac.createStereoPanner ? ac.createStereoPanner() : null;
      if (panner) {
        // Soloist placed at left-of-center (-0.14), bass strings at right (+0.18)
        panner.pan.value = midiNote >= 65 ? -0.14 : 0.18;
      }

      // Chain audio graph: oscillators -> filters -> noteGain -> panner -> masterGain
      osc1.connect(lowpass);
      g2.connect(lowpass);
      g3.connect(lowpass);
      lowpass.connect(bodyFilter);
      bodyFilter.connect(warmFilter);
      warmFilter.connect(noteGain);

      if (panner) {
        noteGain.connect(panner);
        panner.connect(this.masterGain);
      } else {
        noteGain.connect(this.masterGain);
      }

      const stopTime = t0 + durationSeconds + (isFast ? 0.3 : 0.8);
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      osc3.start(t0); osc3.stop(stopTime);
      vibrato.stop(stopTime);

      this.activeNodes.push(osc1, osc2, osc3, vibrato, noteGain);
    }"""
    rep(old_strings, new_strings, "playStringNote() solo violin acoustics & bridge hill")

    # -------------------------------------------------------------
    # 7. LivingPlanetEngine - Prewarming & Isolated Scratch Buffers
    # -------------------------------------------------------------
    old_prewarm = """    prewarmUpcoming(masses, travel) {
      if (!this.initialized) this.init();
      if (!this.initialized || !masses) return;
      for (let i = 0; i < masses.length; i++) {
        const m = masses[i];
        if (m && (m.w || m.kind === 1 || m.kind === 8 || m.kind === 6)) {
          const dz = m.z - travel;
          if (dz > 0 && dz < 28000) {
            const pId = this.getPlanetId(m);
            if (!this.planetCache.has(pId)) {
              this.getPlanetModel(m);
              break; // At most one per frame to keep FPS completely flat
            }
          }
        }
      }
    },"""

    new_prewarm = """    prewarmUpcoming(masses, travel) {
      if (!this.initialized) this.init();
      if (!this.initialized || !masses) return;
      for (let i = 0; i < masses.length; i++) {
        const m = masses[i];
        if (m && (m.w || m.kind === 1 || m.kind === 8 || m.kind === 6)) {
          const dz = m.z - travel;
          if (dz > 0 && dz < 68000) {
            const pId = this.getPlanetId(m);
            if (!this.planetCache.has(pId)) {
              this.getPlanetModel(m);
              break; // At most one per frame to keep FPS completely flat
            }
          }
        }
      }
    },"""
    rep(old_prewarm, new_prewarm, "LivingPlanetEngine.prewarmUpcoming() horizon expansion")

    old_get_model = """      const model = this.createProceduralPlanet(m, pId);
      model.pId = pId;
      this.planetsContainer.add(model.group);
      this.planetCache.set(pId, model);
      return model;"""

    new_get_model = """      const model = this.createProceduralPlanet(m, pId);
      model.pId = pId;
      this.planetsContainer.add(model.group);
      this.planetCache.set(pId, model);
      if (this.renderer && this.scene && this.camera) {
        try { this.renderer.compile(this.scene, this.camera); } catch(e) {}
      }
      return model;"""
    rep(old_get_model, new_get_model, "LivingPlanetEngine.getPlanetModel() background shader precompile")

    old_dispose = """    disposeModel(model) {
      if (!model || !model.group) return;
      this.planetsContainer.remove(model.group);
      model.group.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
          else obj.material.dispose();
        }
      });
    },

    // Renders the living planet to the offscreen canvas and returns the canvas
    renderPlanet(m, rad, lightDir) {
      if (!this.initialized) this.init();
      if (!this.initialized || !m) return null;

      const pId = this.getPlanetId(m);
      const model = this.getPlanetModel(m);
      if (!model) return null;

      this.ensureBufferSize(rad);

      const now = performance.now() * 0.001;
      const dt = Math.min(0.05, now - this.lastTime);
      this.lastTime = now;

      // Fast visibility switch with zero scene graph mutations:
      // ONLY make this planet's group visible; hide all other cached planets
      for (let i = 0; i < this.planetsContainer.children.length; i++) {
        const child = this.planetsContainer.children[i];
        child.visible = (child === model.group);
      }
      this.currentRenderedId = pId;

      // Update Sun light direction from Starfield light coordinates
      if (lightDir) {
        this.sunLight.position.set(lightDir[0] * 80, -lightDir[1] * 80, lightDir[2] * 80);
      }

      // Smooth axial rotation
      const rotSpd = 0.0028;
      model.terrainMesh.rotation.y += rotSpd;
      model.oceanMesh.rotation.y += rotSpd;
      if (model.treesGroup) model.treesGroup.rotation.y += rotSpd;
      if (model.monumentsGroup) model.monumentsGroup.rotation.y += rotSpd;
      if (model.cloudMesh) {
        model.cloudMesh.rotation.y += rotSpd * 1.35;
        model.cloudMesh.rotation.x += rotSpd * 0.12;
      }

      // Zero-allocation fauna animation via group rotation
      if (model.birdsGroup) {
        model.birdsGroup.rotation.y += dt * 0.38;
      }
      if (model.whalesGroup) {
        model.whalesGroup.rotation.y += dt * 0.14;
      }

      // Adaptive Sub-Frame LOD Throttling (游戏级错帧降频渲染):
      // rad < 35 (远距离行星): 每3帧刷新1次 WebGL，其余帧直接复用高质量画布，减少66%着色开销
      // 35 <= rad < 70 (中距离接近): 每2帧刷新1次 WebGL
      // rad >= 70 (近距离特写): 全速 1:1 实时 120 FPS 刷新
      const isSwitch = (this.currentRenderedId !== pId);
      const isBufferChange = (this._bufferResized === true);
      this._bufferResized = false;
      model.renderAge = (model.renderAge || 0) + 1;

      const refreshInterval = rad < 35 ? 3 : (rad < 70 ? 2 : 1);
      const shouldRenderWebGL = isSwitch || isBufferChange || (model.renderAge >= refreshInterval);

      if (shouldRenderWebGL) {
        model.renderAge = 0;
        this.renderer.render(this.scene, this.camera);
      }
      return this.canvas;
    }"""

    new_dispose = """    disposeModel(model) {
      if (!model || !model.group) return;
      this.planetsContainer.remove(model.group);
      model.group.traverse(obj => {
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) {
          if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
          else obj.material.dispose();
        }
      });
      if (model.canvas) {
        model.canvas.width = 1;
        model.canvas.height = 1;
        model.canvas = null;
        model.ctx = null;
      }
    },

    // Renders the living planet to its dedicated isolated scratch canvas and returns it
    // Guaranteed zero cross-planet buffer contamination and zero sub-frame flickering
    renderPlanet(m, rad, lightDir) {
      if (!this.initialized) this.init();
      if (!this.initialized || !m) return null;

      const pId = this.getPlanetId(m);
      const model = this.getPlanetModel(m);
      if (!model) return null;

      this.ensureBufferSize(rad);
      const sz = this.currentBufferSize || 512;

      // Ensure dedicated isolated 2D scratch canvas for this specific planet model
      if (!model.canvas) {
        model.canvas = document.createElement('canvas');
        model.canvas.width = sz;
        model.canvas.height = sz;
        model.ctx = model.canvas.getContext('2d', { alpha: true });
      } else if (model.canvas.width !== sz || model.canvas.height !== sz) {
        model.canvas.width = sz;
        model.canvas.height = sz;
      }

      const now = performance.now() * 0.001;
      const dt = Math.min(0.05, now - this.lastTime);
      this.lastTime = now;

      // Fast visibility switch with zero scene graph mutations:
      // ONLY make this planet's group visible; hide all other cached planets
      for (let i = 0; i < this.planetsContainer.children.length; i++) {
        const child = this.planetsContainer.children[i];
        child.visible = (child === model.group);
      }

      // Update Sun light direction from Starfield light coordinates
      if (lightDir) {
        this.sunLight.position.set(lightDir[0] * 80, -lightDir[1] * 80, lightDir[2] * 80);
      }

      // Smooth axial rotation
      const rotSpd = 0.0028;
      model.terrainMesh.rotation.y += rotSpd;
      model.oceanMesh.rotation.y += rotSpd;
      if (model.treesGroup) model.treesGroup.rotation.y += rotSpd;
      if (model.monumentsGroup) model.monumentsGroup.rotation.y += rotSpd;
      if (model.cloudMesh) {
        model.cloudMesh.rotation.y += rotSpd * 1.35;
        model.cloudMesh.rotation.x += rotSpd * 0.12;
      }

      // Zero-allocation fauna animation via group rotation
      if (model.birdsGroup) {
        model.birdsGroup.rotation.y += dt * 0.38;
      }
      if (model.whalesGroup) {
        model.whalesGroup.rotation.y += dt * 0.14;
      }

      // Adaptive Sub-Frame LOD Throttling:
      const isSwitch = (this._lastRenderedId !== pId);
      this._lastRenderedId = pId;
      this.currentRenderedId = pId;
      const isBufferChange = (this._bufferResized === true);
      this._bufferResized = false;
      model.renderAge = (model.renderAge || 0) + 1;

      const refreshInterval = rad < 35 ? 3 : (rad < 70 ? 2 : 1);
      const shouldRenderWebGL = isSwitch || isBufferChange || (model.renderAge >= refreshInterval) || !model.hasRendered;

      if (shouldRenderWebGL) {
        model.renderAge = 0;
        model.hasRendered = true;
        this.renderer.render(this.scene, this.camera);
        model.ctx.clearRect(0, 0, sz, sz);
        model.ctx.drawImage(this.canvas, 0, 0);
      }
      return model.canvas;
    }"""
    rep(old_dispose, new_dispose, "LivingPlanetEngine per-planet isolated canvas")

    # -------------------------------------------------------------
    # 8. Keyboard '5' key binding for Tesseract
    # -------------------------------------------------------------
    old_key = """ else if(e.key==='4')FleetFormations.set(3);
 else if(e.key.toLowerCase()==='f')FleetFormations.cycle();"""

    new_key = """ else if(e.key==='4')FleetFormations.set(3);
 else if(e.key==='5'){if(window.triggerTesseract)window.triggerTesseract();}
 else if(e.key.toLowerCase()==='f')FleetFormations.cycle();"""
    rep(old_key, new_key, "Key '5' binding for Tesseract")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("ALL FIXES APPLIED SUCCESSFULLY TO starfield.html!")

if __name__ == "__main__":
    apply_fixes()
