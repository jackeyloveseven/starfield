"""MEASURE ONLY - what is the ACTUAL distribution of the massive bodies?

Loads the page in headless Chrome (SwiftShader), drives a long simulated run and
reads, for every rendered mass, its world offset from the lane, its height, the
z-gap to its neighbour, and its screen position/size. Reports histograms split by
lattice body vs star-system body (orbiting).

  python -I measure.py <html> [seed] [totalSeconds] [stepSeconds]

Adds a temporary _dbg() accessor to the COPY it is handed; the live file is
never touched.
"""
import re, sys, os, json, subprocess, tempfile

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HTML = sys.argv[1]
SEED = sys.argv[2] if len(sys.argv) > 2 else '1a2b'
TOTAL = float(sys.argv[3]) if len(sys.argv) > 3 else 6000.0
STEP = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0

DBG = (
 "_dbg:()=>{const k0=Math.floor(camera.eye[2]/CHUNK),cs=[];"
 "for(let k=k0-9;k<=k0+9;k++)cs.push(chunk(k));stepOrbits();const out=[];"
 "for(const c of cs)for(const m of c.masses){const pj=project([m.x,m.y,m.z]);"
 "if(!pj||pj[2]>18000)continue;"
 "out.push([Math.round(m.x-laneX(m.z)),Math.round(m.y),Math.round(m.z),Math.round(m.r),"
 "m.kind,m.orb?1:0,Math.round(pj[0]),Math.round(pj[1]),Math.round(pj[2]),+(m.r*pj[3]).toFixed(1),c.k]);}"
 "const f=flockCentre();"
 "return {W,H,cx:camera.cx,cy:camera.cy,yaw:camera.yaw,pitch:camera.pitch,travel,lane:laneX(travel),fleet:[f[0],f[1],f[2]],m:out};},"
)

