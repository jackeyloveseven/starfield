"""P2: the sky.

  - 420 stars on a power-law magnitude distribution, batched into eight fills
    (the original drew 172, one beginPath/fill each)
  - twelve bright stars with blooms and a cross, so the eye has somewhere to land
  - ink-wash nebulae drawn from pre-rendered, tint-quantised textures: a radial
    gradient per nebula per frame would cost more than everything else together
  - analytic per-star lensing around a black hole: we move arcs we were already
    going to draw, so it costs no extra fill
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def cut(start, end, new):
    global s
    i, j = s.find(start), s.find(end)
    if i < 0 or j < 0 or j < i:
        sys.exit(f"cut markers not found:\n{start[:70]}\n{end[:70]}")
    s = s[:i] + new + s[j:]


cut("const stars=Array.from(", "const grainCanvas=", """/* The star field: a power law of magnitudes, batched into a handful of fills.
 * Real migratory birds steer by these; here they are the whole subject. */
const stars=Array.from({length:coarse?300:420},(_,i)=>{
 const a=hash(i,110)*TAU,e=.03+hash(i,111)*1.46,mag=Math.pow(hash(i,114),2.6);
 return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:.34+mag*2.4,mag,phase:hash(i,113)*TAU};
});
const brightStars=Array.from({length:coarse?7:12},(_,i)=>{
 const a=hash(i,310)*TAU,e=.06+hash(i,311)*1.4;
 return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:1.9+hash(i,312)*2.4,phase:hash(i,313)*TAU,warm:hash(i,314)>.55};
});
/* Ink washes for the deep field. Each is rendered once into an offscreen
 * canvas and then only scaled; the tint is quantised so the cache stays tiny
 * while the palette blends continuously. */
const nebulae=Array.from({length:coarse?14:24},(_,i)=>{
 const a=hash(i,210)*TAU,e=.02+hash(i,211)*1.5;
 return {x:Math.cos(a)*Math.cos(e),y:Math.sin(e),z:Math.sin(a)*Math.cos(e),size:.26+hash(i,212)*.52,seed:1+Math.floor(hash(i,213)*6),rot:hash(i,214)*TAU,alpha:.09+hash(i,215)*.26};
});
const nebCache=new Map();
function nebulaTex(seed,tint){
 const key=seed+'|'+tint.join(',');
 if(nebCache.has(key))return nebCache.get(key);
 const N=192,c=document.createElement('canvas');c.width=c.height=N;
 const g=c.getContext('2d'),r=rng((SEED^Math.imul(seed,0x9e3779b1))>>>0);
 for(let i=0;i<30;i++){
  const x=N*.5+(r()-.5)*N*.86,y=N*.5+(r()-.5)*N*.86,rad=N*(.10+r()*.30);
  const gr=g.createRadialGradient(x,y,0,x,y,rad);
  gr.addColorStop(0,`rgba(255,255,255,${(.05+r()*.15).toFixed(3)})`);
  gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;g.fillRect(0,0,N,N);
 }
 g.globalCompositeOperation='destination-in';
 const m=g.createRadialGradient(N*.5,N*.5,0,N*.5,N*.5,N*.5);
 m.addColorStop(0,'rgba(0,0,0,1)');m.addColorStop(.5,'rgba(0,0,0,.82)');m.addColorStop(1,'rgba(0,0,0,0)');
 g.fillStyle=m;g.fillRect(0,0,N,N);
 g.globalCompositeOperation='source-in';g.fillStyle=css(tint);g.fillRect(0,0,N,N);
 g.globalCompositeOperation='source-over';
 nebCache.set(key,c);return c;
}
function skyPoint(v){
 const d=v[0]*camera.forward[0]+v[1]*camera.forward[1]+v[2]*camera.forward[2];
 if(d<=.02)return null;
 const xx=v[0]*camera.right[0]+v[1]*camera.right[1]+v[2]*camera.right[2];
 const yy=v[0]*camera.up[0]+v[1]*camera.up[1]+v[2]*camera.up[2];
 return [camera.cx+xx/d*camera.focal,camera.cy-yy/d*camera.focal,d];
}
let lensSources=[];
function updateLens(){
 lensSources.length=0;
 const k0=Math.floor(travel/CHUNK);
 for(let k=k0-2;k<=k0+2;k++)for(const m of chunk(k).masses){
  if(m.kind!==4)continue;
  const q=project([m.x,m.y,m.z]);
  if(q&&q[2]>40&&q[2]<14000&&q[0]>-500&&q[0]<W+500&&q[1]>-500&&q[1]<H+500)lensSources.push([q[0],q[1]]);
 }
}
/* Displace a screen point radially away from a horizon. A star 40px out is
 * thrown 105px; the pull fades to nothing by ~360px. */
