# -*- coding: utf-8 -*-
"""
tools/apply_engine_opt.py
Applies Starfield core engine optimizations:
1. Zero-GC Pooling system for project(), clipped(), poly(), line(), sprite(), glow() and queue
2. Reset frame pools per frame in frame()
3. FleetFormations zero-GC slot caching & updateBirds gravity zero-allocation
4. bodies() chunk collection reuse and direct entity passing to project()
5. Starfield CPU fallback clamping (350 mobile / 1800 desktop)
6. bandStars CPU fallback clamping (180 mobile / 1200 desktop)
7. Mobile DPR Safety Clamping (1.5 default, 1.75 limit in 2K mode)
8. Mirror starfield.html to android/app/src/main/assets/starfield.html with SHA256 check
"""
import os
import shutil
import hashlib

src_path = r'd:\items\code\projects\starfield\starfield-pub\starfield.html'
with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# 1. Zero-GC Pooling System
old_painter = '''/* A compact painter\'s renderer, with near-plane clipping and distance haze. */
let queue=[],drawCalls=0,fillPx=0;
function view(p){
 const px = p.x !== undefined ? p.x : p[0];
 const py = p.y !== undefined ? p.y : p[1];
 const pz = p.z !== undefined ? p.z : p[2];
 const x = px - camera.eye[0], y = py - camera.eye[1], z = pz - camera.eye[2];
 const r = camera.right, u = camera.up, f = camera.forward;
 return [x*r[0] + y*r[1] + z*r[2], x*u[0] + y*u[1] + z*u[2], x*f[0] + y*f[1] + z*f[2]];
}
function project(p){
 const px = p.x !== undefined ? p.x : p[0];
 const py = p.y !== undefined ? p.y : p[1];
 const pz = p.z !== undefined ? p.z : p[2];
 const x = px - camera.eye[0], y = py - camera.eye[1], z = pz - camera.eye[2];
 const f = camera.forward;
 const vz = x*f[0] + y*f[1] + z*f[2];
 if(vz < 18) return null;
 const k = camera.focal / vz;
 const r = camera.right, u = camera.up;
 return [camera.cx + (x*r[0] + y*r[1] + z*r[2]) * k, camera.cy - (x*u[0] + y*u[1] + z*u[2]) * k, vz, k];
}
function clipped(points){
 const n = points.length;
 if(n < 3) return null;
 let allIn = true, anyIn = false;
 const v = new Array(n);
 const r0 = camera.right[0], r1 = camera.right[1], r2 = camera.right[2];
 const u0 = camera.up[0], u1 = camera.up[1], u2 = camera.up[2];
 const f0 = camera.forward[0], f1 = camera.forward[1], f2 = camera.forward[2];
 for(let i = 0; i < n; i++){
  const pt = points[i];
  const px = pt.x !== undefined ? pt.x : pt[0];
  const py = pt.y !== undefined ? pt.y : pt[1];
  const pz = pt.z !== undefined ? pt.z : pt[2];
  const x = px - camera.eye[0], y = py - camera.eye[1], z = pz - camera.eye[2];
  const vx = x*r0 + y*r1 + z*r2;
  const vy = x*u0 + y*u1 + z*u2;
  const vz = x*f0 + y*f1 + z*f2;
  v[i] = [vx, vy, vz];
  if(vz >= 18){ anyIn = true; } else { allIn = false; }
 }
 if(!anyIn) return null;
 const out = allIn ? v : [];
 if(!allIn){
  for(let i = 0; i < n; i++){
   const a = v[i], b = v[(i + 1) % n], ia = a[2] >= 18, ib = b[2] >= 18;
   if(ia) out.push(a);
   if(ia !== ib){
    const t = (18 - a[2]) / (b[2] - a[2]);
    out.push([mix(a[0], b[0], t), mix(a[1], b[1], t), 18]);
   }
  }
  if(out.length < 3) return null;
 }
 let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity, d = 0;
 const outLen = out.length;
 const p = new Array(outLen);
 for(let i = 0; i < outLen; i++){
  const a = out[i];
  const k = camera.focal / a[2];
  const x = camera.cx + a[0] * k;
  const y = camera.cy - a[1] * k;
  minX = Math.min(minX, x); maxX = Math.max(maxX, x);
  minY = Math.min(minY, y); maxY = Math.max(maxY, y);
  d += a[2];
  p[i] = [x, y];
 }
 if(maxX < -15 || minX > W + 15 || maxY < -15 || minY > H + 15) return null;
 return {p, d: d / outLen};
}
function haze(c,d,p=currentPalette){const h=smooth((d-2000)/(p.wash>0?9000:15000))*(.70+p.wash*.24);return blend(c,p.fog,h);}
function poly(points,c,options={}){
 const p=clipped(points);if(!p)return;
 queue.push({type:0,...p,c:css(options.noFog?c:haze(c,p.d,options.palette||currentPalette)),alpha:options.alpha??1,stroke:options.stroke,width:options.width||.45});
}
function line(points,c,alpha=1,width=1){
 if(points.length===2){
  const va=view(points[0]), vb=view(points[1]);
  const aIn=va[2]>=18, bIn=vb[2]>=18;
  if(!aIn && !bIn) return;
  let p0, p1;
  if(aIn && bIn){
   p0 = project(points[0]); p1 = project(points[1]);
  } else {
   const t = (18 - va[2]) / (vb[2] - va[2]);
   const cv = [mix(va[0], vb[0], t), mix(va[1], vb[1], t), 18];
   const k = camera.focal / 18;
   const cp = [camera.cx + cv[0] * k, camera.cy - cv[1] * k, 18, k];
   p0 = aIn ? project(points[0]) : cp;
   p1 = bIn ? project(points[1]) : cp;
  }
  if(!p0 || !p1) return;
  if((p0[0]<-10&&p1[0]<-10)||(p0[0]>W+10&&p1[0]>W+10)||(p0[1]<-10&&p1[1]<-10)||(p0[1]>H+10&&p1[1]>H+10)) return;
  const d=(p0[2]+p1[2])*0.5;
  queue.push({type:1,p:[p0,p1],d,c:css(haze(c,d)),alpha,width});
  return;
 }
 const p=points.map(project);if(p.some(v=>!v))return;
 if(p.every(v=>v[0]<-10)||p.every(v=>v[0]>W+10)||p.every(v=>v[1]<-10)||p.every(v=>v[1]>H+10))return;
 const d=p.reduce((s,v)=>s+v[2],0)/p.length;
 queue.push({type:1,p,d,c:css(haze(c,d)),alpha,width});
}
/* A soft radial bloom that takes part in the depth sort, so a glow can sit
 * behind the nearer shards instead of over everything. No 60px sprite clamp. */
function glow(world,size,c,alpha=1,spread=3){const p=project(world);if(!p)return;const s=clamp(size*p[3],1,Math.max(W,H)*.7);const r=s*spread;if(p[0]+r<-20||p[0]-r>W+20||p[1]+r<-20||p[1]-r>H+20)return;queue.push({type:3,p,d:p[2],s,c,alpha,spread});}
function sprite(world,size,c,kind,alpha=1,rotation=0){const p=project(world);if(!p)return;const s=clamp(size*p[3],.4,60);const m=kind==='firefly'?s*4:Math.max(40,s*1.8);if(p[0]<-m||p[0]>W+m||p[1]<-m||p[1]>H+m)return;queue.push({type:2,p,d:p[2],s:clamp(size*p[3],.4,60),c:css(haze(c,p[2])),alpha,kind,rotation});}
function flush(){
 queue.sort((a,b)=>(b.d||0)-(a.d||0));
 for(const o of queue){
  ctx.globalAlpha=o.alpha;
  if(o.type===0){ctx.beginPath();ctx.moveTo(o.p[0][0],o.p[0][1]);for(let i=1;i<o.p.length;i++)ctx.lineTo(o.p[i][0],o.p[i][1]);ctx.closePath();ctx.fillStyle=o.c;ctx.fill();if(o.stroke){ctx.strokeStyle=o.stroke;ctx.lineWidth=o.width;ctx.stroke();}}
  else if(o.type===1){ctx.beginPath();ctx.moveTo(o.p[0][0],o.p[0][1]);for(let i=1;i<o.p.length;i++)ctx.lineTo(o.p[i][0],o.p[i][1]);ctx.strokeStyle=o.c;ctx.lineWidth=o.width;ctx.stroke();}
  else if(o.type===2){
   const [x,y]=o.p,s=o.s;ctx.fillStyle=o.c;ctx.strokeStyle=o.c;
   if(o.kind==='petal'){ctx.save();ctx.translate(x,y);ctx.rotate(o.rotation);ctx.beginPath();ctx.moveTo(-s,0);ctx.quadraticCurveTo(-s*.3,-s*.85,s,0);ctx.quadraticCurveTo(s*.2,s*.75,-s,0);ctx.fill();ctx.restore();}
   else if(o.kind==='snow'&&s>1.3){ctx.save();ctx.translate(x,y);ctx.rotate(o.rotation);ctx.lineWidth=.6;ctx.beginPath();for(let k=0;k<3;k++){const a=k*Math.PI/3;ctx.moveTo(-Math.cos(a)*s,-Math.sin(a)*s);ctx.lineTo(Math.cos(a)*s,Math.sin(a)*s);}ctx.stroke();ctx.restore();}
   else if(o.kind==='firefly'){const g=ctx.createRadialGradient(x,y,0,x,y,s*4);g.addColorStop(0,o.c);g.addColorStop(.23,css([218,232,153],.3));g.addColorStop(1,'rgba(218,232,153,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,s*4,0,TAU);ctx.fill();}
   else{ctx.beginPath();ctx.ellipse(x,y,s,o.kind==='smoke'?s*.75:s,0,0,TAU);ctx.fill();}
  }
  else if(o.type===4){if(o.alpha<1){ctx.save();ctx.globalAlpha=o.alpha;o.fn();ctx.restore();}else o.fn();}
  else if(o.type===3){const g=ctx.createRadialGradient(o.p[0],o.p[1],0,o.p[0],o.p[1],o.s*o.spread);fillPx+=o.s*o.spread*2*(o.s*o.spread*2);g.addColorStop(0,css(o.c,.95));g.addColorStop(.28,css(o.c,.40));g.addColorStop(.62,css(o.c,.11));g.addColorStop(1,css(o.c,0));ctx.fillStyle=g;ctx.fillRect(o.p[0]-o.s*o.spread,o.p[1]-o.s*o.spread,o.s*o.spread*2,o.s*o.spread*2);}
 }
 drawCalls+=queue.length;queue.length=0;ctx.globalAlpha=1;
}'''