JS = r'''<script>window.__m={frames:0,bodies:0,onScreen:0,zeroFrames:0,nearEdge:0,clipped:0,
 offHL:{},offHS:{},yHL:{},yHS:{},zH:{},srHL:{},srHS:{},sxfH:{},syfH:{},nH:{},nH2:{},kindHL:{},kindHS:{},
 nSysH:{},nLatH:{},nChunkH:{},yawH:{},depthH:{},sxfF:{},syfF:{},nF:0,
 sysFrames:0,latOnlyFrames:0,fwdFrames:0,zeroFwd:0,fwdBig:0,zeroFwdBig:0,
 overlapFrames:0,overlapPairs:0,bad:false,minTravel:1e9,maxTravel:-1e9,W:0,H:0,cx:0,cy:0,onBig:0,zeroBig:0,
 offSumL:0,offSumS:0,nL:0,nS:0,offMax:0,offMin:1e9,bigOff:0,yLmin:1e9,yLmax:-1e9,ySmin:1e9,ySmax:-1e9};
function B(o,k){o[k]=(o[k]||0)+1;}
try{
 const d=document.querySelectorAll(".destination")[0];if(d)d.click();
 const b=document.getElementById("begin");if(b)b.click();
 document.getElementById("intro").style.display='none';
 const S=window.Starfield,r=window.__m;
 for(let i=0;i<__N__;i++){
  S.seek(__STEP__);
  const g=S._dbg();r.frames++;
  if(g.travel<r.minTravel)r.minTravel=g.travel;if(g.travel>r.maxTravel)r.maxTravel=g.travel;
  const W=g.W,H=g.H,cx=g.cx,cy=g.cy,list=g.m;
  if(r.frames===1){r.W=W;r.H=H;r.cx=Math.round(cx);r.cy=Math.round(cy);}
  {let deg=g.yaw*180/Math.PI;deg=((deg%360)+360)%360;B(r.yawH,Math.min(23,Math.floor(deg/15)));
   r.__fwd=(deg<25||deg>335);}
  if(!r.yawRaw){r.yawRaw=[g.yaw,g.pitch,g.W,g.H,g.cx,g.cy];}
  else if(r.yawRaw.length<6){r.yawRaw.push(g.yaw);}
  if(r.yawMin===undefined||g.yaw<r.yawMin)r.yawMin=g.yaw;
  if(r.yawMax===undefined||g.yaw>r.yawMax)r.yawMax=g.yaw;
  if(!list.every(v=>v.every(Number.isFinite)))r.bad=true;
  r.bodies+=list.length;
  const zs=list.map(v=>v[2]).sort((a,b)=>a-b);
  for(let j=1;j<zs.length;j++){const gp=zs[j]-zs[j-1];B(r.zH,Math.min(15,Math.floor(gp/400)));}
  let on=0,onBig=0,onSys=0,onLat=0;const scr=[],chset=new Set();
  for(const v of list){
   const off=Math.abs(v[0]),y=v[1],rad=v[9],sx=v[6],sy=v[7],orb=v[5];
   B(orb?r.offHS:r.offHL,Math.min(15,Math.floor(off/500)));
   B(orb?r.yHS:r.yHL,Math.max(0,Math.min(39,Math.floor((y+3000)/100))));
   B(orb?r.srHS:r.srHL,Math.min(9,Math.floor(rad/40)));
   B(orb?r.kindHS:r.kindHL,v[4]);
   if(orb){r.nS++;r.offSumS+=off;if(y<r.ySmin)r.ySmin=y;if(y>r.ySmax)r.ySmax=y;}
   else{r.nL++;r.offSumL+=off;if(y<r.yLmin)r.yLmin=y;if(y>r.yLmax)r.yLmax=y;}
   if(off>r.offMax)r.offMax=off;if(off<r.offMin)r.offMin=off;if(off>3000)r.bigOff++;
   const inside=(sx>=0&&sx<=W&&sy>=0&&sy<=H);
   if(inside){on++;r.onScreen++;chset.add(v[10]);
     B(r.depthH,Math.min(9,Math.floor(v[8]/2000)));
     if(orb)onSys++;else onLat++;
     if(rad>=30){onBig++;r.onBig++;}
     B(r.sxfH,Math.min(9,Math.floor(sx/W*10)));B(r.syfH,Math.min(9,Math.floor(sy/H*10)));
     if(r.__fwd){r.nF++;B(r.sxfF,Math.min(9,Math.floor(sx/W*10)));B(r.syfF,Math.min(9,Math.floor(sy/H*10)));}
     if(sx<W*.25||sx>W*.75||sy<H*.25||sy>H*.75)r.nearEdge++;
     if(sx-rad<0||sx+rad>W||sy-rad<0||sy+rad>H)r.clipped++;
     scr.push([sx,sy,rad]);}
  }
  if(on===0)r.zeroFrames++;
  if(onBig===0)r.zeroBig++;
  if(r.__fwd){r.fwdFrames++;if(on===0)r.zeroFwd++;if(onBig===0)r.zeroFwdBig++;}  B(r.nH,Math.min(20,on));
  B(r.nH2,Math.min(20,onBig));
  B(r.nSysH,Math.min(12,onSys));B(r.nLatH,Math.min(12,onLat));
  B(r.nChunkH,Math.min(12,chset.size));
  if(onSys>0)r.sysFrames++;else if(on>0)r.latOnlyFrames++;
  let of=false;
  for(let a=0;a<scr.length;a++)for(let c=a+1;c<scr.length;c++){
   const dx=scr[a][0]-scr[c][0],dy=scr[a][1]-scr[c][1];
   if(Math.hypot(dx,dy)<(scr[a][2]+scr[c][2])*.8){r.overlapPairs++;of=true;}
  }
  if(of)r.overlapFrames++;
 }
 r.avgOffL=r.nL?Math.round(r.offSumL/r.nL):0;
 r.avgOffS=r.nS?Math.round(r.offSumS/r.nS):0;
 r.minTravel=Math.round(r.minTravel);r.maxTravel=Math.round(r.maxTravel);
 document.title=JSON.stringify(r);
}catch(e){document.title=JSON.stringify({probeError:String(e),stack:String(e&&e.stack).slice(0,500)});}</script>'''

