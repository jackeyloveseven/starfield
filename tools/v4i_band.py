"""V4i: draw the band as a ribbon.

Measured: 272 of 3400 band stars land on screen, against ~1000 from the 5000-star
field - a 27% density bump, which reads as nothing. And the wash was 15 blobs
around a full great circle, so about one was ever in frame. A band has to be drawn
as a band: project the great circle, split it at the horizon, and stroke it in
layers from wide-and-faint to narrow-and-bright.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep(""" // The Milky Way: the corridor's own band of stars and wash, so the route is
 // legible without a road drawn on the ground.
 const bw=.62+p.wash*.40+p.core*.28;
 if(bw>.08){
  for(const n of bandWash){
   const q=skyPoint([n.x,n.y,n.z]);if(!q)continue;
   const rad=n.size*camera.focal*.75,pad=rad*.55;
   if(q[0]<-pad||q[0]>W+pad||q[1]<-pad||q[1]>H+pad)continue;
   const w=lensWarp(q[0],q[1]);
   const al=clamp(n.alpha*bw*1.6,0,.86),g2=ctx.createRadialGradient(w[0],w[1],0,w[0],w[1],rad);
   g2.addColorStop(0,css(blend(p.sun,p.paper,.30),al));g2.addColorStop(.45,css(blend(p.sun,p.paper,.30),al*.32));g2.addColorStop(1,css(blend(p.sun,p.paper,.30),0));
   ctx.fillStyle=g2;ctx.fillRect(w[0]-rad,w[1]-rad,rad*2,rad*2);
   fillPx+=rad*rad*4;
  }
  const bb=[[],[]];
  for(const st of bandStars){
   const q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
   const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
   if(x<-6||x>W+6||y<-6||y>H+6)continue;
   bb[Math.sin(time*.35+st.phase)>0?1:0].push(x,y,st.size);
  }
  ctx.fillStyle=css(blend(p.craft,[255,255,255],.34));
  for(let phase=0;phase<2;phase++){
   const b2=bb[phase];if(!b2.length)continue;
   ctx.globalAlpha=clamp(.72*bw,0,.95)*(phase?.74:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b2.length;j+=3){ctx.moveTo(b2[j]+b2[j+2],b2[j+1]);ctx.arc(b2[j],b2[j+1],b2[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
  ctx.globalAlpha=1;
 }""",
    """ // The Milky Way: the corridor's own band, so the route is legible without a
 // road drawn on the ground. Projected as a ribbon and stroked in layers - a
 // scatter of blobs cannot read as a band from inside it.
 const bw=.62+p.wash*.40+p.core*.28;
 {
  const col=blend(p.sun,p.paper,.34),segs=[];
  let cur=null;
  for(let i=0;i<=260;i++){
   const d=bandDir(i/260*TAU,0),q=skyPoint(d);
   if(!q){cur=null;continue;}
   const w=lensWarp(q[0],q[1]);
   if(!cur){cur=[];segs.push(cur);}
   cur.push(w[0],w[1]);
  }
  ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
  for(const seg of segs){
   if(seg.length<6)continue;
   for(const L of [[250,.055],[160,.072],[92,.098],[42,.140]]){
    ctx.beginPath();ctx.moveTo(seg[0],seg[1]);
    for(let j=2;j<seg.length;j+=2)ctx.lineTo(seg[j],seg[j+1]);
    ctx.strokeStyle=css(col,clamp(L[1]*bw*1.7,0,.5));ctx.lineWidth=L[0];ctx.stroke();
   }
   fillPx+=250*250*4;
  }
  ctx.restore();
  const bb=[[],[]];
  for(const st of bandStars){
   const q=skyPoint([st.x,st.y,st.z]);if(!q)continue;
   const w=lensWarp(q[0],q[1]),x=w[0],y=w[1];
   if(x<-6||x>W+6||y<-6||y>H+6)continue;
   bb[Math.sin(time*.35+st.phase)>0?1:0].push(x,y,st.size);
  }
  ctx.fillStyle=css(blend(p.craft,[255,255,255],.34));
  for(let phase=0;phase<2;phase++){
   const b2=bb[phase];if(!b2.length)continue;
   ctx.globalAlpha=clamp(.80*bw,0,.95)*(phase?.74:1);
   ctx.beginPath();let any=false;
   for(let j=0;j<b2.length;j+=3){ctx.moveTo(b2[j]+b2[j+2],b2[j+1]);ctx.arc(b2[j],b2[j+1],b2[j+2],0,TAU);any=true;}
   if(any)ctx.fill();
  }
  ctx.globalAlpha=1;
 }""")

# the blob field is gone; the ribbon replaces it
rep("""const bandWash=Array.from({length:coarse?9:15},(_,i)=>{
 const a=hash(i,420)*TAU,g=(hash(i,421)-.5)*.10,d=bandDir(a,g);
 return {x:d[0],y:d[1],z:d[2],size:.46+hash(i,422)*.66,alpha:.20+hash(i,423)*.30};
});
""", "")

# and the band needs enough stars to stand out against the 5000-star field
rep("const bandStars=Array.from({length:coarse?1700:3400},(_,i)=>{",
    "const bandStars=Array.from({length:coarse?4200:9000},(_,i)=>{")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4i applied:", len(s), "bytes")