new_painter = '''/* A compact painter\'s renderer, with near-plane clipping and distance haze. */
let queue=[],drawCalls=0,fillPx=0;

// BUILD 198 ZERO-GC POOLING SYSTEM FOR HOT LOOP
const _PROJ_POOL_SIZE = 8192;
const _projPool = Array.from({length: _PROJ_POOL_SIZE}, () => [0, 0, 0, 0]);
let _projPoolIdx = 0;

const _CLIP_PT2_POOL_SIZE = 8192;
const _clipPt2Pool = Array.from({length: _CLIP_PT2_POOL_SIZE}, () => [0, 0]);
let _pt2PoolIdx = 0;

const _CLIP_PT3_POOL_SIZE = 2048;
const _clipPt3Pool = Array.from({length: _CLIP_PT3_POOL_SIZE}, () => [0, 0, 0]);
let _pt3PoolIdx = 0;

const _CLIP_RES_POOL_SIZE = 4096;
const _clipResPool = Array.from({length: _CLIP_RES_POOL_SIZE}, () => ({p: null, d: 0}));
let _clipResPoolIdx = 0;

const _clipV = [];
const _clipOut = [];

const _QUEUE_POOL_SIZE = 4096;
const _qPool = Array.from({length: _QUEUE_POOL_SIZE}, () => ({
  type: 0, p: null, d: 0, c: '', alpha: 1, stroke: null, width: 0, s: 0, kind: '', rotation: 0, spread: 3, fn: null
}));
let _qPoolIdx = 0;

function getQueueEntry() {
  const item = (_qPoolIdx < _qPool.length) ? _qPool[_qPoolIdx++] : {
    type: 0, p: null, d: 0, c: '', alpha: 1, stroke: null, width: 0, s: 0, kind: '', rotation: 0, spread: 3, fn: null
  };
  queue.push(item);
  return item;
}

function resetFramePools() {
  _projPoolIdx = 0;
  _pt2PoolIdx = 0;
  _pt3PoolIdx = 0;
  _clipResPoolIdx = 0;
  _qPoolIdx = 0;
}

function view(p){
 const px = p.x !== undefined ? p.x : p[0];
 const py = p.y !== undefined ? p.y : p[1];
 const pz = p.z !== undefined ? p.z : p[2];
 const x = px - camera.eye[0], y = py - camera.eye[1], z = pz - camera.eye[2];
 const r = camera.right, u = camera.up, f = camera.forward;
 return [x*r[0] + y*r[1] + z*r[2], x*u[0] + y*u[1] + z*u[2], x*f[0] + y*f[1] + z*f[2]];
}
function projectXYZ(px, py, pz) {
 const x = px - camera.eye[0], y = py - camera.eye[1], z = pz - camera.eye[2];
 const f = camera.forward;
 const vz = x*f[0] + y*f[1] + z*f[2];
 if(vz < 18) return null;
 const k = camera.focal / vz;
 const r = camera.right, u = camera.up;
 const res = (_projPoolIdx < _PROJ_POOL_SIZE) ? _projPool[_projPoolIdx++] : [0, 0, 0, 0];
 res[0] = camera.cx + (x*r[0] + y*r[1] + z*r[2]) * k;
 res[1] = camera.cy - (x*u[0] + y*u[1] + z*u[2]) * k;
 res[2] = vz;
 res[3] = k;
 return res;
}
function project(p){
 if (!p) return null;
 const px = p.x !== undefined ? p.x : p[0];
 const py = p.y !== undefined ? p.y : p[1];
 const pz = p.z !== undefined ? p.z : p[2];
 return projectXYZ(px, py, pz);
}
function clipped(points){
 const n = points.length;
 if(n < 3) return null;
 let allIn = true, anyIn = false;
 _clipV.length = n;
 const r0 = camera.right[0], r1 = camera.right[1], r2 = camera.right[2];
 const u0 = camera.up[0], u1 = camera.up[1], u2 = camera.up[2];
 const f0 = camera.forward[0], f1 = camera.forward[1], f2 = camera.forward[2];
 const ce0 = camera.eye[0], ce1 = camera.eye[1], ce2 = camera.eye[2];
 for(let i = 0; i < n; i++){
  const pt = points[i];
  const px = pt.x !== undefined ? pt.x : pt[0];
  const py = pt.y !== undefined ? pt.y : pt[1];
  const pz = pt.z !== undefined ? pt.z : pt[2];
  const x = px - ce0, y = py - ce1, z = pz - ce2;
  const vx = x*r0 + y*r1 + z*r2;
  const vy = x*u0 + y*u1 + z*u2;
  const vz = x*f0 + y*f1 + z*f2;
  const v_i = (_pt3PoolIdx < _CLIP_PT3_POOL_SIZE) ? _clipPt3Pool[_pt3PoolIdx++] : [0, 0, 0];
  v_i[0] = vx; v_i[1] = vy; v_i[2] = vz;
  _clipV[i] = v_i;
  if(vz >= 18){ anyIn = true; } else { allIn = false; }
 }
 if(!anyIn) return null;
 let out;
 if(allIn){
  out = _clipV;
 } else {
  _clipOut.length = 0;
  for(let i = 0; i < n; i++){
   const a = _clipV[i], b = _clipV[(i + 1) % n], ia = a[2] >= 18, ib = b[2] >= 18;
   if(ia) _clipOut.push(a);
   if(ia !== ib){
    const t = (18 - a[2]) / (b[2] - a[2]);
    const ptMid = (_pt3PoolIdx < _CLIP_PT3_POOL_SIZE) ? _clipPt3Pool[_pt3PoolIdx++] : [0, 0, 0];
    ptMid[0] = mix(a[0], b[0], t);
    ptMid[1] = mix(a[1], b[1], t);
    ptMid[2] = 18;
    _clipOut.push(ptMid);
   }
  }
  if(_clipOut.length < 3) return null;
  out = _clipOut;
 }
 let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity, d = 0;
 const outLen = out.length;
 const p = new Array(outLen);
 const focal = camera.focal, cx = camera.cx, cy = camera.cy;
 for(let i = 0; i < outLen; i++){
  const a = out[i];
  const k = focal / a[2];
  const x = cx + a[0] * k;
  const y = cy - a[1] * k;
  minX = Math.min(minX, x); maxX = Math.max(maxX, x);
  minY = Math.min(minY, y); maxY = Math.max(maxY, y);
  d += a[2];
  const p_i = (_pt2PoolIdx < _CLIP_PT2_POOL_SIZE) ? _clipPt2Pool[_pt2PoolIdx++] : [0, 0];
  p_i[0] = x; p_i[1] = y;
  p[i] = p_i;
 }
 if(maxX < -15 || minX > W + 15 || maxY < -15 || minY > H + 15) return null;
 const res = (_clipResPoolIdx < _CLIP_RES_POOL_SIZE) ? _clipResPool[_clipResPoolIdx++] : {p: null, d: 0};
 res.p = p;
 res.d = d / outLen;
 return res;
}
function haze(c,d,p=currentPalette){const h=smooth((d-2000)/(p.wash>0?9000:15000))*(.70+p.wash*.24);return blend(c,p.fog,h);}
function poly(points,c,options={}){
 const p=clipped(points);if(!p)return;
 const entry = getQueueEntry();
 entry.type = 0;
 entry.p = p.p;
 entry.d = p.d;
 entry.c = css(options.noFog?c:haze(c,p.d,options.palette||currentPalette));
 entry.alpha = options.alpha !== undefined ? options.alpha : 1;
 entry.stroke = options.stroke || null;
 entry.width = options.width || 0.45;
 entry.fn = null;
}
function line(points,c,alpha=1,width=1){
 if(points.length===2){
  const va=view(points[0]), vb=view(points[1]);
  const aIn=va[2]>=18, bIn=vb[2]>=18;
  if(!aIn && !bIn) return;
  let p0, p1;
  if(aIn && bIn){
   p0 = project(points[0]); p1 = project(points[1]);
  } else {
   const t = (18 - va[2]) / (vb[2] - va[2]);
   const cv = [mix(va[0], vb[0], t), mix(va[1], vb[1], t), 18];
   const k = camera.focal / 18;
   const cp = [camera.cx + cv[0] * k, camera.cy - cv[1] * k, 18, k];
   p0 = aIn ? project(points[0]) : cp;
   p1 = bIn ? project(points[1]) : cp;
  }
  if(!p0 || !p1) return;
  if((p0[0]<-10&&p1[0]<-10)||(p0[0]>W+10&&p1[0]>W+10)||(p0[1]<-10&&p1[1]<-10)||(p0[1]>H+10&&p1[1]>H+10)) return;
  const d=(p0[2]+p1[2])*0.5;
  const entry = getQueueEntry();
  entry.type = 1;
  entry.p = [p0, p1];
  entry.d = d;
  entry.c = css(haze(c,d));
  entry.alpha = alpha;
  entry.width = width;
  entry.fn = null;
  return;
 }
 const p=points.map(project);if(p.some(v=>!v))return;
 if(p.every(v=>v[0]<-10)||p.every(v=>v[0]>W+10)||p.every(v=>v[1]<-10)||p.every(v=>v[1]>H+10))return;
 const d=p.reduce((s,v)=>s+v[2],0)/p.length;
 const entry = getQueueEntry();
 entry.type = 1;
 entry.p = p;
 entry.d = d;
 entry.c = css(haze(c,d));
 entry.alpha = alpha;
 entry.width = width;
 entry.fn = null;
}
/* A soft radial bloom that takes part in the depth sort, so a glow can sit
 * behind the nearer shards instead of over everything. No 60px sprite clamp. */
function glow(world,size,c,alpha=1,spread=3){
 const p=project(world);if(!p)return;
 const s=clamp(size*p[3],1,Math.max(W,H)*.7);
 const r=s*spread;
 if(p[0]+r<-20||p[0]-r>W+20||p[1]+r<-20||p[1]-r>H+20)return;
 const entry = getQueueEntry();
 entry.type = 3;
 entry.p = p;
 entry.d = p[2];
 entry.s = s;
 entry.c = c;
 entry.alpha = alpha;
 entry.spread = spread;
 entry.fn = null;
}
function sprite(world,size,c,kind,alpha=1,rotation=0){
 const p=project(world);if(!p)return;
 const s=clamp(size*p[3],.4,60);
 const m=kind==='firefly'?s*4:Math.max(40,s*1.8);
 if(p[0]<-m||p[0]>W+m||p[1]<-m||p[1]>H+m)return;
 const entry = getQueueEntry();
 entry.type = 2;
 entry.p = p;
 entry.d = p[2];
 entry.s = s;
 entry.c = css(haze(c,p[2]));
 entry.alpha = alpha;
 entry.kind = kind;
 entry.rotation = rotation;
 entry.fn = null;
}
function flush(){
 queue.sort((a,b)=>(b.d||0)-(a.d||0));
 for(let idx=0;idx<queue.length;idx++){
  const o=queue[idx];
  ctx.globalAlpha=o.alpha;
  if(o.type===0){ctx.beginPath();ctx.moveTo(o.p[0][0],o.p[0][1]);for(let i=1;i<o.p.length;i++)ctx.lineTo(o.p[i][0],o.p[i][1]);ctx.closePath();ctx.fillStyle=o.c;ctx.fill();if(o.stroke){ctx.strokeStyle=o.stroke;ctx.lineWidth=o.width;ctx.stroke();}}
  else if(o.type===1){ctx.beginPath();ctx.moveTo(o.p[0][0],o.p[0][1]);for(let i=1;i<o.p.length;i++)ctx.lineTo(o.p[i][0],o.p[i][1]);ctx.strokeStyle=o.c;ctx.lineWidth=o.width;ctx.stroke();}
  else if(o.type===2){
   const [x,y]=o.p,s=o.s;ctx.fillStyle=o.c;ctx.strokeStyle=o.c;
   if(o.kind==='petal'){ctx.save();ctx.translate(x,y);ctx.rotate(o.rotation);ctx.beginPath();ctx.moveTo(-s,0);ctx.quadraticCurveTo(-s*.3,-s*.85,s,0);ctx.quadraticCurveTo(s*.2,s*.75,-s,0);ctx.fill();ctx.restore();}
   else if(o.kind==='snow'&&s>1.3){ctx.save();ctx.translate(x,y);ctx.rotate(o.rotation);ctx.lineWidth=.6;ctx.beginPath();for(let k=0;k<3;k++){const a=k*Math.PI/3;ctx.moveTo(-Math.cos(a)*s,-Math.sin(a)*s);ctx.lineTo(Math.cos(a)*s,Math.sin(a)*s);}ctx.stroke();ctx.restore();}
   else if(o.kind==='firefly'){const g=ctx.createRadialGradient(x,y,0,x,y,s*4);g.addColorStop(0,o.c);g.addColorStop(.23,css([218,232,153],.3));g.addColorStop(1,'rgba(218,232,153,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,s*4,0,TAU);ctx.fill();}
   else{ctx.beginPath();ctx.ellipse(x,y,s,o.kind==='smoke'?s*.75:s,0,0,TAU);ctx.fill();}
  }
  else if(o.type===4){if(o.alpha<1){ctx.save();ctx.globalAlpha=o.alpha;o.fn();ctx.restore();}else o.fn();}
  else if(o.type===3){const g=ctx.createRadialGradient(o.p[0],o.p[1],0,o.p[0],o.p[1],o.s*o.spread);fillPx+=o.s*o.spread*2*(o.s*o.spread*2);g.addColorStop(0,css(o.c,.95));g.addColorStop(.28,css(o.c,.40));g.addColorStop(.62,css(o.c,.11));g.addColorStop(1,css(o.c,0));ctx.fillStyle=g;ctx.fillRect(o.p[0]-o.s*o.spread,o.p[1]-o.s*o.spread,o.s*o.spread*2,o.s*o.spread*2);}
 }
 drawCalls+=queue.length;queue.length=0;ctx.globalAlpha=1;
 _qPoolIdx=0;
}'''