function lensWarp(x,y){
 if(!lensSources.length)return [x,y];
 let dx=0,dy=0;
 for(const L of lensSources){
  const ex=x-L[0],ey=y-L[1],r2=ex*ex+ey*ey;
  if(r2>129600||r2<1)continue;
  const r=Math.sqrt(r2),pull=clamp(4200/r,0,110)*(1-smooth((r-130)/230));
  if(pull<=0)continue;
  dx+=ex/r*pull;dy+=ey/r*pull;
 }
 return [x+dx,y+dy];
}
""")

cut("function drawSky(){", "function paperFinish(){", """function drawSky(){
 const p=currentPalette,g=ctx.createLinearGradient(0,0,0,H);
 g.addColorStop(0,css(p.sky));g.addColorStop(.68,css(p.horizon));g.addColorStop(1,css(p.fog));
 ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 updateLens();
 const dense=.36+p.void*.36+p.core*.46+p.shimmer*.28;
 // Ink washes first: they are the deep field, everything else prints on top.
 const wash=.22+p.wash*1.15+p.core*.55;
 if(wash>.06){
  const list=lowQuality?nebulae.slice(0,8):nebulae;
  const tint=blend(p.tree,p.treeDark,.35).map(v=>Math.round(v/24)*24);
  for(const n of list){
   const q=skyPoint([n.x,n.y,n.z]);if(!q)continue;
   const rad=n.size*camera.focal,pad=rad*1.05;
   if(q[0]<-pad||q[0]>W+pad||q[1]<-pad||q[1]>H+pad)continue;
   ctx.save();ctx.globalAlpha=clamp(n.alpha*wash,0,.60);
   ctx.translate(q[0],q[1]);ctx.rotate(n.rot);
   ctx.drawImage(nebulaTex(n.seed,tint),-rad,-rad,rad*2,rad*2);ctx.restore();
  }
  ctx.globalAlpha=1;
 }
 // Bright stars: a bloom and a cross each, so the eye has somewhere to land.
 for(const st of brightStars){
  const q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
  const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
  if(x<-40||x>W+40||y<-40||y>H+40)continue;
  const tw=.42+.58*Math.sin(time*.5+st.phase)**2,r=st.size*(1+.35*tw);
  const tint=st.warm?[255,236,206]:[226,240,255],gr=ctx.createRadialGradient(x,y,0,x,y,r*11);
  gr.addColorStop(0,css(tint,.95*clamp(dense,0,1.3)));gr.addColorStop(.16,css(tint,.30*dense));gr.addColorStop(1,css(tint,0));
  ctx.fillStyle=gr;ctx.fillRect(x-r*11,y-r*11,r*22,r*22);
  ctx.fillStyle='rgba(255,255,255,.92)';ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();
  ctx.strokeStyle=css(tint,.55);ctx.lineWidth=.7;ctx.beginPath();
  ctx.moveTo(x-r*3.2,y);ctx.lineTo(x+r*3.2,y);ctx.moveTo(x,y-r*3.2);ctx.lineTo(x,y+r*3.2);ctx.stroke();
 }
 // The faint field, batched: eight fills instead of four hundred.
 const buckets=[[],[],[],[]];
 const limit=lowQuality?Math.floor(stars.length*.45):stars.length;
 for(let i=0;i<limit;i++){
  const st=stars[i],q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
  const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
  if(x<-6||x>W+6||y<-6||y>H+6)continue;
  const tier=st.mag>.70?3:st.mag>.40?2:st.mag>.16?1:0;
  buckets[tier].push(x,y,st.size,Math.sin(time*.35+st.phase)>0?1:0);
 }
 for(let t=0;t<4;t++){
  const b=buckets[t];if(!b.length)continue;
  ctx.fillStyle=css(blend(p.bird,[255,255,255],.25));
  for(let phase=0;phase<2;phase++){
   ctx.globalAlpha=clamp((.30+t*.22)*dense,0,.92)*(phase?.72:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b.length;j+=4){if(b[j+3]!==phase)continue;ctx.moveTo(b[j]+b[j+2],b[j+1]);ctx.arc(b[j],b[j+1],b[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
 }
 ctx.globalAlpha=1;
 const intensity=p.front*.22+p.shimmer*.12+(1-p.void)*.035;
 if(intensity>.008){
  const horizon=camera.cy-camera.focal*Math.tan(Math.asin(clamp(-camera.forward[1],-.99,.99))),x=W*.76,y=clamp(horizon,-H*.35,H*.55),r=H*.82;
  const glow=ctx.createRadialGradient(x,y,0,x,y,r);glow.addColorStop(0,css(p.sun,intensity));glow.addColorStop(.38,css(p.sun,intensity*.46));glow.addColorStop(1,css(p.sun,0));ctx.fillStyle=glow;ctx.fillRect(0,0,W,H);
 }
}
""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("p2 applied")