src = open(HTML, encoding='utf-8').read()
anchor = 'window.Starfield=Object.freeze({'
assert src.count(anchor) == 1, 'anchor for _dbg must occur exactly once'
src = src.replace(anchor, anchor + '\n ' + DBG, 1)
assert src.count('</body>') == 1, 'body anchor must occur exactly once'
probe = JS.replace('__N__', str(int(TOTAL / STEP))).replace('__STEP__', str(STEP))
src = src.replace('</body>', probe + '</body>', 1)

out = os.path.abspath('shots/_measure_place.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8', newline='').write(src)

with tempfile.TemporaryDirectory(prefix='meas-') as prof:
    r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--use-angle=swiftshader',
                        '--enable-unsafe-swiftshader', '--disable-gpu-compositing', '--no-sandbox',
                        '--mute-audio', '--hide-scrollbars', '--no-first-run', '--disable-extensions',
                        '--disable-background-networking', '--window-size=1600,900',
                        f'--user-data-dir={prof}', '--dump-dom',
                        'file:///' + out.replace('\\', '/') + f'?seed={SEED}'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=1800)

m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S)
if not m:
    sys.exit('NO TITLE - ' + (r.stderr or '')[-400:])
d = json.loads(m.group(1))
if d.get('probeError'):
    sys.exit('PROBE FAILED: ' + d['probeError'] + ' ' + (d.get('stack') or ''))

def hist(name, h, labels, tot):
    print(f'  {name} (n={sum(h.values())}):')
    for k in sorted(h, key=lambda s: int(s)):
        print(f'    {labels(int(k)):<16} {h[k]:>7}  {h[k]/max(1,tot)*100:5.1f}%')

F = d['frames']
print(f'=== mass placement, seed={SEED} total={TOTAL}s step={STEP}s ===')
print(f'frames={F}  projected bodies={d["bodies"]} avg/frame={d["bodies"]/max(1,F):.2f}  '
      f'travel={d["minTravel"]}..{d["maxTravel"]}  nan={d["bad"]}  W={d["W"]} H={d["H"]} cx={d["cx"]} cy={d["cy"]}')
print(f'lattice bodies={d["nL"]}  system(orbiting) bodies={d["nS"]}  '
      f'ratio={d["nS"]/max(1,d["nL"]+d["nS"])*100:.0f}% orbiting')
print(f'on-screen bodies={d["onScreen"]} ({d["onScreen"]/max(1,d["bodies"])*100:.1f}% of projected)')
print()
print('--- world offset |x-laneX(z)| (500u bins) ---')
hist('LATTICE', d['offHL'], lambda k: f'{k*500}-{k*500+500}' + ('+' if k == 15 else ''), d['nL'])
hist('SYSTEM ', d['offHS'], lambda k: f'{k*500}-{k*500+500}' + ('+' if k == 15 else ''), d['nS'])
print(f'  off min={d["offMin"]} max={d["offMax"]}  >3000u: {d["bigOff"]} ({d["bigOff"]/max(1,d["bodies"])*100:.1f}%)')
print(f'  avg off lattice={d["avgOffL"]}  system={d["avgOffS"]}')
print()
print('--- world height y (100u bins, -3000..1000) ---')
hist('LATTICE', d['yHL'], lambda k: f'{k*100-3000}-{k*100-2900}', d['nL'])
hist('SYSTEM ', d['yHS'], lambda k: f'{k*100-3000}-{k*100-2900}', d['nS'])
print(f'  y range lattice={d["yLmin"]}..{d["yLmax"]}   system={d["ySmin"]}..{d["ySmax"]}')
print()
print('--- z-gap to previous body (400u bins) ---')
hist('ALL', d['zH'], lambda k: f'{k*400}-{k*400+400}' + ('+' if k == 15 else ''), sum(d['zH'].values()))
print()
print('--- on-screen radius px (40px bins) ---')
hist('LATTICE', d['srHL'], lambda k: f'{k*40}-{k*40+40}' + ('+' if k == 9 else ''), sum(d['srHL'].values()))
hist('SYSTEM ', d['srHS'], lambda k: f'{k*40}-{k*40+40}' + ('+' if k == 9 else ''), sum(d['srHS'].values()))
print()
print('--- bodies on screen per frame ---')
hist('COUNT', d['nH'], lambda k: str(k) + ('+' if k == 20 else ''), F)
print(f'  frames with ZERO on-screen bodies: {d["zeroFrames"]} ({d["zeroFrames"]/max(1,F)*100:.1f}%)')
print('--- bodies on screen per frame, radius>=30px only (real worlds, not specks) ---')
hist('COUNT2', d['nH2'], lambda k: str(k) + ('+' if k == 20 else ''), F)
print(f'  frames with ZERO on-screen world >=30px: {d["zeroBig"]} ({d["zeroBig"]/max(1,F)*100:.1f}%)')
print('--- on-screen count split: SYSTEM(orbiting) vs LATTICE, and distinct chunks on screen ---')
hist('SYSTEM ', d['nSysH'], lambda k: str(k) + ('+' if k == 12 else ''), F)
hist('LATTICE', d['nLatH'], lambda k: str(k) + ('+' if k == 12 else ''), F)
hist('CHUNKS ', d['nChunkH'], lambda k: str(k) + ('+' if k == 12 else ''), F)
print(f'  frames showing >=1 orbiting body: {d["sysFrames"]} ({d["sysFrames"]/max(1,F)*100:.1f}%)'
      f'  frames showing only lattice bodies: {d["latOnlyFrames"]} ({d["latOnlyFrames"]/max(1,F)*100:.1f}%)')