assert old_painter in text, "old_painter not found"
text = text.replace(old_painter, new_painter, 1)
print("1. Replaced painter zero-gc pooling")

# 2. Reset frame pools at beginning of frame()
old_frame_start = ''' const tFrameStart = performance.now();
 const realDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;'''
new_frame_start = ''' const tFrameStart = performance.now();
 if (typeof resetFramePools === 'function') resetFramePools();
 const realDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;'''
assert old_frame_start in text, "old_frame_start not found"
text = text.replace(old_frame_start, new_frame_start, 1)
print("2. Added resetFramePools to frame()")

# 3. FleetFormations zero-GC slot caching
old_formations_slot = '''  getSlot(i, lead, time, b) {
    if (!lead) return [0, 0, 0];
    const k = (i > LEAD) ? (i - 1) : i;

    // 0: Delta V-Formation (Classic)
    if (this.current === 0) {
      const side = (k % 2 === 0) ? -1 : 1;
      const row = Math.floor(k / 2) + 1;
      return [
        lead.x + side * (row * 36 + Math.sin(time * 0.5 + b.phase) * 8),
        lead.y + ((k % 3) - 1.0) * 12 + Math.sin(time * 0.7 + b.phase) * 6,
        lead.z - row * 44 + Math.cos(time * 0.4 + b.phase) * 10
      ];
    }
    // 1: Echelon Wing (Wide Panoramic Sweep)
    else if (this.current === 1) {
      const span = (k < 6) ? (k - 6) : (k - 5);
      return [
        lead.x + span * 48 + Math.sin(time * 0.6 + b.phase) * 10,
        lead.y + Math.sin(k * 0.5 + time) * 16,
        lead.z - Math.abs(span) * 22 + Math.cos(time * 0.5 + b.phase) * 8
      ];
    }
    // 2: Orbital Ring (Halo Escort - Staggered Dual Concentric Rings)
    else if (this.current === 2) {
      const isOuter = (k >= 7);
      let angle, radius, yOff, zBase;
      if (!isOuter) {
        angle = (k / 7.0) * Math.PI * 2 + time * 0.24;
        radius = 160.0;
        yOff = -12.0;
        zBase = -35.0;
      } else {
        angle = ((k - 7) / 6.0) * Math.PI * 2 + time * 0.18;
        radius = 240.0;
        yOff = 16.0;
        zBase = -105.0;
      }
      return [
        lead.x + Math.cos(angle) * radius,
        lead.y + Math.sin(angle) * (radius * 0.45) + yOff,
        lead.z + zBase + Math.sin(angle * 2) * 12.0
      ];
    }
    // 3: Tandem Needle (Single file aerodynamic column)
    else if (this.current === 3) {
      return [
        lead.x + Math.sin(time * 1.2 + k * 0.3) * 8,
        lead.y + Math.cos(time * 0.9 + k * 0.3) * 6,
        lead.z - (k + 1) * 60
      ];
    }
    // 4: Phoenix Wing (Majestic wide sweep with counter-phase flapping)
    else {
      const span = (k < 6) ? (k - 6) : (k - 5);
      const curve = Math.abs(span) * 0.12;
      return [
        lead.x + span * 56,
        lead.y + Math.sin(time * 1.6 + Math.abs(span) * 0.4) * 24 - curve * 18,
        lead.z - curve * 32 + Math.cos(time * 1.2 + b.phase) * 10
      ];
    }
  }'''

