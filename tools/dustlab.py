"""Scratch lab: render the SAME gas with several dust-lane parameter sets in one
shot, so the lane language can be tuned without touching the artwork.

Writes dustlab.html next to it and screenshots it.

Run:  python -I dustlab.py <out.png> [--size 1600x1200]
"""
import sys, os, subprocess, tempfile, argparse
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ap = argparse.ArgumentParser()
ap.add_argument('png'); ap.add_argument('--size', default='1600x1200')
a = ap.parse_args()
W, H = (int(v) for v in a.size.lower().split('x'))

# variants: [label,K,Rmul,plateau,mid,tail,alB,alR,wander,envLo,envPow,wLo,wHi,wScale]
VARIANTS = [
    ["Y1 pl.55",  18, 2.0, 0.55, 1.00, 0.35, 0.22, 0.28, 1.05, 0.28, 0.50, 0.50, 1.35, 0.55, 0.00, 0.00],
    ["Y2 pl.50",  18, 2.0, 0.50, 1.00, 0.30, 0.26, 0.32, 1.05, 0.28, 0.50, 0.50, 1.35, 0.55, 0.00, 0.00],
    ["Y3 pl.60",  18, 2.0, 0.60, 1.00, 0.40, 0.20, 0.26, 1.05, 0.28, 0.50, 0.50, 1.35, 0.55, 0.00, 0.00],
    ["Y4 hybrid", 18, 2.0, 0.55, 1.00, 0.35, 0.24, 0.30, 1.05, 0.28, 0.50, 0.50, 1.35, 0.55, 0.55, 0.50],
]

