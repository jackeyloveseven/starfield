"""V16: a real black hole. Offscreen WebGL, composited into the Canvas2D scene.

The user asked for a 1:1 match and pointed at sayed1145/glsl-black-hole (MIT,
Copyright (c) 2026 sayed1145). Its geodesic physics is ported here with the
copyright notice retained; the pipeline around it is not - theirs is 5 passes
with MRT bloom, this is one sprite inside an existing Canvas2D scene.

WHY THIS WORKS, and why it is much less work than it looked: their own composite
does NOT lens a background star field. It draws procedural stars and masks them
out inside the shadow:

    float holeMask = smoothstep(0.093, 0.102, length(p));
    col += stars(uv) * holeMask;

So the "distortion" is entirely the accretion disc's multiple images, not bent
starlight. That means the sprite can be TRANSPARENT everywhere except the disc
and the shadow, and the scene's own star field shows through - no seam to match,
no doubled stars.

The one number that makes the sprite resolution-independent: in their emission
pass `radius = length(p) * 27.5` is in Schwarzschild radii, and the shadow sits at
radius 2.608, so the shadow is at length(p) = 0.0949 regardless of anything else.

Physics ported verbatim in structure: the central-force null geodesic
    a = -1.5 * h^2 * p / r^5        (i.e. -1.5 h^2 rhat / r^4), rs = 1
integrated kick-drift-kick with an adaptive step, recording up to three crossings
of the equatorial plane. The radial radiance tables are theirs, unmodified.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:150]))
    s = s.replace(a, b, n)


# ---- 1. the WebGL black hole, defined next to blackbody() ----
ANCHOR = "function drawHole(m,q,p,t,rad){"
GL = r"""/* A real black hole, raymarched.
 *
 * Physics ported from sayed1145/glsl-black-hole (MIT License,
 * Copyright (c) 2026 sayed1145) - the central-force null-geodesic form
 * a = -1.5 h^2 rhat / r^4 with rs = 1, kick-drift-kick, adaptive step, and up to
 * three equatorial-plane crossings so the disc's lensed images come out of the
 * integration rather than being drawn in by hand. The radial radiance tables are
 * theirs, unmodified. The five-pass pipeline around it is not: this is one
 * sprite composited into an existing Canvas2D scene, so it renders transparent
 * everywhere except the disc, and the scene's own star field shows through.
 *
 * It does NOT lens the background, and neither does theirs - their composite
 * masks a procedural star field out inside the shadow rather than bending it.
 * The distortion is the disc's multiple images, which is what the eye reads. */