new_formations_slot = '''  _slot: [0, 0, 0],
  getSlot(i, lead, time, b) {
    if (!lead) { this._slot[0]=0; this._slot[1]=0; this._slot[2]=0; return this._slot; }
    const k = (i > LEAD) ? (i - 1) : i;
    const res = this._slot;

    // 0: Delta V-Formation (Classic)
    if (this.current === 0) {
      const side = (k % 2 === 0) ? -1 : 1;
      const row = Math.floor(k / 2) + 1;
      res[0] = lead.x + side * (row * 36 + Math.sin(time * 0.5 + b.phase) * 8);
      res[1] = lead.y + ((k % 3) - 1.0) * 12 + Math.sin(time * 0.7 + b.phase) * 6;
      res[2] = lead.z - row * 44 + Math.cos(time * 0.4 + b.phase) * 10;
      return res;
    }
    // 1: Echelon Wing (Wide Panoramic Sweep)
    else if (this.current === 1) {
      const span = (k < 6) ? (k - 6) : (k - 5);
      res[0] = lead.x + span * 48 + Math.sin(time * 0.6 + b.phase) * 10;
      res[1] = lead.y + Math.sin(k * 0.5 + time) * 16;
      res[2] = lead.z - Math.abs(span) * 22 + Math.cos(time * 0.5 + b.phase) * 8;
      return res;
    }
    // 2: Orbital Ring (Halo Escort - Staggered Dual Concentric Rings)
    else if (this.current === 2) {
      const isOuter = (k >= 7);
      let angle, radius, yOff, zBase;
      if (!isOuter) {
        angle = (k / 7.0) * Math.PI * 2 + time * 0.24;
        radius = 160.0;
        yOff = -12.0;
        zBase = -35.0;
      } else {
        angle = ((k - 7) / 6.0) * Math.PI * 2 + time * 0.18;
        radius = 240.0;
        yOff = 16.0;
        zBase = -105.0;
      }
      res[0] = lead.x + Math.cos(angle) * radius;
      res[1] = lead.y + Math.sin(angle) * (radius * 0.45) + yOff;
      res[2] = lead.z + zBase + Math.sin(angle * 2) * 12.0;
      return res;
    }
    // 3: Tandem Needle (Single file aerodynamic column)
    else if (this.current === 3) {
      res[0] = lead.x + Math.sin(time * 1.2 + k * 0.3) * 8;
      res[1] = lead.y + Math.cos(time * 0.9 + k * 0.3) * 6;
      res[2] = lead.z - (k + 1) * 60;
      return res;
    }
    // 4: Phoenix Wing (Majestic wide sweep with counter-phase flapping)
    else {
      const span = (k < 6) ? (k - 6) : (k - 5);
      const curve = Math.abs(span) * 0.12;
      res[0] = lead.x + span * 56;
      res[1] = lead.y + Math.sin(time * 1.6 + Math.abs(span) * 0.4) * 24 - curve * 18;
      res[2] = lead.z - curve * 32 + Math.cos(time * 1.2 + b.phase) * 10;
      return res;
    }
  }'''