HTML = r"""<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#0c1622;overflow:hidden}</style>
<canvas id="cv"></canvas>
<script>
const TAU=Math.PI*2;
function rng(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
const VARIANTS=__VARIANTS__;
const N=384;
// ---- the gas stage, copied from nebulaTex so the lanes are judged against the
// real thing (blobs -> filaments -> mask -> colour), minus the dust.
function gas(seed,idx){
 const c=document.createElement('canvas');c.width=c.height=N;
 const g=c.getContext('2d'),r=rng((seed*2654435761^idx*40503)>>>0);
 const cx=N*.5,cy=N*.5;
 const nn=2+(r()*2|0),nuc=[];
 for(let i=0;i<nn;i++){const a=r()*TAU,d=N*(.03+r()*.16);nuc.push([cx+Math.cos(a)*d,cy+Math.sin(a)*d]);}
 g.globalCompositeOperation='source-over';
 for(let i=0;i<44;i++){
  const k=nuc[i%nn],a=r()*TAU,d=N*(.02+r()*.30);
  const x=k[0]+Math.cos(a)*d,y=k[1]+Math.sin(a)*d,rad=N*(.05+r()*.17);
  const gr=g.createRadialGradient(x,y,0,x,y,rad);
  gr.addColorStop(0,'rgba(255,255,255,'+(.24+r()*.56).toFixed(3)+')');
  gr.addColorStop(1,'rgba(255,255,255,0)');
  g.fillStyle=gr;
  const bx=Math.max(0,x-rad),by=Math.max(0,y-rad);
  g.fillRect(bx,by,Math.min(N,x+rad)-bx,Math.min(N,y+rad)-by);
 }
 g.globalCompositeOperation='lighter';g.lineCap='round';
 for(let i=0;i<130;i++){
  const around=i%3!==0,a0=r()*TAU;let a1,r0,r1;
  if(around){a1=a0+.5+r()*1.5;r0=N*(.05+r()*.30);r1=r0*(1+(r()-.5)*.24);}
  else{a1=a0+(r()-.5)*.55;r0=N*(.03+r()*.26);r1=r0+N*(.10+r()*.26);}
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  const nx=-(y1-y0),ny=x1-x0,nl=Math.hypot(nx,ny)||1,bow=(r()-.5)*N*(around?.05:.10);
  g.strokeStyle='rgba(255,255,255,'+(.08+r()*.30).toFixed(3)+')';
  g.lineWidth=N*(.003+r()*.011);
  g.beginPath();g.moveTo(x0,y0);
  g.quadraticCurveTo((x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1);g.stroke();
 }
 return {c,g,r,cx,cy};
}
function lanes(g,r,cx,cy,V){
 const K=V[1],Rmul=V[2],pl=V[3],mid=V[4],tail=V[5],alB=V[6],alR=V[7],wan=V[8],envLo=V[9],envPow=V[10],wLo=V[11],wHi=V[12],wSc=V[13],coreR=V[14],coreA=V[15];
 if(String(V[0]).indexOf('ORIG')===0){
  const lane=(x0,y0,mx,my,x1,y1,w,al)=>{
   g.strokeStyle='rgba(0,0,0,'+(al*.55).toFixed(3)+')';g.lineWidth=w*3.1;
   g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
   g.strokeStyle='rgba(0,0,0,'+al.toFixed(3)+')';g.lineWidth=w;
   g.beginPath();g.moveTo(x0,y0);g.quadraticCurveTo(mx,my,x1,y1);g.stroke();
  };
  g.globalCompositeOperation='destination-out';g.lineCap='round';
  for(let i=0;i<8;i++){
   const a0=r()*TAU,a1=a0+1.0+r()*1.8,rr=N*(.14+r()*.30);
   const x0=cx+Math.cos(a0)*rr,y0=cy+Math.sin(a0)*rr;
   const x1=cx+Math.cos(a1)*rr,y1=cy+Math.sin(a1)*rr;
   const nx=-(y1-y0),ny=x1-x0,nl=Math.hypot(nx,ny)||1,bow=(r()<.5?-1:1)*N*(.08+r()*.14);
   lane(x0,y0,(x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1,N*(.008+r()*.020),.40+r()*.45);
  }
  for(let i=0;i<5;i++){
   const a0=r()*TAU,r0=N*(.05+r()*.18),a1=a0+(r()-.5)*1.0,r1=r0+N*(.14+r()*.22);
   const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
   const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
   lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.09,(y0+y1)*.5+(r()-.5)*N*.09,x1,y1,N*(.010+r()*.022),.50+r()*.42);
  }
  for(let i=0;i<2;i++){
   const a0=r()*TAU,a1=a0+Math.PI+(r()-.5)*.7,r0=N*(.28+r()*.18),r1=N*(.28+r()*.18);
   const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
   const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
   lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.22,(y0+y1)*.5+(r()-.5)*N*.22,x1,y1,N*(.010+r()*.024),.45+r()*.40);
  }
  g.globalCompositeOperation='source-over';
  return;
 }
 const lane=(x0,y0,mx,my,x1,y1,w,al)=>{
  w=w*wSc;
  for(let i=0;i<=K;i++){
   const t=i/K,it=1-t;
   const bx=it*it*x0+2*it*t*mx+t*t*x1, by=it*it*y0+2*it*t*my+t*t*y1;
   const dx=2*it*(mx-x0)+2*t*(x1-mx),dy=2*it*(my-y0)+2*t*(y1-my);
   const nl=Math.hypot(dx,dy)||1,ox=-dy/nl,oy=dx/nl;
   const env=envLo+(1-envLo)*Math.pow(Math.sin(Math.PI*t),envPow);
   const rr=w*env*(wLo+r()*wHi);
   const wd=(r()-.5)*w*wan;
   const px=bx+ox*wd,py=by+oy*wd,R=rr*Rmul,aa=al*(alB+r()*alR);
   const gr=g.createRadialGradient(px,py,0,px,py,R);
   gr.addColorStop(0,'rgba(0,0,0,'+aa.toFixed(3)+')');
   gr.addColorStop(pl,'rgba(0,0,0,'+(aa*mid).toFixed(3)+')');
   gr.addColorStop(.82,'rgba(0,0,0,'+(aa*tail).toFixed(3)+')');
   gr.addColorStop(1,'rgba(0,0,0,0)');
   g.fillStyle=gr;
   const bx0=px-R,by0=py-R;g.fillRect(bx0,by0,R*2,R*2);
   if(coreR>0){g.fillStyle='rgba(0,0,0,'+(aa*coreA).toFixed(3)+')';
    g.beginPath();g.arc(px,py,rr*coreR,0,TAU);g.fill();}
  }
 };
 g.globalCompositeOperation='destination-out';
 for(let i=0;i<8;i++){
  const a0=r()*TAU,a1=a0+1.0+r()*1.8,rr=N*(.14+r()*.30);
  const x0=cx+Math.cos(a0)*rr,y0=cy+Math.sin(a0)*rr;
  const x1=cx+Math.cos(a1)*rr,y1=cy+Math.sin(a1)*rr;
  const nx=-(y1-y0),ny=x1-x0,nl=Math.hypot(nx,ny)||1,bow=(r()<.5?-1:1)*N*(.08+r()*.14);
  lane(x0,y0,(x0+x1)*.5+nx/nl*bow,(y0+y1)*.5+ny/nl*bow,x1,y1,N*(.014+r()*.030),.38+r()*.42);
 }
 for(let i=0;i<5;i++){
  const a0=r()*TAU,r0=N*(.05+r()*.18),a1=a0+(r()-.5)*1.0,r1=r0+N*(.14+r()*.22);
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.09,(y0+y1)*.5+(r()-.5)*N*.09,x1,y1,N*(.018+r()*.034),.44+r()*.40);
 }
 for(let i=0;i<2;i++){
  const a0=r()*TAU,a1=a0+Math.PI+(r()-.5)*.7,r0=N*(.28+r()*.18),r1=N*(.28+r()*.18);
  const x0=cx+Math.cos(a0)*r0,y0=cy+Math.sin(a0)*r0;
  const x1=cx+Math.cos(a1)*r1,y1=cy+Math.sin(a1)*r1;
  lane(x0,y0,(x0+x1)*.5+(r()-.5)*N*.22,(y0+y1)*.5+(r()-.5)*N*.22,x1,y1,N*(.016+r()*.034),.42+r()*.38);
 }
 g.globalCompositeOperation='source-over';
}
function finish(o,pal){
 const {c,g,cx,cy}=o;
 g.globalCompositeOperation='destination-in';
 const m=g.createRadialGradient(cx,cy,0,cx,cy,N*.5);
 m.addColorStop(0,'rgba(0,0,0,1)');m.addColorStop(.26,'rgba(0,0,0,.92)');
 m.addColorStop(.52,'rgba(0,0,0,.50)');m.addColorStop(.78,'rgba(0,0,0,.14)');
 m.addColorStop(1,'rgba(0,0,0,0)');
 g.fillStyle=m;g.fillRect(0,0,N,N);
 g.globalCompositeOperation='source-in';
 const cg=g.createRadialGradient(cx,cy,0,cx,cy,N*.5);
 cg.addColorStop(0,pal[0]);cg.addColorStop(.46,pal[1]);cg.addColorStop(1,pal[2]);
 g.fillStyle=cg;g.fillRect(0,0,N,N);
 g.globalCompositeOperation='source-over';
}
// A FOIL-ish palette, matching NEB_PAL[2].
const PAL=['rgb(192,146,62)','rgb(131,146,118)','rgb(70,146,174)'];
const cols=__COLS__,rows=Math.ceil(VARIANTS.length/cols);
const cell=Math.floor(Math.min(window.innerWidth/cols,window.innerHeight/rows));
const cv=document.getElementById('cv');cv.width=cols*cell;cv.height=rows*cell;
const x=cv.getContext('2d');
x.fillStyle='#16273a';x.fillRect(0,0,cv.width,cv.height);
for(let v=0;v<VARIANTS.length;v++){
 const o=gas(1,2);lanes(o.g,o.r,o.cx,o.cy,VARIANTS[v]);finish(o,PAL);
 x.drawImage(o.c,(v%cols)*cell,Math.floor(v/cols)*cell,cell,cell);
 x.fillStyle='#fff';x.font='14px monospace';x.fillText(VARIANTS[v][0],(v%cols)*cell+8,Math.floor(v/cols)*cell+20);
}
</script>"""

HTML = HTML.replace('__VARIANTS__', repr(VARIANTS).replace("'", '"')).replace('__COLS__', '3')
lab = os.path.abspath('dustlab.html')
open(lab, 'w', encoding='utf-8', newline='').write(HTML)
url = 'file:///' + lab.replace('\\', '/')
png = os.path.abspath(a.png)
with tempfile.TemporaryDirectory(prefix='dl-') as prof:
    subprocess.run([CHROME, '--headless=new', '--disable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-gpu-compositing', '--no-sandbox', '--mute-audio',
                    '--hide-scrollbars', '--no-first-run', '--disable-extensions',
                    '--disable-background-networking', f'--window-size={W},{H}',
                    f'--user-data-dir={prof}', f'--screenshot={png}', url],
                   capture_output=True, text=True, timeout=120)
print('png bytes:', os.path.getsize(png) if os.path.exists(png) else 'MISSING')
