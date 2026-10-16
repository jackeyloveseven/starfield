"""V4j: anchor the band's plane to the view.

Measured camera basis: forward=(-0.178,-0.963,0.202) - the director spends most of
its time pitched ~74 degrees down at the fleet. A band pinned to the world horizon
is therefore ~90 degrees out of frame, which is why it projected to (2538,-2015)
on a 1258x566 screen and never appeared. Rebuild the plane from the camera basis
each frame so the band always crosses the frame, rolled 0.62 rad so it runs
diagonally rather than straight across.
"""
import sys

P = r"C:\Users\machine\Downloads\starfield.html"
s = open(P, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    if s.count(a) != n:
        sys.exit("count=%d (want %d): %s" % (s.count(a), n, a[:130]))
    s = s.replace(a, b, n)


rep("""/* The band the corridor runs inside: a great circle through the direction of
 * travel, so flying forward the Milky Way converges ahead and sweeps overhead. */
const BAND_U=[0,0,1],BAND_REF=[.574,.819,0];
function bandBasis(){
 const n0=Math.hypot(...BAND_U),u=BAND_U.map(v=>v/n0);
 const d=BAND_REF[0]*u[0]+BAND_REF[1]*u[1]+BAND_REF[2]*u[2];
 const t=BAND_REF.map((v,i)=>v-d*u[i]),tn=Math.hypot(...t),n=t.map(v=>v/tn);
 const v=[n[1]*u[2]-n[2]*u[1],n[2]*u[0]-n[0]*u[2],n[0]*u[1]-n[1]*u[0]];
 return [u,v,n];
}
const [BAND_U1,BAND_V,BAND_N]=bandBasis();
function bandDir(a,g){
 const x=BAND_U1[0]*Math.cos(a)+BAND_V[0]*Math.sin(a)+BAND_N[0]*g;
 const y=BAND_U1[1]*Math.cos(a)+BAND_V[1]*Math.sin(a)+BAND_N[1]*g;
 const z=BAND_U1[2]*Math.cos(a)+BAND_V[2]*Math.sin(a)+BAND_N[2]*g;
 const n=Math.hypot(x,y,z);
 return [x/n,y/n,z/n];
}
const bandStars=Array.from({length:coarse?4200:9000},(_,i)=>{
 const a=hash(i,410)*TAU,g=(hash(i,411)+hash(i,412)+hash(i,413)-1.5)*.085,mag=Math.pow(hash(i,414),2.4);
 const d=bandDir(a,g);
 return {x:d[0],y:d[1],z:d[2],size:.34+mag*2.4,mag,phase:hash(i,415)*TAU};
});""",
    """/* The band the corridor runs inside. Its plane is rebuilt from the camera basis
 * every frame rather than pinned to the world horizon: the camera director spends
 * most of its time pitched ~74 degrees down at the fleet, so a horizon-locked band
 * is out of shot almost always. The plane contains the view direction - the band
 * therefore always crosses the frame - rolled .62 rad so it runs diagonally. */
function bandBasisNow(){
 const fl=Math.hypot(camera.forward[0],camera.forward[1],camera.forward[2])||1;
 const f=[camera.forward[0]/fl,camera.forward[1]/fl,camera.forward[2]/fl];
 const d=camera.up[0]*f[0]+camera.up[1]*f[1]+camera.up[2]*f[2];
 let u=[camera.up[0]-d*f[0],camera.up[1]-d*f[1],camera.up[2]-d*f[2]];
 const ul=Math.hypot(u[0],u[1],u[2])||1;u=[u[0]/ul,u[1]/ul,u[2]/ul];
 const c=[f[1]*u[2]-f[2]*u[1],f[2]*u[0]-f[0]*u[2],f[0]*u[1]-f[1]*u[0]];
 const th=.62,ct=Math.cos(th),st=Math.sin(th);
 let n=[u[0]*ct+c[0]*st,u[1]*ct+c[1]*st,u[2]*ct+c[2]*st];
 const nl=Math.hypot(n[0],n[1],n[2])||1;n=[n[0]/nl,n[1]/nl,n[2]/nl];
 const v=[n[1]*f[2]-n[2]*f[1],n[2]*f[0]-n[0]*f[2],n[0]*f[1]-n[1]*f[0]];
 return [f,v,n];
}
/* a is fixed per star, so its sine and cosine are precomputed; only the basis
 * changes per frame. */
const bandStars=Array.from({length:coarse?4200:9000},(_,i)=>{
 const a=hash(i,410)*TAU,g=(hash(i,411)+hash(i,412)+hash(i,413)-1.5)*.085,mag=Math.pow(hash(i,414),2.4);
 return {ca:Math.cos(a),sa:Math.sin(a),g,size:.34+mag*2.4,mag,phase:hash(i,415)*TAU};
});""")

rep("""  const col=blend(p.sun,p.paper,.34),segs=[];
  let cur=null;
  for(let i=0;i<=260;i++){
   const d=bandDir(i/260*TAU,0),q=skyPoint(d);""",
    """  const [BU,BV,BN]=bandBasisNow();
  const bdir=(ca,sa,g)=>{const x=BU[0]*ca+BV[0]*sa+BN[0]*g,y=BU[1]*ca+BV[1]*sa+BN[1]*g,z=BU[2]*ca+BV[2]*sa+BN[2]*g,n=Math.hypot(x,y,z)||1;return [x/n,y/n,z/n];};
  const col=blend(p.sun,p.paper,.34),segs=[];
  let cur=null;
  for(let i=0;i<=260;i++){
   const a2=i/260*TAU,d=bdir(Math.cos(a2),Math.sin(a2),0),q=skyPoint(d);""")

rep("""  for(const st of bandStars){
   const q=skyPoint([st.x,st.y,st.z]);if(!q)continue;""",
    """  for(const st of bandStars){
   const q=skyPoint(bdir(st.ca,st.sa,st.g));if(!q)continue;""")

open(P, 'w', encoding='utf-8', newline='').write(s)
print("V4j applied:", len(s), "bytes")