assert old_formations_slot in text, "old_formations_slot not found"
text = text.replace(old_formations_slot, new_formations_slot, 1)
print("3. Replaced FleetFormations slot caching")

# 4. updateBirds zero-GC slot usage and gravity optimization
old_birds = '''   // Dynamic Fleet Formation slot (Delta, Echelon, Orbital Ring, Tandem)
   const [slotX, slotY, slotZ] = FleetFormations.getSlot(i, lead, time, b);

   const escortK = 1.6 + b.k * 0.8;
   const fEscortX = (slotX - b.x) * escortK;
   const fEscortY = (slotY - b.y) * (escortK * 0.85);
   const fEscortZ = (slotZ - b.z) * escortK;

   const fAlignX = alignCount > 0 ? (alignVx / alignCount - b.vx) * 1.4 : 0;
   const fAlignY = alignCount > 0 ? (alignVy / alignCount - b.vy) * 1.1 : 0;
   const fAlignZ = alignCount > 0 ? (alignVz / alignCount - b.vz) * 1.2 : 0;

   const fCohX = cohCount > 0 ? (cohX / cohCount - b.x) * 0.45 : 0;
   const fCohY = cohCount > 0 ? (cohY / cohCount - b.y) * 0.35 : 0;
   const fCohZ = cohCount > 0 ? (cohZ / cohCount - b.z) * 0.45 : 0;

   b.ax = fEscortX + sepX + fAlignX + fCohX;
   b.ay = fEscortY + sepY + fAlignY + fCohY;
   b.az = fEscortZ + sepZ + fAlignZ + fCohZ;
  }

  // 3. Gravity and Celestial forces from active masses
  for (const b of fleet) {
   const wp = craftWorld(b);
   for (const m of activeMasses) {
    if (m.kind !== 4 && !(m.kind >= 5 && m.kind <= 7)) continue;
    const gx = wp[0] - m.x, gy = wp[1] - m.y, gz = wp[2] - m.z;'''