print(f'  camera facing down-corridor (|mod-yaw|<25deg): {d["fwdFrames"]} frames ({d["fwdFrames"]/max(1,F)*100:.1f}%)')
print(f'    of those, ZERO bodies on screen : {d["zeroFwd"]} ({d["zeroFwd"]/max(1,d["fwdFrames"])*100:.1f}%)')
print(f'    of those, ZERO bodies >=30px    : {d["zeroFwdBig"]} ({d["zeroFwdBig"]/max(1,d["fwdFrames"])*100:.1f}%)')
print(f'  on-screen bodies while facing down-corridor: {d["nF"]}')
print('    x/W:', {k: round(v/max(1,d["nF"])*100) for k, v in sorted(d["sxfF"].items(), key=lambda kv: int(kv[0]))})
print('    y/H:', {k: round(v/max(1,d["nF"])*100) for k, v in sorted(d["syfF"].items(), key=lambda kv: int(kv[0]))})
print('--- camera yaw (15deg bins, 0..360) ---')
print('  raw samples [yaw,pitch,W,H,cx,cy, yaw2, yaw3]:', d.get('yawRaw'), ' yawMin/Max:', d.get('yawMin'), d.get('yawMax'))
hist('YAW', d['yawH'], lambda k: f'{k*15}-{k*15+15}', F)
print('--- depth (camera-forward distance) of on-screen bodies (2000u bins) ---')
hist('DEPTH', d['depthH'], lambda k: f'{k*2000}-{k*2000+2000}' + ('+' if k == 9 else ''), d['onScreen'])
print()
print('--- screen position (fraction of W / H) ---')
hist('x/W', d['sxfH'], lambda k: f'{k/10:.1f}-{(k+1)/10:.1f}', d['onScreen'])
hist('y/H', d['syfH'], lambda k: f'{k/10:.1f}-{(k+1)/10:.1f}', d['onScreen'])
print(f'  within outer 25% band of an edge: {d["nearEdge"]} ({d["nearEdge"]/max(1,d["onScreen"])*100:.1f}% of on-screen)')
print(f'  disc clipped by frame edge      : {d["clipped"]} ({d["clipped"]/max(1,d["onScreen"])*100:.1f}%)')
print(f'  frames with >=1 overlapping pair: {d["overlapFrames"]} ({d["overlapFrames"]/max(1,F)*100:.1f}%) pairs={d["overlapPairs"]}')
print()
print('  kinds lattice:', {k: v for k, v in sorted(d['kindHL'].items(), key=lambda kv: int(kv[0]))})
print('  kinds system :', {k: v for k, v in sorted(d['kindHS'].items(), key=lambda kv: int(kv[0]))})