const GLSL_HOLE = `#version 300 es
precision highp float;
uniform vec2 uRes;
uniform float uTilt,uIncl,uScale,uInner,uTime;
uniform vec3 uTint;
out vec4 fragColor;
const float TAU=6.28318530718;
const float OBSERVER=80.0, DISCOUT=34.0, CRIT=2.598;
vec3 accel(vec3 p,float h2){float r2=dot(p,p);return -1.5*h2*p/(r2*r2*sqrt(r2));}
float hash21(vec2 p){vec3 q=fract(vec3(p.xyx)*vec3(0.1031,0.1030,0.0973));
 q+=dot(q,q.yzx+33.33);return fract((q.x+q.y)*q.z);}
float noiseP(vec2 p,float period){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 vec2 i0=vec2(i.x,mod(i.y,period)),i1=vec2(i.x,mod(i.y+1.0,period));
 return mix(mix(hash21(i0),hash21(i0+vec2(1,0)),f.x),
            mix(hash21(i1),hash21(i1+vec2(1,0)),f.x),f.y);}
float fbmP(vec2 p,float period,float footprint){float n=0.0,amp=0.52;
 for(int i=0;i<5;i++){float aa=1.0-smoothstep(0.65,2.1,footprint);
  n+=amp*mix(0.5,noiseP(p,period),aa);p*=2.0;period*=2.0;footprint*=2.0;amp*=0.49;}
 return n;}
const int PROFILE_N=18;
const float RADII[PROFILE_N]=float[PROFILE_N](1.600000,1.850000,2.100000,2.400000,
 2.700000,3.000000,3.400000,3.800000,4.300000,4.900000,5.600000,6.500000,7.600000,
 9.000000,10.700000,12.800000,15.500000,19.000000);
const vec3 UPPER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.255777,0.166983,0.130913),vec3(0.137799,0.112648,0.095081),
 vec3(0.264506,0.176011,0.157152),vec3(0.454691,0.277004,0.215472),
 vec3(0.804536,0.516623,0.372846),vec3(1.150769,0.757494,0.551068),
 vec3(1.673280,1.122596,0.815232),vec3(1.971796,1.355241,0.988191),
 vec3(1.381316,0.953994,0.710846),vec3(1.212427,0.769973,0.538510),
 vec3(0.632655,0.452315,0.354578),vec3(0.504023,0.315987,0.231414),
 vec3(0.303187,0.201846,0.163637),vec3(0.012821,0.011026,0.008847),
 vec3(0.001271,0.001093,0.000877),vec3(0.000438,0.000377,0.000303),
 vec3(0.000001,0.000000,0.000000),vec3(0.000000,0.000000,0.000000));
const vec3 LOWER[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.000000,0.000000,0.000000),vec3(0.233461,0.154232,0.134631),
 vec3(0.392270,0.241803,0.181831),vec3(0.553336,0.335322,0.237910),
 vec3(0.720745,0.450136,0.316339),vec3(0.930359,0.597947,0.426111),
 vec3(1.302152,0.882694,0.646073),vec3(1.496130,1.043103,0.770311),
 vec3(1.466698,1.060739,0.801137),vec3(1.110652,0.758425,0.554937),
 vec3(0.974833,0.643935,0.452933),vec3(0.489304,0.319002,0.232886),
 vec3(0.459541,0.279972,0.193965),vec3(0.207503,0.128341,0.098463),
 vec3(0.019420,0.016701,0.013400),vec3(0.006035,0.005190,0.004164),
 vec3(0.002372,0.002040,0.001636),vec3(0.000000,0.000000,0.000000));
const vec3 GRAZING[PROFILE_N]=vec3[PROFILE_N](
 vec3(0.501431,0.383656,0.323421),vec3(0.594023,0.435577,0.352526),
 vec3(0.444722,0.360840,0.306858),vec3(0.530725,0.417036,0.366201),
 vec3(0.889255,0.628932,0.505206),vec3(1.389388,0.980254,0.755381),
 vec3(1.798031,1.323533,1.027938),vec3(2.046291,1.551282,1.215553),
 vec3(2.129368,1.670683,1.322172),vec3(1.976563,1.561564,1.261436),
 vec3(1.794290,1.370349,1.106133),vec3(1.308990,0.979743,0.789233),
 vec3(0.924975,0.641772,0.498919),vec3(0.479225,0.351105,0.285022),
 vec3(0.200028,0.149638,0.130981),vec3(0.054028,0.046464,0.037279),
 vec3(0.011962,0.010287,0.008254),vec3(0.000000,0.000000,0.000000));
vec3 fittedRadiance(float radius,float incidence,bool upper){
 if(radius<RADII[0]||radius>RADII[PROFILE_N-1])return vec3(0.0);
 int k=0;
 for(int i=0;i<PROFILE_N-2;i++) if(radius>RADII[i+1]) k=i+1;
 float f=clamp((radius-RADII[k])/(RADII[k+1]-RADII[k]),0.0,1.0);
 vec3 a=upper?mix(UPPER[k],UPPER[k+1],f):mix(LOWER[k],LOWER[k+1],f);
 vec3 b=mix(GRAZING[k],GRAZING[k+1],f);
 return mix(a,b,1.0-smoothstep(0.12,0.32,incidence));}
vec3 plasma(vec4 d,vec2 fc,float side){
 float r=d.x; if(r<0.1)return vec3(0.0);
 float phi=d.y,a=phi/TAU,t=uTime/8.0;
 float inner=1.0-smoothstep(3.5,9.0,r);
 float n0=noiseP(vec2(r*1.7,a*48.0-t*12.0),12.0);
 float n1=noiseP(vec2(r*1.7+19.6,a*48.0-t*24.0),12.0);
 float swirl=mix(n0,n1,inner*0.65);
 float finewarp=noiseP(vec2(r*5.3,a*64.0-t*32.0+r*0.3),16.0);
 float rw=r+(swirl-0.5)*0.25+(finewarp-0.5)*0.055;
 float footprint=abs(dFdx(r))+abs(dFdy(r));
 float filament=fbmP(vec2(rw*8.0,a*60.0-t*15.0+rw*0.18),15.0,footprint*8.0);
 float filament2=fbmP(vec2(rw*2.0+72.0,a*128.0-t*64.0),32.0,footprint*2.0);
 float density=pow(0.10+1.64*filament,2.25);
 density*=0.65+0.74*filament2;
 float front=pow(max(0.0,sin(phi)),8.0)*(1.0-smoothstep(0.12,0.32,d.z));
 float frontBoost=1.0+1.9*front*smoothstep(6.0,9.5,r);
 float outerFade=1.0-smoothstep(11.8,15.0,r);
 return fittedRadiance(r,d.z,side>=0.0)*(density/0.84)*frontBoost*outerFade;}
void main(){
 vec2 p=(gl_FragCoord.xy-0.5*uRes)/uRes.y*uScale;
 float c=cos(uTilt),s=sin(uTilt);
 p=mat2(c,-s,s,c)*p;
 // Image-directed compression of the lower lensed image around the critical
 // curve. Their own note: an artistic fit, not an exact Kerr metric.
 float b=length(p);
 float w=smoothstep(0.3,1.5,-p.y)*(1.0-smoothstep(5.0,7.0,b));
 if(b>CRIT) p*=(CRIT+(b-CRIT)*(1.0+0.30*w))/b;
 vec3 origin=OBSERVER*vec3(0.0,sin(uIncl),cos(uIncl));
 vec3 fwd=-normalize(origin),rt=vec3(1.0,0.0,0.0),up=normalize(cross(rt,fwd));
 origin+=p.x*rt+p.y*up;
 vec3 v=fwd; float h2=dot(cross(origin,v),cross(origin,v));
 vec3 pos=origin;
 vec4 m0=vec4(0.0),m1=vec4(0.0),m2=vec4(0.0);
 int hits=0; bool captured=false;
 for(int i=0;i<540;i++){
  float r=length(pos);
  if(r<1.015){captured=true;break;}
  if(r>85.0&&dot(pos,v)>0.0)break;
  float dt=clamp(r*0.052,0.012,3.0);
  vec3 a=accel(pos,h2),hv=v+a*dt*0.5,nx=pos+hv*dt;
  vec3 nv=hv+accel(nx,h2)*dt*0.5;
  if(pos.y*nx.y<0.0){
   float f=pos.y/(pos.y-nx.y);
   vec3 hit=mix(pos,nx,f);
   float rr=length(hit.xz);
   if(rr>uInner&&rr<DISCOUT){
    vec4 dd=vec4(rr,atan(hit.z,hit.x),abs(nv.y),1.0);
    if(hits==0)m0=dd;else if(hits==1)m1=dd;else m2=dd;
    hits++; if(hits>=3)break;
   }
  }
  pos=nx; v=nv;
 }
 // Grazing, cooler foreground plasma also absorbs the secondary image.
 float opacity=0.72*exp(-pow((m0.x-13.0)/5.0,2.0))*(1.0-smoothstep(0.12,0.32,m0.z));
 float trans=exp(-opacity);
 float side=(-sin(uTilt)*p.x+cos(uTilt)*p.y);
 vec3 col=plasma(m0,gl_FragCoord.xy,side)
        + trans*(plasma(m1,gl_FragCoord.xy,side)*0.86+plasma(m2,gl_FragCoord.xy,side)*0.55);
 // the plasma only exists inside the disc annulus and along the thin plane
 float radius=length(p)*27.5;
 vec2 q=mat2(cos(uTilt),-sin(uTilt),sin(uTilt),cos(uTilt))*p;
 col*=max(smoothstep(2.61,2.68,radius),1.0-smoothstep(0.040,0.058,abs(q.y)));
 float az=atan(q.y,q.x)/TAU;
 float stream=noiseP(vec2(radius*2.2,az*20.0-uTime/8.0*5.0),5.0);
 float silk=fbmP(vec2(radius*12.0+(stream-0.5)*0.6,az*32.0-uTime/8.0*8.0),8.0,
                 27.5/uRes.y*12.0);
 col*=mix(1.0,0.58+0.84*silk,smoothstep(0.018,0.055,abs(q.y)));
 // The photon ring, at the critical impact parameter sqrt(27)/2.
 float px=27.5/uRes.y, d=abs(radius-2.598);
 float ring=(1.0-smoothstep(px*0.08,px*0.76,d))*0.54;
 ring+=0.055*exp(-pow(d/(px*2.5),2.0));
 ring*=mix(0.42,1.0,smoothstep(-0.01,0.03,p.y));
 col+=ring*vec3(1.0,0.64,0.46);
 // Belong to the region rather than to the reference render.
 col=mix(col,col*uTint*1.35,0.22);
 // Their tonemap.
 vec3 tone=1.0-exp(-col*1.45);
 float lum=max(tone.r,max(tone.g,tone.b));
 float shadow=1.0-smoothstep(0.093,0.102,length(p));
 float alpha=max(shadow,clamp(lum*2.2,0.0,1.0));
 fragColor=vec4(tone*alpha,alpha);
}`;
const holeGL=(()=>{
 try{
  const cv=document.createElement('canvas');
  const opts={alpha:true,antialias:false,depth:false,stencil:false,premultipliedAlpha:true};
  const gl=cv.getContext('webgl2',opts)||cv.getContext('webgl',opts);
  if(!gl)return null;
  const vs=gl.createShader(gl.VERTEX_SHADER);
  gl.shaderSource(vs,'#version 300 es\nvoid main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.0-1.0,0,1);}');
  gl.compileShader(vs);
  const fs=gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(fs,GLSL_HOLE);gl.compileShader(fs);
  if(!gl.getShaderParameter(fs,gl.COMPILE_STATUS)){
   if(typeof console!=='undefined')console.warn('hole shader:',gl.getShaderInfoLog(fs));
   return null;
  }
  const pr=gl.createProgram();
  gl.attachShader(pr,vs);gl.attachShader(pr,fs);gl.linkProgram(pr);
  if(!gl.getProgramParameter(pr,gl.LINK_STATUS))return null;
  gl.useProgram(pr);
  const U=n=>gl.getUniformLocation(pr,n);
  const u={res:U('uRes'),tilt:U('uTilt'),incl:U('uIncl'),scale:U('uScale'),
           inner:U('uInner'),time:U('uTime'),tint:U('uTint')};
  const S=512;cv.width=S;cv.height=S;
  gl.viewport(0,0,S,S);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
  return {cv,gl,S,u};
 }catch(e){return null;}
})();
"""
rep(ANCHOR, GL + ANCHOR)

# ---- 2. rename the hand-drawn version to a fallback, and dispatch ----
rep("function drawHole(m,q,p,t,rad){\n const cx=q[0],cy=q[1];",
    "function drawHole2D(m,q,p,t,rad){\n const cx=q[0],cy=q[1];")

# ---- 3. the sprite path ----
rep("function drawMass(m,p,t){",
    r"""/* Screen radius of the shadow, and the sprite that has to contain the disc.
 *
 * In the emission pass radius = length(p)*27.5 is Schwarzschild radii and the
 * shadow sits at radius 2.608, so the shadow is always at length(p) = 0.0949.
 * The radial profile is dead past 9 rs, which is length(p) = 0.327 - so a
 * uScale of 0.654 makes the sprite cover exactly the part of the disc that has
 * any light in it, and the sprite's pixel size never has to change with rad. */