new_birds = '''   // Dynamic Fleet Formation slot (Delta, Echelon, Orbital Ring, Tandem)
   const slot = FleetFormations.getSlot(i, lead, time, b);
   const slotX = slot[0], slotY = slot[1], slotZ = slot[2];

   const escortK = 1.6 + b.k * 0.8;
   const fEscortX = (slotX - b.x) * escortK;
   const fEscortY = (slotY - b.y) * (escortK * 0.85);
   const fEscortZ = (slotZ - b.z) * escortK;

   const fAlignX = alignCount > 0 ? (alignVx / alignCount - b.vx) * 1.4 : 0;
   const fAlignY = alignCount > 0 ? (alignVy / alignCount - b.vy) * 1.1 : 0;
   const fAlignZ = alignCount > 0 ? (alignVz / alignCount - b.vz) * 1.2 : 0;

   const fCohX = cohCount > 0 ? (cohX / cohCount - b.x) * 0.45 : 0;
   const fCohY = cohCount > 0 ? (cohY / cohCount - b.y) * 0.35 : 0;
   const fCohZ = cohCount > 0 ? (cohZ / cohCount - b.z) * 0.45 : 0;

   b.ax = fEscortX + sepX + fAlignX + fCohX;
   b.ay = fEscortY + sepY + fAlignY + fCohY;
   b.az = fEscortZ + sepZ + fAlignZ + fCohZ;
  }

  // 3. Gravity and Celestial forces from active masses (Zero-allocation pass)
  const _rx = routeX(travel), _ry = courseY(travel);
  for (const b of fleet) {
   const wpx = _rx + b.x, wpy = _ry + b.y, wpz = travel + b.z;
   for (const m of activeMasses) {
    if (m.kind !== 4 && !(m.kind >= 5 && m.kind <= 7)) continue;
    const gx = wpx - m.x, gy = wpy - m.y, gz = wpz - m.z;'''
assert old_birds in text, "old_birds not found"
text = text.replace(old_birds, new_birds, 1)
print("4. Replaced updateBirds slot and gravity allocations")

# 5. bodies() active chunk reuse & project parameter optimization
old_bodies = ''' const k0=Math.floor(camera.eye[2]/CHUNK);
 const backRadius = _isMobileDevice ? 18 : (lowQuality ? 16 : 36);
 const fwdRadius = _isMobileDevice ? 32 : (lowQuality ? 28 : 52);
 const active = [];
 for(let k=k0-backRadius;k<=k0+fwdRadius;k++)active.push(chunk(k));
 for(const [k] of chunks)if(k < k0 - 42 || k > k0 + fwdRadius + 16)chunks.delete(k);
 for(const c of active){
  // Frustum-culled distance fade for galaxies & clusters
  for(const g of c.galaxies){
   const pj=project(g);if(!pj||pj[2]>75000)continue;
   const R=g.rad*pj[3];if(R<4.5)continue;
   if(pj[0]+R<-80||pj[0]-R>W+80||pj[1]+R<-80||pj[1]-R>H+80)continue;
   massVis=clamp((75000-pj[2])/30000);if(massVis<=0)continue;
   drawGalaxy(g,region(g.x,g.z),time,pj);massVis=1;
  }
  // BUILD 187: Frustum-culled deep space supply stations & docking pads
  for(const st of (c.stations||[])){
   const pj=project([st.x,st.y,st.z]);
   if(!pj||pj[2]>65000)continue;
   const padR = Math.max(24, (st.r || 650) * pj[3]);
   if(pj[0]+padR<-100||pj[0]-padR>W+100||pj[1]+padR<-100||pj[1]-padR>H+100)continue;
   drawSupplyStation(st,pj,time);
  }
  // Render procedural space events (frustum-culled)
  for(const ev of (c.events||[])){SpaceEventEngine.drawEvent(ev,time);}
  // Frustum-culled space skirmishes
  for(const b of (c.battles||[])){
   const pj=project([b.x,b.y,b.z]);if(!pj||pj[2]>34000)continue;
   if(pj[0]<-250||pj[0]>W+250||pj[1]<-250||pj[1]>H+250)continue;
   drawBattle(b,time);
  }
  // Frustum-culled jump gates
  for(const g of (c.gates||[])){
   const pj=project([g.x,g.y,g.z]);if(!pj||pj[2]>52000)continue;
   const R=Math.max(6,g.r*pj[3]);if(R<5)continue;
   if(pj[0]+R<-40||pj[0]-R>W+40||pj[1]+R<-40||pj[1]-R>H+40)continue;
   massVis=clamp((52000-pj[2])/18000);if(massVis<=0)continue;
   drawGate(g,pj,time);massVis=1;
  }
  // Frustum-culled encounter ships
  for(const s of c.ships){
   const pj=project([s.x,s.y,s.z]);if(!pj||pj[2]>52000)continue;
   const L=s.len*pj[3];if(L<9)continue;
   if(pj[0]+L<-40||pj[0]-L>W+40||pj[1]+L<-40||pj[1]-L>H+40)continue;
   if(pj[2]<18000&&activeShips.length<8)activeShips.push(s);
   massVis=clamp((52000-pj[2])/18000);if(massVis<=0)continue;
   drawShip(s,pj,time);massVis=1;
  }
  // Frustum-culled celestial masses & stars
  for(const m of c.masses){
   const pj=project([m.x,m.y,m.z]);'''