function drawHole(m,q,p,t,rad){
 const cx=q[0],cy=q[1];
 if(!holeGL||rad<3){drawHole2D(m,q,p,t,rad);return;}
 const G=holeGL,DRAW=rad*3.5;
 queue.push({type:4,d:q[2],alpha:1,fn:()=>{
  const g=G.gl;
  g.uniform2f(G.u.res,G.S,G.S);
  g.uniform1f(G.u.tilt,lensRoll);
  g.uniform1f(G.u.incl,1.28);
  g.uniform1f(G.u.scale,0.654);
  g.uniform1f(G.u.inner,1.9);
  g.uniform1f(G.u.time,t);
  g.uniform3f(G.u.tint,tintHole[0]/255,tintHole[1]/255,tintHole[2]/255);
  g.drawArrays(g.TRIANGLES,0,3);
  ctx.drawImage(G.cv,cx-DRAW,cy-DRAW,DRAW*2,DRAW*2);
 }});
}
/* The disc's roll on screen. A fixed angle rather than 0: a perfectly level disc
 * reads as a diagram, and the reference is never level. */
const lensRoll=0.34;
let tintHole=[255,236,214];
function drawMass(m,p,t){""")

# ---- 4. keep the hole's palette tint current ----
rep(" const tint=massTint(m,p);\n if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);",
    " const tint=massTint(m,p);\n if(m.kind===4)tintHole=blend(tint,[255,236,214],.5);\n if(rad<6)glow([m.x,m.y,m.z],m.r*.85,tint,.55,2.8);")

# ---- 5. the old screen-space lensing stays, it still bends the scene's stars ----
rep(" getState:()=>({seed:SEED,started,paused,autoCamera,",
    " holeGL:!!holeGL,\n getState:()=>({seed:SEED,started,paused,autoCamera,")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V16 applied:", len(s), "chars")