new_bodies = ''' const k0=Math.floor(camera.eye[2]/CHUNK);
 const backRadius = _isMobileDevice ? 18 : (lowQuality ? 16 : 36);
 const fwdRadius = _isMobileDevice ? 32 : (lowQuality ? 28 : 52);
 if (!bodies._active) bodies._active = [];
 const active = bodies._active;
 active.length = 0;
 for(let k=k0-backRadius;k<=k0+fwdRadius;k++){
  const ch = chunk(k);
  if(ch) active.push(ch);
 }
 for(const [k] of chunks)if(k < k0 - 42 || k > k0 + fwdRadius + 16)chunks.delete(k);
 for(const c of active){
  // Frustum-culled distance fade for galaxies & clusters
  for(const g of c.galaxies){
   const pj=project(g);if(!pj||pj[2]>75000)continue;
   const R=g.rad*pj[3];if(R<4.5)continue;
   if(pj[0]+R<-80||pj[0]-R>W+80||pj[1]+R<-80||pj[1]-R>H+80)continue;
   massVis=clamp((75000-pj[2])/30000);if(massVis<=0)continue;
   drawGalaxy(g,region(g.x,g.z),time,pj);massVis=1;
  }
  // BUILD 187: Frustum-culled deep space supply stations & docking pads
  for(const st of (c.stations||[])){
   const pj=project(st);
   if(!pj||pj[2]>65000)continue;
   const padR = Math.max(24, (st.r || 650) * pj[3]);
   if(pj[0]+padR<-100||pj[0]-padR>W+100||pj[1]+padR<-100||pj[1]-padR>H+100)continue;
   drawSupplyStation(st,pj,time);
  }
  // Render procedural space events (frustum-culled)
  for(const ev of (c.events||[])){SpaceEventEngine.drawEvent(ev,time);}
  // Frustum-culled space skirmishes
  for(const b of (c.battles||[])){
   const pj=project(b);if(!pj||pj[2]>34000)continue;
   if(pj[0]<-250||pj[0]>W+250||pj[1]<-250||pj[1]>H+250)continue;
   drawBattle(b,time);
  }
  // Frustum-culled jump gates
  for(const g of (c.gates||[])){
   const pj=project(g);if(!pj||pj[2]>52000)continue;
   const R=Math.max(6,g.r*pj[3]);if(R<5)continue;
   if(pj[0]+R<-40||pj[0]-R>W+40||pj[1]+R<-40||pj[1]-R>H+40)continue;
   massVis=clamp((52000-pj[2])/18000);if(massVis<=0)continue;
   drawGate(g,pj,time);massVis=1;
  }
  // Frustum-culled encounter ships
  for(const s of c.ships){
   const pj=project(s);if(!pj||pj[2]>52000)continue;
   const L=s.len*pj[3];if(L<9)continue;
   if(pj[0]+L<-40||pj[0]-L>W+40||pj[1]+L<-40||pj[1]-L>H+40)continue;
   if(pj[2]<18000&&activeShips.length<8)activeShips.push(s);
   massVis=clamp((52000-pj[2])/18000);if(massVis<=0)continue;
   drawShip(s,pj,time);massVis=1;
  }
  // Frustum-culled celestial masses & stars
  for(const m of c.masses){
   const pj=project(m);'''
assert old_bodies in text, "old_bodies not found"
text = text.replace(old_bodies, new_bodies, 1)
print("5. Replaced bodies active chunk and project direct object passing")

# 6. Starfield CPU fallback clamping to prevent 20ms freeze
old_star_cpu = '''  } else if (eps > 0) {
    const cpuLimit = _isMobileDevice ? Math.min(limit, 450) : limit;'''
new_star_cpu = '''  } else if (eps > 0) {
    const cpuLimit = _isMobileDevice ? Math.min(limit, 350) : Math.min(limit, 1800);'''
assert old_star_cpu in text, "old_star_cpu not found"
text = text.replace(old_star_cpu, new_star_cpu, 1)

old_star_cpu2 = '''  } else {
    const cpuLimit = _isMobileDevice ? Math.min(limit, 450) : limit;'''
new_star_cpu2 = '''  } else {
    const cpuLimit = _isMobileDevice ? Math.min(limit, 350) : Math.min(limit, 1800);'''
assert old_star_cpu2 in text, "old_star_cpu2 not found"
text = text.replace(old_star_cpu2, new_star_cpu2, 1)
print("6. Clamped CPU stars fallback limit")

# 7. bandStars CPU fallback clamping
old_band_cpu1 = '''const maxBandCount = _isMobileDevice ? 240 : bandStars.length;'''
new_band_cpu1 = '''const maxBandCount = _isMobileDevice ? 180 : Math.min(1200, bandStars.length);'''
assert old_band_cpu1 in text, "old_band_cpu1 not found"
text = text.replace(old_band_cpu1, new_band_cpu1)
print("7. Clamped CPU bandStars fallback limit")

# 8. DPR Safety Clamping (Mobile 1.5 default, 1.75 limit in 2k)
old_max_dpr = '''  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    const cap = _isMobileDevice ? 1.75 : (this.tierCap[_GPU.tier] || 2.0);
    if (this.profile === '2k') {
      const limit = _isMobileDevice ? 2.0 : 3.0;
      return Math.min(raw, Math.max(cap, limit));
    }
    if (this.profile === 'balanced') return Math.min(raw, _isMobileDevice ? 1.5 : cap);
    return Math.min(raw, 1.0);
  },'''

new_max_dpr = '''  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    const cap = _isMobileDevice ? 1.75 : (this.tierCap[_GPU.tier] || 2.0);
    if (this.profile === '2k') {
      const limit = _isMobileDevice ? 1.75 : 3.0;
      return Math.min(raw, limit);
    }
    if (this.profile === 'balanced') return Math.min(raw, _isMobileDevice ? 1.5 : cap);
    return Math.min(raw, 1.0);
  },'''
assert old_max_dpr in text, "old_max_dpr not found"
text = text.replace(old_max_dpr, new_max_dpr, 1)
print("8. Clamped getMaxDPR mobile limit to 1.75")

# 9. resize fallback DPR clamping
old_resize_dpr = '''DPR=Math.max(1,(window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(devicePixelRatio||1,2))*qualityScale); window.DPR = DPR;'''
new_resize_dpr = '''DPR=Math.max(1,(window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(devicePixelRatio||1,_isMobileDevice?1.5:2))*qualityScale); window.DPR = DPR;'''
assert old_resize_dpr in text, "old_resize_dpr not found"
text = text.replace(old_resize_dpr, new_resize_dpr, 1)
print("9. Updated resize fallback DPR")

with open(src_path, 'w', encoding='utf-8') as f:
    f.write(text)

# Mirror to Android assets
android_path = r'd:\items\code\projects\starfield\starfield-pub\android\app\src\main\assets\starfield.html'
shutil.copyfile(src_path, android_path)

h1 = hashlib.sha256(open(src_path, 'rb').read()).hexdigest()
h2 = hashlib.sha256(open(android_path, 'rb').read()).hexdigest()
assert h1 == h2, 'Mirror mismatch'

print('SUCCESS! Engine optimization applied and mirrored. SHA256:', h1[:16])
